import {test,expect} from '@playwright/test';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

test('產品、公司與原始證據形成真實閱讀路徑',async({page})=>{
  await page.goto('/next');
  await expect(page.locator('.rs-detail > h2')).toHaveText('液冷冷板');
  await expect(page.locator('.rs-diagram img')).toBeVisible();
  await expect.poll(()=>page.locator('.rs-diagram img').evaluate((image:HTMLImageElement)=>image.naturalWidth)).toBeGreaterThan(0);
  await page.locator('.rs-company-links a').filter({hasText:'雙鴻'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  await expect(page.locator('.rs-detail')).toContainText('研發措辭');
  await expect(page.locator('.rs-citation').first()).toContainText('2025-10-15');
  await expect(page.locator('.rs-citation a').first()).toHaveAttribute('href','https://www.auras.com.tw/News/NewsContent/14-10/en');
  await expect(page.locator('body')).not.toContainText(/進階資訊|待核對佇列|parser|company-auras/);
});

test('CDU 到 Vertiv、分享及返回維持同一研究版本',async({page,context})=>{
  await page.goto('/next?focus=product-liquid-to-liquid-cdu');
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
  await expect(page.locator('.rs-detail')).toContainText('液對氣');
  await page.locator('.rs-company-links a').filter({hasText:'Vertiv'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('Vertiv');
  const shared=page.url(),release=new URL(shared).searchParams.get('release_id');
  expect(release).toBeTruthy();
  const other=await context.newPage();await other.goto(shared);
  await expect(other.locator('.rs-detail > h2')).toHaveText('Vertiv');
  expect(new URL(other.url()).searchParams.get('release_id')).toBe(release);
  await other.close();await page.goBack();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
});

test('鍵盤搜尋可進公司，維護導覽不出現在閱讀入口',async({page})=>{
  await page.goto('/next');
  const search=page.getByLabel('搜尋公司、產品或術語');
  await search.fill('雙鴻');await expect(page.locator('#rs-results a')).toHaveCount(1);
  await search.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  await expect(page.locator('.rs-header')).not.toContainText(/來源狀態|資料覆蓋|管理/);
});

test('手機可先選產品閱讀並以文字清單讀取能力連線',async({page})=>{
  await page.setViewportSize({width:390,height:844});await page.goto('/next');
  await expect(page.locator('.rs-detail > h2')).toHaveText('液冷冷板');
  await page.getByRole('button',{name:/^液對液 CDU 控制/}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
  await expect(page.locator('.rs-detail > h2')).toBeInViewport();
  await page.getByLabel('閱讀連線').selectOption({label:'Vertiv — 液對液 CDU（產品能力）'});
  await expect(page.getByRole('region',{name:'連線說明'})).toContainText('不指認交易客戶');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1)).toBeTruthy();
});

test('較慢的舊產品回應不覆蓋當前選取',async({page})=>{
  await page.route('**/api/v2/products/product-cold-plate?*',async route=>{
    await new Promise(resolve=>setTimeout(resolve,400));
    await route.continue().catch(()=>{});
  });
  await page.goto('/next');await page.getByRole('button',{name:/^液對液 CDU 控制/}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
  await page.waitForTimeout(450);
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
});

test('圖解讀取失敗仍能閱讀已發布研究與來源',async({page})=>{
  await page.route('**/api/v2/assets/**',route=>route.abort());
  await page.goto('/next');
  await expect(page.locator('.rs-detail > h2')).toHaveText('液冷冷板');
  await expect(page.getByText('圖解目前無法讀取，可先閱讀產品邊界及來源。')).toBeVisible();
  await expect(page.locator('.rs-citation a')).toHaveCount(1);
});
