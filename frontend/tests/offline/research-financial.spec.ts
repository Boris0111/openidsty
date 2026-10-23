import {test,expect,Page} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';

// Synthetic API responses only. No application database writes.
const release='11111111-1111-4111-8111-111111111111';
const summary=(id:string)=>({id,kind:'company',name:id==='company-a'?'合成甲公司':'合成乙公司',summary:'明示合成的流程樣本',reviewed:null});
const fact=(patch:Record<string,unknown>={})=>({observation_id:'current',company_id:'company-a',metric_id:'revenue',label:'營收',value:'9007199254740993.12',unit:'amount',currency:'TWD',basis:'annual',scope:'consolidated',source_family:'tw-mops-summary',share_class:'',period_start:'2025-01-01',period_end:'2025-12-31',revision:2,filed_at:'2026-03-01',source_as_of:null,derived:false,provenance_kind:'official',limitations:'合成數值，不是實際財報。',sources:[{source_url:'https://example.invalid/official',raw_value:'9007199254740.99312',raw_unit:'TWD thousand',multiplier:'1000',filed_at:'2026-03-01',source_as_of:null,accession:'synthetic-filing',tag:'合成營收',locator:{page:4,section:'合成損益表'}}],sources_truncated:false,lineage:[],lineage_truncated:false,formula_version:null,...patch});
async function fixtures(page:Page,{failure=false,delay=false}={}){
  const requests:string[]=[];
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v2/','');requests.push(path+'?'+url.searchParams);
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-17'};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(path==='search')data={items:['company-a','company-b','company-c','company-d','company-e'].map(summary),has_more:false,next_cursor:null};
    else if(path.includes('/financials/observations/')){
      if(failure)return route.fulfill({status:503,json:{message:'來源目前無法讀取，既有研究保留。'}});
      const id=path.split('/').at(-1),old=id==='old';
      const observation=id==='derived'?fact({observation_id:'derived',value:'10',unit:'percent',metric_id:'gross-margin',label:'毛利率',derived:true,formula_version:'financial-v1:gross-margin',lineage:[fact({observation_id:'input'})]}):fact({observation_id:id,value:old?'0':'9007199254740993.12',revision:old?1:2});
      data={as_of:'2026-10-18T01:00:00Z',observation,active_observation_id:'current',revisions:[fact(),fact({observation_id:'old',revision:1,value:'0',filed_at:'2026-02-01'})],has_more:!url.searchParams.has('before_revision'),next_before_revision:1};
    }else if(path.endsWith('/financials')){
      if(delay&&path.includes('company-a'))await new Promise(resolve=>setTimeout(resolve,500));
      const basis=url.searchParams.get('basis'),metric=url.searchParams.get('metric'),cursor=url.searchParams.get('cursor');
      const first=fact({basis,metric_id:metric,label:metric==='eps-basic'?'基本 EPS':'營收',...(metric==='eps-basic'?{unit:'per-share',share_class:'unspecified'}:{})});
      data={as_of:'2026-10-18T01:00:00Z',items:path.includes('company-b')?[]:cursor?[fact({observation_id:'derived',value:'10',derived:true,unit:'percent',metric_id:'gross-margin',label:'毛利率'})]:[first,fact({observation_id:'usd',source_family:'sec-companyfacts',currency:'USD',value:'0',period_start:'2025-02-01',period_end:'2026-01-31',basis})],has_more:!cursor,next_cursor:'synthetic-financial-next',gaps:path.includes('company-b')?['尚未取得此口徑，不代表零。']:[],source_selection_gap:'主要來源尚未核對，各來源分開。'};
    }else if(path==='compare'){
      const ids=url.searchParams.get('company_ids')!.split(',');
      data={as_of:'2026-10-18T01:00:00Z',policy:'保留原幣與實際期間，不自動換匯。',companies:ids.map(id=>({...summary(id),roles:[{segment_id:'segment-thermal',description:'合成取熱角色'}],products:[{product_id:'product-sample',name:'合成產品',role_name:'合成交付',conditions:[]}],business_model:'[合成產品](/next?focus=product-sample)',risks:'合成供應風險',gaps:['尚未完成全部深研'],truncated:false})),metrics:[{metric_id:'revenue',label:'營收',comparable:false,reasons:['幣別與實際期間不同','主要申報來源未核對'],values:[fact(),fact({company_id:ids[1],observation_id:'usd',currency:'USD',period_start:'2025-02-01',period_end:'2026-01-31'})],missing_company_ids:[],candidates_truncated_company_ids:[]},{metric_id:'gross-margin',label:'毛利率',comparable:true,reasons:[],values:ids.map((id,index)=>fact({company_id:id,observation_id:'ratio-'+index,value:'10',unit:'percent',metric_id:'gross-margin',label:'毛利率'})),missing_company_ids:[],candidates_truncated_company_ids:[]},{metric_id:'eps-basic',label:'基本 EPS',comparable:false,reasons:['股別／ADR 尚未核對'],values:[],missing_company_ids:ids,candidates_truncated_company_ids:[]}]};
    }else if(path==='events'||path==='observations'){
      if(failure)return route.fulfill({status:503,json:{message:'資訊目前無法讀取。'}});
      const rumor=path==='observations',cursor=url.searchParams.get('cursor');
      data={as_of:'2026-10-18T01:00:00Z',items:cursor?[]:[{id:1,title:rumor?'合成未證實消息':'合成官方發布',excerpt:'明示合成資訊，非實際事件。',url:'https://example.invalid/event',source_name:'合成來源',source_nature:rumor?'rumor':'official',published_at:null,reported_at:null,published_precision:'unknown',date_unknown:true,period:null,entities:[{entity_id:'company-a',name:'合成甲公司',kind:'company',relevance:'mention'}],entities_truncated:false}],has_more:!cursor,next_cursor:'synthetic-event-next',classification_limit:'自動分類仍需核對'};
    }else if(path.startsWith('companies/'))data={...summary(path.split('/')[1]),markdown:'## 商業模式\n\n保留合成研究內容',content:{listings:[{ticker:'SAMPLE',market:'US'}]},claims:[],related:[],assets:[],truncated:false};
    else data={id:'product-sample',kind:'product',name:'合成產品',summary:'合成產品',markdown:'',content:{},claims:[],related:[],assets:[],truncated:false};
    return route.fulfill({json:{release_id:release,schema_version:'research-v1',data}}).catch(()=>{});
  });return requests;
}

