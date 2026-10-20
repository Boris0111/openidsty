import {test,expect,Page} from '@playwright/test';

// Explicitly synthetic reader responses; never seed the application DB.
const release='11111111-1111-4111-8111-111111111111';
const row=(id:string,name:string)=>({id,kind:id.split('-')[0],name,summary:'離線導覽樣本',reviewed:null});
const application=row('application-sample','測試應用'),role=row('role-sample','測試供應角色'),product=row('product-sample','測試產品'),company=row('company-sample','測試公司');
async function fixtures(page:Page){
  const requests:string[]=[];
  await page.route('**/api/v2/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v2/','');requests.push(path+'?'+url.searchParams);
    let data:unknown;
    if(path==='manifest')data={published_at:'2026-10-17'};
    else if(path.includes('/financials'))data={as_of:'2026-10-17T12:00:00Z',items:[],has_more:false,next_cursor:null,gaps:[],source_selection_gap:null};
    else if(path==='graphs')data={root:url.searchParams.get('root'),nodes:[product,company,role],edges:[{id:'capability:test',source:company.id,target:product.id,kind:'capability',mechanism:'只證明產品能力',conditions:['不指認具名交易'],claims:[]},{id:'classification:test',source:role.id,target:product.id,kind:'classification',mechanism:'產品分類',conditions:[],claims:[]}],truncated:true,continue_from:[]};
    else if(path.includes('/')){
      const id=path.split('/')[1];if(id==='company-missing')return route.fulfill({status:404,json:{message:'找不到這筆研究。'}});
      if(id==='product-slow')await new Promise(resolve=>setTimeout(resolve,500));
      data={...row(id,id===company.id?'測試公司':id===product.id?'測試產品':'測試研究'),markdown:'## 研究內容\n\n離線研究樣本',content:{},claims:[],related:[],assets:[],truncated:false,legacy_return:{url:'/?layer=ai-server&segment=thermal',label:'回到「散熱」產業地圖'},
        trail:id.startsWith('company-')?[]:[{id:'segment-thermal',kind:'segment',name:'散熱',url:'/?layer=ai-server&segment=thermal'},{id:application.id,kind:'application',name:application.name,url:null}]};
    }else{
      const items=path==='applications'?[application]:path==='roles'?[role]:path==='products'?[product]:path==='companies'?(url.searchParams.get('market')==='US'?[]:[company]):path==='concepts'?[]:[row(path==='themes'?'theme-sample':'segment-thermal',path==='themes'?'測試題材':'測試環節')];
      data={items,has_more:path==='companies'&&!url.searchParams.has('cursor')&&items.length>0,next_cursor:'synthetic-next'};
    }
    await route.fulfill({json:{release_id:release,schema_version:'research-v1',data}}).catch(()=>{});
  });return requests;
}

test('七類目錄、篩選、分頁與返回保留 URL 及固定版本',async({page})=>{
  const requests=await fixtures(page);await page.goto('/next?view=applications');
  const nav=page.getByRole('navigation',{name:'研究目錄分類'});await expect(nav.getByRole('link')).toHaveCount(7);
  await nav.getByRole('link',{name:'公司',exact:true}).click();
  await page.getByLabel('上市市場').selectOption('TW');await page.getByLabel('供應角色或環節').selectOption(role.id);await page.getByLabel('應用範圍').selectOption(application.id);
  await expect(page.locator('.rs-directory li')).toHaveCount(1);await page.getByRole('link',{name:'下一頁',exact:true}).click();
  await expect(page).toHaveURL(/cursor=synthetic-next/);const directoryUrl=page.url();
  await page.locator('.rs-directory li a').click();await expect(page.locator('.rs-detail > h2')).toHaveText('測試公司');
  await page.getByRole('link',{name:'回原目錄'}).click();await expect(page).toHaveURL(directoryUrl);
  await page.getByLabel('上市市場').selectOption('US');await expect(page).not.toHaveURL(/cursor=/);await expect(page.getByText('此範圍尚未列出研究',{exact:false})).toBeVisible();
  await nav.getByRole('link',{name:'術語',exact:true}).click();await expect(page.getByText('此分類尚未建立研究',{exact:false})).toBeVisible();await expect(page).not.toHaveURL(/market=|role=|category=|cursor=/);
  expect(requests.filter(path=>path.startsWith('companies?')).some(path=>path.includes('market=TW')&&path.includes('role=role-sample')&&path.includes('category=application-sample')&&path.includes('cursor=synthetic-next'))).toBe(true);
  expect(new URL(page.url()).searchParams.get('release_id')).toBe(release);
});

test('連線可由鍵盤選取、分享及返回，手機無溢出且 resize 保留縮放',async({page,context})=>{
  await fixtures(page);await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=product-sample');
  const picker=page.getByLabel('閱讀連線');await picker.focus();await picker.selectOption('capability:test');
  await expect(page.getByRole('region',{name:'連線說明'})).toContainText('不指認具名交易');await expect(page).toHaveURL(/edge=capability%3Atest/);
  const shared=await context.newPage();await fixtures(shared);await shared.goto(page.url());await expect(shared.getByLabel('閱讀連線')).toHaveValue('capability:test');await shared.close();
  await page.getByRole('button',{name:'放大關係圖'}).click();const zoom=await page.getByLabel('關係圖縮放比例').textContent();
  await page.setViewportSize({width:1100,height:900});await page.setViewportSize({width:390,height:844});await expect(page.getByLabel('關係圖縮放比例')).toHaveText(zoom!);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await picker.selectOption('classification:test');await expect(page).toHaveURL(/edge=classification%3Atest/);await page.goBack();await expect(picker).toHaveValue('capability:test');
  await page.getByRole('button',{name:'閱讀測試公司',exact:true}).click();await expect(page.locator('.rs-detail > h2')).toHaveText('測試公司');await expect(page).not.toHaveURL(/edge=/);
});

test('安全返回位置丟棄外部或管理參數，慢回應不覆蓋與未知物件可恢復',async({page})=>{
  await fixtures(page);
  await page.goto('/next?'+new URLSearchParams({focus:product.id,from:'/?layer=ai-server&segment=thermal&relation=thermal-odm&next=https://evil.invalid&admin=1'}));
  const crumbs=page.getByRole('navigation',{name:'研究位置'});
  await expect(crumbs.getByRole('link')).toHaveText(['產業地圖','散熱','測試應用']);await expect(crumbs.locator('[aria-current=page]')).toHaveText('測試產品');
  await expect(crumbs.getByRole('link',{name:'散熱'})).toHaveAttribute('href','/?layer=ai-server&segment=thermal&relation=thermal-odm');
  await page.goto('/next?'+new URLSearchParams({focus:product.id,from:'https://evil.invalid',index:'/admin?view=companies'}));
  await expect(crumbs.getByRole('link',{name:'散熱'})).toHaveAttribute('href','/?layer=ai-server&segment=thermal');await expect(page.getByRole('link',{name:'回原目錄'})).toHaveCount(0);
  await page.goto('/next?focus=product-slow');await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'公司',exact:true}).click();await page.waitForTimeout(600);await expect(page.locator('h1')).toHaveText('公司');await expect(page.locator('.rs-detail')).toHaveCount(0);
  await page.goto('/next?focus=company-missing');await expect(page.locator('.rs-error')).toContainText('找不到這筆研究');await expect(page.locator('.rs-error').getByRole('link',{name:'回產業地圖'})).toHaveAttribute('href','/');
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'公司',exact:true}).click();await expect(page.locator('.rs-directory li')).toHaveCount(1);
});
