import {test,expect} from '@playwright/test';
import {installOfflineApi,assessment,theme,source,event} from './fixture-data';
import {readableNumber} from '../../lib/display';

test('事件卡片使用來源名稱；不展示內部識別或通用進階資訊',async({page})=>{
  await installOfflineApi(page);await page.route('**/api/events?*',r=>r.fulfill({json:[event,{...event,id:2,kind:'future-enum',source_name:null}]}));
  await page.goto('/events');const cards=page.locator('.event-row');await expect(cards).toHaveCount(2);
  await expect(cards.first().locator('.muted')).toContainText(source.name);
  await expect(cards.first()).not.toContainText(source.id);
  await expect(cards.nth(1)).toContainText('來源名稱待補');await expect(cards.nth(1)).toContainText('資訊類型待確認');
  await expect(page.getByText('進階資訊',{exact:true})).toHaveCount(0);
});

test('大數值、原幣、百分點、零與未知保持衡量界線',()=>{
  expect(readableNumber('12345678901.12345678','amount','TWD')).toBe('123.46 億 TWD');
  expect(readableNumber('-123456.789','amount','USD')).toBe('-12.35 萬 USD');
  expect(readableNumber('0','amount','USD')).toBe('0 USD');
  expect(readableNumber(null,'percent')).toBe('尚未取得');
  expect(readableNumber('3.125','percent')).toBe('3.13 %');
  expect(readableNumber('-0.75','percentage-point')).toBe('-0.75 百分點');
});

