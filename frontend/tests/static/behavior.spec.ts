import {test, expect} from '@playwright/test';
import {FIXTURE_RELEASE, manifest, visit} from './snapshot';

// Behaviour of the public build on the synthetic snapshot; a real snapshot is covered by crawl.spec.ts and snapshot-parity.
test.skip(manifest.release_id !== FIXTURE_RELEASE, 'needs the synthetic fixture snapshot');

test('search, then open the company from the header', async ({page}) => {
  await visit(page, '/');
  await page.getByLabel('搜尋公司、產品、環節或題材').fill('台積');
  await expect(page.locator('#search-results a').first()).toContainText('台積電');
  await page.locator('#search-results a').first().click();
  await expect(page).toHaveURL(/focus=company-tsmc/);
  await expect(page.getByRole('heading', {level: 1})).toHaveText('台積電');
});

test('combined directory filters and an empty market read like the private service', async ({page}) => {
  await visit(page, '/next?view=companies&market=TW&role=role-cold-plate-maker&category=application-liquid-cooling');
  await expect(page.locator('.rs-directory ul li')).toHaveText([/奇鋐/]);
  await visit(page, '/next?view=companies&market=US');
  await expect(page.getByText('此範圍尚未列出研究')).toBeVisible();
});

test('compare any two companies, and ask for two to four', async ({page}) => {
  await visit(page, '/next?view=compare&company_ids=company-tsmc,company-avc');
  await expect(page.locator('.rf-company-comparison h2')).toHaveText(['台積電', '奇鋐']);
  await visit(page, '/next?view=compare&company_ids=company-avc');
  await expect(page.getByText('請選擇 2–4 家不同公司。')).toBeVisible();
});

test('research outside the snapshot says so and offers a way back', async ({page}) => {
  await page.goto('/next?focus=company-missing');
  await expect(page.locator('.rs-error')).toContainText('公開版未收錄');
  await expect(page.locator('.rs-error').getByRole('link', {name: '回產業地圖'})).toBeVisible();
  await page.goto('/next?view=watchlist');
  await expect(page.locator('.rs-error')).toContainText('公開版未收錄這個檢視');
});

test('a link to another release points back to the snapshot release', async ({page}) => {
  await page.goto('/next?focus=company-avc&release_id=11111111-1111-4111-8111-111111111111');
  await expect(page.getByText('此公開版只收錄')).toBeVisible();
  await page.getByRole('button', {name: '改看公開版本'}).click();
  await expect(page).toHaveURL(new RegExp('release_id=' + FIXTURE_RELEASE));
  await expect(page.getByRole('heading', {level: 1})).toHaveText('奇鋐');
});

test('events, indicators, history and watchlist are absent; milestones and citations remain', async ({page}) => {
  await visit(page, '/?layer=ai-server&segment=thermal');
  await expect(page.getByText('近期直接相關事件')).toHaveCount(0);
  await expect(page.getByRole('link', {name: '查看資料覆蓋'})).toHaveCount(0);
  await page.getByRole('tab', {name: '技術與限制'}).click();
  await page.getByText('查看這項說明的來源').click();
  await expect(page.getByRole('link', {name: /合成冷板規範/})).toBeVisible();
  await visit(page, '/themes/liquid-cooling');
  await expect(page.getByRole('button', {name: /收藏/})).toHaveCount(0);
  await expect(page.locator('#versions, #indicators, #events, #candidates')).toHaveCount(0);
  await page.getByRole('tab', {name: '里程碑與追蹤'}).click();
  await expect(page.getByText('整櫃液冷交付')).toBeVisible();
  await visit(page, '/next?focus=company-avc');
  await expect(page.getByRole('link', {name: '比較這家公司'})).toBeVisible();
  await expect(page.getByText('近期資訊')).toHaveCount(0);
  await page.getByText('查閱這份引用').first().click();
  await expect(page.getByText('合成摘錄。').first()).toBeVisible();
});

test('the chain diagram loads from the snapshot and tickers open company research', async ({page}) => {
  await visit(page, '/next?focus=application-liquid-cooling');
  const diagram = page.locator('img[alt="液冷步驟圖"]').first();
  await expect.poll(() => diagram.evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
  await page.goto('/companies?ticker=3017.TW');
  await expect(page).toHaveURL(/focus=company-avc/);
});

test('private routes and API paths do not exist in the public build', async ({page}) => {
  for (const path of ['/events', '/admin', '/coverage', '/sources', '/watchlist', '/api/v2/manifest', '/api/themes'])
    expect((await page.goto(path))?.status(), path).toBe(404);
});
