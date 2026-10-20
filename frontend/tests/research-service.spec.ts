import {test,expect} from '@playwright/test';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

test('供應鏈、產品、公司與原始證據形成真實閱讀路徑',async({page})=>{
  await page.goto('/next?focus=application-ai-rack-cooling');
  await expect(page.locator('h1')).toHaveText('AI 機櫃的熱，怎麼送出去？');
  await expect.poll(()=>page.locator('.rs-chain-diagram img').evaluate((image:HTMLImageElement)=>image.naturalWidth)).toBeGreaterThan(0);
  await expect(page.getByRole('list',{name:'供應鏈步驟'}).getByRole('listitem')).toHaveCount(3);
  await expect(page.locator('.rs-chain-product').filter({hasText:'液冷冷板'})).toContainText('雙鴻');
  await page.locator('.rs-chain-product').filter({hasText:'液冷冷板'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液冷冷板');
  await expect(page.getByRole('complementary',{name:'所在供應鏈'}).locator('[aria-current=step]')).toContainText('伺服器二次側');
  await page.locator('.rs-company-links a').filter({hasText:'雙鴻'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  // Company research is its own page: it lists its chains instead of embedding a chain diagram.
  await expect(page.getByRole('region',{name:'所屬供應鏈與產品'})).toContainText('AI 機櫃液冷');
  await expect(page.locator('.rs-chain-diagram')).toHaveCount(0);
  await expect(page.locator('.rs-detail')).toContainText('研發措辭');
  // The OCP 2025 news stays one of several primary sources after the annual-report deep research.
  await expect(page.locator('.rs-citation').filter({has:page.locator('a[href="https://www.auras.com.tw/News/NewsContent/14-10/en"]')}).first()).toContainText('2025-10-15');
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
  const search=page.getByLabel('搜尋公司、產品、環節或題材');
  await search.fill('雙鴻');await expect(page.locator('.search-results a')).toHaveCount(1);
  await search.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  await expect(page.locator('.site-header')).not.toContainText(/來源狀態|資料覆蓋|管理/);
});

test('手機開產品頁先讀到產品與所在步驟，可回供應鏈並以文字清單讀取能力連線',async({page})=>{
  await page.setViewportSize({width:390,height:844});await page.goto('/next?focus=product-cold-plate');
  await expect(page.locator('h1')).toHaveText('液冷冷板');await expect(page.locator('h1')).toBeInViewport();
  const strip=page.getByRole('complementary',{name:'所在供應鏈'});await expect(strip).toBeInViewport();
  await strip.getByRole('link',{name:'看完整圖解與產品'}).click();
  await expect(page.locator('h1')).toHaveText('AI 機櫃的熱，怎麼送出去？');
  await page.locator('.rs-chain-product').filter({hasText:'液對液 CDU'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
  await page.getByLabel('閱讀連線').selectOption({label:'Vertiv — 液對液 CDU（產品能力）'});
  await expect(page.getByRole('region',{name:'連線說明'})).toContainText('不指認交易客戶');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1)).toBeTruthy();
});

test('較慢的舊產品回應不覆蓋當前選取',async({page})=>{
  await page.route('**/api/v2/products/product-cold-plate?*',async route=>{
    await new Promise(resolve=>setTimeout(resolve,1500));
    await route.continue().catch(()=>{});
  });
  await page.goto('/next?focus=product-cold-plate');
  await page.getByLabel('搜尋公司、產品、環節或題材').fill('液對液');
  await page.locator('.search-results a').filter({hasText:'液對液 CDU'}).first().click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
  await page.waitForTimeout(1600);
  await expect(page.locator('.rs-detail > h2')).toHaveText('液對液 CDU');
});

test('圖解讀取失敗仍能閱讀已發布研究與來源',async({page})=>{
  await page.route('**/api/v2/assets/**',route=>route.abort());
  await page.goto('/next?focus=application-ai-rack-cooling');
  await expect(page.locator('h1')).toHaveText('AI 機櫃的熱，怎麼送出去？');
  await expect(page.getByText('圖解目前無法讀取，可先閱讀下方說明與來源。')).toBeVisible();
  await expect(page.locator('.rs-chain-product').filter({hasText:'液冷冷板'})).toBeVisible();
});
