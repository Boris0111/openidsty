'use client';
import {use} from 'react';
import Link from 'next/link';
import Markdown from 'react-markdown';
import {useApi,themeStatus,segmentUrl} from '@/lib/api';
import type {Theme,AssessmentResponse,SegmentLink,IndicatorsResponse} from '@/lib/types';
import {EventList} from '@/components/Events';
import {Status} from '@/components/Status';
import {AssessmentPanel} from '@/components/Assessment';
import {IndicatorsPanel,CommercialProgress} from '@/components/Indicators';
import {AssessmentHistory} from '@/components/AssessmentHistory';
import {WatchTheme} from '@/components/WatchTheme';
export default function Page({params}:{params:Promise<{id:string}>}){
  const {id}=use(params),api=useApi<Theme>(`/api/themes/${encodeURIComponent(id)}`),data=api.data;
  const assessment=useApi<AssessmentResponse>(`/api/themes/${encodeURIComponent(id)}/assessment`);
  const segments=useApi<SegmentLink[]>('/api/segments');
  const indicators=useApi<IndicatorsResponse>(`/api/themes/${encodeURIComponent(id)}/indicators`);
  const names=Object.fromEntries((segments.data||[]).map(s=>[s.id,s.name]));
  return <div className="page-content theme-detail">
    <div className="breadcrumb"><Link href="/themes">題材研究</Link><span>/</span><span>{id}</span></div>
    <Status {...api}/>{data&&<>
      <div className="page-heading"><h1>{data.name_zh}</h1><p><span className="theme-status">{themeStatus[data.status]}</span>　狀態查核 {data.checked||'未提供'}；狀態不隨事件自動改寫。</p></div>
      <div className="theme-tags">{data.segments_detail?.map(s=><Link key={s.id} href={segmentUrl(s.id,s.layer)}>{s.name}</Link>)}</div>
      <WatchTheme id={id}/>
      <Status {...assessment}/>{assessment.data&&<AssessmentPanel data={assessment.data} segmentNames={names}/>}
      <Status {...indicators}/>{indicators.data&&<IndicatorsPanel data={indicators.data}/>}
      {assessment.data&&<CommercialProgress theme={data} data={assessment.data}/>}
      <AssessmentHistory id={id}/>
      <section className="theme-full-research" aria-label="完整研究"><h2>完整研究與原查核基準</h2><div className="prose theme-research"><Markdown>{data.prose}</Markdown></div></section>
      <section className="milestones"><h2>預期里程碑與查核點</h2><p className="data-note">以下為研究監測計畫；時間經過不代表已實現。</p>{data.milestones.map((m,i)=><article key={m.id||i}><time>{m.date}</time><div><h3>{m.event}</h3><p>{m.evidence}</p></div></article>)}</section>
      {assessment.data&&<section id="candidates" className="assessment-candidates"><div className="section-heading"><h2>待納入判讀的資訊</h2><Link href={`/events?theme=${data.theme}`}>查看全部</Link></div><p className="data-note">原查核基準之後 {assessment.data.candidate_count} 則直接相關資訊；尚未自動納入研究結論。</p><EventList events={assessment.data.candidates}/>{assessment.data.unknown_date_count>0&&<><h3>發布日待確認</h3><p className="data-note">{assessment.data.unknown_date_count} 則資訊的發布日期未知，不能認定為較新的產業事件。</p><EventList events={assessment.data.undated_candidates}/></>}</section>}
      <section className="company-events"><div className="section-heading"><h2>已發布的相關事件</h2><Link href={`/events?theme=${data.theme}`}>查看全部</Link></div><EventList events={(data.events||[]).filter(e=>e.lifecycle==='published')}/></section>
    </>}
  </div>;
}
