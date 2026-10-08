'use client';
import {use} from 'react';
import Link from 'next/link';
import Markdown from 'react-markdown';
import {useApi,themeStatus,segmentUrl} from '@/lib/api';
import type {Theme} from '@/lib/types';
import {EventList} from '@/components/Events';
import {Status} from '@/components/Status';
export default function Page({params}:{params:Promise<{id:string}>}){
  const {id}=use(params),api=useApi<Theme>(`/api/themes/${encodeURIComponent(id)}`),data=api.data;
  return <div className="page-content theme-detail"><div className="breadcrumb"><Link href="/themes">題材研究</Link><span>/</span><span>{id}</span></div><Status {...api}/>{data&&<><div className="page-heading"><h1>{data.name_zh}</h1><p><span className="theme-status">{themeStatus[data.status]}</span>　狀態查核 {data.checked||'未提供'}；狀態不隨事件自動改寫。</p></div><div className="theme-tags">{data.segments_detail?.map(s=><Link key={s.id} href={segmentUrl(s.id,s.layer)}>{s.name}</Link>)}</div><div className="prose theme-research"><Markdown>{data.prose}</Markdown></div><section className="milestones"><h2>預期里程碑與查核點</h2><p className="data-note">以下為研究監測計畫；時間經過不代表已實現。</p>{data.milestones.map((m,i)=><article key={i}><time>{m.date}</time><div><h3>{m.event}</h3><p>{m.evidence}</p></div></article>)}</section><section className="company-events"><div className="section-heading"><h2>已發布的相關事件</h2><Link href={`/events?theme=${data.theme}`}>查看全部</Link></div><EventList events={(data.events||[]).filter(e=>e.lifecycle==='published')}/></section></>}</div>
}
