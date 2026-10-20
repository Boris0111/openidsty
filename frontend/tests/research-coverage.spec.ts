import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

const release='88888888-8888-4888-8888-888888888888';
const zero={not_researched:0,not_public:0,not_obtained:0,not_applicable:0,unclassified:0};
const basic={...zero,entity_id:'company-synthetic-basic',kind:'company',name:'合成基本公司',reviewed:null,research_depth:'basic',claims:0,implied_not_researched:true,not_researched:1,unclassified:1,gaps:[{status:null,reason:'尚未完成合成獨立深研。'}]};
const deep={...zero,entity_id:'company-synthetic-deep',kind:'company',name:'合成深研公司',reviewed:'2026-10-16',research_depth:'deep',claims:3,implied_not_researched:false,not_public:1,not_obtained:1,gaps:[{status:'not-public',reason:'合成公司未揭露產品別營收'},{status:'not-obtained',reason:'合成年報入口回應 403'}]};
const product={...zero,entity_id:'product-synthetic',kind:'product',name:'合成產品',reviewed:'2026-10-16',research_depth:null,claims:1,implied_not_researched:false,not_applicable:1,gaps:[{status:'not-applicable',reason:'合成分類頁不承載公司財務'}]};
const totals=[{...zero,kind:'company',entities:2,basic_companies:1,not_researched:1,not_public:1,not_obtained:1,unclassified:1},{...zero,kind:'product',entities:1,basic_companies:0,not_applicable:1}];
const scopes={as_of:'2026-10-18T02:00:00Z',counting:'合成計數說明：直接事件、背景、公司提及與未知日期分開。',review_note:'待核對候選只在管理端呈現。',rows:[
  {id:'thermal',kind:'segment',name:'合成散熱',research_available:true,direct_30d:1,direct_90d:2,background_90d:3,unknown_date:4,company_mentions_90d:5,routine_90d:6,gaps:['合成來源待設定'],technical_reviewed:'2026-10-16',technical_gaps:['合成技術缺口'],
    technical_documents:[{id:'doc-synthetic',title:'合成技術文件',doc_kind:'normative',adopted:[{version_id:'v1',label:'1.0',reviewed:'2026-10-16',read_scope:'只讀合成章節',locators:[{id:'loop',section:'合成迴路章節'}]}],review_counts:{adopted:1,pending:2},
      candidates:[{observation_id:9,official_version:'1.1',fetched_at:'2026-10-17T00:00:00Z',status:'pending',reason:null}],citations:[{claim_id:'loop-scope',version_id:'v1',locator:'loop'}]}],assessment_candidates:null},
  {id:'liquid-cooling',kind:'theme',name:'合成液冷題材',research_available:true,direct_30d:0,direct_90d:0,background_90d:0,unknown_date:1,company_mentions_90d:0,routine_90d:0,gaps:[],technical_reviewed:null,technical_gaps:[],technical_documents:[],
    assessment_candidates:{baseline:'2026-10-07',dated_count:7,undated_count:1,samples:[{id:42,title:'合成待納入事件',published_at:'2026-10-12T00:00:00Z'}]}}]};

for(const mobile of [false,true])test(`維護覆蓋分開缺口類型與待核對候選${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize({width:mobile?390:1440,height:mobile?844:1000});
  const requested:string[]=[];
  await page.route('**/api/admin/**',async route=>{
    const url=new URL(route.request().url());requested.push(url.pathname+url.search);
    if(url.pathname.endsWith('/session'))await route.fulfill({json:{authenticated:true,csrf_token:'synthetic-csrf'}});
    else if(url.pathname.endsWith('/releases'))await route.fulfill({json:{items:[],active_release_id:release,has_more:false}});
    else if(url.pathname.endsWith('/drafts'))await route.fulfill({json:{items:[]}});
    else if(url.pathname==='/api/admin/coverage/entities'){
      const status=url.searchParams.get('status'),cursor=url.searchParams.get('cursor');
      const items=status==='not-public'?[deep]:cursor?[product]:[basic,deep];
      await route.fulfill({json:{release_id:release,totals,items,has_more:!status&&!cursor,next_cursor:!status&&!cursor?'company:company-synthetic-deep':null,counting:'合成缺口計數說明'}})}
    else if(url.pathname==='/api/admin/coverage')await route.fulfill({json:scopes});
    else await route.fulfill({status:404,json:{message:'Unexpected synthetic request'}});
  });
  await page.goto('/admin');await page.getByRole('button',{name:'研究覆蓋',exact:true}).click();
  const summary=page.getByRole('table',{name:'已發布研究的缺口分類（各類物件合計）'});
  await expect(summary.getByRole('row',{name:/公司/})).toContainText('basic 1');
  await expect(page.getByText('合成公司未揭露產品別營收')).toBeVisible();
  await expect(page.getByRole('cell',{name:/未研究\s*basic 公司尚未深研/})).toBeVisible();
  await expect(page.getByRole('cell',{name:/未分類\s*尚未完成合成獨立深研/})).toBeVisible();
  await expect(page.getByRole('link',{name:'合成深研公司'})).toHaveAttribute('href',new RegExp('focus=company-synthetic-deep&release_id='+release));
  await page.getByRole('button',{name:'載入更多研究物件'}).click();await expect(page.getByText('合成分類頁不承載公司財務')).toBeVisible();
  await page.getByLabel('缺口').selectOption('not-public');
  await expect(page.getByRole('link',{name:'合成基本公司'})).toHaveCount(0);await expect(page.getByRole('link',{name:'合成深研公司'})).toBeVisible();
  expect(requested).toContain('/api/admin/coverage/entities?status=not-public');
  await mkdir('../.work/research-coverage-review',{recursive:true});
  await page.screenshot({path:`../.work/research-coverage-review/${mobile?'mobile':'desktop'}-gaps.png`,fullPage:true});

  await page.getByRole('button',{name:'環節與題材',exact:true}).click();
  const thermal=page.getByRole('row',{name:/合成散熱/});
  for(const value of ['1／2','3','4','5'])await expect(thermal).toContainText(value);
  await page.getByText(/合成散熱：技術查核 2026-10-16；待核對文件 2/).click();
  await expect(page.getByText(/已核對 1.0（查核 2026-10-16）：合成迴路章節/)).toBeVisible();
  await expect(page.getByText('論述定位：loop-scope → v1／loop')).toBeVisible();
  await expect(page.getByText(/待核對：1.1/)).toBeVisible();
  await page.getByText(/合成液冷題材.*待納入判讀事件 7（未知日期 1）/).click();
  await expect(page.getByRole('link',{name:'合成待納入事件'})).toHaveAttribute('href','/events/42');
  await mkdir('../.work/research-coverage-review',{recursive:true});
  await page.screenshot({path:`../.work/research-coverage-review/${mobile?'mobile':'desktop'}.png`,fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
