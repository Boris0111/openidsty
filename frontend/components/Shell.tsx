'use client';
import {useEffect,useState,ReactNode,useRef,Suspense} from 'react';
import Link from 'next/link';
import {usePathname,useSearchParams} from 'next/navigation';
import {useResearch,ResearchPage} from '@/lib/research-api';

const kindNames:Record<string,string>={segment:'環節',theme:'題材',application:'供應鏈',role:'供應角色',product:'產品',company:'公司',concept:'術語',research:'研究'};
// One reading shell for the industry map, themes, events and /next research.
export const readerSections=[['map','/','產業地圖'],['chains','/next?view=applications','供應鏈'],['companies','/next?view=companies','公司'],
  ['themes','/themes','題材'],['compare','/next?view=compare','公司比較'],['events','/events','事件'],['watchlist','/next?view=watchlist','收藏']] as const;

export function readerSection(pathname:string,params:URLSearchParams){
  if(pathname==='/')return 'map';
  if(pathname.startsWith('/themes'))return 'themes';
  if(pathname.startsWith('/events'))return 'events';
  if(!pathname.startsWith('/next'))return null;
  const view=params.get('view'),focus=params.get('focus')||'';
  if(view==='companies'||(!view&&focus.startsWith('company-')))return 'companies';
  if(view==='themes'||(!view&&focus.startsWith('theme-')))return 'themes';
  if(view==='compare')return 'compare';
  if(view==='observations')return 'events';
  if(view==='watchlist')return 'watchlist';
  return 'chains';
}

/** Themes keep their judgment, indicator and version reading on the theme page; everything else opens in /next. */
export function searchHref(id:string,release:string|null){
  if(id.startsWith('theme-'))return '/themes/'+encodeURIComponent(id.slice(6));
  return '/next?'+new URLSearchParams({focus:id,...(release?{release_id:release}:{})});
}

function Search() {
  const pathname=usePathname(),params=useSearchParams();
  const release=pathname.startsWith('/next')?params.get('release_id'):null;
  const [query,setQuery]=useState(''),[debounced,setDebounced]=useState('');
  const wrapper=useRef<HTMLDivElement>(null);
  useEffect(()=>{const timer=setTimeout(()=>setDebounced(query),200);return ()=>clearTimeout(timer)},[query]);
  // Clear only when the reader moves to another page; pinning release_id into the URL must not wipe typed text.
  const page=pathname+'|'+params.get('focus')+'|'+params.get('view');
  useEffect(()=>setQuery(''),[page]);
  const result=useResearch<ResearchPage>(debounced.trim()?'/api/v2/search?'+new URLSearchParams({q:debounced,...(release?{release_id:release}:{})}):null);
  const items=query===debounced?result.data?.data.items:undefined;
  return <div className="search" ref={wrapper}><label className="sr-only" htmlFor="research-search">搜尋公司、產品、環節或題材</label><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="research-search" placeholder="搜尋公司、產品、環節或題材" value={query} onChange={e=>setQuery(e.target.value)} aria-controls={query?'search-results':undefined} aria-expanded={Boolean(query)} onKeyDown={e=>{if(e.key==='Escape')setQuery('');if(e.key==='ArrowDown'&&items?.length){e.preventDefault();(wrapper.current?.querySelector('.search-results a') as HTMLElement)?.focus()}if(e.key==='Enter'&&items?.length){e.preventDefault();(wrapper.current?.querySelector('.search-results a') as HTMLElement)?.click()}}} autoComplete="off"/>{query&&<div id="search-results" className="search-results" aria-label="搜尋結果">{result.error?<p role="alert">搜尋暫時無法取得，請稍後再試。</p>:!items?<p role="status">搜尋中…</p>:items.map((item,i)=><Link key={item.id} href={searchHref(item.id,release)} onClick={()=>setQuery('')} onKeyDown={e=>{const links=wrapper.current?.querySelectorAll<HTMLAnchorElement>('.search-results a');if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();links?.[(i+(e.key==='ArrowDown'?1:-1)+(links?.length||0))%(links?.length||1)]?.focus()}if(e.key==='Escape'){setQuery('');wrapper.current?.querySelector('input')?.focus()}}}><strong>{item.name}</strong><span>{kindNames[item.kind]}　{item.summary}</span></Link>)}{items?.length===0&&<p>找不到結果，請試公司代號、產品或環節名稱。</p>}</div>}</div>
}

function Navigation() {
  const pathname=usePathname(),params=useSearchParams();
  const current=readerSection(pathname,params);
  return <nav aria-label="主要導覽">{readerSections.map(([key,url,label])=><Link key={key} href={url} aria-current={current===key?'page':undefined}>{label}</Link>)}</nav>
}

export function Shell({children}:{children:ReactNode}) {
  return <><header className="site-header"><Link href="/" className="brand" aria-label="IndustryFlow 產業地圖首頁"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 8h12v16h8M6 8v16h12M18 8h8"/><circle cx="6" cy="8" r="3"/><circle cx="6" cy="24" r="3"/><circle cx="18" cy="16" r="3"/><circle cx="26" cy="8" r="3"/><circle cx="26" cy="24" r="3"/></svg><span>IndustryFlow<small>半導體與 AI 產業研究</small></span></Link><Suspense fallback={<nav aria-label="主要導覽"/>}><Navigation/><Search/></Suspense></header><main id="main">{children}</main><footer className="site-footer"><span>從產業結構，理解每一則資訊。</span><span>研究保留查核基準，事件持續自動更新。媒體摘錄與官方統計可回溯原始來源。</span><span>結構推導標為有條件推論；來源涵蓋與實際資料覆蓋分開呈現。</span></footer></>
}
