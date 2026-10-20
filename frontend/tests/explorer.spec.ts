import {test,expect,Page,Locator} from '@playwright/test';

async function readyGraph(graph:Locator){
  await expect(graph).toBeVisible();
  await expect.poll(()=>graph.evaluate(e=>(e as any)._cyreg?.cy?.nodes().length)).toBe(Number(await graph.getAttribute('data-nodes')));
}
async function clickGraphNode(page:Page,id:string){
  const graph=page.locator('.desktop-map').getByTestId('network');
  await readyGraph(graph);
  const point=await graph.evaluate((e,id)=>(e as any)._cyreg.cy.getElementById(id).renderedPosition(),id);
  await graph.click({position:point});
}
const heading=(page:Page,name:string)=>page.locator('#segment-reading').getByRole('heading',{name,exact:true});
test.afterEach(async({page})=>{
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

test('desktop graph selection, neighbor highlighting, viewport, URL history and sharing',async({page,context})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(heading(page,'運算晶片')).toBeVisible();
  const graph=page.locator('.desktop-map').getByTestId('network');
  const industry=await (await page.request.get('/api/industries/ai-server/graph')).json();
  await expect(graph).toHaveAttribute('data-nodes',String(industry.nodes.filter((n:any)=>!n.external).length));
  await clickGraphNode(page,'thermal');
  await expect(heading(page,'散熱')).toBeVisible();
  await expect(page).toHaveURL(/segment=thermal/);
  const style=await graph.evaluate(e=>{const cy=(e as any)._cyreg.cy;return {selected:cy.$('node.selected').id(),neighbors:cy.$('node.neighbor').length,highlighted:cy.$('edge.highlighted').length,dimmed:cy.$('.dimmed').length,font:Math.min(...cy.nodes().map((n:any)=>n.numericStyle('font-size')*cy.zoom()))}});
  expect(style).toMatchObject({selected:'thermal'});expect(style.neighbors).toBeGreaterThan(0);expect(style.highlighted).toBeGreaterThan(0);expect(style.dimmed).toBeGreaterThan(0);expect(style.font).toBeGreaterThanOrEqual(13.99);
  await page.locator('.desktop-map').getByRole('button',{name:'放大圖形'}).click();
  const viewport=await graph.evaluate(e=>({zoom:(e as any)._cyreg.cy.zoom(),pan:(e as any)._cyreg.cy.pan()}));
  await page.setViewportSize({width:1360,height:900});
  await expect.poll(()=>graph.evaluate(e=>({zoom:(e as any)._cyreg.cy.zoom(),pan:(e as any)._cyreg.cy.pan()}))).toEqual(viewport);
  await page.getByRole('button',{name:'記憶體',exact:true}).click();
  await expect(heading(page,'記憶體')).toBeVisible();
  await page.goBack();await expect(heading(page,'散熱')).toBeVisible();
  const shared=await context.newPage();await shared.goto(page.url());await expect(heading(shared,'散熱')).toBeVisible();await shared.close();
  await page.getByRole('checkbox',{name:'展開跨產業'}).check();
  await expect(graph).toHaveAttribute('data-nodes',String(industry.nodes.length));
  await page.locator('.desktop-map').getByRole('button',{name:'重設視角'}).click();
  await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  await page.screenshot({path:'test-results/desktop-explorer.png'});
  expect(errors).toEqual([]);
});

test('all 17 segments and seven themes expose full research and evidence links',async({page})=>{
  test.setTimeout(90000);
  const segments=await (await page.request.get('/api/segments')).json();expect(segments).toHaveLength(17);
  for(const s of segments){
    await page.goto(`/?layer=${s.layer}&segment=${s.id}`);
    await expect(heading(page,s.name)).toBeVisible();
    const reading=page.locator('#segment-reading');
    await expect(reading.getByRole('heading',{name:'供應與需求關係'})).toBeVisible();
    await expect(reading.getByRole('heading',{name:'代表公司與供應角色'})).toBeVisible();
    await reading.getByRole('tab',{name:'技術與限制'}).click();
    await expect(reading.getByRole('heading',{name:'技術變數',exact:true})).toBeVisible();
    expect(await reading.locator('.prose a[href^="https://"]').count()).toBeGreaterThan(0);
    await reading.getByRole('tab',{name:'追蹤重點'}).click();
    await expect(reading.getByRole('heading',{name:'監測指標與轉折訊號'})).toBeVisible();
  }
  await page.goto('/themes');await expect(page.locator('.theme-list article')).toHaveCount(7);
  const themes=await (await page.request.get('/api/themes')).json();
  for(const t of themes){
    await page.goto(`/themes/${t.theme}`);await expect(page.getByRole('heading',{name:t.name_zh,exact:true})).toBeVisible();
    await expect(page.getByText(`狀態查核 ${t.checked}`,{exact:false})).toBeVisible();
    await page.getByRole('tab',{name:'數據與追蹤'}).click();
    await expect(page.getByRole('heading',{name:'里程碑與實際進展'})).toBeVisible();
    await expect(page.getByRole('heading',{name:'已發布的相關事件'})).toBeVisible();
    expect(await page.locator('.theme-research a[href^="https://"]').count()).toBeGreaterThan(0);
  }
  await page.goto('/themes/liquid-cooling');await expect(page.getByRole('heading',{name:'目前判讀'})).toBeVisible();await page.screenshot({path:'test-results/desktop-theme.png',fullPage:true});
  await page.locator('.theme-tags a[href*="segment=thermal"]').click();await expect(heading(page,'散熱')).toBeVisible();
});

test('rapid selection discards slow response; loading, retry and empty states remain readable',async({page})=>{
  await page.route('**/api/segments/memory',async route=>{const response=await route.fetch();await new Promise(r=>setTimeout(r,1000));await route.fulfill({response})});
  await page.goto('/');await expect(heading(page,'運算晶片')).toBeVisible();
  await page.getByRole('button',{name:'記憶體',exact:true}).click();
  await expect(page.locator('#segment-reading')).toHaveAttribute('aria-busy','true');
  await expect(heading(page,'運算晶片')).toHaveCount(0);
  await page.getByRole('button',{name:'散熱',exact:true}).click();await expect(heading(page,'散熱')).toBeVisible();
  await expect(page.locator('#segment-reading')).toHaveAttribute('aria-busy','false');
  await page.waitForTimeout(1200);await expect(heading(page,'散熱')).toBeVisible();await expect(heading(page,'記憶體')).toHaveCount(0);
  await page.route('**/api/segments/interconnect',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'測試來源暂時不可用'})}));
  await page.getByRole('button',{name:'連接器、線材與滑軌',exact:true}).click();await expect(page.locator('#segment-reading').getByRole('alert')).toBeVisible();
  await page.unroute('**/api/segments/interconnect');await page.locator('#segment-reading').getByRole('button',{name:'重新取得'}).click();await expect(heading(page,'連接器、線材與滑軌')).toBeVisible();
  await page.goto('/events?date_from=2099-01-01');await expect(page.getByText('尚未取得直接相關事件。',{exact:false})).toBeVisible();
});

