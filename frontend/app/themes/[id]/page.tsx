'use client';
import {use} from 'react';
import Link from 'next/link';
import {ResearchMarkdown as Markdown} from '@/components/Reading';
import {useApi,themeStatus,segmentUrl} from '@/lib/api';
import type {Theme,AssessmentResponse,IndicatorsResponse} from '@/lib/types';
import {EventList} from '@/components/Events';
import {Status} from '@/components/Status';
import {AssessmentPanel} from '@/components/Assessment';
import {IndicatorsPanel,CommercialProgress} from '@/components/Indicators';
import {AssessmentHistory} from '@/components/AssessmentHistory';
import {WatchTheme} from '@/components/WatchTheme';
import {ReadingTabs} from '@/components/ReadingTabs';
import {TechnicalResearch} from '@/components/TechnicalResearch';
import {useResearchNames} from '@/lib/research-names';
export default function Page({params}:{params:Promise<{id:string}>}){
  const {id}=use(params),api=useApi<Theme>(`/api/themes/${encodeURIComponent(id)}`),data=api.data;
  const assessment=useApi<AssessmentResponse>(`/api/themes/${encodeURIComponent(id)}/assessment`);
  const researchNames=useResearchNames();
  const indicators=useApi<IndicatorsResponse>(`/api/themes/${encodeURIComponent(id)}/indicators`);
  const names={...researchNames,...(data?{[id]:data.name_zh}:{})};
  return <div className="page-content theme-detail">
    <div className="breadcrumb"><Link href="/themes">題材研究</Link><span>/</span><span>{data?.name_zh||'題材研究'}</span></div>
    <Status {...api}/>{data&&<>
      <div className="theme-header">
        <div className="page-heading"><h1>{data.name_zh}</h1><p><span className="theme-status">{themeStatus[data.status]||'狀態待確認'}</span>　狀態查核 {data.checked||'未提供'}</p></div>
        <div className="theme-actions"><WatchTheme id={id} name={data.name_zh}/><button onClick={()=>{api.retry();assessment.retry();indicators.retry();}}>重新取得資料</button></div>
      </div>
      <div className="theme-tags related-segments">{data.segments_detail?.map(s=><Link key={s.id} href={segmentUrl(s.id,s.layer)}>{s.name}</Link>)}</div>
      <ReadingTabs label="題材閱讀" tabs={[
        {id:'research',label:'研究判讀',anchors:['assessment','versions'],content:<>
          <Status {...assessment}/>{assessment.data&&<AssessmentPanel data={assessment.data} segmentNames={names}/>}
          <AssessmentHistory id={id}/>
        </>},
        {id:'technical',label:'技術與供應鏈',content:<>
          <section className="theme-full-research" aria-label="完整研究"><div className="prose theme-research"><Markdown names={names}>{data.prose}</Markdown></div></section>
          <TechnicalResearch profile={data['technical-profile']}/>
        </>},
        {id:'tracking',label:'數據與追蹤',anchors:['indicators','candidates','milestones','events'],content:<>
          <Status {...indicators}/>{indicators.data&&<IndicatorsPanel data={indicators.data}/>}
          {assessment.data?<CommercialProgress theme={data} data={assessment.data}/>:<section id="milestones" className="milestones"><h2>預期里程碑與查核點</h2>{data.milestones.map((m,i)=><article key={m.id||i}><time>{m.date}</time><div><h3>{m.event}</h3><p>{m.evidence}</p></div></article>)}</section>}
          <p id="candidates" className="data-note">待納入判讀的資訊已移至維護端核對；這裡可閱讀公開事件與指標，判讀以查核日為準。</p>
          <section id="events" className="company-events"><div className="section-heading"><h2>已發布的相關事件</h2><Link href={`/events?theme=${data.theme}`}>查看全部</Link></div><EventList events={(data.events||[]).filter(e=>e.lifecycle==='published')}/></section>
        </>},
      ]}/>

    </>}
  </div>;
}
