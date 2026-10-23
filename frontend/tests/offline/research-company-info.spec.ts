import {test,expect,Page} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';

// Explicitly synthetic reader responses; never seed the application DB.
const release='11111111-1111-4111-8111-111111111111';
const summary=(id:string)=>({id,kind:'company',name:id==='company-a'?'合成甲公司':'合成乙公司',summary:'明示合成的流程樣本',reviewed:null});
async function fixtures(page:Page,{failure=false}={}){
  const requests:string[]=[];
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v2/','');requests.push(path+'?'+url.searchParams);
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-17'};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(path==='search')data={items:['company-a','company-b','company-c','company-d','company-e'].map(summary),has_more:false,next_cursor:null};
    else if(path==='compare'){
      const ids=url.searchParams.get('company_ids')!.split(',');
      data={companies:ids.map((id,index)=>({...summary(id),roles:[{segment_id:'segment-thermal',description:'合成取熱角色'}],products:index?[]:[{product_id:'product-sample',name:'合成產品',role_name:'合成交付',conditions:[]}],
        business_model:index?null:'[合成產品](/next?focus=product-sample)',risks:index?null:'合成供應風險',claims:[],gaps:['尚未完成全部深研'],truncated:false}))};
    }else if(path==='events'||path==='observations'){
      if(failure)return route.fulfill({status:503,json:{message:'資訊目前無法讀取。'}});
      const rumor=path==='observations',cursor=url.searchParams.get('cursor');
      data={as_of:'2026-10-18T01:00:00Z',items:cursor?[]:[{id:1,title:rumor?'合成未證實消息':'合成官方發布',excerpt:'明示合成資訊，非實際事件。',url:'https://example.invalid/event',source_name:'合成來源',source_nature:rumor?'rumor':'official',published_at:null,reported_at:null,published_precision:'unknown',date_unknown:true,period:null,entities:[{entity_id:'company-a',name:'合成甲公司',kind:'company',relevance:'mention'}],entities_truncated:false}],has_more:!cursor,next_cursor:'synthetic-event-next',classification_limit:'自動分類仍需核對'};
    }else if(path.startsWith('companies/'))data={...summary(path.split('/')[1]),markdown:'## 商業模式\n\n保留合成研究內容',content:{listings:[{ticker:'SAMPLE',market:'US'}]},claims:[],related:[],assets:[],truncated:false};
    else data={id:'product-sample',kind:'product',name:'合成產品',summary:'合成產品',markdown:'',content:{},claims:[],related:[],assets:[],truncated:false};
    return route.fulfill({json:{release_id:release,schema_version:'research-v1',data}}).catch(()=>{});
  });return requests;
}

test('公司頁只列近期資訊，舊財務分享連結仍可開啟且不顯示財務',async({page})=>{
  const requests=await fixtures(page);
  await page.goto('/next?focus=company-a&release_id='+release+'&panel=financials&basis=quarterly&observation_id=current#company-data');
  const section=page.locator('#company-data');await expect(section.locator('.rs-section-top h2')).toHaveText('合成甲公司：近期資訊');
  const tabs=section.getByRole('navigation',{name:'公司近期資訊'}).getByRole('button');
  await expect(tabs).toHaveText(['官方與報導','傳聞觀察']);await expect(tabs.first()).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('region',{name:'官方與報導清單'})).toContainText('合成官方發布');
  await expect(page.getByText('基本財務')).toHaveCount(0);
  expect(requests.some(path=>path.includes('/financials'))).toBe(false);
});

test('比較可選 2–4 家，只並列業務、角色、產品與風險，缺口明示',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?view=compare&release_id='+release);
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await page.getByRole('button',{name:'加入合成甲公司',exact:true}).click();
  await expect(page.getByText('請選擇 2–4 家不同公司。')).toBeVisible();
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await page.getByRole('button',{name:'加入合成乙公司',exact:true}).first().click();
  await expect(page.locator('.rf-company-comparison')).toContainText('合成供應風險');
  await expect(page.locator('.rf-company-comparison')).toContainText('尚未完成風險深研。');
  await expect(page.locator('.rf-company-comparison a').filter({hasText:'合成產品'}).first()).toHaveAttribute('href',/release_id=/);
  await expect(page.getByLabel('比較財務口徑')).toHaveCount(0);await expect(page.getByRole('region',{name:'財務比較結果'})).toHaveCount(0);
  expect(requests.filter(path=>path.startsWith('compare?')).every(path=>!path.includes('basis='))).toBe(true);
  await page.goto('/next?view=compare&release_id='+release+'&company_ids=company-a,company-b,company-c,company-d');
  await page.getByLabel('搜尋加入比較的公司').fill('合成');await expect(page.getByRole('region',{name:'公司比較'}).getByRole('button',{name:'加入合成甲公司'})).toBeDisabled();
  await page.locator('.rf-compare-selected button').first().click();await expect(page.locator('.rf-compare-selected li')).toHaveCount(3);
});

test('傳聞獨立查詢、未知發布日與提及標籤、日期篩選及返回分頁',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?focus=company-a&release_id='+release);
  expect(requests.some(path=>path.startsWith('observations?'))).toBe(false);
  await page.getByRole('navigation',{name:'公司近期資訊'}).getByRole('button',{name:'官方與報導'}).click();
  await expect(page.getByRole('region',{name:'官方與報導清單'})).toContainText('合成官方發布');await expect(page.locator('.rf-event-list')).toContainText('發布日期未知；不以收錄時間代替');
  await page.goto('/next?view=observations&release_id='+release);
  await expect(page.getByRole('navigation',{name:'事件類型'}).getByRole('link',{name:'傳聞觀察'})).toHaveAttribute('aria-current','page');
  await expect(page.getByRole('region',{name:'傳聞觀察清單'})).toContainText('不會變成正式供應或客戶關係');await expect(page.locator('.rf-event-list')).toContainText('內容提及');
  await page.getByLabel('起始日期').fill('2026-10-01');await expect(page).toHaveURL(/period_from=2026-10-01/);await expect(page.getByText('日期篩選仍保留發布日未知的資訊，並逐筆明示。')).toBeVisible();
  await page.getByRole('button',{name:'下一頁資訊'}).click();await expect(page.getByText('此範圍尚未取得傳聞觀察。')).toBeVisible();
  await page.goBack();await expect(page.locator('.rf-event-list')).toContainText('合成未證實消息');
  expect(requests.filter(path=>path.startsWith('observations?')).every(path=>path.includes('source_nature=rumor')&&path.includes('release_id='+release))).toBe(true);
});

test('資訊來源失效仍能閱讀研究，並有可理解狀態',async({page})=>{
  await fixtures(page,{failure:true});await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=company-a&release_id='+release);
  await expect(page.locator('.rs-prose')).toContainText('保留合成研究內容');
  await expect(page.getByRole('region',{name:'官方與報導清單'})).toContainText('資訊目前無法讀取');
  await expectNoHorizontalOverflow(page);
});
