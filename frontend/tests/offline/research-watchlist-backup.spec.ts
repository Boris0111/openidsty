import {test,expect,Page} from '@playwright/test';
import {readFile} from 'node:fs/promises';
import {server,stored,card,key,shown} from './watchlist-fixture';

const local={kind:'theme',id:'theme-liquid-cooling',name:'合成液冷題材',seen:{research:'t1',values:'i1',events:0}};
const backup=(targets:unknown[],extra:Record<string,unknown>={})=>JSON.stringify({format:'industryflow-research-watchlist',schema_version:2,exported_at:'2026-10-18T00:00:00Z',targets,...extra});
async function open(page:Page,targets:unknown[]=[local]){
  await server(page);
  await page.addInitScript(([k,value])=>{if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');localStorage.setItem(k,value)}},[key,JSON.stringify({schema_version:2,targets,v1_migrated:true})] as const);
  await page.goto('/next?view=watchlist&release_id='+shown);await expect(page.getByRole('region',{name:'備份與交換'})).toBeVisible();
}
const upload=(page:Page,body:string|Buffer)=>page.getByLabel('匯入收藏備份').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:Buffer.isBuffer(body)?body:Buffer.from(body)});

test('匯出只含身分、名稱與已讀基準',async({page})=>{
  await open(page);
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'匯出收藏 JSON'}).click()]);
  expect(download.suggestedFilename()).toMatch(/^industryflow-watchlist-\d{4}-\d{2}-\d{2}\.json$/);
  const text=await readFile((await download.path())!,'utf8');const data=JSON.parse(text);
  expect(data).toMatchObject({format:'industryflow-research-watchlist',schema_version:2,targets:[local]});
  expect(text).not.toMatch(/markdown|summary|password|token_hash|csrf/);
});

test('合併預覽列出新增、重複、無效與失效項目；確認後既有已讀不被覆寫',async({page})=>{
  await open(page);
  await upload(page,backup([{...local,seen:{research:'older',values:'older',events:0}},{kind:'company',id:'company-sample',name:'合成公司',seen:{research:'r1',values:'v1',events:0}},
    {kind:'company',id:'company-gone',name:'已封存公司',seen:{research:null,values:null,events:null}},{kind:'segment',id:'segment-x',name:'不支援類型',seen:{research:null,values:null,events:null}},{kind:'company',id:'BAD ID',name:'格式錯誤',seen:{}}]));
  const preview=page.getByLabel('匯入預覽');
  await expect(preview).toContainText('匯入預覽（共 5 項）');await expect(preview).toContainText('新增 1 項：合成公司');
  await expect(preview).toContainText('已存在 1 項，保留此瀏覽器的已讀狀態');
  await expect(preview).toContainText('無法解析 2 項，不匯入：不支援類型、格式錯誤');
  await expect(preview).toContainText('目前已發布研究找不到 1 項');await expect(preview).toContainText('已封存公司');
  expect((await stored(page)).targets).toHaveLength(1);  // Nothing changes before confirmation.
  await preview.getByRole('button',{name:'確認合併'}).click();
  await expect(page.getByText('已合併 1 項',{exact:false})).toBeVisible();
  const targets=(await stored(page)).targets;
  expect(targets.map((t:{id:string})=>t.id)).toEqual(['theme-liquid-cooling','company-sample']);
  expect(targets[0].seen).toEqual(local.seen);
  await expect(card(page,'合成公司')).toContainText('研究無變更');
});

test('超過大小、危險欄位、超額與格式錯誤整份拒絕，原清單保留',async({page})=>{
  const many=Array.from({length:99},(_,index)=>({kind:'company',id:`company-many-${index}`,name:`合成 ${index}`,seen:{research:null,values:null,events:null}}));
  await open(page,many);
  const extra=(id:string)=>({kind:'company',id,name:id,seen:{research:null,values:null,events:null}});
  const cases:[string|Buffer,RegExp][]=[
    [Buffer.alloc(1024*1024+1,32),/超過 1 MiB/],
    ['{"format":"industryflow-research-watchlist","schema_version":2,"targets":[],"__proto__":{"polluted":true}}',/不安全的欄位/],
    [backup(Array.from({length:101},(_,index)=>extra(`company-over-${index}`))),/101 項，超過 100 項上限/],
    [backup([extra('company-new-a'),extra('company-new-b')]),/合併後會有 101 項/],
    ['{not json',/不是有效的 JSON/],
    [JSON.stringify({schema_version:2,targets:[]}),/不是 IndustryFlow 收藏備份/],
  ];
  for(const [body,message] of cases){
    await upload(page,body);
    await expect(page.getByRole('region',{name:'備份與交換'}).getByText(message)).toBeVisible();
    await expect(page.getByLabel('匯入預覽')).toHaveCount(0);
    expect((await stored(page)).targets).toHaveLength(99);
  }
  expect(await page.evaluate(()=>({} as Record<string,unknown>).polluted)).toBeUndefined();
});
