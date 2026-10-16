import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

for(const mobile of [false,true])test(`草稿編輯、預覽與 stale revision 保留輸入${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  if(mobile)await page.setViewportSize({width:390,height:844});
  const id='11111111-1111-4111-8111-111111111111',base='22222222-2222-4222-8222-222222222222';
  const path='industry-map/companies/company-auras.md';
  let revision=1,conflict=false,summary='合成既有摘要';
  const frontmatter=()=>({'entity-id':'company-auras',kind:'company','name-zh':'雙鴻',summary,claims:[{id:'keep'}]});
  const draft=()=>({draft_id:id,base_release_id:base,revision,schema_version:'research-draft-v1',files:{[path]:'synthetic markdown'},assets:{}});
  await page.route('**/api/admin/**',async route=>{
    const request=route.request(),url=new URL(request.url());let data:unknown;
    if(url.pathname.endsWith('/session'))data={authenticated:true,csrf_token:'synthetic-csrf'};
    else if(url.pathname==='/api/admin/drafts')data={items:[{draft_id:id,current_revision:revision,status:'editing',created_at:'2026-10-17'}]};
    else if(url.pathname.endsWith('/document'))data={path,content:'synthetic markdown',frontmatter:frontmatter(),markdown:'## 合成研究\n測試內文'};
    else if(url.pathname.endsWith('/validate'))data={valid:true,errors:[],revision};
    else if(url.pathname.endsWith('/preview'))data={data:{id:'company-auras',kind:'company',name:'雙鴻',summary,markdown:'## 合成研究\n測試內文',content:{gaps:['合成測試界線']},claims:[],related:[],assets:[],truncated:false},graph:{root:'company-auras',nodes:[],edges:[],truncated:false,continue_from:[]}};
    else if(request.method()==='PATCH'){
      const body=request.postDataJSON();expect(body.changes[0].frontmatter.claims).toEqual([{id:'keep'}]);
      expect(request.headers()['if-match']).toBe(`"${revision}"`);
      if(conflict){await route.fulfill({status:409,json:{message:'草稿已有較新修訂，請先比對差異；原內容未被覆寫。'}});return}
      summary=body.changes[0].frontmatter.summary;revision++;data=draft();
    }else data=draft();
    await route.fulfill({json:data});
  });
  await page.goto('/admin');
  await page.getByLabel('工作草稿').selectOption(id);
  await page.getByLabel('摘要',{exact:true}).fill('合成新摘要');
  await expect(page.getByRole('button',{name:'閱讀預覽'})).toBeDisabled();
  await page.getByRole('button',{name:'儲存修訂'}).click();
  await expect(page.getByRole('status')).toContainText('已儲存修訂 2');
  await page.getByRole('button',{name:'閱讀預覽'}).click();
  await expect(page.locator('.rs-detail')).toContainText('合成新摘要');
  await mkdir('../.work/editor-review',{recursive:true});
  await page.getByRole('heading',{name:'草稿工作台'}).click();
  await page.screenshot({path:`../.work/editor-review/${mobile?'mobile':'desktop'}-preview.png`,fullPage:true});
  conflict=true;
  await page.getByLabel('摘要',{exact:true}).fill('不得遺失的本機輸入');
  await page.getByRole('button',{name:'儲存修訂'}).click();
  await expect(page.locator('.ra-error[role="alert"]')).toContainText('較新修訂');
  await expect(page.getByLabel('摘要',{exact:true})).toHaveValue('不得遺失的本機輸入');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await mkdir('../.work/editor-review',{recursive:true});
  await page.screenshot({path:`../.work/editor-review/${mobile?'mobile':'desktop'}.png`,fullPage:true});
});

test('真實管理入口未設定 owner 時顯示本機設定說明',async({page})=>{
  await page.goto('/admin');
  await expect(page.getByRole('heading',{name:'草稿工作台'})).toBeVisible();
  await expect(page.getByText('尚未設定維護者。',{exact:false})).toBeVisible();
  await expect(page.getByRole('button',{name:'儲存修訂'})).toHaveCount(0);
});

test('資產代理有獨立 owner 邊界且未知管理路徑不轉送',async({request,baseURL})=>{
  const path='/api/admin/drafts/asset-upload?path=industry-map/assets/test.svg';
  const content='<svg xmlns="http://www.w3.org/2000/svg"/>';
  expect((await request.post(path,{data:content,headers:{Origin:baseURL!,'Content-Type':'image/svg+xml'}})).status()).toBe(401);
  expect((await request.post(path,{data:content,headers:{Origin:'https://evil.example','Content-Type':'image/svg+xml'}})).status()).toBe(403);
  expect((await request.get('/api/admin/unknown-resource')).status()).toBe(404);
});
