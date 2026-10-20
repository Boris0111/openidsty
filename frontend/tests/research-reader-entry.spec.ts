import {test,expect} from '@playwright/test';
test.skip(!process.env.RESEARCH_READER_E2E,'Use the optional isolated reader gateway explicitly');

test('讀者入口能閱讀研究、圖解及公司，版本與網址留在讀者入口',async({page,baseURL})=>{
  await page.goto('/next');
  await expect(page.locator('h1')).toHaveText('供應鏈');
  await page.locator('.rs-chain-card').filter({hasText:'AI 機櫃液冷'}).click();
  await expect.poll(()=>page.locator('.rs-chain-diagram img').evaluate((element:HTMLImageElement)=>element.naturalWidth)).toBeGreaterThan(0);
  await page.locator('.rs-chain-product').filter({hasText:'液冷冷板'}).click();
  await page.locator('.rs-company-links a').filter({hasText:'雙鴻'}).click();
  await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  expect(new URL(page.url()).origin).toBe(new URL(baseURL!).origin);
  expect(new URL(page.url()).searchParams.get('release_id')).toBeTruthy();
  await expect(page.locator('body')).not.toContainText(/草稿工作台|來源健康|csrf_token|owner_configured/);
});

test('讀者入口拒絕管理、舊診斷與寫入，偽造 cookie 不會取得管理資料',async({request})=>{
  for(const path of ['/admin','/api/admin/session','/api/admin/drafts','/api/admin/sources','/sources','/api/sources','/coverage','/api/coverage','/api/theme-updates','/api/docs']){
    const response=await request.get(path,{headers:{Cookie:'industryflow_owner=synthetic-forged'}});
    expect(response.status()).toBe(403);
    expect(response.headers()['cache-control']).toBe('no-store');
    expect(response.headers()['set-cookie']).toBeUndefined();
  }
  expect((await request.post('/api/admin/drafts',{data:{}})).status()).toBe(403);
  expect((await request.post('/next',{data:{}})).status()).toBe(403);
  expect((await request.get('/next',{headers:{Host:'evil.example'}})).status()).toBe(403);
  // The map, themes and events share the reading shell, so readers reach them through the same entry.
  for(const path of ['/','/themes','/events','/api/segments/thermal'])expect((await request.get(path)).status(),path).toBe(200);
});
