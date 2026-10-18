'use client';
import {createContext,useCallback,useContext,useEffect,useRef,useState,ReactNode} from 'react';

export const RESEARCH_WATCHLIST_KEY='industryflow.research-watchlist.v2';
export const WATCH_LIMIT=100;
export const watchKinds=['company','product','theme','research'] as const;
export type WatchKind=typeof watchKinds[number];
// null means no baseline yet: shown as 待確認, never as read.
export type WatchSeen={research:string|null;values:string|null;events:number|null};
export type WatchTarget={kind:WatchKind;id:string;name:string;seen:WatchSeen};
export type UpdateItem={kind:WatchKind;id:string;available:boolean;reason?:string;name?:string;
  research?:{token:string;changed:boolean|null};values?:{applicable:boolean;token:string|null;changed:boolean|null};
  events?:{marker:number;changed:boolean|null;new_dated:number;new_undated:number}};
export type UpdatesResult={release_id:string;data:{as_of:string;release_id:string;items:UpdateItem[];note:string}};
type Saved={schema_version:2;targets:WatchTarget[]};
type Context={targets:WatchTarget[];ready:boolean;notice:string;
  has:(kind:string,id:string)=>boolean;add:(target:{kind:WatchKind;id:string;name:string},item?:UpdateItem)=>boolean;
  remove:(kind:string,id:string)=>void;mark:(item:UpdateItem)=>void};

const ID=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const empty:Saved={schema_version:2,targets:[]};
const Watchlist=createContext<Context|null>(null);
export const isWatchKind=(value:string):value is WatchKind=>(watchKinds as readonly string[]).includes(value);
const key=(kind:string,id:string)=>kind+':'+id;

export function seenFrom(item:UpdateItem):WatchSeen{
  if(!item.available||!item.research||!item.events)return {research:null,values:null,events:null};
  return {research:item.research.token,values:item.values?.token??null,events:item.events.marker};
}

function validSeen(value:unknown):value is WatchSeen{
  if(!value||typeof value!=='object')return false;
  const seen=value as Record<string,unknown>;
  const token=(v:unknown)=>v===null||typeof v==='string'&&v.length<=128;
  return token(seen.research)&&token(seen.values)&&(seen.events===null||Number.isSafeInteger(seen.events)&&(seen.events as number)>=0);
}

export function decodeWatchlist(value:string|null):{saved:Saved;damaged:boolean}{
  if(value===null)return {saved:empty,damaged:false};
  const parsed=JSON.parse(value);
  if(!parsed||parsed.schema_version!==2||!Array.isArray(parsed.targets))throw new Error('收藏格式損壞');
  const targets:WatchTarget[]=[];const seen=new Set<string>();let damaged=false;
  for(const raw of parsed.targets){
    const target=raw as Partial<WatchTarget>;
    if(!target||typeof target.kind!=='string'||!isWatchKind(target.kind)||typeof target.id!=='string'||!ID.test(target.id)||target.id.length>200||
      typeof target.name!=='string'||!validSeen(target.seen)||seen.has(key(target.kind,target.id))){damaged=true;continue}
    seen.add(key(target.kind,target.id));targets.push({kind:target.kind,id:target.id,name:target.name.slice(0,200),seen:target.seen});
  }
  if(targets.length>WATCH_LIMIT)damaged=true;
  return {saved:{schema_version:2,targets:targets.slice(0,WATCH_LIMIT)},damaged};
}

export function ResearchWatchlistProvider({children}:{children:ReactNode}){
  const [saved,setSaved]=useState<Saved>(empty),[ready,setReady]=useState(false),[notice,setNotice]=useState('');
  const persistent=useRef(true);
  useEffect(()=>{
    try{const result=decodeWatchlist(localStorage.getItem(RESEARCH_WATCHLIST_KEY));setSaved(result.saved);
      if(result.damaged){persistent.current=false;setNotice('部分收藏內容損壞；有效收藏已保留，目前使用本次記憶體暫存，重新整理可能不保留。')}}
    catch{persistent.current=false;setNotice('此瀏覽器無法讀取收藏，目前使用本次記憶體暫存；重新整理可能不保留。')}
    setReady(true);
  },[]);
  useEffect(()=>{
    if(!ready||!persistent.current)return;
    try{localStorage.setItem(RESEARCH_WATCHLIST_KEY,JSON.stringify(saved))}
    catch{persistent.current=false;setNotice('無法保存收藏，目前使用本次記憶體暫存；重新整理可能不保留。')}
  },[saved,ready]);
  const has=useCallback((kind:string,id:string)=>saved.targets.some(t=>t.kind===kind&&t.id===id),[saved]);
  function add(target:{kind:WatchKind;id:string;name:string},item?:UpdateItem){
    if(has(target.kind,target.id))return true;
    if(saved.targets.length>=WATCH_LIMIT){setNotice(`此瀏覽器最多收藏 ${WATCH_LIMIT} 項，請先移除不再追蹤的研究。`);return false}
    const seen=item&&item.kind===target.kind&&item.id===target.id?seenFrom(item):{research:null,values:null,events:null};
    setSaved(old=>old.targets.some(t=>t.kind===target.kind&&t.id===target.id)?old:{...old,targets:[...old.targets,{...target,seen}]});
    return true;
  }
  const remove=(kind:string,id:string)=>setSaved(old=>({...old,targets:old.targets.filter(t=>!(t.kind===kind&&t.id===id))}));
  // Records only the response that is on screen; a newer server state stays unread.
  const mark=(item:UpdateItem)=>{if(item.available)setSaved(old=>({...old,targets:old.targets.map(t=>t.kind===item.kind&&t.id===item.id?{...t,name:item.name||t.name,seen:seenFrom(item)}:t)}))};
  return <Watchlist.Provider value={{targets:saved.targets,ready,notice,has,add,remove,mark}}>{children}</Watchlist.Provider>;
}

export function useResearchWatchlist(){const context=useContext(Watchlist);if(!context)throw new Error('Missing ResearchWatchlistProvider');return context}

export async function queryUpdates(targets:{kind:WatchKind;id:string;seen?:WatchSeen}[],release?:string):Promise<UpdatesResult>{
  const response=await fetch('/api/v2/updates/query',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({...(release?{release_id:release}:{}),items:targets.map(({kind,id,seen})=>({kind,id,...(seen?{seen}:{})}))})});
  const body=await response.json().catch(()=>null);
  if(!response.ok||!body?.data)throw new Error(body?.message||'目前無法檢查收藏更新，請稍後重試。');
  return body as UpdatesResult;
}
