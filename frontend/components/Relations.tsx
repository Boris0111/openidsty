'use client';
import {useEffect,useRef} from 'react';
import {DocumentCitation} from './TechnicalDocuments';
import type {GraphData,GraphEdge,TechnicalReference} from '@/lib/types';
import {confidenceLabel} from '@/lib/display';

export const relationKind:Record<string,string>={supply:'供應關係','demand-feedback':'需求回饋',unreviewed:'關係尚未核對'};
export function relationNames(edge:GraphEdge,graph:GraphData){
  return `${edge.source_name||graph.nodes.find(n=>n.id===edge.source)?.name||'起點名稱待補'} → ${edge.target_name||graph.nodes.find(n=>n.id===edge.target)?.name||'終點名稱待補'}`;
}
export function TechnicalEvidence({items}:{items:TechnicalReference[]}){
  return <ul className="technical-evidence">{items.map((ref,index)=><li key={index}>{ref['document-id']?<DocumentCitation id={ref['document-id']} version={ref['version-id']} locator={ref.locator}/>:<>
    <a href={ref.url} target="_blank" rel="noreferrer">閱讀原始來源 ↗</a><p className="data-note">{ref.locator}</p>{ref['read-scope']&&<p className="data-note">引用範圍：{ref['read-scope']}</p>}{ref.excerpt&&<blockquote>{ref.excerpt}</blockquote>}
  </>}</li>)}</ul>;
}
export function RelationList({graph,selected,onSelect}:{graph:GraphData;selected:string|null;onSelect:(id:string,trigger?:HTMLButtonElement)=>void}){
  return <details className="relation-index"><summary>關係文字清單（{graph.edges.length}）</summary><p className="data-note">鍵盤可開啟與圖相同的說明。供應表示環節角色；不能推定特定公司交易。</p><div>{graph.edges.map(edge=><button key={edge.id} data-relation-id={edge.id} aria-pressed={selected===edge.id} onClick={e=>onSelect(edge.id,e.currentTarget)}>{relationNames(edge,graph)}<small>{relationKind[edge.kind]||'關係尚未核對'}</small></button>)}</div></details>;
}
export function RelationReading({id,graph,onClose}:{id:string;graph:GraphData;onClose:()=>void}){
  const heading=useRef<HTMLHeadingElement>(null),edge=graph.edges.find(e=>e.id===id);
  useEffect(()=>{heading.current?.focus({preventScroll:true});if(window.matchMedia('(max-width:800px)').matches)heading.current?.scrollIntoView({block:'start',behavior:'instant'})},[id]);
  const detail=edge?.relation;
  return <section id="relation-reading" className="relation-reading" aria-label="連線依據"><div className="section-heading"><h2 ref={heading} tabIndex={-1}>{edge?relationNames(edge,graph):'找不到這條關係'}</h2><button onClick={onClose}>{edge?'關閉連線詳情':'清除無效連線'}</button></div>{edge?<><p className={`relation-kind ${edge.kind}`}>{relationKind[edge.kind]||'關係尚未核對'} · {confidenceLabel[detail?.confidence||'needs-verification']||'支持程度待確認'}</p><p>{detail?.summary||'這條舊格式關係尚未提供完整說明，請回到研究核對。'}</p><p className="data-note">這是環節關係，不能視為公司之間已確認交易。說明查核 {detail?.reviewed||'尚未完成'}。</p>{[['items',edge.kind==='demand-feedback'?'需求形成機制':'供應項目'],['dependencies','介面依賴'],['conditions','成立條件'],['gaps','證據缺口']] .map(([key,label])=><section key={key}><h3>{label}</h3>{(detail?.[key as 'items']||[]).length?<ul>{(detail![key as 'items']).map(text=><li key={text}>{text}</li>)}</ul>:<p>尚待補充核對。</p>}</section>)}<section><h3>證據與定位</h3>{detail?.evidence.length?<TechnicalEvidence items={detail.evidence}/>:<p>尚未取得可解析的公開引用，以上保留具體核對缺口。</p>}</section></>:<><p>目前產業圖沒有這條連線。可清除選取，再從文字清單查看。</p></>}</section>;
}
