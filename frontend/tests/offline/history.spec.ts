import {test,expect} from '@playwright/test';
import {installOfflineApi} from './fixture-data';
test('版本選擇器在手机支援鍵盤與來源連結，查核日和記錄時間分開',async({page})=>{
  const unexpected=await installOfflineApi(page);
  const versions=[2,1].map(n=>({version_id:n,version_number:n,theme_id:'liquid-cooling',reviewed:'2026-10-07',recorded_at:'2026-10-14T00:00:00Z',reason:n===2?'範圍重新核對':'首次基準'}));
  await page.route('**/api/themes/liquid-cooling/assessment/versions?*',r=>r.fulfill({json:{current_version_id:2,total:2,versions}}));
  await page.route('**/api/themes/liquid-cooling/assessment/compare?*',r=>{const url=new URL(r.request().url());return r.fulfill({json:{from:versions[1],to:versions[0],changes:url.searchParams.get('from_version')==='1'?[{path:'assessment.evidence[new].url',kind:'added',before:null,after:'https://example.org/new-proof'}]:[]}})});
  await page.setViewportSize({width:390,height:844});await page.goto('/themes/liquid-cooling');
  const section=page.locator('#versions');await section.locator('summary').click();
  await section.getByLabel('原版本',{exact:true}).selectOption('1');await section.getByLabel('比較版本',{exact:true}).selectOption('2');
  await expect(section.getByText('變更原因：範圍重新核對')).toBeVisible();
  await expect(section.getByRole('link',{name:'原始來源 ↗'})).toHaveAttribute('href','https://example.org/new-proof');
  await section.getByLabel('原版本',{exact:true}).focus();await page.keyboard.press('ArrowUp');await page.keyboard.press('Enter');
  await expect(section.getByText('變更原因：範圍重新核對')).not.toBeVisible();
  await section.getByLabel('原版本',{exact:true}).selectOption('1');
  await section.getByRole('link',{name:'返回目前判讀'}).click();await expect(page).toHaveURL(/#assessment$/);
  expect(unexpected).toEqual([]);
});

test('分享指定兩版會自動展開並取得比較，未選版本不發差異請求',async({page})=>{
  await installOfflineApi(page);
  const versions=[2,1].map(n=>({version_id:n,version_number:n,theme_id:'liquid-cooling',reviewed:'2026-10-07',recorded_at:'2026-10-14T00:00:00Z',reason:'分享比較測試'}));
  await page.route(/\/assessment\/versions\?/,r=>r.fulfill({json:{current_version_id:2,total:2,versions}}));
  await page.route(/\/assessment\/versions\/[12]$/,r=>r.fulfill({json:versions.find(v=>String(v.version_id)===new URL(r.request().url()).pathname.split('/').at(-1))}));
  await page.route('**/api/segments',r=>r.fulfill({json:[{id:'power',name:'電源供應',layer:'ai-server'}]}));
  await page.route('**/api/themes/liquid-cooling/assessment/compare?*',r=>r.fulfill({json:{from:versions[1],to:versions[0],changes:[{path:'assessment.summary',kind:'modified',before:'原基準',after:'分享指定版本'},{path:'milestones[check].date',kind:'modified',before:2026,after:2027},{path:'assessment.evidence[power-plan].excerpt',kind:'modified',before:'power infrastructure',after:'power supply'}]}}));
  await page.goto('/themes/liquid-cooling?from_version=1&to_version=2#versions');
  const section=page.locator('#versions');await expect(section.locator('details').first()).toHaveAttribute('open','');await expect(section.getByLabel('原版本',{exact:true})).toHaveValue('1');await expect(section.getByLabel('比較版本',{exact:true})).toHaveValue('2');await expect(section.getByText('分享指定版本',{exact:true})).toBeVisible();
  await expect(section.getByText('2027',{exact:true})).toBeVisible();await expect(section.getByText('power infrastructure',{exact:true})).toBeVisible();
});
