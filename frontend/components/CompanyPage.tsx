'use client';
import Link from 'next/link';
import {useApi,segmentUrl} from '@/lib/api';
import type {Company} from '@/lib/types';
import {EventList} from './Events';
import {Status} from './Status';
import {ResearchEntry} from './ResearchEntry';

export function CompanyPage({ticker}:{ticker:string}) {
  const company=useApi<Company>(`/api/companies/${encodeURIComponent(ticker)}`);
  if(company.loading||company.error)return <div className="page-content"><Status {...company}/><Link href="/">回產業探索</Link></div>;
  const data=company.data!;
  return <div className="page-content company-page"><div className="breadcrumb"><Link href="/">產業探索</Link><span>/</span><span>{ticker}</span></div><div className="company-hero"><div><span className="ticker">{ticker}</span><h1>{data.name}</h1><p>{data.roles.map(r=>r.segment_name).join('、')}</p></div></div><ResearchEntry kind="company" identity={ticker}/><section className="role-section"><h2>產業鏈定位</h2>{data.roles.map(r=><div className="role-row" key={r.segment}><Link href={segmentUrl(r.segment,r.layer)}>{r.segment_name}</Link><p>{r.role}</p></div>)}</section><section className="company-events"><div className="section-heading"><h2>相關事件與來源</h2><Link href={`/events?ticker=${encodeURIComponent(ticker)}&include_routine=true`}>查看全部</Link></div>{data.events.length+data.mentioned_events.length===0?<p className="empty">尚未取得這家公司的相關事件，可從上方環節繼續研究。</p>:<>{data.events.length>0&&<><h3>公司主體資訊</h3><EventList events={data.events}/></>}{data.mentioned_events.length>0&&<><h3>內容提及此公司</h3><p className="data-note">提及與事件主體分開；不表示公司必然受惠。</p><EventList events={data.mentioned_events}/></>}</>}</section></div>
}