test('mobile readable list, immediate reading, local map, fullscreen and keyboard search',async({page})=>{
  await page.setViewportSize({width:390,height:844});await page.goto('/');
  await expect(page.locator('.desktop-map')).toBeHidden();await expect(page.getByTestId('local-network')).toBeVisible();
  const thermal=page.getByRole('button',{name:'散熱',exact:true});await thermal.focus();await page.keyboard.press('Enter');
  await expect(heading(page,'散熱')).toBeVisible();
  await expect.poll(()=>page.locator('#segment-reading').evaluate(e=>e.getBoundingClientRect().top)).toBeLessThan(80);
  await page.screenshot({path:'test-results/mobile-reading.png'});
  await page.getByRole('button',{name:'全螢幕完整圖'}).click();
  const modal=page.getByRole('dialog',{name:'全螢幕完整產業圖'});await expect(modal).toBeVisible();await readyGraph(modal.getByTestId('network'));
  await page.screenshot({path:'test-results/mobile-fullscreen.png'});
  await modal.getByRole('button',{name:'運算晶片',exact:true}).click();await expect(modal).toBeHidden();await expect(heading(page,'運算晶片')).toBeVisible();
  const search=page.getByRole('textbox',{name:'搜尋公司、產品、環節或題材'});await search.fill('臺積電');
  await expect(page.locator('.search-results a').first()).toContainText('台積電');await search.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/focus=company-tsmc/);await expect(page.locator('.rs-detail > h2')).toHaveText('台積電');
  await search.fill('液冷');await page.locator('.search-results a[href="/themes/liquid-cooling"]').click();await expect(page).toHaveURL(/themes\/liquid-cooling/);
  await search.fill('不存在的搜尋');await expect(page.getByText('找不到結果，請試公司代號、產品或環節名稱。')).toBeVisible();await search.press('Escape');await expect(page.locator('.search-results')).toHaveCount(0);
});

