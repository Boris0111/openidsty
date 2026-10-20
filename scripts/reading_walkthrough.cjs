const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const fs=require('node:fs');
const origin=process.env.READING_ORIGIN||'http://127.0.0.1:3013';
fs.mkdirSync('.work/reading',{recursive:true});
(async()=>{
 const browser=await chromium.launch();const page=await browser.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const segments=await(await fetch(origin+'/api/segments')).json(),themes=await(await fetch(origin+'/api/themes')).json(),matrix=[];
 const before=fs.existsSync('.work/reading/review-before-metrics.json')?JSON.parse(fs.readFileSync('.work/reading/review-before-metrics.json','utf8')):fs.existsSync('docs/reading-review-walkthrough.json')?JSON.parse(fs.readFileSync('docs/reading-review-walkthrough.json','utf8')).representative_layout.before:[];
 const after=[];
 for(const mobile of [false,true]){
  await page.setViewportSize(mobile?{width:390,height:844}:{width:1440,height:1000});
  for(const item of [...segments.map(s=>({id:s.id,name:s.name,url:`/?layer=${s.layer}&segment=${s.id}`,type:'segment'})),...themes.map(t=>({id:t.theme,name:t.name_zh,url:`/themes/${t.theme}`,type:'theme'}))]){
   const requests=[];const track=r=>{if(r.url().includes('/api/'))requests.push(new URL(r.url()).pathname)};page.on('request',track);
   await page.goto(origin+item.url);
   const reading=item.type==='segment'?page.locator('#segment-reading'):page.locator('.theme-detail');
   await expect(reading.getByRole('heading',{name:item.name,exact:true})).toBeVisible();
   const first=reading.getByRole('tab',{name:item.type==='segment'?'產業角色':'研究判讀'});
   await expect(first).toHaveAttribute('aria-selected','true');
   if(mobile&&item.type==='segment')await expect.poll(()=>reading.evaluate(e=>e.getBoundingClientRect().top)).toBeLessThan(80);
   await expect(reading.getByRole('heading',{name:item.type==='segment'?'傳導鏈':'目前判讀',exact:true})).toBeVisible();
   for(const label of ['進階資訊','技術文件與待核對','進階診斷'])await expect(reading.getByText(label,{exact:true})).toHaveCount(0);
   if(!mobile&&['thermal','liquid-cooling'].includes(item.id)){
    after.push({id:item.id,...await page.evaluate(()=>({main_height:Math.round(document.querySelector('main').getBoundingClientRect().height),advanced_count:document.querySelectorAll('.advanced-info').length,maintenance_lists:document.querySelectorAll('.technical-documents').length}))});
    await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
    await page.screenshot({path:`.work/reading/review-after-${item.id}-desktop.png`});
   }
   if(mobile&&item.id==='thermal')await page.screenshot({path:'.work/reading/review-after-thermal-mobile.png'});
   await first.focus();await page.keyboard.press('ArrowRight');
   await expect(reading.getByRole('tab',{name:item.type==='segment'?'技術與限制':'技術與供應鏈'})).toHaveAttribute('aria-selected','true');
   const section=reading.locator('.technical-research');await expect(section.getByRole('heading',{name:'導入條件與限制'})).toBeVisible();
   if(/\b(?:[a-z-]+\.(?:upstream|themes)|beneficiaries|led_by|market_coverage)\b/.test(await reading.innerText()))throw new Error('Authoring fields leaked '+item.id);
   for(const name of ['導入前要滿足什麼條件？','什麼會卡住交付？','哪些方案不能直接替換？','目前還不能確認什麼？'])await expect(section.getByRole('heading',{name,exact:true})).toBeVisible();
   const evidence=section.locator('.technical-claim summary').first();await evidence.focus();await page.keyboard.press('Enter');
   await expect(section.locator('.technical-evidence a').first()).toBeVisible();
   const links=await section.locator('.technical-evidence a').evaluateAll(els=>els.map(a=>({text:a.textContent,url:a.getAttribute('href')})));
   if(!mobile&&item.id==='thermal')await page.screenshot({path:'.work/reading/review-after-thermal-technical.png'});
   if(mobile&&item.id==='cpo-silicon-photonics')await page.screenshot({path:'.work/reading/review-after-cpo-mobile.png'});
   await reading.getByRole('tab',{name:item.type==='segment'?'追蹤重點':'數據與追蹤'}).focus();await page.keyboard.press('Enter');
   await expect(reading.getByRole('heading',{name:item.type==='segment'?'監測指標與轉折訊號':'指標與衡量界線',exact:true})).toBeVisible();
   if(item.type==='theme')await expect(reading.getByRole('heading',{name:'里程碑與實際進展',exact:true})).toBeVisible();
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
   if(overflow)throw new Error('Horizontal overflow '+item.id+' '+mobile);
   if(requests.includes('/api/technical-documents'))throw new Error('Monitoring list fetched '+item.id);
   matrix.push({...item,viewport:mobile?'390x844':'1440x1000',default_reading:true,keyboard_tabs:true,technical_facets:5,citations:links,tracking:true,maintenance_list_requests:0,overflow:false});page.off('request',track);
  }
 }
 await page.goto(origin+'/themes/liquid-cooling#indicators');await expect(page.getByRole('tab',{name:'數據與追蹤'})).toHaveAttribute('aria-selected','true');await expect(page.locator('#indicators')).toBeVisible();
 await page.goto(origin+'/themes/liquid-cooling#candidates');await expect(page.locator('#candidates')).toBeVisible();
 await page.goto(origin+'/coverage');await expect(page.locator('tbody tr')).toHaveCount(24);await expect(page.getByRole('heading',{name:'技術文件與待核對'})).toHaveCount(0);
 await page.goto(origin+'/technical-documents/oif-cmis?version=revision-5-4#locator-management-scope');await expect(page.getByRole('heading',{name:'5.4',exact:true})).toBeVisible();await expect(page.locator('#locator-management-scope')).toBeVisible();await expect(page.getByRole('heading',{name:'內容觀測與人工核對'})).toHaveCount(0);
 const ocp=await(await fetch(origin+'/api/technical-documents/ocp-cold-plate-requirements')).json();
 await page.goto(origin+'/technical-documents/ocp-cold-plate-requirements?version=revision-one#locator-loop-boundary');await expect(page.locator('#locator-loop-boundary')).toBeVisible();
 const report={origin,checked:new Date().toISOString(),matrix,representative_layout:{before,after},deep_links:['#indicators','#candidates'],coverage_rows:24,retained_citation:{id:ocp.id,source_status:ocp.source.status,version:'revision-one',locator:'loop-boundary'},errors};
 fs.writeFileSync('docs/reading-review-walkthrough.json',JSON.stringify(report,null,2));
 await browser.close();if(errors.length)throw new Error(errors.join('\n'));console.log(JSON.stringify({rows:matrix.length,coverage_rows:24,errors,layout:report.representative_layout}));
})().catch(e=>{console.error(e);process.exit(1)});
