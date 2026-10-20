'use client';
import {Suspense} from 'react';
import {useRouter,useSearchParams} from 'next/navigation';
import {useApi} from '@/lib/api';
import type {InfoEvent,Industry,Theme} from '@/lib/types';
import {EventList} from '@/components/Events';
import {Status} from '@/components/Status';
import {EventTabs} from '@/components/EventTabs';
function EventsPage(){
  const params=useSearchParams(),router=useRouter();
  const page=Number(params.get('page')||0),ticker=params.get('ticker'),kind=params.get('kind')||'',industry=params.get('industry')||'';
  const query=new URLSearchParams(params);query.delete('page');query.set('limit','30');query.set('offset',String(page*30));
  const api=useApi<InfoEvent[]>(`/api/events?${query}`);
  const industries=useApi<Industry[]>('/api/industries'),themes=useApi<Theme[]>('/api/themes');
  const graph=useApi<{id:string;name:string;layer:string}[]>(`/api/segments${industry?'?industry='+industry:''}`);
  function set(key:string,value:string){const next=new URLSearchParams(params);value?next.set(key,value):next.delete(key);next.delete('page');if(key==='industry')next.delete('segment');router.push(`/events?${next}`,{scroll:false})}
  function paginate(value:number){const next=new URLSearchParams(params);next.set('page',String(value));router.push(`/events?${next}`,{scroll:false})}
  return <div className="page-content"><div className="page-heading"><h1>{ticker?`${ticker} 相關資訊`:'近期產業事件'}</h1><p>產業變化優先，例行財報可另行開啟。直接分類、背景統計與活動預告分開標示。</p></div>{!ticker&&<EventTabs current="official"/>}<div className="event-toolbar"><label>資訊類型<select aria-label="資訊類型" value={kind} onChange={e=>set('kind',e.target.value)}><option value="">全部類型</option><option value="industry_news">產業消息</option><option value="official_stats">背景統計</option><option value="announcement">重大訊息</option><option value="financials">財報／營收</option><option value="filing">官方申報</option><option value="earnings_call">法說資料</option></select></label><label>產業<select aria-label="事件產業" value={industry} onChange={e=>set('industry',e.target.value)}><option value="">全部產業</option>{industries.data?.map(i=><option key={i.id} value={i.id}>{i.name}</option>)}</select></label><label>環節<select aria-label="事件環節" value={params.get('segment')||''} onChange={e=>set('segment',e.target.value)}><option value="">全部環節</option>{graph.data?.map(n=><option key={n.id} value={n.id}>{n.name}</option>)}</select></label><label>題材<select aria-label="事件題材" value={params.get('theme')||''} onChange={e=>set('theme',e.target.value)}><option value="">全部題材</option>{themes.data?.map(t=><option key={t.theme} value={t.theme}>{t.name_zh}</option>)}</select></label><label>發布起日<input aria-label="發布起日" type="date" value={params.get('date_from')||''} onChange={e=>set('date_from',e.target.value)}/></label><label>發布迄日<input aria-label="發布迄日" type="date" value={params.get('date_to')||''} onChange={e=>set('date_to',e.target.value)}/></label><label>內容關聯<select aria-label="內容關聯" value={params.get('relevance')||'direct'} onChange={e=>set('relevance',e.target.value)}><option value="direct">直接相關</option><option value="background">背景統計</option><option value="all">直接＋背景</option></select></label><label className="toggle"><input type="checkbox" checked={params.get('include_routine')==='true'} onChange={e=>set('include_routine',e.target.checked?'true':'')}/>包含例行財報／法說</label>{ticker&&<span className="muted">事件主體：{ticker}</span>}</div><Status {...api}/>{api.data&&<EventList events={api.data}/>}<div className="pagination"><button disabled={page<=0||api.loading} onClick={()=>paginate(page-1)}>上一頁</button><span>第 {page+1} 頁</span><button disabled={!api.data||api.data.length<30||api.loading} onClick={()=>paginate(page+1)}>下一頁</button></div></div>
}
export default function Page(){return <Suspense fallback={<Status loading/>}><EventsPage/></Suspense>}
