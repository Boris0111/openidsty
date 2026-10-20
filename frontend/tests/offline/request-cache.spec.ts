import {test,expect} from '@playwright/test';
import {subscribeRequest} from '../../lib/request-cache';
import {installOfflineApi} from './fixture-data';

const flush=()=>new Promise(resolve=>setImmediate(resolve));
test('共同訂閱只取得一次；移除其中一位不取消，最後離開才取消，舊回應無法回填',async()=>{
  const original=globalThis.fetch;let calls=0;const pending:{resolve:(response:Response)=>void;signal:AbortSignal}[]=[];
  globalThis.fetch=(_path,options)=>{calls++;return new Promise(resolve=>pending.push({resolve,signal:options!.signal as AbortSignal}));};
  try{
    const a:any[]=[],b:any[]=[];const first=subscribeRequest('/api/segments?case=shared&b=2&a=1',s=>a.push(s));
    const second=subscribeRequest('/api/segments?a=1&b=2&case=shared',s=>b.push(s));expect(calls).toBe(1);
    first.unsubscribe();expect(pending[0].signal.aborted).toBe(false);pending[0].resolve(Response.json({name:'正確回應'}));await flush();expect(b.at(-1).data.name).toBe('正確回應');second.unsubscribe();
    const old=subscribeRequest('/api/themes?case=cancel',()=>{});old.unsubscribe();expect(pending[1].signal.aborted).toBe(true);
    const states:any[]=[];const fresh=subscribeRequest('/api/themes?case=cancel',s=>states.push(s));pending[1].resolve(Response.json({name:'過期'}));pending[2].resolve(Response.json({name:'目前'}));await flush();expect(states.at(-1).data.name).toBe('目前');fresh.unsubscribe();
  }finally{globalThis.fetch=original;}
});
test('60／30 秒固定 TTL、動態不保存、query 隔離及失敗重試共用新結果',async()=>{
  const originalFetch=globalThis.fetch,originalNow=Date.now;let now=100000,calls=0,fail=false;Date.now=()=>now;
  globalThis.fetch=async()=>{calls++;return fail?Response.json({detail:'測試失敗'},{status:503}):Response.json({number:calls});};
  const read=async(path:string)=>{let state:any;const s=subscribeRequest(path,v=>state=v);await flush();s.unsubscribe();return state;};
  try{
    await read('/api/segments?case=ttl');now+=59000;await read('/api/segments?case=ttl');expect(calls).toBe(1);now+=1001;await read('/api/segments?case=ttl');expect(calls).toBe(2);
    await read('/api/coverage?case=ttl');now+=30001;await read('/api/coverage?case=ttl');expect(calls).toBe(4);
    await read('/api/themes/liquid-cooling/assessment?case=ttl');await read('/api/themes/liquid-cooling/assessment?case=ttl');expect(calls).toBe(6);
    await read('/api/segments?case=other');expect(calls).toBe(7);
    fail=true;const states:any[]=[];const a=subscribeRequest('/api/coverage?case=retry',s=>states.push(s));const b=subscribeRequest('/api/coverage?case=retry',s=>states.push(s));await flush();expect(states.at(-1).error).toBe('測試失敗');fail=false;a.retry();b.retry();await flush();expect(calls).toBe(9);expect(states.at(-1).error).toBe('');a.unsubscribe();b.unsubscribe();
  }finally{globalThis.fetch=originalFetch;Date.now=originalNow;}
});
test('已完成且無訂閱的 LRU 有界，重新讀最舊項目會再次取得',async()=>{
  const original=globalThis.fetch;let calls=0;globalThis.fetch=async()=>{calls++;return Response.json([]);};
  try{for(let i=0;i<102;i++){const s=subscribeRequest(`/api/segments?case=lru-${i}`,()=>{});await flush();s.unsubscribe();}const s=subscribeRequest('/api/segments?case=lru-0',()=>{});await flush();expect(calls).toBe(103);s.unsubscribe();}finally{globalThis.fetch=original;}
});
test('事件頁多個題材訂閱共用請求；初次閱讀不取歷史，單版不自我比較',async({page})=>{
  const unexpected=await installOfflineApi(page);const requests:string[]=[];page.on('request',r=>{if(r.url().includes('/api/'))requests.push(new URL(r.url()).pathname);});
  await page.route('**/api/themes',async route=>{await new Promise(resolve=>setTimeout(resolve,200));await route.fallback();});
  await page.goto('/events/1');await expect(page.getByRole('heading',{name:'直接相關題材的判讀'})).toBeVisible();
  await expect(page.getByRole('link',{name:'閱讀液冷判讀'})).toBeVisible();expect(requests.filter(p=>p==='/api/themes')).toHaveLength(1);
  await page.getByRole('link',{name:'閱讀液冷判讀'}).click();await expect(page.getByRole('heading',{name:'液冷',exact:true})).toBeVisible();
  expect(requests.filter(p=>p.includes('/assessment/versions'))).toHaveLength(0);await page.locator('#versions summary').click();await expect(page.getByText('首次只保存目前研究基準，沒有虛構更早歷史。')).toBeVisible();expect(requests.filter(p=>p.includes('/assessment/compare'))).toHaveLength(0);expect(unexpected).toEqual([]);
});
