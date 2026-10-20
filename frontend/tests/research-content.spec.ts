import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

for(const mobile of [false,true])test(`真實術語比較、公司角色與固定引用可連續閱讀${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize(mobile?{width:390,height:844}:{width:1440,height:1000});await page.goto('/next?focus=concept-liquid-cooling-loop');
  await expect(page.locator('.rs-detail > h2')).toHaveText('兩個液冷回路');
  const comparison=page.getByRole('region',{name:'技術比較'});await expect(comparison).toContainText('互補而非可替代');
  await expect(comparison.getByRole('link',{name:'液冷冷板',exact:true})).toBeVisible();await expect(comparison.getByRole('link',{name:'液對液 CDU',exact:true})).toBeVisible();
  await expect(page.getByRole('region',{name:'延伸研究'})).toContainText('雙鴻');
  await page.locator('.rs-citation summary').click();await expect(page.locator('.rs-citation-reading')).toContainText('未讀 NVOnline');
  const release=new URL(page.url()).searchParams.get('release_id');
  await mkdir('../.work/research-content-review',{recursive:true});await page.locator('.rs-intro h1').click();
  await page.screenshot({path:`../.work/research-content-review/${mobile?'mobile':'desktop'}-concept.png`,fullPage:true});
  await comparison.getByRole('link',{name:'液冷冷板',exact:true}).click();await expect(page.locator('.rs-prose')).toContainText('熱如何離開晶片');
  await page.locator('.rs-company-links a').filter({hasText:'雙鴻'}).click();await expect(page.locator('.rs-company-roles')).toContainText('散熱');await expect(page.locator('.rs-prose')).toContainText('出貨量、具名客戶與各產品收入都沒有揭露');
  const news=page.locator('.rs-citation').filter({has:page.locator('a[href="https://www.auras.com.tw/News/NewsContent/14-10/en"]')}).first();
  await news.locator('summary').click();await expect(news.locator('.rs-citation-reading')).toContainText('已讀公開新聞內文');await expect(news.locator('.rs-citation-reading')).not.toContainText(/HTTP 200|JavaScript/);
  expect(new URL(page.url()).searchParams.get('release_id')).toBe(release);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.locator('.rs-intro h1').click();await page.screenshot({path:`../.work/research-content-review/${mobile?'mobile':'desktop'}-company.png`,fullPage:true});
  await expect(page.locator('.rs-detail')).not.toContainText(/進階資訊|待核對佇列|parser|document-|company-auras/);
});
