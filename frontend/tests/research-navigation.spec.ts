import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');
const screenshots=path.resolve('../.work/research-navigation-review');

test('真實 release 的 17 環節、7 題材與 95 公司都可從完整目錄到達',async({page})=>{
  await mkdir(screenshots,{recursive:true});await page.setViewportSize({width:1440,height:1000});
  for(const [view,count] of [['segments',17],['themes',7],['companies',95]] as const){
    await page.goto('/next?view='+view);const ids=new Set<string>();
    while(true){
      await expect(page.locator('.rs-directory li a').first()).toBeVisible();
      const hrefs=await page.locator('.rs-directory li a').evaluateAll(nodes=>nodes.map(node=>(node as HTMLAnchorElement).href));
      for(const href of hrefs)ids.add(new URL(href).searchParams.get('focus')!);
      if(await page.getByRole('link',{name:'下一頁',exact:true}).count()===0)break;
      await page.getByRole('link',{name:'下一頁',exact:true}).click();await expect(page).toHaveURL(/cursor=/);
    }
    expect(ids.size).toBe(count);
  }
  await page.goto('/next?view=companies');await page.getByLabel('應用範圍').selectOption('application-ai-rack-cooling');
  const listed=page.locator('.rs-directory li');
  await expect(listed.filter({hasText:'雙鴻'})).toHaveCount(1);await expect(listed.filter({hasText:'Vertiv'})).toHaveCount(1);
  expect(await listed.count()).toBeLessThan(95);
  await page.screenshot({path:path.join(screenshots,'desktop-company-directory.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(screenshots,'mobile-company-directory.png'),fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});

test('舊散熱地圖到應用、角色、產品、公司，麵包屑回原地圖，舊公司網址開啟新版公司研究',async({page})=>{
  await page.goto('/?layer=ai-server&segment=thermal');
  const entry=page.getByRole('link',{name:'閱讀產品與公司研究'});await expect(entry).toBeVisible();await entry.focus();await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/focus=segment-thermal/);
  await page.locator('.rs-node-list').getByRole('button',{name:'AI 機櫃液冷',exact:false}).first().click();
  await expect(page).toHaveURL(/focus=application-ai-rack-cooling/);
  // IDs are stable navigation contracts; names and research are from the real release.
  const role=await page.request.get('/api/v2/roles/role-chip-heat-capture?release_id='+new URL(page.url()).searchParams.get('release_id'));
  const roleName=(await role.json()).data.name;
  await page.locator('.rs-node-list').getByRole('button',{name:roleName,exact:true}).click();
  await page.locator('.rs-node-list').getByRole('button',{name:'液冷冷板',exact:true}).click();
  const crumbs=page.getByRole('navigation',{name:'研究位置'});
  await expect(crumbs.getByRole('link')).toHaveText(['產業地圖','散熱','AI 機櫃液冷']);
  await page.locator('.rs-company-links a').filter({hasText:'雙鴻'}).click();await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  await expect(crumbs.getByRole('link')).toHaveText(['公司']);
  await page.goBack();await crumbs.getByRole('link',{name:'散熱'}).click();await expect(page).toHaveURL(/layer=ai-server&segment=thermal/);
  await expect(page.locator('.segment-heading h2')).toHaveText('散熱');
  await page.goto('/companies/3324.TW');await expect(page).toHaveURL(/focus=company-auras/);await expect(page.locator('.rs-detail > h2')).toHaveText('雙鴻');
  await page.goBack();await expect(page).toHaveURL(/layer=ai-server&segment=thermal/);
});

test('真實圖的連線 URL、縮放平移與手機 resize',async({page,context})=>{
  await mkdir(screenshots,{recursive:true});await page.setViewportSize({width:1440,height:1000});await page.goto('/next');
  const picker=page.getByLabel('閱讀連線');await picker.selectOption({label:'雙鴻 — 液冷冷板（產品能力）'});
  await expect(page.getByRole('region',{name:'連線說明'})).toContainText('不指認交易客戶');
  const shared=await context.newPage();await shared.goto(page.url());await expect(shared.getByLabel('閱讀連線')).toHaveValue(await picker.inputValue());await shared.close();
  const canvas=page.getByTestId('research-network');await canvas.scrollIntoViewIfNeeded();await page.getByRole('button',{name:'放大關係圖'}).click();
  const zoom=await page.getByLabel('關係圖縮放比例').textContent();
  const box=(await canvas.boundingBox())!;await page.mouse.move(box.x+12,box.y+12);await page.mouse.down();await page.mouse.move(box.x+72,box.y+45,{steps:5});await page.mouse.up();
  await page.waitForTimeout(150);const before=await canvas.screenshot();
  await page.setViewportSize({width:1100,height:900});await page.waitForTimeout(100);await page.setViewportSize({width:1440,height:1000});await page.waitForTimeout(150);
  await expect(page.getByLabel('關係圖縮放比例')).toHaveText(zoom!);expect((await canvas.screenshot()).equals(before)).toBe(true);
  await page.screenshot({path:path.join(screenshots,'desktop-research.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await expect(page.getByLabel('關係圖縮放比例')).toHaveText(zoom!);
  await page.screenshot({path:path.join(screenshots,'mobile-research.png'),fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
