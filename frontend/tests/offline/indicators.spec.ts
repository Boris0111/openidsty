import {test,expect} from '@playwright/test';
import {installOfflineApi,assessment,theme} from './fixture-data';
import type {Observation,ThemeIndicator} from '../../lib/types';

test('指標期間、修訂、單筆無連線與商業化核對在手機可讀',async({page})=>{
  const unexpected=await installOfflineApi(page);
  const row:Observation={id:1,identity:'offline',revision:2,content_hash:'offline',source_id:'offline',original_period:'FY26 Q3',period_start:'2026-03-01',period_end:'2026-05-28',basis:'quarterly',scope:'公司整體收入',unit:'amount',currency:'USD',value:'123.45678901',published_at:null,reported_at:null,published_precision:'unknown',date_semantics:'unknown',fetched_at:'2026-10-14T00:00:00Z',url:'https://example.org/quarter',raw_excerpt:'離線數值',valid:true,invalid_reason:null};
  const indicator:ThemeIndicator={id:'offline-proxy',name:'離線代理總營收',kind:'proxy',scope:row.scope,limitations:'不是題材專屬收入',unit:'amount',currency:'USD',frequency:'quarterly',basis:'quarterly',status:'stale',data_age_days:200,source:{id:'offline',status:'failed',last_success:null,error:'HTTP 403'},latest:row,observations:[row],revisions:[row],trend:[row],comparison:{value:null,unit:'percent',reason:'缺少前期',previous_period:null},gaps:['來源失敗；保留歷史數值']};
  await page.route('**/api/themes/liquid-cooling/indicators',r=>r.fulfill({json:{theme_id:'liquid-cooling',as_of:'2026-10-14',indicators:[indicator],gaps:[]}}));
  await page.setViewportSize({width:390,height:844});await page.goto('/themes/liquid-cooling#indicators');
  await expect(page.locator('.indicator-value')).toContainText('123.46 USD');
  await expect(page.locator('.indicator-value>span')).toHaveAttribute('title',/123.45678901/);
  await expect(page.getByText('不是題材專屬收入')).toBeVisible();
  await expect(page.getByText('資料過舊；距期末 200 日。修訂 2')).toBeVisible();
  await expect(page.locator('.indicator-trend')).toHaveCount(0);
  await page.getByText('期別、來源與修訂明細').focus();await page.keyboard.press('Enter');
  await expect(page.getByRole('columnheader',{name:'原期別／起迄'})).toBeVisible();await expect(page.locator('.exact-number')).toContainText('123.45678901 USD');
  await expect(page.getByRole('heading',{name:'里程碑與實際進展'})).toBeVisible();
  expect(unexpected).toEqual([]);
});

test('兩筆同口徑值可閱讀趨勢，已確認里程碑可回到證據',async({page})=>{
  await installOfflineApi(page);
  const rows=[{identity:'a',original_period:'2026 Q1',period_end:'2026-03-31',value:'1'},{identity:'b',original_period:'2026 Q2',period_start:'2026-04-01',period_end:'2026-06-30',value:'2',currency:'USD',basis:'quarterly',revision:1}];
  await page.route('**/api/themes/liquid-cooling/indicators',r=>r.fulfill({json:{theme_id:'liquid-cooling',indicators:[{id:'offline-direct',name:'离線直接指標',kind:'direct',scope:'具名產品',limitations:'不是全市場',latest:rows[1],status:'available',data_age_days:100,source:{id:'offline',status:'success',last_success:null},comparison:{value:'100',previous_period:'2026 Q1',unit:'percent'},trend:rows,observations:[],revisions:[],gaps:[]}]}}));
  const evidence=assessment.assessment!.evidence[0];
  await page.route('**/api/themes/liquid-cooling',r=>r.fulfill({json:{...theme,milestones:[{id:'shipment',date:'2025',event:'交付核對',evidence:'具名產品'}]}}));
  await page.route('**/api/themes/liquid-cooling/assessment',r=>r.fulfill({json:{...assessment,assessment:{...assessment.assessment,milestone_reviews:[{milestone_id:'shipment',state:'confirmed',reviewed:'2026-10-07',note:'僅具名產品，不推論全部供應商',evidence_ids:[evidence.id],occurred:null}]}}}));
  await page.goto('/themes/liquid-cooling#indicators');
  await expect(page.getByRole('img',{name:'同口徑歷史趨勢，精確數值與期別見下方表格'})).toBeVisible();
  const section=page.locator('.commercial-progress');
  await expect(section.getByText('預期 2025｜已確認')).toBeVisible();
  await section.getByText('核對依據與適用範圍').focus();await page.keyboard.press('Enter');
  await expect(section.getByRole('link')).toHaveAttribute('href',evidence.url);
  await expect(section.getByText('實際發生 日期未確認',{exact:false})).toBeVisible();
});