test('精確原值、原幣／原期間分組，來源修訂與歷史分頁保留固定版本',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?focus=company-a&release_id='+release);
  await expect(page.locator('.rf-series')).toHaveCount(2);
  await expect(page.locator('.rf-series').first()).toContainText('TWD');await expect(page.locator('.rf-series').nth(1)).toContainText('USD');
  await expect(page.locator('[title$="9007199254740993.12 TWD"]').first()).toBeAttached();
  await expect(page.locator('.rf-series').nth(1)).toContainText('0 USD');await expect(page.locator('.rf-series').nth(1)).toContainText('2025-02-01 ～ 2026-01-31');
  await page.locator('.rf-series button').first().click();const sources=page.getByRole('region',{name:'財務來源與修訂'});
  await expect(sources).toContainText('申報日：2026-03-01');await expect(sources).toContainText('倍率 1000');await expect(sources).toContainText('頁碼：4');
  await expect(sources).toContainText('合成數值，不是實際財報。');
  await sources.getByRole('button',{name:/修訂 1：/}).click();await expect(sources).toContainText('這筆是歷史數值');await expect(sources).toContainText('0 TWD');
  await sources.getByRole('button',{name:'更早的修訂'}).click();await expect(page).toHaveURL(/before_revision=1/);
  await sources.getByRole('button',{name:'查看最新有效值'}).click();await expect(sources).toContainText('這是此期間的最新有效值');await expect(page).not.toHaveURL(/before_revision=/);
  expect(requests.filter(path=>path.includes('/financials')).every(path=>path.includes('release_id='+release))).toBe(true);
});

test('分享的財務連結在補上研究版本後仍保留錨點，並落在財務區',async({page})=>{
  await fixtures(page);await page.setViewportSize({width:390,height:400});
  await page.goto('/next?focus=company-a#company-data');
  await expect(page).toHaveURL(new RegExp('release_id='+release+'#company-data$'));
  await expect(page.locator('.rf-series').first()).toBeVisible();
  await expect(page.locator('#company-data')).toBeInViewport();
});

test('累計不連線、基本 EPS 股別明示；按需讀衍生公式、原始觀測及財務分頁',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?focus=company-a&release_id='+release);
  await page.getByRole('combobox',{name:'財務口徑',exact:true}).selectOption('ytd');await expect(page.locator('.rf-series').first()).toContainText('累計');
  await expect(page.locator('.rf-trend svg line')).toHaveCount(2); // axes only, no fabricated cumulative trend
  await page.getByRole('combobox',{name:'財務指標',exact:true}).selectOption('eps-basic');await expect(page.locator('.rf-series').first()).toContainText('股別未核對');
  await page.getByRole('button',{name:'下一頁財務'}).click();await expect(page).toHaveURL(/financial_cursor=/);
  await page.locator('.rf-series button').first().click();const sources=page.getByRole('region',{name:'財務來源與修訂'});
  await expect(sources).toContainText('毛利 ÷ 營收 × 100');await sources.getByRole('button',{name:'查閱這筆原始觀測'}).click();await expect(page).toHaveURL(/observation_id=input/);
  await page.getByRole('combobox',{name:'財務口徑',exact:true}).selectOption('quarterly');await expect(page).not.toHaveURL(/financial_cursor=|observation_id=/);
  expect(requests.some(path=>path.includes('basis=ytd')&&path.includes('metric=eps-basic'))).toBe(true);
});