test('old company and comparison URLs open the new research pages',async({page})=>{
  await page.goto('/companies/2330.TW');await expect(page).toHaveURL(/focus=company-tsmc/);await expect(page.locator('.rs-detail > h2')).toHaveText('台積電');
  await expect(page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'公司',exact:true})).toHaveAttribute('aria-current','page');
  await page.goto('/compare?tickers=NVDA,AMD');await expect(page).toHaveURL(/\/next\?view=compare/);
  await page.goto('/companies/UNKNOWN');await expect(page.getByRole('heading',{name:'無法開啟這家公司的研究'})).toBeVisible();
});

test('event filtering, provenance, day precision and official background statistics',async({page})=>{
  await page.goto('/events');await expect(page.getByRole('heading',{name:'近期產業事件'})).toBeVisible();
  await expect(page.locator('.event-title').first()).toBeVisible();
  const all=await (await page.request.get('/api/events?limit=30')).json();expect(all.every((e:any)=>!e.routine)).toBeTruthy();
  expect(all.every((e:any)=>e.segments.some((s:any)=>s.relevance==='direct')||e.themes.some((t:any)=>t.relevance==='direct'))).toBeTruthy();
  await expect(page.getByRole('combobox',{name:'事件環節'}).locator('option')).toHaveCount(18);
  await page.getByRole('combobox',{name:'事件環節'}).selectOption('thermal');await expect(page).toHaveURL(/segment=thermal/);await expect(page.locator('.event-title').first()).toBeVisible();
  await page.locator('.event-title').first().click();await expect(page.getByRole('heading',{name:'來源摘錄'})).toBeVisible();await expect(page.getByRole('heading',{name:'內容分類與依據'})).toBeVisible();await expect(page.getByRole('link',{name:'閱讀原始來源 ↗'})).toHaveAttribute('href',/^https:\/\//);
  await expect(page.getByText('產業資訊，無單一公司主體')).toBeVisible();await expect(page.locator('.classification-evidence').first()).toBeVisible();
  await page.goto('/events?kind=official_stats&relevance=background');await expect(page.locator('.event-title').first()).toBeVisible();
  await expect(page.locator('.event-date time').first()).not.toContainText('00:00');await page.locator('.event-title').first().click();await expect(page.getByText('統計／資料期間',{exact:false})).toBeVisible();await expect(page.getByText('此事件沒有直接環節起點，保留資料缺口。')).toBeVisible();
  await page.goto('/events?relevance=background');await expect(page.locator('.event-title').first()).toBeVisible();
  const background=await (await page.request.get('/api/events?relevance=background')).json();expect(background.every((e:any)=>e.kind==='official_stats')).toBeTruthy();
  const day=background.find((e:any)=>e.published_precision==='day');expect(day).toBeTruthy();
  await page.goto(`/events/${day.id}`);await expect(page.locator('.page-heading p')).toContainText(`發布 ${new Date(day.published_at).toLocaleDateString('sv-SE',{timeZone:'Asia/Taipei'})}`);
  const substrate=await (await page.request.get('/api/events?segment=substrate&limit=100')).json();
  const twDay=substrate.find((e:any)=>e.source_id==='tpca-news'&&e.published_precision==='day');expect(twDay).toBeTruthy();
  const twDate=new Date(twDay.published_at).toLocaleDateString('sv-SE',{timeZone:'Asia/Taipei'});expect(twDate).not.toBe(twDay.published_at.slice(0,10));
  await page.goto(`/events/${twDay.id}`);await expect(page.locator('.page-heading p')).toContainText(`發布 ${twDate}`);
});

test('coverage matrix agrees with API, exports and source health including partial retrieval',async({page})=>{
  const response=await page.request.get('/api/coverage'),data=await response.json();expect(data.rows).toHaveLength(24);
  await page.goto('/coverage');await expect(page.locator('tbody tr')).toHaveCount(24);
  for(const row of data.rows){const tr=page.locator('tbody tr').filter({has:page.getByRole('link',{name:row.name,exact:true})});await expect(tr).toContainText(`${row.direct_30d}／${row.direct_90d}`);await expect(tr).toContainText(`${row.configured_sources}／${row.successful_sources}`)}
  const report=await (await page.request.get('/api/coverage/report')).text();for(const r of data.rows)expect(report).toContain(`| ${r.kind} | ${r.name} (${r.id}) |`);
  await page.screenshot({path:'test-results/desktop-coverage.png',fullPage:true});
  await page.goto('/sources');await expect(page.getByRole('heading',{name:'來源更新狀態'})).toBeVisible();
  const sources=await (await page.request.get('/api/sources')).json();await expect(page.locator('.source-row')).toHaveCount(sources.sources.length);expect(sources.sources.some((s:any)=>['failed','partial','configuration_required'].includes(s.status))).toBeTruthy();
  await expect(page.locator('.source-row').first()).toContainText('網頁可讀性');
});
