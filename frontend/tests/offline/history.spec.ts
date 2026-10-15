import {test,expect} from '@playwright/test';
import {installOfflineApi} from './fixture-data';
test('版本選擇器在手机支援鍵盤與來源連結，查核日和記錄時間分開',async({page})=>{
  const unexpected=await installOfflineApi(page);
  const versions=[2,1].map(n=>({version_id:n,version_number:n,theme_id:'liquid-cooling',reviewed:'2026-10-07',recorded_at:'2026-10-14T00:00:00Z',reason:n===2?'範圍重新核對':'首次基準'}));
  await page.route('**/api/themes/liquid-cooling/assessment/versions?*',r=>r.fulfill({json:{current_version_id:2,total:2,versions}}));
  await page.route('**/api/themes/liquid-cooling/assessment/compare?*',r=>{const url=new URL(r.request().url());return r.fulfill({json:{from:versions[1],to:versions[0],changes:url.searchParams.get('from_version')==='1'?[{path:'assessment.evidence[new].url',kind:'added',before:null,after:'https://example.org/new-proof'}]:[]}})});
  await page.setViewportSize({width:390,height:844});await page.goto('/themes/liquid-cooling');
  const section=page.locator('#versions');await expect(section.getByText('變更原因：範圍重新核對')).toBeVisible();
  await expect(section.getByRole('link',{name:'原始來源 ↗'})).toHaveAttribute('href','https://example.org/new-proof');
  await section.getByLabel('原版本',{exact:true}).focus();await page.keyboard.press('Home');await page.keyboard.press('Enter');
  await expect(section.getByText('兩版本的判讀內容相同。')).toBeVisible();
  await section.getByRole('link',{name:'返回目前判讀'}).click();await expect(page).toHaveURL(/#assessment$/);
  expect(unexpected).toEqual([]);
});
