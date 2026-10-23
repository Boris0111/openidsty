import {test,expect,Page} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';

const release='11111111-1111-4111-8111-111111111111';
const summary=(id:string,name:string)=>({id,kind:id.split('-')[0],name,summary:'明示合成的內容閱讀樣本',reviewed:'2026-10-17'});
const roles=[summary('segment-compute','運算'),summary('segment-networking','網通')];
const product=summary('product-sample','測試冷板'),other=summary('product-other','測試換熱設備'),company=summary('company-sample','合成公司');
const source={document_id:'document-sample',revision_id:'fixed-old-version',title:'合成原始來源',url:'https://example.invalid/official',locator:'chapter-one',applicable_period:'合成 2025 年資料，不是新申報',stance:'supporting'};
const claim={id:'sample',statement:'合成測試主張：僅支持產品能力',confidence:'inference',conditions:['不代表已知客戶交易'],reviewed:'2026-10-17',evidence:[source]};
async function fixtures(page:Page,failed=false){
  const requests:string[]=[];
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),pathname=url.pathname.replace('/api/v2/','');requests.push(url.pathname+url.search);
    if(pathname.startsWith('assets/'))return route.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="180"><rect width="400" height="180" fill="#edf5f7"/><text x="30" y="80">Synthetic research diagram</text></svg>'});
    if(pathname.startsWith('documents/')&&failed)return route.fulfill({status:404,json:{message:'固定引用不可用'}});
    let data:unknown;
    if(pathname==='manifest')data={published_at:'2026-10-17'};
    else if(pathname.includes('/financials'))data={as_of:'2026-10-17T12:00:00Z',items:[],has_more:false,next_cursor:null,gaps:[],source_selection_gap:null};
    else if(pathname==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(pathname.startsWith('documents/'))data={...source,document_kind:'draft',published:'2025-01-01',read_scope:'只讀第一章，未核對量產',locators:[{id:'chapter-one',page:4,section:'合成章節',excerpt:'合成合法摘錄，僅供測試固定版本。'},{id:'chapter-two',excerpt:'不應顯示的另一章'}],parser_error:'不得顯示的維護資料'};
    else if(pathname.startsWith('companies/'))data={...company,markdown:['供應角色','研究界線','產品與用途','商業模式','客戶與供應商','競爭與替代','業務曝險','風險','財務可取性'].map(heading=>'## '+heading+'\n\n合成'+heading+'說明，僅用於流程測試。').join('\n\n'),content:{roles:roles.map(row=>({segment_id:row.id,description:'合成跨環節角色'}))},claims:[claim],related:roles,assets:[],truncated:false};
    else if(pathname.startsWith('products/'))data={...product,markdown:'## 定義與用途\n\n完整產品研究：材質與壓降需一起驗證。\n\n## 供應角色與公司\n\n[合成公司](/next?focus=company-sample)',content:{},claims:[claim],related:[company],assets:[],truncated:false};
    else data={...summary('concept-sample','合成技術圖解'),markdown:'## 中文解釋\n\n原創圖解的說明。\n\n## 適用範圍\n\n僅為合成測試。',content:{scope:'限於同一設備邊界',comparisons:[{left:product.id,right:other.id,conditions:['相同回路與流量'],limitations:['兩者互補，不可用額定量排名']}]},claims:[claim],related:[product,other,company],assets:['desktop','mobile'].map(kind=>({id:'asset-test-'+kind,url:'/api/v2/assets/'+kind+'?release_id='+release,alt:'合成研究圖解',attribution:'合成原創資產'})),truncated:false};
    return route.fulfill({json:{release_id:release,schema_version:'research-v1',data}});
  });return requests;
}

