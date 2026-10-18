'use client';
import {createContext,useCallback,useContext,useEffect,useRef,useState,ReactNode} from 'react';

export const RESEARCH_WATCHLIST_KEY='industryflow.research-watchlist.v2';
export const LEGACY_WATCHLIST_KEY='industryflow.theme-watchlist.v1';
export const WATCH_LIMIT=100;
export const IMPORT_LIMIT_BYTES=1024*1024;
export const EXPORT_FORMAT='industryflow-research-watchlist';
export const watchKinds=['company','product','theme','research'] as const;
export type WatchKind=typeof watchKinds[number];
// null means no baseline yet: shown as 待確認, never as read.
export type WatchSeen={research:string|null;values:string|null;events:number|null};
export type WatchTarget={kind:WatchKind;id:string;name:string;seen:WatchSeen};
export type UpdateItem={kind:WatchKind;id:string;available:boolean;reason?:string;name?:string;
  research?:{token:string;changed:boolean|null};values?:{applicable:boolean;token:string|null;changed:boolean|null};
  events?:{marker:number;changed:boolean|null;new_dated:number;new_undated:number}};
export type UpdatesResult={release_id:string;data:{as_of:string;release_id:string;items:UpdateItem[];note:string}};
// v1_migrated: the one-time theme-watchlist import already ran; v1 is never read again.
type Saved={schema_version:2;targets:WatchTarget[];v1_migrated?:boolean};
type Context={targets:WatchTarget[];ready:boolean;notice:string;
  has:(kind:string,id:string)=>boolean;add:(target:{kind:WatchKind;id:string;name:string},item?:UpdateItem)=>boolean;
  remove:(kind:string,id:string)=>void;mark:(item:UpdateItem)=>void;merge:(targets:WatchTarget[])=>boolean};

const ID=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const empty:Saved={schema_version:2,targets:[]};
const PENDING:WatchSeen={research:null,values:null,events:null};
const Watchlist=createContext<Context|null>(null);
export const isWatchKind=(value:string):value is WatchKind=>(watchKinds as readonly string[]).includes(value);
export const targetKey=(kind:string,id:string)=>kind+':'+id;

export function seenFrom(item:UpdateItem):WatchSeen{
  if(!item.available||!item.research||!item.events)return {...PENDING};
  return {research:item.research.token,values:item.values?.token??null,events:item.events.marker};
}

function validSeen(value:unknown):value is WatchSeen{
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  const seen=value as Record<string,unknown>;
  const token=(v:unknown)=>v===null||typeof v==='string'&&v.length<=128;
  return Object.keys(seen).every(k=>['research','values','events'].includes(k))&&token(seen.research)&&token(seen.values)&&
    (seen.events===null||Number.isSafeInteger(seen.events)&&(seen.events as number)>=0);
}

export function validTarget(raw:unknown):WatchTarget|null{
  if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
  const target=raw as Record<string,unknown>;
  if(typeof target.kind!=='string'||!isWatchKind(target.kind)||typeof target.id!=='string'||!ID.test(target.id)||target.id.length>200||
    typeof target.name!=='string'||!target.name.trim()||target.name.length>200||!validSeen(target.seen))return null;
  return {kind:target.kind,id:target.id,name:target.name,seen:{...(target.seen as WatchSeen)}};
}

export function decodeWatchlist(value:string|null):{saved:Saved;damaged:boolean}{
  if(value===null)return {saved:empty,damaged:false};
  const parsed=JSON.parse(value);
  if(!parsed||parsed.schema_version!==2||!Array.isArray(parsed.targets))throw new Error('收藏格式損壞');
  const targets:WatchTarget[]=[];const seen=new Set<string>();let damaged=false;
  for(const raw of parsed.targets){
    const target=validTarget(raw);
    if(!target||seen.has(targetKey(target.kind,target.id))){damaged=true;continue}
    seen.add(targetKey(target.kind,target.id));targets.push(target);
  }
  if(targets.length>WATCH_LIMIT)damaged=true;
  return {saved:{schema_version:2,targets:targets.slice(0,WATCH_LIMIT),v1_migrated:parsed.v1_migrated===true},damaged};
}

