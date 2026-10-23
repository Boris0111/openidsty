import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

for(const mobile of [false,true])test(`真實研究收藏：重查不產生假更新，研究與事件分開，公司不追蹤數值${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize({width:mobile?390:1440,height:mobile?844:1000});
  const bodies:string[]=[];page.on('request',request=>{if(request.url().includes('/api/v2/updates/query'))bodies.push(request.postData()||'')});
  await page.goto('/next?focus=company-vertiv');await expect(page.getByRole('article',{name:'選中研究內容'})).toContainText('Vertiv');
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  const release=new URL(page.url()).searchParams.get('release_id');
  expect(JSON.parse(bodies[0])).toEqual({release_id:release,items:[{kind:'company',id:'company-vertiv'}]});
  await page.goto('/next?focus=product-cold-plate');await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'收藏',exact:true}).click();
  const vertiv=page.locator('.rs-watch-card').filter({hasText:'Vertiv'});
  for(const text of ['研究無變更','沒有新事件'])await expect(vertiv).toContainText(text);await expect(vertiv).not.toContainText('數值');
  const coldPlate=page.locator('.rs-watch-card').filter({hasText:'冷板'});
  await expect(coldPlate).toContainText('研究無變更');await expect(coldPlate).not.toContainText('數值');
  await page.getByRole('button',{name:'檢查收藏更新'}).click();await expect(vertiv).toContainText('研究無變更');
  const stored=await page.evaluate(()=>JSON.parse(localStorage.getItem('industryflow.research-watchlist.v2')||'{}'));
  expect(stored.targets.map((t:{id:string})=>t.id)).toEqual(['company-vertiv','product-cold-plate']);
  expect(JSON.stringify(stored)).not.toMatch(/markdown|summary|供應角色/);  // Not an offline copy of the research.
  await mkdir('../.work/research-watchlist-review',{recursive:true});
  await page.screenshot({path:`../.work/research-watchlist-review/${mobile?'mobile':'desktop'}.png`,fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('真實預覽：匯出備份後在另一個瀏覽器環境匯入',async({page,browser})=>{
  await page.goto('/next?focus=company-vertiv');await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'收藏',exact:true}).click();
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'匯出收藏 JSON'}).click()]);
  const other=await browser.newContext({baseURL:test.info().project.use.baseURL});const second=await other.newPage();
  try{
    await second.goto('/next?view=watchlist');await expect(second.getByText('尚未收藏研究',{exact:false})).toBeVisible();
    await second.getByLabel('匯入收藏備份').setInputFiles((await download.path())!);
    await expect(second.getByLabel('匯入預覽')).toContainText('新增 1 項');
    await second.getByRole('button',{name:'確認合併'}).click();
    const vertiv=second.locator('.rs-watch-card').filter({hasText:'Vertiv'});
    for(const text of ['研究無變更','沒有新事件'])await expect(vertiv).toContainText(text);await expect(vertiv).not.toContainText('數值');
    await second.screenshot({path:'../.work/research-watchlist-review/imported.png',fullPage:true});
  }finally{await other.close()}
});
