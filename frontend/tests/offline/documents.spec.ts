import {test,expect} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';
import {installOfflineApi} from './fixture-data';

const definition={title:'測試用管理介面文件',publisher:'離線測試', 'doc-kind':'formal-specification',versions:[{id:'reviewed-v1',label:'1.0',url:'https://example.org/official.pdf',published:null,'published-precision':'unknown',reviewed:'2026-10-16','read-scope':'僅核讀管理介面章節','access-limitations':'未讀完整規格與客戶測試',scope:'不證明商業採用',locators:[{id:'management',section:'1.1 管理範圍',excerpt:'必要短摘錄'}]}]};
test('手機引用頁保留固定章節及適用範圍，不展示監測佇列',async({page})=>{
  await installOfflineApi(page);
  await page.route('**/api/technical-documents/test-document?*',route=>route.fulfill({json:{id:'test-document',active:true,definition,source:{id:'offline',name:'離線來源',status:'failed',last_success:null,last_attempt:'2026-10-16T00:00:00Z',error:'HTTP 403'},history:{total:2,offset:0,limit:10,items:[{id:2,official_version:null,content_hash:'hash',parser_version:'test-v1',url:'https://example.org/official.pdf',fetched_at:'2026-10-16T00:00:00Z',data:{read_scope:'自動取得，尚未核對'},review:{status:'pending',reviewed:null,reason:null,version_id:null}},{id:1,official_version:'1.0',content_hash:'baseline',parser_version:'test-v1',url:'https://example.org/official.pdf',fetched_at:'2026-10-15T00:00:00Z',data:{read_scope:'人工已讀範圍'},review:{status:'no-impact',reviewed:'2026-10-16',reason:'未改變既有研究',version_id:null}}]}}}));
  await page.setViewportSize({width:390,height:844});await page.goto('/technical-documents/test-document?version=reviewed-v1#locator-management');
  await expect(page.getByRole('heading',{name:'1.0'})).toBeVisible();await expect(page.locator('#locator-management')).toContainText('必要短摘錄');
  await expect(page.getByText('未讀完整規格與客戶測試')).toBeVisible();
  await expect(page.getByText('不證明商業採用',{exact:false})).toBeVisible();
  for(const text of ['進階資訊','HTTP 403','內容觀測與人工核對'])await expect(page.getByText(text,{exact:true})).toHaveCount(0);
  await expectNoHorizontalOverflow(page,2);
});
test('失效固定版本明示缺口，未知文件可以重試而不捏造文件內容',async({page})=>{
  await installOfflineApi(page);
  await page.route('**/api/technical-documents/test-document?*',r=>r.fulfill({json:{id:'test-document',active:true,definition,source:{id:'offline',name:'離線來源',status:'manual',last_success:null,error:null},history:{total:0,limit:10,offset:0,items:[]}}}));
  await page.goto('/technical-documents/test-document?version=missing');await expect(page.getByText('找不到引用的版本，請返回研究內容核實。')).toBeVisible();await expect(page.getByRole('heading',{name:'1.0'})).toHaveCount(0);
});


test('論述來源按需取得指定版本摘錄；失效引用不替換成最新版',async({page})=>{
  await installOfflineApi(page);let requests=0;
  const profile={'product-boundary':'產品介面邊界','adoption-conditions':['需通過互通測試'],bottlenecks:['測試尚未完成'],'substitution-limits':['不能直接替換'],claims:[{id:'test-claim',statement:'只支持管理介面，不能推論客戶採用',confidence:'well-supported',evidence:[{'document-id':'test-document','version-id':'reviewed-v1',locator:'management'}]},{id:'missing',statement:'失效版本的引用',confidence:'needs-verification',evidence:[{'document-id':'test-document','version-id':'missing',locator:'management'}]}],'evidence-gaps':['缺少客戶驗收'],reviewed:'2026-10-16'};
  await page.route('**/api/themes/liquid-cooling',async r=>{const {theme}=await import('./fixture-data');return r.fulfill({json:{...theme,'technical-profile':profile}})});
  await page.route('**/api/technical-documents/test-document?*',r=>{requests++;return r.fulfill({json:{definition}})});
  await page.goto('/themes/liquid-cooling#technical');await expect(page.getByRole('heading',{name:'導入條件與限制'})).toBeVisible();expect(requests).toBe(0);
  const claims=page.locator('.technical-claim');await claims.first().locator('summary').focus();await page.keyboard.press('Enter');
  await expect(claims.first().getByRole('link',{name:'測試用管理介面文件 ↗'})).toHaveAttribute('href','https://example.org/official.pdf');
  await expect(claims.first().getByRole('blockquote')).toContainText('必要短摘錄');await expect(claims.first()).toContainText('僅核讀管理介面章節');expect(requests).toBe(1);
  await claims.nth(1).locator('summary').click();await expect(claims.nth(1)).toContainText('這項引用的版本或章節暫時無法確認');await expect(claims.nth(1).getByRole('link')).toHaveCount(0);
});
