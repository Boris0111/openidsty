import {test,expect,Page} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';
import {mkdir} from 'node:fs/promises';
const first='11111111-1111-4111-8111-111111111111',second='22222222-2222-4222-8222-222222222222';

async function fixture(page:Page){
  const state={active:first,generation:1,value:'100',slow:false,offline:false,wrong:false,noStore:false};
  const requests:{path:string;release:string|null;conditional:string|undefined}[]=[];
  const profile=(id:string,release:string)=>({id,kind:id.split('-')[0],name:release===first?'版本一公司':'版本二公司',summary:release===first?'第一版研究內容':'第二版研究內容',reviewed:null,markdown:'## 商業模式\n\n固定版本的研究說明',content:{listings:[{ticker:'SAMPLE',market:'US'}]},related:[],assets:[],claims:[{id:'one',statement:release===first?'第一版判斷':'第二版判斷',confidence:'inference',reviewed:'2026-10-18',conditions:[],evidence:[{document_id:'document-test',revision_id:release===first?'fixed-one':'fixed-two',title:'固定研究引用',url:'https://example.invalid/source',locator:'one',applicable_period:'合成期間'}]}]});
  // Events are the dynamic data inside a pinned release; their title carries the current synthetic value.
  const event=()=>({id:1,title:'合成動態事件 '+state.value,excerpt:'明示合成資訊。',url:'https://example.invalid/event',source_name:'合成來源',source_nature:'official',published_at:'2026-10-18T01:00:00Z',reported_at:null,published_precision:'day',date_unknown:false,period:null,entities:[],entities_truncated:false});
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v2/',''),release=url.searchParams.get('release_id')||state.active;
    const conditional=route.request().headers()['if-none-match'];requests.push({path,release:url.searchParams.get('release_id'),conditional});
    if(state.offline&&path!=='manifest')return route.fulfill({status:503,json:{message:'合成服務中斷'},headers:{'Cache-Control':'no-store'}});
    const dynamic=path==='events'||path==='observations';
    const tag='"'+path+':'+release+(dynamic?':'+state.value:'')+'"';
    const headers={'Cache-Control':path==='manifest'||state.noStore&&dynamic?'no-store':dynamic?'public,max-age=30':'public,max-age=86400',ETag:tag};
    if(path!=='manifest'&&conditional===tag)return route.fulfill({status:304,headers});
    if(state.slow&&path==='companies/company-cache'&&release===first)await new Promise(resolve=>setTimeout(resolve,600));
    let data:unknown;
    if(path==='manifest')data={generation:state.generation,published_at:'2026-10-18'};
    else if(path==='graphs')data={root:'company-cache',nodes:[profile('company-cache',release)],edges:[],truncated:false,continue_from:[]};
    else if(dynamic)data={as_of:'2026-10-18T01:00:00Z',items:path==='events'?[event()]:[],has_more:false,next_cursor:null,classification_limit:'自動分類仍需核對'};
    else if(path.startsWith('documents/'))data={locators:[{id:'one',excerpt:release===first?'第一版固定引用':'第二版固定引用'}],read_scope:'合成已讀範圍'};
    else data=profile(path.split('/')[1],release);
    return route.fulfill({headers,json:{release_id:state.wrong&&path==='companies/company-cache'?second:release,schema_version:'research-v1',data}}).catch(()=>{});
  });return {state,requests};
}