/** v1 theme favourites → v2 theme targets. Only the indicator token is the same measure in both versions. */
export function migrateLegacy(value:string|null):{targets:WatchTarget[];damaged:boolean}{
  if(value===null)return {targets:[],damaged:false};
  let parsed:unknown;
  try{parsed=JSON.parse(value)}catch{return {targets:[],damaged:true}}
  const legacy=parsed as {theme_ids?:unknown;seen?:unknown};
  if(!legacy||typeof legacy!=='object'||!Array.isArray(legacy.theme_ids))return {targets:[],damaged:true};
  const marks=legacy.seen&&typeof legacy.seen==='object'?legacy.seen as Record<string,unknown>:{};
  const targets:WatchTarget[]=[];const known=new Set<string>();let damaged=!(legacy.seen&&typeof legacy.seen==='object');
  for(const id of legacy.theme_ids){
    if(typeof id!=='string'||!ID.test(id)||id.length>190||known.has(id)){damaged=true;continue}
    known.add(id);
    const mark=marks[id] as {indicator_token?:unknown}|undefined;
    const indicator=mark&&typeof mark.indicator_token==='string'&&mark.indicator_token&&mark.indicator_token.length<=128?mark.indicator_token:null;
    if(mark===undefined||indicator===null)damaged=damaged||mark!==undefined&&typeof mark?.indicator_token!=='string';
    // Research and events have no v1 equivalent, so they stay pending instead of being marked read.
    targets.push({kind:'theme',id:'theme-'+id,name:'題材 '+id,seen:{research:null,values:indicator,events:null}});
  }
  return {targets:targets.slice(0,WATCH_LIMIT),damaged};
}

function mergeTargets(current:WatchTarget[],incoming:WatchTarget[]){
  const existing=new Set(current.map(t=>targetKey(t.kind,t.id)));
  return [...current,...incoming.filter(t=>!existing.has(targetKey(t.kind,t.id)))];
}

export function ResearchWatchlistProvider({children}:{children:ReactNode}){
  const [saved,setSaved]=useState<Saved>(empty),[ready,setReady]=useState(false),[notice,setNotice]=useState('');
  const persistent=useRef(true);
  useEffect(()=>{
    const notices:string[]=[];let current:Saved=empty;
    try{const result=decodeWatchlist(localStorage.getItem(RESEARCH_WATCHLIST_KEY));current=result.saved;
      if(result.damaged){persistent.current=false;notices.push('部分收藏內容損壞；有效收藏已保留，目前使用本次記憶體暫存，重新整理可能不保留。')}}
    catch{persistent.current=false;notices.push('此瀏覽器無法讀取收藏，目前使用本次記憶體暫存；重新整理可能不保留。')}
    if(!current.v1_migrated&&persistent.current){
      let legacy:string|null=null;
      try{legacy=localStorage.getItem(LEGACY_WATCHLIST_KEY)}catch{legacy=null}
      const migrated=migrateLegacy(legacy);
      const merged=mergeTargets(current.targets,migrated.targets).slice(0,WATCH_LIMIT);
      const added=merged.length-current.targets.length;
      current={schema_version:2,targets:merged,v1_migrated:true};
      if(added)notices.push(`已從舊版題材關注匯入 ${added} 項；研究與事件的已讀基準需重新確認，舊清單仍保留作備份。`);
      if(migrated.damaged)notices.push('舊版題材關注有部分內容無法讀取，已略過；舊清單仍保留。');
    }
    setSaved(current);setNotice(notices.join(' '));setReady(true);
  },[]);
  useEffect(()=>{
    if(!ready||!persistent.current)return;
    const encoded=JSON.stringify(saved);
    try{
      localStorage.setItem(RESEARCH_WATCHLIST_KEY,encoded);
      // A migration only counts as done once the new format reads back intact; v1 is never deleted.
      if(localStorage.getItem(RESEARCH_WATCHLIST_KEY)!==encoded)throw new Error('verify');
    }catch{persistent.current=false;setNotice('無法保存收藏，目前使用本次記憶體暫存；重新整理可能不保留，可先匯出備份。')}
  },[saved,ready]);
  const has=useCallback((kind:string,id:string)=>saved.targets.some(t=>t.kind===kind&&t.id===id),[saved]);
  function add(target:{kind:WatchKind;id:string;name:string},item?:UpdateItem){
    if(has(target.kind,target.id))return true;
    if(saved.targets.length>=WATCH_LIMIT){setNotice(`此瀏覽器最多收藏 ${WATCH_LIMIT} 項，請先移除不再追蹤的研究。`);return false}
    const seen=item&&item.kind===target.kind&&item.id===target.id?seenFrom(item):{...PENDING};
    setSaved(old=>old.targets.some(t=>t.kind===target.kind&&t.id===target.id)?old:{...old,targets:[...old.targets,{...target,seen}]});
    return true;
  }
  const remove=(kind:string,id:string)=>setSaved(old=>({...old,targets:old.targets.filter(t=>!(t.kind===kind&&t.id===id))}));
  // Records only the response that is on screen; a newer server state stays unread.
  const mark=(item:UpdateItem)=>{if(item.available)setSaved(old=>({...old,targets:old.targets.map(t=>t.kind===item.kind&&t.id===item.id?{...t,name:item.name||t.name,seen:seenFrom(item)}:t)}))};
  // Existing targets keep their local baseline; an older backup never rolls it back.
  function merge(targets:WatchTarget[]){
    const merged=mergeTargets(saved.targets,targets);
    if(merged.length>WATCH_LIMIT)return false;
    setSaved(old=>({...old,targets:mergeTargets(old.targets,targets)}));return true;
  }
  return <Watchlist.Provider value={{targets:saved.targets,ready,notice,has,add,remove,mark,merge}}>{children}</Watchlist.Provider>;
}

