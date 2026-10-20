import {test,expect,Page} from '@playwright/test';
import {installOfflineApi} from './fixture-data';

async function relations(page:Page){
  const unexpected=await installOfflineApi(page);
  const nodes=[['thermal','散熱'],['odm','ODM 組裝'],['datacenter','資料中心'],['compute','運算晶片']].map(([id,name],i)=>({id,name,position:i+1,layer:'ai-server',company_count:1}));
  const detail={summary:'離線關係樣本；不代表公司交易。',items:['冷板與熱管理模組'],dependencies:['流量壓降與介面'],conditions:['平台驗證通過且有採購'],confidence:'inference',evidence:[],gaps:['未取得指定客戶、料號與驗收資料。'],reviewed:'2026-10-16'};
  const graph={layer:'ai-server',nodes,edges:[{id:'thermal:odm',source:'thermal',target:'odm',kind:'supply',direction:'one_way',relation:detail},{id:'datacenter:compute',source:'datacenter',target:'compute',kind:'demand-feedback',direction:'one_way',relation:{...detail,summary:'預算與部署回饋晶片需求。',items:['GPU／ASIC 採購需求'],conditions:['預算實際用於運算設備']}}]};
  await page.route('**/api/industries/ai-server/graph',r=>r.fulfill({json:graph}));
  return unexpected;
}

test('圖與文字清單共用關係、URL、返回、清除與無效選取',async({page})=>{
  const unexpected=await relations(page);
  await page.goto('/?layer=ai-server&segment=thermal');
  const list=page.locator('.relation-index');await list.locator(':scope > summary').click();
  const supply=list.getByRole('button',{name:/散熱 → ODM 組裝/});
  await supply.focus();await page.keyboard.press('Enter');
  const reading=page.getByRole('region',{name:'連線依據'});
  await expect(reading).toContainText('冷板與熱管理模組');
  await expect(reading).toContainText('未取得指定客戶、料號與驗收資料');
  expect(new URL(page.url()).searchParams.get('relation')).toBe('thermal:odm');
  await list.getByRole('button',{name:/資料中心 → 運算晶片/}).click();
  await expect(reading).toContainText('需求形成機制');await expect(reading).toContainText('GPU／ASIC 採購需求');
  await page.goBack();await expect(reading).toContainText('冷板與熱管理模組');
  await reading.getByRole('button',{name:'關閉連線詳情'}).click();
  await expect(supply).toBeFocused();expect(new URL(page.url()).searchParams.has('relation')).toBe(false);
  await page.goto('/?layer=ai-server&segment=thermal&relation=missing%3Aedge');
  await expect(page.getByRole('heading',{name:'找不到這條關係'})).toBeVisible();
  await page.getByRole('button',{name:'清除無效連線'}).click();await expect(reading).toHaveCount(0);
  expect(unexpected).toEqual([]);
});

test('手機鍵盤可直接分享、閱讀並返回清單焦點',async({page})=>{
  await relations(page);await page.setViewportSize({width:390,height:844});
  await page.goto('/?layer=ai-server&segment=thermal&relation=datacenter%3Acompute');
  const reading=page.getByRole('region',{name:'連線依據'});
  await expect(reading.getByRole('heading',{level:2})).toBeFocused();
  await expect(reading).toContainText('有條件推論');
  const close=reading.getByRole('button',{name:'關閉連線詳情'});await close.focus();await page.keyboard.press('Enter');
  // Navigation commits asynchronously; wait for the close before acting on the list.
  await expect(reading).toHaveCount(0);
  const list=page.locator('.relation-index');await list.locator(':scope > summary').focus();await page.keyboard.press('Enter');
  const item=list.getByRole('button',{name:/散熱 → ODM 組裝/});await item.focus();await page.keyboard.press('Enter');
  // Both sample relations share this text, so check the heading to be sure the new one is open.
  await expect(reading.getByRole('heading',{level:2})).toHaveText(/散熱 → ODM 組裝/);
  await expect(reading).toContainText('流量壓降與介面');
  await reading.getByRole('button',{name:'關閉連線詳情'}).focus();await page.keyboard.press('Enter');
  await expect(item).toBeFocused();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('點擊連線與 resize 保留同一張圖與視角',async({page})=>{
  await relations(page);await page.goto('/?layer=ai-server&segment=thermal');
  const graph=page.getByTestId('network');
  await expect(graph.locator('canvas').first()).toBeVisible();
  await expect.poll(()=>graph.evaluate(node=>Boolean((node as any)._cyreg?.cy))).toBe(true);
  await page.getByRole('button',{name:'放大圖形'}).first().click();
  const before=await graph.evaluate(node=>{const cy=(node as any)._cyreg.cy;return {zoom:cy.zoom(),pan:cy.pan()}});
  const point=await graph.evaluate(node=>{const cy=(node as any)._cyreg.cy;const point=cy.getElementById('thermal:odm').renderedMidpoint();const box=node.getBoundingClientRect();return {x:box.x+point.x,y:box.y+point.y}});
  await page.mouse.click(point.x,point.y);
  await expect(page.getByRole('region',{name:'連線依據'})).toContainText('冷板與熱管理模組');
  await page.setViewportSize({width:1250,height:900});
  const after=await graph.evaluate(node=>{const cy=(node as any)._cyreg.cy;return {zoom:cy.zoom(),pan:cy.pan()}});
  expect(after.zoom).toBeCloseTo(before.zoom,5);expect(after.pan).toEqual(before.pan);
});