test('發布與還原須明確採用，整頁同版；舊慢回應與舊事件快取不倒退',async({page})=>{
  const {state,requests}=await fixture(page);await page.goto('/next?'+new URLSearchParams({focus:'company-cache',release_id:first,index:'/next?view=companies&market=TW&cursor=old-page&release_id='+first}));
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');await expect(page.locator('.rf-event-list')).toContainText('合成動態事件 100');
  state.active=second;state.generation=2;state.slow=true;
  await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.getByRole('button',{name:'載入新版研究'})).toBeVisible();
  await expect(page.locator('.rs-detail')).toContainText('第一版判斷');expect(requests.some(row=>row.release===second)).toBe(false);
  await mkdir('../.work/research-cache-review',{recursive:true});await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:'../.work/research-cache-review/desktop-update-synthetic.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});await expectNoHorizontalOverflow(page);await page.screenshot({path:'../.work/research-cache-review/mobile-update-synthetic.png',fullPage:false});
  await page.getByRole('button',{name:'載入新版研究'}).click();await expect(page).toHaveURL(new RegExp('release_id='+second));
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本二公司');await expect(page.locator('.rs-detail')).toContainText('第二版判斷');
  await expect(page.getByRole('link',{name:'回原目錄'})).toHaveAttribute('href',new RegExp('release_id='+second));await expect(page.getByRole('link',{name:'回原目錄'})).not.toHaveAttribute('href',/cursor=/);
  await page.waitForTimeout(700);await expect(page.locator('.rs-detail > h2')).toHaveText('版本二公司');
  state.slow=false;state.active=first;state.generation=3;state.value='250';
  await page.getByRole('button',{name:'檢查更新',exact:true}).click();await page.getByRole('button',{name:'載入新版研究'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');await expect(page.locator('.rf-event-list')).toContainText('合成動態事件 250');
  await expect(page.locator('.rs-detail')).not.toContainText('第二版判斷');
});

// Requests fired by the last tick may still be reaching the route handler; take a count only once it holds still.
async function settledCount(rows:unknown[]){let last=-1;await expect.poll(()=>{const now=rows.length,same=now===last;last=now;return same},{intervals:[300]}).toBe(true);return rows.length}

test('可見時每 60 秒查 manifest，隱藏時停止，回來後只提示而不換版',async({page})=>{
  await page.clock.install();const {state,requests}=await fixture(page);await page.goto('/next?focus=company-cache&release_id='+first);
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');
  const before=requests.filter(row=>row.path==='manifest').length;state.active=second;
  await page.clock.fastForward(60050);await expect(page.getByRole('button',{name:'載入新版研究'})).toBeVisible();
  expect(requests.filter(row=>row.path==='manifest').length).toBeGreaterThan(before);
  await settledCount(requests);
  await page.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'hidden'});document.dispatchEvent(new Event('visibilitychange'))});
  const hidden=requests.length;await page.clock.fastForward(120050);expect(requests.length).toBe(hidden);
  await page.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'visible'});document.dispatchEvent(new Event('visibilitychange'))});
  await expect.poll(()=>requests.filter(row=>row.path==='manifest').length).toBeGreaterThan(before+1);
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');
});

test('事件最多 30 秒，304 保留內容；新資料會重新顯示',async({page})=>{
  await page.clock.install();const {state,requests}=await fixture(page);await page.goto('/next?focus=company-cache&release_id='+first);
  const list=page.locator('.rf-event-list');await expect(list).toContainText('合成動態事件 100');
  await page.clock.fastForward(30050);await expect.poll(()=>requests.filter(row=>row.path==='events').length).toBe(2);
  expect(requests.filter(row=>row.path==='events')[1].conditional).toBeTruthy();await expect(list).toContainText('合成動態事件 100');
  state.value='350';await page.clock.fastForward(30050);await expect(list).toContainText('合成動態事件 350');
});

test('固定引用按需載入，更新失敗保留成功內容並可重試',async({page})=>{
  const {state,requests}=await fixture(page);await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=company-cache&release_id='+first);
  await expect(page.locator('.rf-event-list')).toContainText('合成動態事件 100');expect(requests.some(row=>row.path.startsWith('documents/'))).toBe(false);
  await page.locator('.rs-citation summary').click();await expect(page.locator('.rs-citation-reading')).toContainText('第一版固定引用');
  expect(requests.filter(row=>row.path.startsWith('documents/'))).toHaveLength(1);
  state.offline=true;await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.getByText('目前無法更新，先保留上次成功讀取的內容。',{exact:false}).first()).toBeVisible();
  await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');await expect(page.locator('.rf-event-list')).toContainText('合成動態事件 100');
  await mkdir('../.work/research-cache-review',{recursive:true});await page.screenshot({path:'../.work/research-cache-review/mobile-stale.png',fullPage:false});
  state.offline=false;await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.getByText('目前無法更新，先保留上次成功讀取的內容。',{exact:false})).toHaveCount(0);
  await expectNoHorizontalOverflow(page);
});

test('版本錯誤回應不成為研究或成功快取，修正後重試可恢復',async({page})=>{
  const {state}=await fixture(page);state.wrong=true;await page.goto('/next?focus=company-cache&release_id='+first);
  await expect(page.locator('.rs-error')).toContainText('研究版本不一致');await expect(page.locator('.rs-detail > h2')).toHaveCount(0);
  state.wrong=false;await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.locator('.rs-detail > h2')).toHaveText('版本一公司');
});

test('動態 no-store 回應不導致密集重送，仍以有界間隔更新',async({page})=>{
  await page.clock.install();const {state,requests}=await fixture(page);state.noStore=true;
  await page.goto('/next?focus=company-cache&release_id='+first);await expect(page.locator('.rf-event-list')).toContainText('合成動態事件 100');
  await page.clock.fastForward(5000);expect(requests.filter(row=>row.path==='events')).toHaveLength(1);
  await page.clock.fastForward(30050);await expect.poll(()=>requests.filter(row=>row.path==='events').length).toBe(2);
});
