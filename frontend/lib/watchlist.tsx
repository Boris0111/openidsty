'use client';
import {createContext,useContext,useEffect,useState,ReactNode} from 'react';
import type {ThemeUpdate} from './types';
export const WATCHLIST_KEY='industryflow.theme-watchlist.v1';
export type Seen={version_id:number|null;indicator_token:string;candidate_token:string};
type Saved={theme_ids:string[];seen:Record<string,Seen>};
type Context={saved:Saved;ready:boolean;notice:string;follow:(item:ThemeUpdate)=>void;remove:(id:string)=>void;mark:(item:ThemeUpdate)=>void};
const empty:Saved={theme_ids:[],seen:{}};
const WatchlistContext=createContext<Context|null>(null);
export function snapshot(item:ThemeUpdate):Seen{return {version_id:item.current_version_id??null,indicator_token:item.indicator_token||'',candidate_token:item.candidate_token||''}}
function decode(value:string|null):{saved:Saved;warning:boolean}{
  if(value===null)return {saved:empty,warning:false};
  const parsed=JSON.parse(value);
  if(!parsed||!Array.isArray(parsed.theme_ids)||!parsed.seen||typeof parsed.seen!=='object')throw new Error('清單格式損壞');
  const ids=[...new Set(parsed.theme_ids.filter((v:unknown)=>typeof v==='string'&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(v)))] as string[];
  const saved:Saved={theme_ids:ids.slice(0,20),seen:{}};let warning=ids.length!==parsed.theme_ids.length||ids.length>20;
  for(const id of saved.theme_ids){const s=parsed.seen[id];if(s&&(s.version_id===null||Number.isSafeInteger(s.version_id)&&s.version_id>0)&&typeof s.indicator_token==='string'&&typeof s.candidate_token==='string')saved.seen[id]=s;else warning=true}
  return {saved,warning};
}
export function WatchlistProvider({children}:{children:ReactNode}){
  const [saved,setSaved]=useState<Saved>(empty),[ready,setReady]=useState(false),[persistent,setPersistent]=useState(true),[notice,setNotice]=useState('');
  useEffect(()=>{try{const result=decode(localStorage.getItem(WATCHLIST_KEY));setSaved(result.saved);if(result.warning){setNotice('部分儲存內容損壞；有效題材已保留，目前使用本次記憶體暫存。');setPersistent(false)}}catch{setNotice('此裝置儲存不可用或已損壞，目前使用本次記憶體暫存；重新整理可能不保留。');setPersistent(false)}setReady(true)},[]);
  useEffect(()=>{if(!ready||!persistent)return;try{localStorage.setItem(WATCHLIST_KEY,JSON.stringify(saved))}catch{setPersistent(false);setNotice('無法保存此裝置清單，目前使用本次記憶體暫存；重新整理可能不保留。')}},[saved,ready,persistent]);
  const remove=(id:string)=>setSaved(old=>{const seen={...old.seen};delete seen[id];return {theme_ids:old.theme_ids.filter(t=>t!==id),seen}});
  const follow=(item:ThemeUpdate)=>{if(!item.available)return;if(saved.theme_ids.length>=20&&!saved.theme_ids.includes(item.theme_id)){setNotice('此裝置最多關注 20 個題材。');return}setSaved(old=>old.theme_ids.includes(item.theme_id)?old:{theme_ids:[...old.theme_ids,item.theme_id],seen:{...old.seen,[item.theme_id]:snapshot(item)}})};
  const mark=(item:ThemeUpdate)=>{if(item.available)setSaved(old=>old.theme_ids.includes(item.theme_id)?{...old,seen:{...old.seen,[item.theme_id]:snapshot(item)}}:old)};
  return <WatchlistContext.Provider value={{saved,ready,notice,follow,remove,mark}}>{children}</WatchlistContext.Provider>;
}
export function useWatchlist(){const context=useContext(WatchlistContext);if(!context)throw new Error('Missing WatchlistProvider');return context}
