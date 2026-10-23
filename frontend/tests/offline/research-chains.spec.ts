import {test,expect,Page} from '@playwright/test';
import {expectNoHorizontalOverflow} from './layout';

// Explicitly synthetic supply-chain responses; never seed the application DB.
const release='22222222-2222-4222-8222-222222222222';
const trail=[{id:'segment-thermal',kind:'segment',name:'散熱',url:'/?layer=ai-server&segment=thermal'},{id:'application-sample',kind:'application',name:'合成供應鏈',url:null}];
const steps=[{label:'取熱',here:true},{label:'排熱',here:false}];
const detail=(id:string,kind:string,name:string,extra:Record<string,unknown>={})=>({id,kind,name,summary:'合成供應鏈樣本',reviewed:null,
  markdown:'## 研究內容\n\n合成研究樣本',content:{},claims:[],related:[],assets:[],truncated:false,legacy_return:null,trail:[],chain:null,chains:[],...extra});

async function fixtures(page:Page){
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v2/','');
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-20'};
    else if(path==='chains')data={items:[
      {id:'application-sample',name:'合成供應鏈',summary:'合成供應鏈樣本',question:'熱怎麼送出去？',segments:[{id:'segment-thermal',name:'散熱'}],steps:['取熱','排熱'],assets:[]},
      {id:'application-two',name:'第二條合成供應鏈',summary:'合成樣本',question:null,segments:[{id:'segment-test',name:'測試'}],steps:[],assets:[]}]};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[],edges:[],truncated:false,continue_from:[]};
    else if(path.endsWith('/financials'))data={as_of:'2026-10-20T00:00:00Z',items:[],has_more:false,next_cursor:null,gaps:[],source_selection_gap:null};
    else if(path==='applications/application-sample')data=detail('application-sample','application','合成供應鏈',{trail:trail.slice(0,1),content:{question:'熱怎麼送出去？'},
      chain:{question:'熱怎麼送出去？',diagram:null,steps:[{label:'取熱',note:'晶片端',products:[{id:'product-sample',name:'合成產品',companies:[{id:'company-sample',name:'合成公司'}]}]},{label:'排熱',note:null,products:[]}],
        other_products:[{id:'product-other',name:'其他合成產品',companies:[]}]}});
    else if(path==='products/product-sample')data=detail('product-sample','product','合成產品',{trail,chains:[{id:'application-sample',name:'合成供應鏈',question:'熱怎麼送出去？',steps,products:[]}]});
    else if(path==='companies/company-sample')data=detail('company-sample','company','合成公司',{chains:[
      {id:'application-sample',name:'合成供應鏈',question:'熱怎麼送出去？',steps,products:[{id:'product-sample',name:'合成產品'}]},
      {id:'application-two',name:'第二條合成供應鏈',question:null,steps:[],products:[]}]});
    else if(path==='segments/segment-thermal')data=detail('segment-thermal','segment','散熱',{legacy_return:{url:'/?layer=ai-server&segment=thermal',label:'回到「散熱」產業地圖'}});
    else return route.fulfill({status:404,json:{message:'找不到這筆研究。'}});
    await route.fulfill({json:{release_id:release,schema_version:'research-v1',data}}).catch(()=>{});
  });
}

test('供應鏈索引與無圖解的鏈頁依步驟呈現產品與證據',async({page})=>{
  await fixtures(page);await page.goto('/next');
  await expect(page.locator('h1')).toHaveText('供應鏈');
  await expect(page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'供應鏈'})).toHaveAttribute('aria-current','page');
  await expect(page.locator('.rs-chain-card')).toHaveCount(2);await expect(page.locator('.rs-chain-card').filter({hasText:'合成供應鏈'}).first()).toContainText('取熱 → 排熱');
  await page.locator('.rs-chain-card').filter({hasText:'熱怎麼送出去？'}).click();
  await expect(page).toHaveURL(/focus=application-sample/);await expect(page.locator('h1')).toHaveText('熱怎麼送出去？');
  await expect(page.getByText('這條供應鏈尚無圖解，先以文字步驟說明交付順序。')).toBeVisible();
  await expect(page.getByRole('list',{name:'供應鏈步驟'}).getByRole('listitem')).toHaveText([/取熱晶片端/,/排熱/]);
  await expect(page.locator('.rs-chain-product').filter({hasText:'合成產品'}).first()).toContainText('有產品證據：合成公司');
  await expect(page.locator('.rs-chain-other')).toContainText('尚未核對公司的產品證據');
  await expect(page.getByRole('navigation',{name:'研究位置'}).getByRole('link')).toHaveText(['產業地圖','散熱']);
});

test('產品頁位置列標出所在步驟並回到供應鏈；公司頁獨立列出所屬供應鏈',async({page})=>{
  await fixtures(page);await page.setViewportSize({width:390,height:844});
  await page.goto('/next?focus=product-sample&release_id='+release);
  const strip=page.getByRole('complementary',{name:'所在供應鏈'});
  await expect(strip).toBeInViewport();await expect(strip.locator('[aria-current=step]')).toHaveText('取熱');
  await expect(strip.getByRole('link',{name:'看完整圖解與產品'})).toHaveAttribute('href',/focus=application-sample/);
  await expectNoHorizontalOverflow(page);
  await page.goto('/next?focus=company-sample&release_id='+release);
  const chains=page.getByRole('region',{name:'所屬供應鏈與產品'});
  await expect(chains.getByRole('listitem')).toHaveCount(2);
  await expect(chains.getByRole('listitem').first()).toContainText('有產品證據：合成產品');
  await expect(chains.getByRole('listitem').nth(1)).toContainText('依既有環節角色列入，尚未核對產品證據');
  await expect(page.locator('.rs-chain')).toHaveCount(0);await expect(page.getByRole('complementary',{name:'所在供應鏈'})).toHaveCount(0);
});

test('環節的研究網址轉回產業地圖',async({page})=>{
  await fixtures(page);await page.goto('/next?focus=segment-thermal&release_id='+release);
  await expect(page).toHaveURL(/\/\?layer=ai-server&segment=thermal$/);
});
