import {readerFetch} from './reader-fetch';
export type Snapshot={data:unknown;error:string;loading:boolean};
type Entry={state:Snapshot;listeners:Set<()=>void>;controller?:AbortController;expires:number;used:number;generation:number};
const registry=new Map<string,Entry>();
const empty:Snapshot={data:null,error:'',loading:true};
function requestKey(path:string){const url=new URL(path,'http://local');url.searchParams.sort();return url.pathname+url.search;}
function ttl(key:string){
  if(/\/assessment(?:\?|$|\/compare)|\/indicators|\/sources|\/theme-updates|\/technical-documents\/[^/?]+(?:\?|$)/.test(key))return 0;
  if(/^\/api\/(coverage|technical-documents)(?:\?|$)/.test(key))return 30000;
  return 60000;
}
function trim(){const unused=[...registry.entries()].filter(([,e])=>!e.listeners.size&&!e.controller).sort((a,b)=>a[1].used-b[1].used);while(unused.length>100){const [key]=unused.shift()!;registry.delete(key);}}
function begin(key:string,e:Entry){
  e.controller?.abort();const controller=new AbortController();e.controller=controller;const generation=++e.generation;
  e.state={...empty};e.listeners.forEach(fn=>fn());
  readerFetch(key,{cache:'no-store',signal:controller.signal}).then(async response=>{const body=await response.json();if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:'資料暫時無法取得');return body;}).then(data=>{
    if(e.generation!==generation||controller.signal.aborted)return;e.state={data,error:'',loading:false};e.expires=Date.now()+ttl(key);
  }).catch(error=>{if(e.generation===generation&&!controller.signal.aborted){e.state={data:null,error:error.message,loading:false};e.expires=0;}}).finally(()=>{
    if(e.generation!==generation)return;e.controller=undefined;e.used=Date.now();e.listeners.forEach(fn=>fn());trim();
  });
}
export function subscribeRequest(path:string,listener:(state:Snapshot)=>void){
  const key=requestKey(path);let e=registry.get(key);if(!e){e={state:empty,listeners:new Set(),expires:0,used:Date.now(),generation:0};registry.set(key,e);}
  const entry=e;const update=()=>listener(entry.state);entry.listeners.add(update);entry.used=Date.now();
  if(!entry.controller&&entry.expires<=Date.now())begin(key,entry);update();
  return {unsubscribe:()=>{entry.listeners.delete(update);if(!entry.listeners.size&&entry.controller){entry.controller.abort();entry.controller=undefined;entry.generation++;entry.expires=0;}trim();},retry:()=>{if(!entry.controller)begin(key,entry);}};
}
export {requestKey,empty};
