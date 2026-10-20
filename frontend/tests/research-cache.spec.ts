import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

test('真實 Next proxy 轉送條件標頭與 304；研究／動態比較／資產各自快取',async({request})=>{
  const manifest=await (await request.get('/api/v2/manifest')).json(),release=manifest.release_id;
  const path='/api/v2/companies/company-auras?release_id='+release;
  const profile=await request.get(path);expect(profile.status()).toBe(200);expect(profile.headers()['cache-control']).toContain('max-age=86400');
  const same=await request.get(path,{headers:{'If-None-Match':profile.headers()['etag']}});expect(same.status()).toBe(304);expect((await same.body()).length).toBe(0);
  const unpinned=await request.get('/api/v2/companies/company-auras',{headers:{'If-None-Match':profile.headers()['etag']}});expect(unpinned.status()).toBe(200);expect(unpinned.headers()['cache-control']).toBe('no-store');
  const comparePath='/api/v2/compare?company_ids=company-auras,company-vertiv&release_id='+release;
  const compare=await request.get(comparePath);expect(compare.headers()['cache-control']).toContain('max-age=30');expect(compare.headers()['cache-control']).not.toContain('immutable');
  expect((await request.get(comparePath,{headers:{'If-None-Match':compare.headers()['etag']}})).status()).toBe(304);
  const concept=await (await request.get('/api/v2/concepts/concept-liquid-cooling-loop?release_id='+release)).json();
  const assetPath=concept.data.assets[0].url,asset=await request.get(assetPath);expect(asset.status()).toBe(200);expect(asset.headers()['cache-control']).toContain('immutable');
  expect((await request.get(assetPath,{headers:{'If-None-Match':asset.headers()['etag']}})).status()).toBe(304);
  const notPublished=new URL(assetPath,'http://reader.invalid');notPublished.searchParams.set('release_id','99999999-9999-4999-8999-999999999999');
  const denied=await request.get(notPublished.pathname+notPublished.search,{headers:{'If-None-Match':'*'}});expect(denied.status()).toBe(404);expect(denied.headers()['cache-control']).toBe('no-store');
  const admin=await request.get('/api/admin/session',{headers:{'If-None-Match':'*'}});expect(admin.status()).not.toBe(304);expect(admin.headers()['cache-control']).toBe('no-store');
});

for(const mobile of [false,true])test(`真實研究共用請求、手動檢查與暫時失敗保留閱讀${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize(mobile?{width:390,height:844}:{width:1440,height:1000});
  const calls:string[]=[];page.on('request',request=>{if(request.url().includes('/api/v2/'))calls.push(request.url())});
  await page.goto('/next?focus=concept-liquid-cooling-loop');await expect(page.locator('.rs-detail > h2')).toHaveText('兩個液冷回路');
  await expect(page.locator('.rs-illustration img').first()).toBeVisible();
  expect(calls.filter(url=>new URL(url).pathname==='/api/v2/concepts/concept-liquid-cooling-loop')).toHaveLength(1);
  expect(calls.some(url=>url.includes('/financials/')||url.includes('/documents/'))).toBe(false);
  await page.route('**/api/v2/concepts/concept-liquid-cooling-loop?*',route=>route.fulfill({status:503,json:{message:'明示測試服務中斷'},headers:{'Cache-Control':'no-store'}}));
  await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.getByText('目前無法更新，先保留上次成功讀取的內容。',{exact:false})).toBeVisible();
  await expect(page.locator('.rs-detail > h2')).toHaveText('兩個液冷回路');await expect(page.locator('.rs-citation a')).toBeVisible();
  await mkdir('../.work/research-cache-review',{recursive:true});await page.screenshot({path:`../.work/research-cache-review/${mobile?'mobile':'desktop'}-real-stale.png`,fullPage:false});
  await page.unroute('**/api/v2/concepts/concept-liquid-cooling-loop?*');await page.getByRole('button',{name:'檢查更新',exact:true}).click();await expect(page.getByText('目前無法更新，先保留上次成功讀取的內容。',{exact:false})).toHaveCount(0);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
