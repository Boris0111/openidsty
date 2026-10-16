'use client';
import Link from 'next/link';
import {eventDate} from '@/lib/api';
import type {InfoEvent} from '@/lib/types';
const labels:Record<string,string>={announcement:'重大訊息',financials:'財報／營收',filing:'官方申報',earnings_call:'法說資料',industry_news:'產業消息',official_stats:'背景統計'};
export function EventList({events}:{events:InfoEvent[]}) {
  if(!events.length)return <p className="empty">尚未取得直接相關事件。研究內容仍可閱讀，<Link href="/coverage">查看資料覆蓋與來源狀態</Link>。</p>;
  return <div className="event-list">{events.map(e=><article className="event-row" key={e.id}><div className="event-date"><time dateTime={e.published_at||undefined}>{eventDate(e)}</time><span>{labels[e.kind]||'資訊類型待確認'}{e.lifecycle==='preview'&&<b className="candidate-badge">活動預告</b>}{e.routine&&<b className="source-status">例行</b>}</span></div><div><Link href={`/events/${e.id}`} className="event-title">{e.title}</Link><p>{e.body.slice(0,160)}{e.body.length>160?'…':''}</p><span className="muted">{e.source_name||'來源名稱待補'}{e.ticker?`　主體 ${e.ticker}`:'　產業資訊'}{e.period?`　資料期間 ${e.period}`:''}</span></div><a className="source-link" href={e.url} target="_blank" rel="noreferrer" aria-label={`閱讀 ${e.title} 的來源`}>來源 ↗</a></article>)}</div>
}
