import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

for(const mobile of [false,true])test(`來源能力、單次更新與限流後完成${mobile?'（手機）':'（桌機）'}`,async({page})=>{
  await page.setViewportSize({width:mobile?390:1440,height:mobile?844:1000});
  await page.clock.install();
  const id='77777777-7777-4777-8777-777777777777';let polls=0,updates=0;
  const source={id:'twse-synthetic',name:'合成測試官方月營收',url:'https://official.example/',adapter:'tw',status:'not_run',last_success:null,error:null};
  const job={job_id:id,status:'queued',available_at:'2026-10-17T10:00:00Z',requests:0};
  const detail={...source,declared:{can_refresh:true,frequency_hours:24,history_limit:'僅依官方提供期間；不保證任意歷史。',classification_limit:'分類不提升研究主張確定性。'},last_job:null,last_result:null};
  await page.route('**/api/admin/**',async route=>{
    const request=route.request(),url=new URL(request.url());
    if(url.pathname.endsWith('/session'))await route.fulfill({json:{authenticated:true,csrf_token:'synthetic-csrf'}});
    else if(url.pathname.endsWith('/releases'))await route.fulfill({json:{items:[],active_release_id:id,has_more:false}});
    else if(url.pathname.endsWith('/drafts'))await route.fulfill({json:{items:[]}});
    else if(url.pathname==='/api/admin/sources')await route.fulfill({json:{items:[source],has_more:true,next_cursor:'twse-synthetic'}});
    else if(url.pathname.endsWith('/refresh')){updates++;await route.fulfill({status:202,json:job})}
    else if(url.pathname.endsWith('/source-jobs/'+id)){polls++;await route.fulfill({json:{...job,status:polls===1?'deferred':'success',requests:polls,failure:polls===1?{message:'提供者暫停存取，已保存稍後重試時間。'}:null}})}
    else if(url.pathname.endsWith('/twse-synthetic'))await route.fulfill({json:polls>1?{...detail,status:'success',last_success:'2026-10-17T11:00:00Z'}:detail});
    else await route.fulfill({status:404,json:{message:'Unexpected synthetic request'}});
  });
  await page.goto('/admin');await page.getByRole('button',{name:'來源健康',exact:true}).click();
  await page.getByRole('button',{name:'來源能力',exact:true}).click();
  await expect(page.getByRole('region',{name:source.name+'來源能力'})).toContainText('每 24 小時');
  if(mobile){const bounds=await page.getByRole('region',{name:source.name+'來源能力'}).boundingBox();expect(bounds!.x).toBeGreaterThanOrEqual(0);expect(bounds!.x+bounds!.width).toBeLessThanOrEqual(390)}
  // Source capability no longer lists company financial metrics.
  await expect(page.getByRole('region',{name:source.name+'來源能力'})).toContainText('僅依官方提供期間');await expect(page.getByText('營業現金流')).toHaveCount(0);
  const update=page.getByRole('button',{name:'更新一次',exact:true});await update.click();
  await expect(update).toBeDisabled();await expect(page.getByText('等待背景服務',{exact:true})).toBeVisible();
  await page.clock.fastForward(5100);
  await expect(page.getByText(/依提供者要求稍後再試/)).toBeVisible();
  await mkdir('../.work/source-update-review',{recursive:true});
  await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  await page.screenshot({path:`../.work/source-update-review/${mobile?'mobile':'desktop'}.png`,fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.clock.fastForward(30100);
  await expect(page.getByText('本輪已完成',{exact:true})).toBeVisible();
  await expect(update).toBeEnabled();await expect(page.getByRole('cell',{name:/已取得$/})).toBeVisible();
  await expect(page.getByRole('button',{name:'載入更多來源'})).toBeVisible();expect(updates).toBe(1);
});

test('來源更新代理拒絕匿名與跨站請求',async({request,baseURL})=>{
  expect((await request.post('/api/admin/sources/twse-synthetic/refresh',{headers:{Origin:'https://untrusted.invalid'}})).status()).toBe(403);
  expect((await request.post('/api/admin/sources/twse-synthetic/refresh',{headers:{Origin:baseURL!}})).status()).toBe(401);
  expect((await request.get('/api/admin/sources/twse-synthetic')).status()).toBe(401);
  expect((await request.get('/api/admin/source-jobs/77777777-7777-4777-8777-777777777777')).status()).toBe(401);
});
