import {test,expect} from '@playwright/test';
import {installOfflineApi,assessment,event,source} from './fixture-data';

test('judgment precedes prose and evidence is keyboard accessible',async({page})=>{
  const unexpected=await installOfflineApi(page);
  await page.goto('/themes/liquid-cooling');
  const reading=page.getByRole('region',{name:'題材判讀'});
  await expect(reading.getByRole('heading',{name:'目前判讀'})).toBeVisible();
  await expect(reading).toContainText('研究查核 2026-10-07');
  await expect(reading).toContainText('候選公司份額尚未核實');
  await expect(reading).toContainText('尚未取得可核對的反向證據');
  const evidence=reading.locator('summary').filter({hasText:'查看證據'}).first();
  await evidence.focus();await page.keyboard.press('Enter');
  await expect(reading.locator('blockquote')).toContainText('Synthetic browser-only evidence.');
  await expect(reading.locator('.evidence-period')).toContainText('發布 日期未知');
  await expect(reading.getByRole('link',{name:'離線測試來源 ↗'})).toHaveAttribute('href','https://example.invalid/source');
  await expect(page.getByRole('region',{name:'完整研究'})).toBeHidden();
  await page.getByRole('tab',{name:'數據與追蹤'}).click();
  // Pending candidates are maintenance data; readers keep public events and the review baseline.
  await expect(page.getByRole('heading',{name:'研究查核後的新資訊'})).toHaveCount(0);
  await expect(page.getByText('尚不能判定新舊',{exact:false})).toHaveCount(0);
  await expect(page.getByText('待納入判讀的資訊已移至維護端核對',{exact:false})).toBeVisible();
  await expect(page.getByRole('heading',{name:'已發布的相關事件'})).toBeVisible();
  await page.screenshot({path:'test-results/assessment-desktop.png',fullPage:true});
  expect(unexpected).toEqual([]);
});

test('mobile has readable conditions and evidence without overflow',async({page})=>{
  await installOfflineApi(page);await page.setViewportSize({width:390,height:844});
  await page.goto('/themes/liquid-cooling');
  await expect(page.getByRole('heading',{name:'成立條件',exact:true})).toBeVisible();
  await page.locator('.assessment-claim summary').first().click();
  await expect(page.locator('.assessment-evidence blockquote')).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:'test-results/assessment-mobile.png',fullPage:true});
});

test('missing judgment and failed judgment API preserve original research',async({page})=>{
  await installOfflineApi(page);
  await page.route('**/api/themes/liquid-cooling/assessment',route=>route.fulfill({json:{...assessment,available:false,assessment:null}}));
  await page.goto('/themes/liquid-cooling');
  await expect(page.getByRole('heading',{name:'判讀尚未整理'})).toBeVisible();
  await page.getByRole('tab',{name:'技術與供應鏈'}).click();await expect(page.getByRole('region',{name:'完整研究'})).toContainText('離線研究樣本');
  await page.unroute('**/api/themes/liquid-cooling/assessment');
  await page.route('**/api/themes/liquid-cooling/assessment',route=>route.fulfill({status:503,json:{detail:'判讀資料暫時不可用'}}));
  await page.reload();await page.getByRole('tab',{name:'研究判讀'}).click();
  await expect(page.getByRole('main').getByRole('alert')).toContainText('此區資料暫時無法取得');
  await page.getByRole('tab',{name:'技術與供應鏈'}).click();await expect(page.getByRole('region',{name:'完整研究'})).toContainText('離線研究樣本');
});

test('list, segment and event links lead to judgment; all structural candidates can expand',async({page})=>{
  await installOfflineApi(page);
  const paths=Array.from({length:7},(_,i)=>({segment:`segment-${i}`,name:`離線候選 ${i+1}`,mechanism:i%2?'theme':'sibling',via:'odm',path:['thermal',`segment-${i}`],companies:Array.from({length:8},(_,j)=>`TEST${j+1}`),confidence:'inference'}));
  await page.route('**/api/events/1',route=>route.fulfill({json:{...event,source,impact:{confidence:'inference',seeds:['thermal'],paths},raw:{offline:true}}}));
  await page.goto('/themes');await expect(page.locator('.theme-list')).toContainText('供應商份額仍待核對');
  await page.goto('/');await page.getByRole('tab',{name:'追蹤重點'}).click();await expect(page.locator('#segment-reading .theme-tags')).toContainText('供應商份額仍待核對');
  await page.goto('/events/1');
  const candidates=page.locator('.structural-candidates');
  await expect(candidates).not.toHaveAttribute('open','');
  await expect(page.locator('.impact-list')).toBeHidden();
  await candidates.locator(':scope > summary').focus();await page.keyboard.press('Enter');
  await expect(page.locator('.impact-list>div')).toHaveCount(7);
  await expect(page.locator('.impact-list>div').first().getByRole('link')).toHaveCount(8);
  await page.getByRole('link',{name:'閱讀液冷判讀',exact:true}).click();
  await expect(page).toHaveURL(/themes\/liquid-cooling#assessment/);
  await expect(page.getByRole('heading',{name:'目前判讀'})).toBeVisible();
});
