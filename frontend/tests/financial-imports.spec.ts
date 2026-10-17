import {test,expect} from '@playwright/test';
import {mkdir,readFile} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

for(const mobile of [false,true])test(`官方補錄預覽、明確確認與同 key 重試${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize({width:mobile?390:1440,height:mobile?844:1000});
  const id='77777777-7777-4777-8777-777777777777';let attempts=0;let key='';let previewCount=0;
  const batch={batch_id:id,payload_hash:'a'.repeat(64),status:'preview',document:{title:'合成官方財報測試',source_url:'https://www.sec.gov/synthetic-test',filed_at:'2026-02-01',source_as_of:null},items:[{company_id:'company-synthetic',label:'營收',period_start:'2025-01-01',period_end:'2025-12-31',basis:'annual',scope:'consolidated',currency:'TWD',unit:'amount',share_class:'',raw_value:'1234',raw_unit:'新台幣千元',multiplier:'1000',value:'1234000',previous_value:'1200000',changed:true,locator:'合成測試第 12 頁，合併損益表營業收入列',supersedes:null,revision_note:''}],result:null};
  await page.route('**/api/admin/**',async route=>{
    const request=route.request(),url=new URL(request.url());
    if(url.pathname.endsWith('/session'))await route.fulfill({json:{authenticated:true,csrf_token:'synthetic-test-csrf'}});
    else if(url.pathname.endsWith('/releases'))await route.fulfill({json:{items:[],active_release_id:id,has_more:false}});
    else if(url.pathname.endsWith('/drafts'))await route.fulfill({json:{items:[]}});
    else if(url.pathname==='/api/admin/financial-imports'){
      previewCount++;expect(request.headers()['content-type']).toBe('text/csv');expect(request.postData()).toContain('synthetic,csv');
      await route.fulfill({status:201,json:batch});
    }else if(url.pathname.endsWith('/confirm')){
      const body=request.postDataJSON();expect(body.confirmed_official_source).toBe(true);expect(body.payload_hash).toBe(batch.payload_hash);
      attempts++;if(attempts===1){key=request.headers()['idempotency-key'];await route.fulfill({status:503,json:{message:'合成測試：暫時無法寫入，請重試。'}})}
      else {expect(request.headers()['idempotency-key']).toBe(key);await route.fulfill({json:{...batch,status:'confirmed',result:{new_revisions:1,active_changes:1}}})}
    }else await route.fulfill({status:404,json:{message:'Unexpected synthetic test request'}});
  });
  await page.goto('/admin');await page.getByRole('button',{name:'財務補錄',exact:true}).click();
  await page.getByLabel('財務檔案（最多 1 MiB）').setInputFiles({name:'synthetic.csv',mimeType:'text/csv',buffer:Buffer.from('synthetic,csv\nonly,test')});
  await expect(page.getByLabel('輸入格式')).toHaveValue('csv');
  const pendingDownload=page.waitForEvent('download');await page.getByRole('button',{name:'下載空白範本'}).click();
  const download=await pendingDownload;expect(download.suggestedFilename()).toBe('official-financial-import-template.csv');
  expect(await readFile((await download.path())!,'utf8')).toContain('document_source_id');
  await page.getByRole('button',{name:'驗證並預覽財務'}).click();
  await expect(page.getByRole('heading',{name:'核對匯入差異'})).toBeVisible();
  await expect(page.getByRole('cell',{name:/1234 新台幣千元/})).toBeVisible();
  const confirm=page.getByRole('button',{name:'確認財務入庫',exact:true});await expect(confirm).toBeDisabled();
  await page.getByRole('checkbox').check();await expect(confirm).toBeDisabled();
  await page.getByLabel('財務確認理由').fill('已核對合成測試官方原文、頁碼與千元倍率。');
  await mkdir('../.work/financial-import-review',{recursive:true});
  await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  await page.screenshot({path:`../.work/financial-import-review/${mobile?'mobile':'desktop'}-preview.png`,fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await confirm.click();await expect(page.locator('.ra-financial-import [role="alert"]')).toContainText('請重試');
  await expect(page.getByLabel('財務確認理由')).toHaveValue('已核對合成測試官方原文、頁碼與千元倍率。');
  await confirm.click();await expect(page.locator('.ra-financial-import [role="status"]')).toContainText('新增 1 筆數值修訂');
  await page.getByLabel('財務匯入內容').fill('changed synthetic,csv');
  await expect(page.getByRole('heading',{name:'核對匯入差異'})).toHaveCount(0);
  expect(previewCount).toBe(1);expect(attempts).toBe(2);
});

test('財務代理拒絕匿名確認與跨站，大小有限制',async({request,baseURL})=>{
  const origin=baseURL!;
  expect((await request.post('/api/admin/financial-imports',{headers:{Origin:'https://untrusted.invalid'},data:{}})).status()).toBe(403);
  expect((await request.post('/api/admin/financial-imports',{headers:{Origin:origin},data:{}})).status()).toBe(401);
  expect((await request.post('/api/admin/financial-imports/77777777-7777-4777-8777-777777777777/confirm',{headers:{Origin:origin},data:{}})).status()).toBe(401);
  expect((await request.post('/api/admin/financial-imports',{headers:{Origin:origin,'Content-Type':'text/csv'},data:'x'.repeat(1024*1024+1)})).status()).toBe(413);
});
