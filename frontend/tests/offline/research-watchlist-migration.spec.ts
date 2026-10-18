import {test,expect} from '@playwright/test';
import {server,stored,card,key,legacyKey,shown} from './watchlist-fixture';

const v1={theme_ids:['liquid-cooling','retired-theme'],seen:{'liquid-cooling':{version_id:1,indicator_token:'i1',candidate_token:'c1'},'retired-theme':{version_id:null,indicator_token:'',candidate_token:''}}};
const seed=(value:unknown,name=legacyKey)=>({name,text:typeof value==='string'?value:JSON.stringify(value)});

test('同網址一次遷移：數值基準沿用，研究與事件待確認，舊清單保留且移除後不回加',async({page})=>{
  await server(page);
  await page.addInitScript(({name,text})=>{if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');localStorage.setItem(name,text)}},seed(v1));
  await page.goto('/next?view=watchlist&release_id='+shown);
  await expect(page.getByText('已從舊版題材關注匯入 2 項',{exact:false})).toBeVisible();
  const theme=card(page,'合成液冷題材');
  await expect(theme).toContainText('數值無變更');  // v1 indicator token is the same measure as v2 values.
  await expect(theme.getByText('待確認：尚未建立已讀基準')).toHaveCount(2);  // research and events are never auto-read.
  await expect(card(page,'題材 retired-theme')).toContainText('可能已改名、合併或封存');
  const saved=await stored(page);
  expect(saved.v1_migrated).toBe(true);
  expect(saved.targets.map((t:{id:string})=>t.id)).toEqual(['theme-liquid-cooling','theme-retired-theme']);
  expect(await stored(page,legacyKey)).toEqual(v1);
  await theme.getByRole('button',{name:'移除收藏'}).click();
  await page.reload();
  await expect(page.locator('.rs-watch-card')).toHaveCount(1);await expect(card(page,'合成液冷題材')).toHaveCount(0);
  await expect(page.getByText('已從舊版題材關注匯入',{exact:false})).toHaveCount(0);
  expect(await stored(page,legacyKey)).toEqual(v1);
});

test('既有新版收藏與舊清單合併不重複，保留新版已讀狀態',async({page})=>{
  await server(page);
  const current={schema_version:2,targets:[{kind:'theme',id:'theme-liquid-cooling',name:'合成液冷題材',seen:{research:'t1',values:'i1',events:0}}]};
  await page.addInitScript(([a,b])=>{localStorage.setItem(a.name,a.text);localStorage.setItem(b.name,b.text)},[seed(v1),seed(current,key)] as const);
  await page.goto('/next?view=watchlist&release_id='+shown);
  await expect(page.getByText('已從舊版題材關注匯入 1 項',{exact:false})).toBeVisible();
  const saved=await stored(page);
  expect(saved.targets).toHaveLength(2);expect(saved.targets[0].seen).toEqual({research:'t1',values:'i1',events:0});
  await expect(card(page,'合成液冷題材')).toContainText('研究無變更');
});

test('儲存被拒絕時每次只在記憶體遷移，重跑不重複',async({page})=>{
  await server(page);
  await page.addInitScript(({name,text})=>{localStorage.setItem(name,text);Object.defineProperty(Storage.prototype,'setItem',{value(){throw new Error('blocked')}})},seed(v1));
  for(let round=0;round<2;round++){
    await page.goto('/next?view=watchlist&release_id='+shown);
    await expect(page.locator('.rs-watch-card')).toHaveCount(2);
    await expect(page.getByText('記憶體暫存',{exact:false})).toBeVisible();
  }
});

test('舊清單部分損壞只匯入有效題材；整份無法讀取時不匯入並保留舊資料',async({page})=>{
  await server(page);
  const damaged={theme_ids:['liquid-cooling',123,'BAD ID','liquid-cooling'],seen:{'liquid-cooling':{version_id:1,indicator_token:'i0',candidate_token:'c'}}};
  await page.addInitScript(({name,text})=>{if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');localStorage.setItem(name,text)}},seed(damaged));
  await page.goto('/next?view=watchlist&release_id='+shown);
  await expect(page.getByText('部分內容無法讀取',{exact:false})).toBeVisible();
  await expect(page.locator('.rs-watch-card')).toHaveCount(1);
  await expect(card(page,'合成液冷題材')).toContainText('有效數值有新期或修訂');  // a different v1 token is an update, not read.
  const broken=await page.context().newPage();await server(broken);
  await broken.addInitScript(({name,text})=>{localStorage.clear();localStorage.setItem(name,text)},seed('{broken'));
  await broken.goto('/next?view=watchlist&release_id='+shown);
  await expect(broken.getByText('部分內容無法讀取',{exact:false})).toBeVisible();
  await expect(broken.getByText('尚未收藏研究',{exact:false})).toBeVisible();
  expect(await broken.evaluate(k=>localStorage.getItem(k),legacyKey)).toBe('{broken');
});
