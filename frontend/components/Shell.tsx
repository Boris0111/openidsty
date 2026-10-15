'use client';
import {useEffect,useState,ReactNode,useRef} from 'react';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {useApi} from '@/lib/api';

function Search() {
  const [query,setQuery]=useState(''),[debounced,setDebounced]=useState('');
  const wrapper=useRef<HTMLDivElement>(null);
  useEffect(()=>{const timer=setTimeout(()=>setDebounced(query),180);return ()=>clearTimeout(timer)},[query]);
  const {data,error,loading}=useApi<{kind:string;id:string;name:string;url:string}[]>(`/api/search?q=${encodeURIComponent(debounced)}`);
  const pathname=usePathname();
  useEffect(()=>setQuery(''),[pathname]);
  const results=query===debounced?data:null;
  return <div className="search" ref={wrapper}><label className="sr-only" htmlFor="research-search">搜尋環節、題材或公司</label><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="research-search" placeholder="搜尋環節、題材、公司" value={query} onChange={e=>setQuery(e.target.value)} aria-controls={query?'search-results':undefined} aria-expanded={Boolean(query)} onKeyDown={e=>{if(e.key==='Escape')setQuery('');if(e.key==='ArrowDown'&&results?.length){e.preventDefault();(wrapper.current?.querySelector('.search-results a') as HTMLElement)?.focus()}if(e.key==='Enter'&&results?.length){e.preventDefault();(wrapper.current?.querySelector('.search-results a') as HTMLElement)?.click()}}} autoComplete="off"/>{query&&<div id="search-results" className="search-results" aria-label="搜尋結果">{error?<p role="alert">{error}</p>:loading||!results?<p role="status">搜尋中…</p>:results.map((r,i)=><Link key={`${r.kind}-${r.id}`} href={r.url} onClick={()=>setQuery('')} onKeyDown={e=>{const links=wrapper.current?.querySelectorAll<HTMLAnchorElement>('.search-results a');if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();links?.[(i+(e.key==='ArrowDown'?1:-1)+(links?.length||0))%(links?.length||1)]?.focus()}if(e.key==='Escape'){setQuery('');wrapper.current?.querySelector('input')?.focus()}}}><strong>{r.name}</strong><span>{({segment:'環節',theme:'題材',company:'公司'} as Record<string,string>)[r.kind]}　{r.id}</span></Link>)}{results?.length===0&&<p>找不到結果，請嘗試名稱或識別碼。</p>}</div>}</div>
}

export function Shell({children}:{children:ReactNode}) {
  const pathname=usePathname();
  return <><header className="site-header"><Link href="/" className="brand" aria-label="IndustryFlow 產業地圖首頁"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 8h12v16h8M6 8v16h12M18 8h8"/><circle cx="6" cy="8" r="3"/><circle cx="6" cy="24" r="3"/><circle cx="18" cy="16" r="3"/><circle cx="26" cy="8" r="3"/><circle cx="26" cy="24" r="3"/></svg><span>IndustryFlow<small>半導體與 AI 產業研究</small></span></Link><nav aria-label="主要導覽">{[['/','產業探索'],['/themes','題材研究'],['/events','近期事件'],['/coverage','資料覆蓋'],['/sources','來源狀態'],['/watchlist','此裝置關注']].map(([url,label])=><Link key={url} href={url} aria-current={(url==='/'?pathname==='/':pathname.startsWith(url))?'page':undefined}>{label}</Link>)}</nav><Search/></header><main id="main">{children}</main><footer className="site-footer"><span>從產業結構，理解每一則資訊。</span><span>研究保留查核基準，事件持續自動更新。媒體摘錄與官方統計可回溯原始來源。</span><span>結構推導標為 inference；來源涵蓋與實際資料覆蓋分開呈現。</span></footer></>
}