export function useResearchWatchlist(){const context=useContext(Watchlist);if(!context)throw new Error('Missing ResearchWatchlistProvider');return context}

export async function queryUpdates(targets:{kind:WatchKind;id:string;seen?:WatchSeen}[],release?:string):Promise<UpdatesResult>{
  const response=await fetch('/api/v2/updates/query',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({...(release?{release_id:release}:{}),items:targets.map(({kind,id,seen})=>({kind,id,...(seen?{seen}:{})}))})});
  const body=await response.json().catch(()=>null);
  if(!response.ok||!body?.data)throw new Error(body?.message||'目前無法檢查收藏更新，請稍後重試。');
  return body as UpdatesResult;
}

/** Backup holds identities, names and baselines only: no research text, no credentials. */
export function exportWatchlist(targets:WatchTarget[]){
  return JSON.stringify({format:EXPORT_FORMAT,schema_version:2,exported_at:new Date().toISOString(),targets},null,2);
}

export type ImportPreview={fresh:WatchTarget[];duplicates:WatchTarget[];invalid:{index:number;label:string}[];total:number};

/** Whole-file problems reject the import; individual bad entries are listed and skipped. */
export function parseImport(text:string,current:WatchTarget[]):{preview?:ImportPreview;error?:string}{
  if(new Blob([text]).size>IMPORT_LIMIT_BYTES)return {error:'備份超過 1 MiB，未匯入；原清單保留。'};
  let unsafe=false;let parsed:unknown;
  try{parsed=JSON.parse(text,(key,value)=>{if(key==='__proto__'||key==='constructor'||key==='prototype')unsafe=true;return value})}
  catch{return {error:'檔案不是有效的 JSON 收藏備份，未匯入；原清單保留。'}}
  if(unsafe)return {error:'備份含不安全的欄位名稱，整份拒絕匯入；原清單保留。'};
  const backup=parsed as {format?:unknown;schema_version?:unknown;targets?:unknown};
  if(!backup||typeof backup!=='object'||Array.isArray(backup)||backup.format!==EXPORT_FORMAT||backup.schema_version!==2||!Array.isArray(backup.targets))
    return {error:'這不是 IndustryFlow 收藏備份（格式版本 2），未匯入；原清單保留。'};
  if(backup.targets.length>WATCH_LIMIT)return {error:`備份含 ${backup.targets.length} 項，超過 ${WATCH_LIMIT} 項上限，未匯入；原清單保留。`};
  const existing=new Set(current.map(t=>targetKey(t.kind,t.id)));const seen=new Set<string>();
  const preview:ImportPreview={fresh:[],duplicates:[],invalid:[],total:backup.targets.length};
  backup.targets.forEach((raw,index)=>{
    const target=validTarget(raw);
    if(!target){preview.invalid.push({index,label:typeof (raw as {name?:unknown})?.name==='string'?String((raw as {name:string}).name).slice(0,80):`第 ${index+1} 項`});return}
    const id=targetKey(target.kind,target.id);
    if(existing.has(id)||seen.has(id)){preview.duplicates.push(target);return}
    seen.add(id);preview.fresh.push(target);
  });
  if(current.length+preview.fresh.length>WATCH_LIMIT)return {error:`合併後會有 ${current.length+preview.fresh.length} 項，超過 ${WATCH_LIMIT} 項上限，未匯入；請先移除部分收藏。`};
  return {preview};
}
