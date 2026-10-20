import {test,expect} from '@playwright/test';
import {installOfflineApi} from './fixture-data';
// Theme pages share the device watchlist with the research pages; the retired v1 key is only a migration source.
const v1='industryflow.theme-watchlist.v1',v2='industryflow.research-watchlist.v2';

test('題材頁收藏寫入共用收藏，可在收藏頁閱讀且不再寫入舊版清單',async({page})=>{
  const unexpected=await installOfflineApi(page);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/themes/liquid-cooling');
  await page.getByRole('button',{name:'加入收藏'}).click();await expect(page.getByText('已加入收藏',{exact:true})).toBeVisible();
  await page.getByRole('navigation',{name:'主要導覽'}).getByRole('link',{name:'收藏',exact:true}).click();
  await expect(page).toHaveURL(/\/next\?view=watchlist/);
  await expect(page.locator('.rs-watch-card').filter({hasText:'液冷'})).toBeVisible();
  const stored=await page.evaluate(([a,b])=>[localStorage.getItem(a),JSON.parse(localStorage.getItem(b)!).targets.map((t:{id:string})=>t.id)],[v1,v2]);
  expect(stored).toEqual([null,['theme-liquid-cooling']]);
  await page.goto('/themes/liquid-cooling');await page.getByRole('button',{name:'移除收藏'}).click();
  await expect(page.getByRole('button',{name:'加入收藏'})).toBeVisible();
  expect(errors).toEqual([]);expect(unexpected).toEqual([]);
});

test('舊收藏網址轉到共用收藏，舊版題材清單遷移後保留',async({page})=>{
  const unexpected=await installOfflineApi(page);
  await page.addInitScript(k=>{if(!localStorage.getItem(k))localStorage.setItem(k,JSON.stringify({theme_ids:['liquid-cooling'],seen:{'liquid-cooling':{version_id:1,indicator_token:'i1',candidate_token:'c1'}}}))},v1);
  await page.goto('/watchlist');
  await expect(page).toHaveURL(/\/next\?view=watchlist/);
  await expect(page.locator('.rs-watch-card').filter({hasText:'液冷'})).toBeVisible();
  expect(await page.evaluate(k=>localStorage.getItem(k),v1)).not.toBeNull();
  expect(unexpected).toEqual([]);
});