test('比較可選 2–4 家、業務與產品、缺值與不可比較原因，不在前端排名換匯',async({page})=>{
  await fixtures(page);await page.goto('/next?view=compare&release_id='+release);
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await page.getByRole('button',{name:'加入合成甲公司',exact:true}).click();
  await expect(page.getByText('請選擇 2–4 家不同公司。')).toBeVisible();
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await page.getByRole('button',{name:'加入合成乙公司',exact:true}).first().click();
  await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('幣別與實際期間不同');
  await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('這些值在目前基準下可比較');await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('缺值不代表零');
  await expect(page.locator('.rf-company-comparison')).toContainText('合成供應風險');
  await expect(page.locator('.rf-company-comparison a').filter({hasText:'合成產品'}).first()).toHaveAttribute('href',/release_id=/);
  await page.goto('/next?view=compare&release_id='+release+'&company_ids=company-a,company-b,company-c,company-d');
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await expect(page.getByRole('region',{name:'公司比較'}).getByRole('button',{name:'加入合成甲公司'})).toBeDisabled();
  await page.locator('.rf-compare-selected button').first().click();await expect(page.locator('.rf-compare-selected li')).toHaveCount(3);
});

test('傳聞獨立查詢、未知發布日與提及標籤、日期篩選及返回分頁',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?focus=company-a&release_id='+release);
  expect(requests.some(path=>path.startsWith('observations?'))).toBe(false);
  await page.getByRole('navigation',{name:'公司數據與資訊'}).getByRole('button',{name:'官方與報導'}).click();
  await expect(page.getByRole('region',{name:'官方與報導清單'})).toContainText('合成官方發布');await expect(page.locator('.rf-event-list')).toContainText('發布日期未知；不以收錄時間代替');
  await page.goto('/next?view=observations&release_id='+release);
  await expect(page.getByRole('navigation',{name:'事件類型'}).getByRole('link',{name:'傳聞觀察'})).toHaveAttribute('aria-current','page');
  await expect(page.getByRole('region',{name:'傳聞觀察清單'})).toContainText('不會變成正式供應或客戶關係');await expect(page.locator('.rf-event-list')).toContainText('內容提及');
  await page.getByLabel('起始日期').fill('2026-10-01');await expect(page).toHaveURL(/period_from=2026-10-01/);await expect(page.getByText('日期篩選仍保留發布日未知的資訊，並逐筆明示。')).toBeVisible();
  await page.getByRole('button',{name:'下一頁資訊'}).click();await expect(page.getByText('此範圍尚未取得傳聞觀察。')).toBeVisible();
  await page.goBack();await expect(page.locator('.rf-event-list')).toContainText('合成未證實消息');
  expect(requests.filter(path=>path.startsWith('observations?')).every(path=>path.includes('source_nature=rumor')&&path.includes('release_id='+release))).toBe(true);
});

test('來源失效仍能閱讀研究；資訊失效有可理解狀態',async({page})=>{
  await fixtures(page,{failure:true});await page.goto('/next?focus=company-a&release_id='+release+'&observation_id=current');
  await expect(page.getByRole('region',{name:'財務來源與修訂'})).toContainText('來源目前無法讀取');await expect(page.locator('.rs-prose')).toContainText('保留合成研究內容');
  await page.getByRole('navigation',{name:'公司數據與資訊'}).getByRole('button',{name:'官方與報導'}).click();await expect(page.getByRole('region',{name:'官方與報導清單'})).toContainText('資訊目前無法讀取');
});

test('手機、鍵盤、分享 URL 與快速換公司不殘留前一家公司數值',async({page,context})=>{
  await fixtures(page,{delay:true});await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=company-a&release_id='+release);
  const basis=page.getByRole('combobox',{name:'財務口徑',exact:true});await basis.focus();await page.keyboard.press('Home');await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/basis=quarterly/);await expect(page.locator('.rf-series')).toHaveCount(2);
  await expectNoHorizontalOverflow(page);
  const shared=await context.newPage();await fixtures(shared);await shared.goto(page.url());await expect(shared.getByRole('combobox',{name:'財務口徑',exact:true})).toHaveValue('quarterly');await shared.close();
  await page.getByLabel('搜尋公司、產品、環節或題材').fill('合成');await page.locator('.search-results').getByRole('link').nth(1).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('合成乙公司');await expect(page.locator('.rf-series')).toHaveCount(0);await expect(page.getByText('尚未取得此口徑，不代表零。')).toBeVisible();
  await page.waitForTimeout(600);await expect(page.locator('.rf-series')).toHaveCount(0);
});
