import {test,expect} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

for(const mobile of [false,true])test(`真實台灣月營收、SEC 財務與來源可由研究頁操作${mobile?'（手機）':'（桌機）'}`,async({page,request})=>{
  await page.setViewportSize(mobile?{width:390,height:844}:{width:1440,height:1000});
  const manifest=await (await request.get('/api/v2/manifest')).json(),release=manifest.release_id;
  const response=await request.get('/api/v2/companies/company-auras/financials',{params:{release_id:release,metric:'revenue',basis:'monthly'}});expect(response.status()).toBe(200);
  const rows=(await response.json()).data.items;expect(rows.length).toBeGreaterThan(0);const latest=rows[0];
  expect(latest.currency).toBe('TWD');expect(latest.value).toBe('2884061000');expect(latest.period_start).toBe('2026-09-01');expect(latest.period_end).toBe('2026-09-30');
  await page.goto('/next?focus=company-auras&release_id='+release);await page.getByRole('link',{name:'查看財務與近期資訊'}).click();
  await expect(page.getByRole('combobox',{name:'財務口徑',exact:true})).toHaveValue('monthly');await expect(page.locator('.rf-series')).toContainText('2026-09-01 ～ 2026-09-30');
  await expect(page.locator('.rf-series [title="原值：2884061000 TWD"]')).toBeVisible();
  await page.locator('.rf-series button').first().click();const sources=page.getByRole('region',{name:'財務來源與修訂'});
  await expect(sources).toContainText('2884061 TWD thousand；倍率 1000');await expect(sources).toContainText('提供者彙整日期：2026-10-17');await expect(sources.getByRole('link',{name:'原始官方文件',exact:true})).toHaveAttribute('href',/tpex\.org\.tw/);
  await mkdir('../.work/research-financial-review',{recursive:true});await sources.scrollIntoViewIfNeeded();await page.screenshot({path:`../.work/research-financial-review/${mobile?'mobile':'desktop'}-taiwan-source.png`,fullPage:false});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.goto('/next?focus=company-vertiv&release_id='+release);await page.getByRole('link',{name:'查看財務與近期資訊'}).click();
  await expect(page.locator('.rf-series')).toContainText('SEC XBRL');await expect(page.locator('.rf-series [title="原值：10229900000 USD"]')).toBeVisible();
  await page.getByRole('combobox',{name:'財務口徑',exact:true}).selectOption('quarterly');await expect(page.locator('.rf-series')).toContainText('單季');await expect(page.locator('.rf-series tbody tr').first()).toContainText('USD');
  await page.locator('.rf-company-data').scrollIntoViewIfNeeded();await page.screenshot({path:`../.work/research-financial-review/${mobile?'mobile':'desktop'}-sec-trend.png`,fullPage:false});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.locator('.rf-table-wrap').screenshot({path:`../.work/research-financial-review/${mobile?'mobile':'desktop'}-sec-table.png`});
  await writeFile(`../.work/research-financial-review/${mobile?'mobile':'desktop'}-verified.json`,JSON.stringify({release,taiwan:{value:latest.value,period_start:latest.period_start,period_end:latest.period_end,source:latest.sources[0]},secAnnualValue:'10229900000',currency:'USD'},null,2));
});

test('真實公司比較保留非曆年期間與缺口，獨立觀察不混入正式關係',async({page,request})=>{
  await page.goto('/next?view=compare&company_ids=company-vertiv,company-nvda');
  await expect(page.locator('.rf-company-comparison')).toContainText('Vertiv');await expect(page.locator('.rf-company-comparison')).toContainText('輝達');
  await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('實際期間或單季／累計／全年／期末口徑不同');
  await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('2025-12-31');await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('2026-01-25');
  await expect(page.getByRole('region',{name:'財務比較結果'})).toContainText('尚未全部核對為合併報表範圍');
  await expect(page.getByRole('region',{name:'財務比較結果'})).not.toContainText('XML context ID');
  await mkdir('../.work/research-financial-review',{recursive:true});await page.locator('.rf-comparison-metrics > article').first().screenshot({path:'../.work/research-financial-review/desktop-compare-values.png'});await page.locator('.rf-compare').scrollIntoViewIfNeeded();await page.screenshot({path:'../.work/research-financial-review/desktop-compare.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);await page.screenshot({path:'../.work/research-financial-review/mobile-compare.png',fullPage:false});
  const release=new URL(page.url()).searchParams.get('release_id')!;
  const graph=await (await request.get('/api/v2/graphs',{params:{root:'company-vertiv',release_id:release}})).json();
  expect(graph.data.edges.every((edge:{kind:string})=>!edge.kind.includes('rumor'))).toBe(true);
  await page.getByRole('navigation',{name:'研究導覽'}).getByRole('link',{name:'傳聞觀察',exact:true}).click();
  await expect(page.getByRole('region',{name:'傳聞觀察清單'})).toContainText('有來源、尚未證實');
  const observations=await (await request.get('/api/v2/observations',{params:{release_id:release,limit:20}})).json();
  if(!observations.data.items.length)await expect(page.getByText('此範圍尚未取得傳聞觀察。')).toBeVisible();
  await page.screenshot({path:'../.work/research-financial-review/mobile-observations.png',fullPage:false});
});
