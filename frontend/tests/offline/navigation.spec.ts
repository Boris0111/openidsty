import {test, expect} from '@playwright/test';
import {installOfflineApi} from './fixture-data';

test('tracked public routes work without a backend', async ({page, request}) => {
  const unexpected = await installOfflineApi(page), errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  // APIRequestContext bypasses browser interception: the test server really has no backend.
  const failed=await request.get('/api/health');expect(failed.status()).toBe(503);expect(failed.headers()['cache-control']).toBe('no-store');
  await page.goto('/');
  await expect(page.locator('#segment-reading').getByRole('heading', {name: '運算晶片', exact: true})).toBeVisible();
  const nav = page.getByRole('navigation', {name: '主要導覽'});
  await expect(nav.getByRole('link')).toHaveText(['產業地圖', '供應鏈', '公司', '題材', '公司比較', '事件', '收藏']);
  await expect(nav.getByRole('link', {name: '產業地圖'})).toHaveAttribute('aria-current', 'page');
  await nav.getByRole('link', {name: '題材', exact: true}).click();
  await expect(nav.getByRole('link', {name: '題材', exact: true})).toHaveAttribute('aria-current', 'page');
  await page.getByRole('link', {name: '液冷', exact: true}).click();
  await expect(page.getByRole('heading', {name: '液冷', exact: true})).toBeVisible();
  await expect(page.getByText('狀態查核 2026-10-07', {exact: false})).toBeVisible();
  await page.getByRole('tab',{name:'數據與追蹤'}).click();await expect(page.getByRole('heading', {name: '里程碑與實際進展'})).toBeVisible();
  await nav.getByRole('link', {name: '事件', exact: true}).click();
  await expect(page.getByRole('navigation', {name: '事件類型'}).getByRole('link', {name: '官方與報導'})).toHaveAttribute('aria-current', 'page');
  await page.locator('.event-title').first().click();
  await expect(page.getByRole('heading', {name: '來源摘錄'})).toBeVisible();
  // Coverage and source status are maintenance views: reachable by URL here, never in the reader navigation.
  await page.goto('/coverage');
  await expect(page.locator('tbody tr')).toHaveCount(2);
  await expect(page.getByRole('columnheader',{name:'題材判讀',exact:true})).toBeVisible();
  await expect(page.locator('tbody tr').nth(1).getByRole('cell').nth(1)).toContainText('查核 2026-10-07');
  await expect(page.locator('tbody tr').first()).toContainText('0／1');
  await expect(page.locator('tbody tr').first().locator('.coverage-gap')).toContainText('近 30 日尚無直接事件');
  await expect(nav.getByRole('link', {name: /資料覆蓋|來源狀態/})).toHaveCount(0);
  await page.goto('/sources');
  await expect(page.locator('.source-row')).toContainText('待設定');
  // Old company URLs resolve to the new company research; without it the reader is pointed to the company index.
  await page.goto('/companies/2330.TW');
  await expect(page.getByRole('heading', {name: '無法開啟這家公司的研究'})).toBeVisible();
  await expect(page.getByRole('link', {name: '前往公司索引'})).toHaveAttribute('href', '/next?view=companies');
  await page.goto('/compare?tickers=NVDA,AMD');
  await expect(page).toHaveURL(/\/next\?view=compare/);
  await expect(nav.getByRole('link', {name: '公司比較'})).toHaveAttribute('aria-current', 'page');
  expect(unexpected).toEqual([]); expect(errors).toEqual([]);
});

test('mobile selection and keyboard search remain readable', async ({page}) => {
  const unexpected = await installOfflineApi(page);
  await page.setViewportSize({width: 390, height: 844}); await page.goto('/');
  await page.getByRole('button', {name: '散熱', exact: true}).focus(); await page.keyboard.press('Enter');
  await expect(page.locator('#segment-reading').getByRole('heading', {name: '散熱', exact: true})).toBeVisible();
  const search = page.getByRole('textbox', {name: '搜尋公司、產品、環節或題材'});
  await search.fill('散熱'); await expect(page.locator('.search-results a').first()).toHaveAttribute('href', '/next?focus=segment-thermal');
  await search.fill('液冷'); await expect(page.locator('.search-results a').first()).toContainText('液冷');
  await search.press('ArrowDown'); await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/themes\/liquid-cooling/);
  await expect(page.getByRole('heading', {name: '液冷', exact: true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(unexpected).toEqual([]);
});

test('loading failure, retry and empty events preserve navigation', async ({page}) => {
  const unexpected = await installOfflineApi(page);
  await page.route('**/api/themes', route => route.fulfill({status: 503, json: {detail: '離線測試服務失敗'}}));
  await page.goto('/themes'); await expect(page.locator('.status-box[role=alert]')).toContainText('此區資料暫時無法取得');
  await page.unroute('**/api/themes');
  await page.getByRole('button', {name: '重新取得'}).click();
  await expect(page.getByRole('link', {name: '液冷', exact: true})).toBeVisible();
  await page.goto('/events?date_from=2099-01-01');
  await expect(page.getByText('尚未取得直接相關事件。研究內容仍可閱讀。', {exact: false})).toBeVisible();
  await expect(page.getByRole('main').getByRole('link', {name: /資料覆蓋|來源狀態/})).toHaveCount(0);
  await expect(page.getByRole('navigation', {name: '主要導覽'})).toBeVisible();
  expect(unexpected).toEqual([]);
});
