'use client';
import {useState,useMemo,useRef,useEffect} from 'react';
import {useSearchParams,useRouter} from 'next/navigation';
import Link from 'next/link';
import {ResearchMarkdown as Markdown} from './Reading';
import {useApi,companyUrl,segmentUrl,themeStatus} from '@/lib/api';
import type {Industry,GraphData,Segment} from '@/lib/types';
import {Network} from './Network';
import {EventList} from './Events';
import {Status} from './Status';
import {useResearchNames} from '@/lib/research-names';
import {RelationList,RelationReading} from './Relations';
import {ReadingTabs} from './ReadingTabs';
import {TechnicalResearch} from './TechnicalResearch';
import {ResearchEntry} from './ResearchEntry';

function SegmentPanel({id,autoRead}:{id:string;autoRead:boolean}) {
  const api=useApi<Segment>(`/api/segments/${encodeURIComponent(id)}`),data=api.data;
  const names=useResearchNames();
  const sections=data?.prose.split(/(?=^## )/m)||[];
  const section=(title:string)=>sections.find(s=>s.startsWith(`## ${title}`))||'';
  const known=['環節定義','技術變數','玩家格局','傳導鏈','監測指標','風險'];
  useEffect(()=>{if(data&&autoRead&&window.matchMedia('(max-width:800px)').matches){document.getElementById('segment-reading')?.scrollIntoView({block:'start',behavior:'instant'});document.querySelector<HTMLElement>('#segment-reading h2')?.focus({preventScroll:true})}},[data,autoRead]);
  return <aside className="segment-panel" id="segment-reading" aria-label="環節詳細資訊" aria-busy={api.loading}>
    <Status {...api}/>{data&&<>
      <div className="segment-heading"><span className="muted">{data.layer==='ai-server'?'AI 伺服器':'半導體'}環節</span><h2 tabIndex={-1}>{data.name_zh}</h2>
        <div className="prose"><Markdown names={names}>{section('環節定義').replace(/^## 環節定義\s*/,'')}</Markdown></div>
      </div>
      <ResearchEntry kind="segment" identity={id}/>
      <ReadingTabs label="環節閱讀" tabs={[
        {id:'segment-role',label:'產業角色',content:<>
          <section><h3>供應與需求關係</h3>{(['upstream','downstream'] as const).map(direction=><div className="neighbor-row" key={direction}><span>{direction==='upstream'?'上游供應':'下游需求'}</span><div>{data[direction].length?data[direction].map(sid=>{const n=data.neighbors.find(n=>n.id===sid);return <Link key={sid} href={segmentUrl(sid,n?.layer||data.layer)}>{n?.name||'環節名稱待補'}</Link>}):<span className="muted">此範圍未列關係</span>}</div></div>)}</section>
          <div className="prose research-body"><Markdown names={names}>{section('傳導鏈')}</Markdown></div>
          <section><h3>代表公司與供應角色</h3><div className="company-list">{data.companies.map(c=><div className="company-row" key={c.ticker}><Link href={companyUrl(c.ticker)} className="company-name">{c.name_zh}<span>{c.ticker}</span></Link><p>{c.role}</p></div>)}</div></section>
          <details className="research-more"><summary>玩家格局與競爭說明</summary><div className="prose"><Markdown names={names}>{section('玩家格局').replace(/^## 玩家格局\s*/,'')}</Markdown></div></details>
        </>},
        {id:'segment-technology',label:'技術與限制',content:<>
          <div className="prose research-body"><Markdown names={names}>{section('技術變數')}</Markdown></div>
          <TechnicalResearch profile={data['technical-profile']}/>
          <div className="prose research-body"><Markdown names={names}>{sections.filter(s=>!known.some(k=>s.startsWith(`## ${k}`))).join('\n\n')}</Markdown></div>
        </>},
        {id:'segment-tracking',label:'追蹤重點',content:<>
          <section><h3>監測指標與轉折訊號</h3><h4>要觀察的指標</h4><ul>{data.kpis.map(k=><li key={k}>{k}</li>)}</ul><h4>轉折訊號</h4><ul>{data.signals.map(s=><li key={s}>{s}</li>)}</ul>
            <details><summary>指標判讀方式</summary><div className="prose"><Markdown names={names}>{section('監測指標').replace(/^## 監測指標\s*/,'')}</Markdown></div></details>
          </section>
          <div className="prose research-body"><Markdown names={names}>{section('風險')}</Markdown></div>
          <section><h3>相關題材</h3><div className="theme-tags">{data.themes_detail.map(t=><Link key={t.theme} href={`/themes/${t.theme}`}>{t.name_zh}<small>{themeStatus[t.status]||'狀態待確認'}</small>{t.assessment_summary?.summary&&<span className="theme-link-summary">{t.assessment_summary.summary}</span>}</Link>)}</div>{!data.themes_detail.length&&<p className="data-note">此環節尚未列題材。</p>}</section>
          <section><div className="section-heading"><h3>近期直接相關事件</h3><Link href={`/events?segment=${data.segment}`}>全部事件</Link></div><EventList events={data.events}/></section>
        </>},
      ]}/>
    </>}
  </aside>;
}

export function Explorer() {
  const params=useSearchParams(),router=useRouter();
  const layer=params.get('layer')==='semiconductor'?'semiconductor':'ai-server';
  const selected=params.get('segment')||(layer==='ai-server'?'compute':'foundry');
  const relation=params.get('relation');
  const relationTrigger=useRef<HTMLButtonElement|null>(null),previousRelation=useRef<string|null>(null);
  const [external,setExternal]=useState(false),[fullscreen,setFullscreen]=useState(false);
  const modal=useRef<HTMLDialogElement>(null),lastSelection=useRef(selected);
  const industries=useApi<Industry[]>('/api/industries');
  const {data:graph,loading,error,retry}=useApi<GraphData>(`/api/industries/${layer}/graph`);
  const visible=useMemo(()=>{if(!graph)return null;const nodes=graph.nodes.filter(n=>external||!n.external||n.id===selected);const ids=new Set(nodes.map(n=>n.id));return {...graph,nodes,edges:graph.edges.filter(e=>ids.has(e.source)&&ids.has(e.target))}},[graph,external,selected]);
  // Keep the same graph object across selection, so pan and zoom stay stable.
  const full=useMemo(()=>{if(!graph)return null;const nodes=graph.nodes.filter(n=>external||!n.external);const ids=new Set(nodes.map(n=>n.id));return {...graph,nodes,edges:graph.edges.filter(e=>ids.has(e.source)&&ids.has(e.target))}},[graph,external]);
  const local=useMemo(()=>{if(!graph)return null;const ids=new Set([selected]);graph.edges.forEach(e=>{if(e.source===selected)ids.add(e.target);if(e.target===selected)ids.add(e.source)});return {...graph,nodes:graph.nodes.filter(n=>ids.has(n.id)),edges:graph.edges.filter(e=>ids.has(e.source)&&ids.has(e.target))}},[graph,selected]);
  useEffect(()=>{if(graph?.nodes.find(n=>n.id===selected)?.external)setExternal(true)},[graph,selected]);
  useEffect(()=>{if(!relation&&lastSelection.current!==selected&&window.matchMedia('(max-width:800px)').matches){document.getElementById('segment-reading')?.scrollIntoView({block:'start',behavior:'instant'});document.querySelector<HTMLElement>('#segment-reading h2')?.focus({preventScroll:true})}lastSelection.current=selected},[selected]);
  useEffect(()=>{if(fullscreen&&!modal.current?.open)modal.current?.showModal();else if(!fullscreen&&modal.current?.open)modal.current?.close()},[fullscreen]);
  useEffect(()=>{if(!relation&&previousRelation.current){const target=Array.from(document.querySelectorAll<HTMLButtonElement>('[data-relation-id]')).find(b=>b.dataset.relationId===previousRelation.current);if(target?.closest('details')?.open)target.focus({preventScroll:true});else document.querySelector<HTMLElement>('.relation-index>summary')?.focus({preventScroll:true})}previousRelation.current=relation},[relation]);
  useEffect(()=>{const edge=graph?.edges.find(e=>e.id===relation);if(edge&&graph?.nodes.some(n=>n.external&&(n.id===edge.source||n.id===edge.target)))setExternal(true)},[graph,relation]);
  function select(id:string){const next=new URLSearchParams(params);next.set('layer',layer);next.set('segment',id);router.push(`/?${next}`,{scroll:false})}
  function selectRelation(id:string|null,trigger?:HTMLButtonElement){if(trigger)relationTrigger.current=trigger;const next=new URLSearchParams(params);next.set('layer',layer);next.set('segment',selected);if(id)next.set('relation',id);else next.delete('relation');router.push(`/?${next}`,{scroll:false})}
  return <div className="explorer"><div className="page-intro"><div><h1>從產業結構，讀懂變化</h1><p>選擇環節，理解技術、供需關係與題材，再追溯近期事件。</p></div><div className="industry-switch" aria-label="選擇產業">{(industries.data||[{id:'ai-server',name:'AI 伺服器',segment_count:0},{id:'semiconductor',name:'半導體',segment_count:0}]).map(i=><button key={i.id} className={i.id===layer?'active':''} aria-pressed={i.id===layer} onClick={()=>{setExternal(false);router.push(segmentUrl(i.id==='ai-server'?'compute':'foundry',i.id),{scroll:false})}}>{i.name}</button>)}</div></div><div className="explorer-workspace"><section className="map-panel" aria-label="產業鏈總覽"><div className="map-toolbar"><div><strong>{layer==='ai-server'?'AI 伺服器產業鏈':'半導體產業鏈'}</strong>{graph&&<span>{graph.nodes.filter(n=>!n.external).length} 個環節</span>}</div><label className="toggle"><input type="checkbox" checked={external} onChange={e=>setExternal(e.target.checked)}/>展開跨產業</label></div><Status {...{loading,error,retry}}/>{relation&&graph&&<RelationReading id={relation} graph={graph} onClose={()=>selectRelation(null)}/>}{full&&local&&visible&&<><div className="desktop-map"><Network graph={full} selected={selected} onSelect={select} selectedRelation={relation} onRelation={selectRelation}/></div><div className="segment-index" aria-label="環節清單">{visible.nodes.map(n=><button key={n.id} className={`${selected===n.id?'active':''} ${n.external?'external':''}`} aria-pressed={selected===n.id} onClick={()=>select(n.id)}>{n.name}{n.external&&<small>跨產業</small>}</button>)}</div><div className="mobile-map"><div className="map-toolbar"><strong>選中環節的供需關係</strong><button onClick={()=>setFullscreen(true)}>全螢幕完整圖</button></div><Network graph={local} selected={selected} onSelect={select} compact selectedRelation={relation} onRelation={selectRelation}/></div><div className="relation-legend" aria-label="連線圖例"><span className="supply">實線：供應關係</span><span className="demand-feedback">虛線：需求回饋</span><span className="unreviewed">點線：尚未核對</span></div><RelationList graph={visible} selected={relation} onSelect={selectRelation}/><p className="map-note">序位提供方向感；箭頭表示關係方向，回路保留需求回饋。<Link href="/coverage">查看資料覆蓋</Link></p></>}</section><SegmentPanel key={selected} id={selected} autoRead={Boolean(graph)&&(!graph?.nodes.find(n=>n.id===selected)?.external||external)&&params.has("segment")&&!relation}/></div><dialog ref={modal} className="graph-dialog" onCancel={()=>setFullscreen(false)} onClose={()=>setFullscreen(false)} aria-label="全螢幕完整產業圖"><div className="map-toolbar"><strong>完整產業供應鏈</strong><button onClick={()=>setFullscreen(false)}>關閉完整圖</button></div>{fullscreen&&graph&&<Network graph={graph} selected={selected} onSelect={id=>{select(id);setFullscreen(false)}} selectedRelation={relation} onRelation={id=>{selectRelation(id);setFullscreen(false)}}/>}<div className="segment-index">{graph?.nodes.map(n=><button key={n.id} onClick={()=>{select(n.id);setFullscreen(false)}}>{n.name}</button>)}</div></dialog></div>
}