test('環節預設先讀供應角色；鍵盤切換技術與追蹤可分享，不預取文件清單',async({page})=>{
  const unexpected=await installOfflineApi(page),requests:string[]=[];
  page.on('request',r=>requests.push(new URL(r.url()).pathname));
  await page.goto('/?layer=ai-server&segment=thermal');
  const reading=page.locator('#segment-reading');
  await expect(reading.getByRole('tab',{name:'產業角色'})).toHaveAttribute('aria-selected','true');
  await expect(reading.getByRole('heading',{name:'供應與需求關係'})).toBeVisible();
  await expect(reading.getByRole('heading',{name:'傳導鏈'})).toBeVisible();
  await expect(reading.getByRole('heading',{name:'技術變數'})).toBeHidden();
  await reading.getByRole('tab',{name:'產業角色'}).focus();await page.keyboard.press('ArrowRight');
  await expect(reading.getByRole('tab',{name:'技術與限制'})).toBeFocused();
  await expect(reading.getByRole('heading',{name:'技術變數'})).toBeVisible();
  await expect(page).toHaveURL(/#segment-technology$/);await page.reload();
  await expect(reading.getByRole('heading',{name:'技術變數'})).toBeVisible();
  await reading.getByRole('tab',{name:'技術與限制'}).focus();await page.keyboard.press('End');
  await expect(reading.getByRole('heading',{name:'近期直接相關事件'})).toBeVisible();
  await page.keyboard.press('Home');await expect(reading.getByRole('heading',{name:'傳導鏈'})).toBeVisible();
  expect(requests.filter(p=>p.startsWith('/api/technical-documents'))).toEqual([]);expect(unexpected).toEqual([]);
});

test('題材先讀判讀；中文原文與證據網址保留，數據深連結能返回判讀',async({page})=>{
  const unexpected=await installOfflineApi(page);
  await page.route('**/api/themes/liquid-cooling',r=>r.fulfill({json:{...theme,status:'future-state',prose:'## 題材範圍\n\n**inference**：`thermal` 的條件，經 `odm.upstream` 取得其他環節；`beneficiaries` 不保證受惠。`liquid-cooling` 仍在 `scaling`。 [原始來源](https://example.invalid/thermal?state=inference)'}}));
  await page.goto('/themes/liquid-cooling');
  await expect(page.locator('.page-heading')).toContainText('狀態待確認');
  await expect(page.locator('.assessment-baseline')).toContainText('有條件推論');
  await expect(page.locator('.assessment-baseline')).not.toContainText('inference');
  await expect(page.getByRole('region',{name:'完整研究'})).toBeHidden();
  await page.getByRole('tab',{name:'技術與供應鏈'}).click();
  const research=page.getByRole('region',{name:'完整研究'});
  await expect(research).toContainText('有條件推論');await expect(research).toContainText('散熱');
  await expect(research).toContainText('ODM 組裝的上游供應');await expect(research).toContainText('候選公司清單');await expect(research).toContainText(/液冷\s*仍在\s*擴張/);
  for(const raw of ['odm.upstream','beneficiaries','liquid-cooling','scaling'])await expect(research).not.toContainText(raw);
  await expect(research.getByRole('link',{name:'原始來源'})).toHaveAttribute('href','https://example.invalid/thermal?state=inference');
  await page.goto('/themes/liquid-cooling#candidates');
  await expect(page.getByRole('tab',{name:'數據與追蹤'})).toHaveAttribute('aria-selected','true');
  await expect(page.getByRole('heading',{name:'研究查核後的新資訊'})).toBeVisible();
  await page.getByRole('tab',{name:'研究判讀'}).click();await expect(page.getByRole('heading',{name:'目前判讀'})).toBeVisible();
  for(const name of ['進階資訊','技術文件與待核對'])await expect(page.getByText(name,{exact:true})).toHaveCount(0);
  expect(unexpected).toEqual([]);
});

test('手機直接開啟環節時，較慢的圖形回應不會把正文推回畫面下方',async({page})=>{
  await installOfflineApi(page);
  await page.route('**/api/industries/ai-server/graph',async r=>{await new Promise(resolve=>setTimeout(resolve,400));await r.fallback()});
  await page.setViewportSize({width:390,height:844});await page.goto('/?layer=ai-server&segment=thermal');
  await expect(page.getByTestId('local-network')).toHaveAttribute('data-nodes','2');
  await expect.poll(()=>page.locator('#segment-reading').evaluate(e=>e.getBoundingClientRect().top)).toBeLessThan(80);
  await expect(page.locator('#segment-reading h2').first()).toBeFocused();
});

test('手機局部錯誤有重試且不展示診斷；原研究仍可切換閱讀',async({page})=>{
  await installOfflineApi(page);let attempts=0;
  await page.route('**/api/themes/liquid-cooling/assessment',r=>++attempts===1?r.fulfill({status:503,json:{detail:'HTTP 503 internal diagnostic'}}):r.fulfill({json:assessment}));
  await page.setViewportSize({width:390,height:844});await page.goto('/themes/liquid-cooling');
  const alert=page.getByRole('main').getByRole('alert');await expect(alert).toContainText('已載入的研究仍可閱讀');
  await expect(page.getByText('HTTP 503 internal diagnostic')).toHaveCount(0);
  await page.getByRole('tab',{name:'技術與供應鏈'}).click();await expect(page.getByRole('region',{name:'完整研究'})).toBeVisible();
  await page.getByRole('tab',{name:'研究判讀'}).click();await alert.getByRole('button',{name:'重新取得'}).focus();await page.keyboard.press('Enter');
  await expect(page.getByRole('heading',{name:'目前判讀'})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('來源失敗保留中文原因與更新時間，不展示設定與內部錯誤',async({page})=>{
  await installOfflineApi(page);await page.goto('/sources');
  const row=page.locator('.source-row');await expect(row).toContainText('此來源尚待完成必要設定');
  await expect(row).not.toContainText('offline-source');await expect(row).not.toContainText('configuration_required');
  await expect(page.getByText('進階資訊',{exact:true})).toHaveCount(0);
});

test('手機指標金額、精確原值與不可比較原因各自可讀',async({page})=>{
  await installOfflineApi(page);
  const values=[['大額營收','12345678901.12345678','amount','TWD'],['零營收','0','amount','USD'],['負值','-123456.789','amount','USD'],['占比','3.125','percent',null],['未知',null,'amount','USD']];
  await page.route('**/api/themes/liquid-cooling/indicators',r=>r.fulfill({json:{theme_id:'liquid-cooling',indicators:values.map(([name,value,unit,currency],index)=>({id:String(index),name,kind:'proxy',scope:'公司整體單季營收',limitations:'不是題材收入',latest:value===null?null:{value,unit,currency,basis:'quarterly',original_period:'2026 Q2',period_start:'2026-04-01',period_end:'2026-06-30',revision:1},unit,currency,status:'available',data_age_days:30,source:{id:'offline',name:'測試來源',status:'success',error:null,last_success:null},comparison:index===3?{value:'-0.75',unit:'percentage-point',previous_period:'2026 Q1',reason:null}:{value:null,unit:'percent',previous_period:null,reason:'單位、幣別、口徑、範圍或期間不可比較'},trend:[],observations:[],revisions:[],gaps:[]}))}}));
  await page.setViewportSize({width:390,height:844});await page.goto('/themes/liquid-cooling#indicators');
  const cards=page.locator('.indicator-card');
  await expect(cards.nth(0).locator('.indicator-value')).toContainText('123.46 億 TWD');
  await expect(cards.nth(0).locator('.indicator-value>span')).toHaveAttribute('title',/12345678901.12345678 TWD/);
  await expect(cards.nth(0).locator('.exact-value')).toHaveCount(0);
  await expect(cards.nth(1).locator('.indicator-value')).toContainText('0 USD');
  await expect(cards.nth(2).locator('.indicator-value')).toContainText('-12.35 萬 USD');
  await expect(cards.nth(3)).toContainText('-0.75 百分點');
  await expect(cards.nth(4)).toContainText('尚未取得有效數值；不以零值代替');
  await expect(cards.nth(0)).toContainText('口徑、範圍或期間不可比較');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
