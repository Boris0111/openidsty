'use client';
import Link from 'next/link';
import type {AssessmentResponse, AssessmentEvidence, EvidenceSource, Confidence} from '@/lib/types';

import {confidenceLabel,displayName} from '@/lib/display';
export {confidenceLabel} from '@/lib/display';

export function Evidence({evidence,sources}:{evidence:AssessmentEvidence[];sources:Record<string,EvidenceSource>}) {
  return <div className="assessment-evidence">{evidence.map(e=><article key={e.id}>
    <a href={e.url} target="_blank" rel="noreferrer">{sources[e.source_id]?.name||'來源名稱待補'} ↗</a>
    <p className="evidence-period">{e.period}<br/>發布 {e.published||'日期未知'}</p>
    <blockquote>{e.excerpt}</blockquote>
  </article>)}</div>;
}

export function AssessmentPanel({data,segmentNames={}}:{data:AssessmentResponse;segmentNames?:Record<string,string>}) {
  const a=data.assessment;
  if(!data.available||!a)return <section id="assessment" className="assessment-empty" aria-label="題材判讀"><h2>判讀尚未整理</h2><p>原研究與查核基準仍可閱讀；目前缺少結構化的支持／反向證據。</p><a href="#technical">閱讀原研究</a></section>;
  return <section id="assessment" className="assessment-reading" aria-label="題材判讀">
    <div className="assessment-summary">
      <div className="assessment-baseline"><h2>目前判讀</h2><span className={`confidence ${a.confidence}`}>{confidenceLabel[a.confidence]||'支持程度待確認'}</span></div>
      <p className="assessment-conclusion">{a.summary}</p>
      <p className="data-note">研究查核 {a.reviewed}。支持程度描述證據，並非報酬機率。</p>
    </div>
    <div className="assessment-claims">{(['supporting','counter'] as const).map(stance=><section key={stance}>
      <h3>{stance==='supporting'?'支持依據':'反向證據'}</h3>
      {a.claims.filter(c=>c.stance===stance).map(c=><article className={`assessment-claim ${stance}`} key={c.id}>
        <p>{c.statement}</p><span className={`confidence ${c.confidence}`}>{confidenceLabel[c.confidence]}</span>
        <details><summary>查看證據（{c.evidence_ids.length}）</summary><Evidence evidence={a.evidence.filter(e=>c.evidence_ids.includes(e.id))} sources={data.evidence_sources}/></details>
      </article>)}
      {!a.claims.some(c=>c.stance===stance)&&<p className="data-note">尚未取得可核對的反向證據。成立條件與風險另列。</p>}
    </section>)}</div>
    <div className="assessment-limits"><section><h3>成立條件</h3><ul>{a.conditions.map(c=><li key={c}>{c}</li>)}</ul></section><section><h3>仍待確認</h3>{a.gaps.length?<ul>{a.gaps.map(g=><li key={g}>{g}</li>)}</ul>:<p>本次研究未列額外缺口；仍請留意查核基準。</p>}</section></div>
    <section className="assessment-next"><h3>下一個確認點</h3>{a.next_checks.map((c,i)=><div key={i}><p><strong>{c.question}</strong></p><p className="data-note">需要 {c.evidence_required}</p></div>)}</section>
    {a.paths.length>0&&<section className="assessment-paths"><h3>有條件的傳導假設</h3><p className="data-note">以下為有條件推論，需成立條件與實際採購支持。</p>{a.paths.map(p=><details key={p.id}>
      <summary>{p.steps.map((s,i)=>`${i===0?(displayName(s.from,segmentNames))+' → ':''}${displayName(s.to,segmentNames)}`).join(' → ')}　{({positive:'可能正向',negative:'可能負向',mixed:'影響混合',unknown:'方向待查'})[p.direction]}</summary>
      <p>{p.mechanism}</p><ul>{p.conditions.map(c=><li key={c}>{c}</li>)}</ul>
      <p className="data-note">{p.steps.map(s=>s.type==='sibling'?`共同下游：${displayName(s.via||'',segmentNames)}`:s.type==='theme'?'題材橫向擴散':s.type==='upstream'?'上游供應':'下游需求').join('；')}</p>
      {p.claim_ids.map(id=><p className="data-note" key={id}>{a.claims.find(c=>c.id===id)?.statement}</p>)}
    </details>)}</section>}
    {data.source_warnings.length>0&&<details className="assessment-source-warning"><summary>來源取得限制（{data.source_warnings.length}）</summary><p className="data-note">取得狀態與研究查核分開；來源失敗時仍保留原判讀。</p>{data.source_warnings.map((w,i)=><p key={i}>{data.evidence_sources[w.source_id]?.name||'來源名稱待補'}：{w.kind==='configuration_required'?'來源待設定':w.kind==='unverified'?'原文件可讀性待確認':w.kind==='partial'?'來源僅部分取得':'來源目前無法取得'}</p>)}<Link href="/sources">查看來源狀態</Link></details>}
  </section>;
}
