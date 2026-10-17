/** Browser memory only. Public reader GETs; no admin/session/owner-preview data. */
import type {ResearchEnvelope} from './research-api';

type Payload=ResearchEnvelope<unknown>;
type Stored={payload:Payload;etag:string|null;expires:number;ttl:number};
type Pending={promise:Promise<Stored>;controller:AbortController;users:number};
const completed=new Map<string,Stored>(),pending=new Map<string,Pending>();
const roots=new Set(['manifest','catalog','search','resolve','companies','products','themes','concepts','research','applications','roles','segments','documents','graphs','impact','events','observations','compare']);
const LIMIT=100;

export function researchKey(path:string){
  const url=new URL(path,'http://reader.invalid');
  if(!path.startsWith('/api/v2/')||url.origin!=='http://reader.invalid'||!roots.has(url.pathname.split('/')[3])||url.hash)throw new Error('找不到這個閱讀請求。');
  url.searchParams.sort();
  return url.pathname+url.search;
}
export function dynamicResearch(key:string){const root=key.split('?')[0].split('/')[3];return ['compare','events','observations'].includes(root)||key.split('?')[0].includes('/financials')}
function ceiling(key:string){const url=new URL(key,'http://reader.invalid');return url.searchParams.getAll('release_id').length===1&&url.searchParams.get('release_id')?(dynamicResearch(key)?30000:86400000):0}
function ttl(key:string,response:Response,previous?:Stored){
  const control=response.headers.get('cache-control')||'';
  if(/\bno-store\b|\bno-cache\b/i.test(control))return 0;
  const match=/(?:^|,)\s*max-age=(\d+)/i.exec(control);
  const seconds=match?Number(match[1])*1000:response.status===304?previous?.ttl||0:0;
  return Math.max(0,Math.min(ceiling(key),seconds)-Math.max(0,Number(response.headers.get('age')||0))*1000);
}
export function peekResearch(key:string){const entry=completed.get(key);if(entry){completed.delete(key);completed.set(key,entry)}return entry}
function save(key:string,entry:Stored){
  if(!entry.ttl){completed.delete(key);return}
  completed.delete(key);completed.set(key,entry);
  while(completed.size>LIMIT)completed.delete(completed.keys().next().value!);
}
export function acquireResearch(key:string,force=false){
  const cached=peekResearch(key);
  if(!force&&cached&&cached.expires>Date.now())return {promise:Promise.resolve(cached),release:()=>{}};
  let task=pending.get(key);
  if(!task){
    if(pending.size>=LIMIT)throw new Error('閱讀請求較多，請稍後重試。');
    const controller=new AbortController();
    task={controller,users:0,promise:null as unknown as Promise<Stored>};
    const current=task;
    task.promise=(async()=>{
      const response=await fetch(key,{cache:'no-store',credentials:'omit',signal:controller.signal,headers:cached?.etag?{'If-None-Match':cached.etag}:{}});
      let payload:Payload;
      if(response.status===304){
        if(!cached?.etag||response.headers.get('etag')!==cached.etag)throw new Error('目前無法確認資料，請重新讀取。');
        payload=cached.payload;
      }else{
        const body=await response.json();
        if(!response.ok)throw new Error(typeof body.message==='string'?body.message:'研究目前無法讀取，請稍後重試。');
        const release=new URL(key,'http://reader.invalid').searchParams.get('release_id');
        if(!body||typeof body.release_id!=='string'||typeof body.schema_version!=='string'||!body.data||release&&body.release_id.toLowerCase()!==release.toLowerCase())throw new Error('研究版本不一致，請重新開啟這份研究。');
        payload=body;
      }
      if(controller.signal.aborted)throw new DOMException('Aborted','AbortError');
      const duration=ttl(key,response,cached),entry={payload,etag:response.headers.get('etag'),expires:Date.now()+duration,ttl:duration};
      save(key,entry);return entry;
    })().finally(()=>{if(pending.get(key)===current)pending.delete(key)});
    pending.set(key,task);
  }
  const current=task;current.users++;
  let released=false;
  return {promise:current.promise,release:()=>{
    if(released)return;released=true;current.users--;
    // A StrictMode remount or another reader of the same key can retain the request.
    queueMicrotask(()=>{if(current.users===0&&pending.get(key)===current){pending.delete(key);current.controller.abort()}});
  }};
}

export function refreshResearch(){window.dispatchEvent(new Event('research:refresh'))}
export function resetDynamicResearch(){
  for(const key of completed.keys())if(dynamicResearch(key))completed.delete(key);
  for(const [key,task] of pending)if(dynamicResearch(key)){pending.delete(key);task.controller.abort()}
}
