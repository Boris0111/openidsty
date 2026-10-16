import {test,expect,Page} from '@playwright/test';
import {installOfflineApi} from './fixture-data';
const key='industryflow.theme-watchlist.v1';
const base={theme_id:'liquid-cooling',available:true,name:'液冷',current_version_id:1,version_number:1,reviewed:'2026-10-07',assessment_summary:'只支持具名產品',indicator_token:'i1',candidate_token:'c1',candidate_count:1,unknown_date_count:1,indicator_count:1,available_indicator_count:1,indicator_summary:[{id:'sample',name:'產品值',kind:'direct',period:'2026 Q2',revision:1}],pending_summary:'1 則待納入；1 則新收錄發布日待確認（不代表新發生）',source_warnings:[] as {source_id:string;kind:string;message:string}[]};
async function follow(page:Page){await page.goto('/themes');await page.getByRole('button',{name:'加入此裝置關注'}).click();await page.getByRole('navigation').getByRole('link',{name:'此裝置關注'}).click()}

test('已讀只保存顯示回應，三類更新、重新整理與移除再加入',async({page})=>{
  const unexpected=await installOfflineApi(page);let current={...base};const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/theme-updates?*',r=>r.fulfill({json:{items:[current]}}));
  await follow(page);await expect(page.getByText('判讀無變更')).toBeVisible();
  current={...current,current_version_id:2,version_number:2,indicator_token:'i2',candidate_token:'c2'};
  await page.getByRole('button',{name:'重新檢查更新'}).click();
  for(const text of ['判讀有更新','指標新期／修訂','候選資訊有變化'])await expect(page.getByText(text,{exact:true})).toBeVisible();
  // Server changes after this response; clicking read must not fetch/mark v3.
  current={...current,current_version_id:3,version_number:3,indicator_token:'i3',candidate_token:'c3'};
  await page.getByRole('button',{name:'將目前顯示標為已讀'}).click();
  await expect.poll(()=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)!).seen['liquid-cooling'].version_id,key)).toBe(2);
  await page.getByRole('button',{name:'重新檢查更新'}).click();await expect(page.getByText('判讀有更新')).toBeVisible();
  await page.reload();await expect(page.getByText('判讀有更新')).toBeVisible();
  await page.getByRole('button',{name:'移除關注',exact:true}).click();await expect(page.getByText('尚未關注題材。')).toBeVisible();
  await expect.poll(()=>page.evaluate(k=>Object.keys(JSON.parse(localStorage.getItem(k)!).seen).length,key)).toBe(0);
  await page.getByRole('link',{name:'前往題材研究加入關注'}).click();await page.getByRole('button',{name:'加入此裝置關注'}).click();
  await page.getByRole('navigation').getByRole('link',{name:'此裝置關注'}).click();await expect(page.getByText('判讀無變更')).toBeVisible();
  expect(errors).toEqual([]);expect(unexpected).toEqual([]);
});

test('來源失敗不產生未讀，未知日期只標新收錄且可回到三個入口',async({page})=>{
  await installOfflineApi(page);let current={...base};await page.route('**/api/theme-updates?*',r=>r.fulfill({json:{items:[current]}}));await follow(page);
  current={...current,source_warnings:[{source_id:'failed',kind:'failed',message:'HTTP 403'}]};await page.getByRole('button',{name:'重新檢查更新'}).click();
  await expect(page.getByText('判讀無變更')).toBeVisible();await expect(page.getByText('指標無變更')).toBeVisible();await expect(page.getByText('候選資訊無變更')).toBeVisible();
  await expect(page.getByText('不代表新發生',{exact:false})).toBeVisible();
  await page.getByText('來源取得警示（不計未讀）').focus();await page.keyboard.press('Enter');await expect(page.getByText('來源：取得失敗')).toBeVisible();
  await expect(page.getByRole('link',{name:'判讀無變更'})).toHaveAttribute('href',/from_version=1#versions$/);
  await expect(page.getByRole('link',{name:'指標無變更'})).toHaveAttribute('href',/#indicators$/);
  await expect(page.getByRole('link',{name:'候選資訊無變更'})).toHaveAttribute('href',/#candidates$/);
});

test('損壞儲存改用記憶體；讀取或寫入被拒絕仍能關注',async({page})=>{
  await installOfflineApi(page);await page.addInitScript(k=>localStorage.setItem(k,'{broken'),key);
  await follow(page);await expect(page.getByText('目前使用本次記憶體暫存',{exact:false})).toBeVisible();
  await expect(page.getByText('判讀無變更')).toBeVisible();
});

for(const method of ['getItem','setItem'])test(`storage ${method} 被拒絕仍可在手機使用`,async({page})=>{
  await installOfflineApi(page);await page.addInitScript(m=>Object.defineProperty(Storage.prototype,m,{value(){throw new Error('blocked')}}),method);
  await page.setViewportSize({width:390,height:844});await follow(page);
  await expect(page.getByText('記憶體暫存',{exact:false})).toBeVisible();await expect(page.getByText('判讀無變更')).toBeVisible();
  await page.getByRole('button',{name:'移除關注',exact:true}).focus();await page.keyboard.press('Enter');await expect(page.getByText('尚未關注題材。')).toBeVisible();
});

test('含未知與部分損壞項目時有效關注仍保留，無效題材可移除',async({page})=>{
  await installOfflineApi(page);await page.addInitScript(k=>localStorage.setItem(k,JSON.stringify({theme_ids:['liquid-cooling','missing',123],seen:{'liquid-cooling':{version_id:1,indicator_token:'i1',candidate_token:'c1'},missing:{version_id:null,indicator_token:'',candidate_token:''}}})),key);
  await page.goto('/watchlist');await expect(page.getByRole('heading',{name:'液冷',exact:true})).toBeVisible();await expect(page.getByText('題材已不可用')).toBeVisible();
  await page.locator('.watch-card').filter({has:page.getByRole('heading',{name:'無法取得的題材',exact:true})}).getByRole('button',{name:'移除關注'}).click();
  await expect(page.getByText('題材已不可用')).toHaveCount(0);await expect(page.getByRole('heading',{name:'液冷',exact:true})).toBeVisible();
});