test('公司模板保留八項實質段落與跨環節角色，不增空白研究或內部資訊',async({page})=>{
  await fixtures(page);await page.goto('/next?focus=company-sample');
  await expect(page.locator('.rs-company-roles a')).toHaveText(['運算','網通']);
  const nav=page.getByRole('navigation',{name:'公司研究內容'});await expect(nav.getByRole('link')).toHaveCount(9);
  await nav.getByRole('link',{name:'商業模式',exact:true}).click();await expect(page).toHaveURL(/#rs-section-company-sample-/);
  await expect(page.getByRole('heading',{name:'商業模式',exact:true})).toBeInViewport();
  for(const heading of ['產品與用途','客戶與供應商','競爭與替代','業務曝險','風險','財務可取性'])await expect(page.getByRole('heading',{name:heading,exact:true})).toBeAttached();
  await expect(page.locator('body')).not.toContainText(/parser_error|不得顯示的維護資料|進階資訊|待核對佇列/);
});

test('產品完整說明與術語比較可閱讀，圖解適應手機並能返回原研究',async({page})=>{
  await fixtures(page);await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=concept-sample');
  await expect(page.getByRole('img',{name:'合成研究圖解'})).toBeVisible();await expect(page.locator('.rs-illustration source')).toHaveAttribute('srcset',/assets\/mobile/);
  await expect(page.getByRole('region',{name:'技術比較'})).toBeVisible();
  const comparison=page.locator('.rs-technical-comparisons');await expect(comparison).toContainText('相同回路與流量');await expect(comparison).toContainText('互補');
  await comparison.getByRole('link',{name:'測試冷板',exact:true}).click();await expect(page.locator('.rs-prose')).toContainText('材質與壓降需一起驗證');
  await page.locator('.rs-prose').getByRole('link',{name:'合成公司',exact:true}).click();await expect(page.locator('.rs-detail > h2')).toHaveText('合成公司');
  await page.goBack();await page.goBack();await expect(page.locator('.rs-detail > h2')).toHaveText('合成技術圖解');
  await expectNoHorizontalOverflow(page);
});

test('引用按需讀固定版本、章節與頁碼，失效保留研究而不查 latest',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?focus=product-sample&release_id='+release);
  await expect(page.locator('.rs-citation')).toContainText('chapter-one');expect(requests.some(path=>path.includes('/documents/'))).toBe(false);
  await page.getByText('查閱這份引用',{exact:true}).click();await expect(page.locator('.rs-citation-reading')).toContainText('頁碼：4');await expect(page.locator('.rs-citation-reading')).toContainText('只讀第一章');
  await expect(page.locator('.rs-citation-reading')).toContainText('文件性質：草案');
  await expect(page.locator('.rs-citation-reading')).toContainText('合成合法摘錄');await expect(page.locator('.rs-citation-reading')).not.toContainText('另一章');
  expect(requests.filter(path=>path.includes('/documents/'))).toEqual(['/api/v2/documents/document-sample/revisions/fixed-old-version?release_id='+release]);
  await expect(page.locator('body')).not.toContainText('不得顯示的維護資料');
  await page.unroute('**/api/v2/**');const failures=await fixtures(page,true);await page.reload();await page.getByText('查閱這份引用',{exact:true}).click();
  await expect(page.locator('.rs-citation')).toContainText('原判斷與引用位置保留');await expect(page.locator('.rs-prose')).toContainText('材質與壓降需一起驗證');
  expect(failures.filter(path=>path.includes('/documents/')).every(path=>path.includes('/fixed-old-version?')&&!path.includes('latest'))).toBe(true);
});

test('圖解失效仍有原創說明、技術條件與來源',async({page})=>{
  await fixtures(page);await page.route('**/api/v2/assets/**',route=>route.abort());await page.goto('/next?focus=concept-sample');
  await expect(page.getByText('圖解目前無法讀取，可先閱讀下方說明與來源。')).toBeVisible();await expect(page.locator('.rs-prose')).toContainText('原創圖解的說明');await expect(page.locator('.rs-citation a')).toBeVisible();
});
