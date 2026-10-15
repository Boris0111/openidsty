'use client';
import type {IndicatorsResponse,Observation,Theme,AssessmentResponse} from '@/lib/types';
import {dateLabel,basisLabel} from '@/lib/api';
import {Evidence} from './Assessment';

function Trend({rows}:{rows:Observation[]}){
  if(rows.length<2)return null;
  const values=rows.map(r=>Number(r.value)),low=Math.min(...values),high=Math.max(...values);
  const days=rows.map(r=>Date.parse(r.period_end)),start=days[0],end=days.at(-1)!;
  const points=rows.map((r,i)=>({x:20+(days[i]-start)/(end-start||1)*560,y:120-(values[i]-low)/(high-low||1)*95,r}));
  return <svg className="indicator-trend" viewBox="0 0 600 155" role="img" aria-label="同口徑歷史趨勢，精確數值與期別見下方表格"><polyline points={points.map(p=>`${p.x},${p.y}`).join(' ')} fill="none" stroke="#2563EB" strokeWidth="3"/>{points.map(p=><circle key={p.r.identity} cx={p.x} cy={p.y} r="4" fill="#2563EB"><title>{p.r.original_period}：{p.r.value}</title></circle>)}<text x="20" y="148">{rows[0].period_end}</text><text x="580" y="148" textAnchor="end">{rows.at(-1)!.period_end}</text></svg>;
}

export function IndicatorsPanel({data}:{data:IndicatorsResponse}){
  return <section id="indicators" className="theme-indicators"><h2>指標與衡量界線</h2><p className="data-note">數值更新不自動改寫研究結論。資料期間與來源最後成功時間分開。</p>{!data.indicators.length&&<p className="empty">尚無指標設定。</p>}{data.indicators.map(i=><article className="indicator-card" key={i.id}>
    <h3>{i.name} <span className="theme-status">{i.kind==='direct'?'特定產品 direct':'整體營收 proxy'}</span></h3>
    <p>{i.scope}</p><p className="data-note">{i.limitations}</p>
    {i.latest?<><p className="indicator-value">{i.latest.value} <small>{i.currency|| (i.unit==='percent'?'%':i.unit)}</small></p><p>{i.latest.original_period}｜{i.latest.period_start} — {i.latest.period_end}｜{basisLabel[i.latest.basis]||i.latest.basis}</p><p>{i.status==='stale'?'資料過舊':'已有數值'}；距期末 {i.data_age_days} 日。修訂 {i.latest.revision}</p><p className="data-note">{i.comparison.value!==null?`較 ${i.comparison.previous_period} 變化 ${i.comparison.value} ${i.comparison.unit==='percentage-point'?'百分點':'%'}`:i.comparison.reason}</p><Trend rows={i.trend}/></>:<p className="empty">尚未取得有效數值；不以零值代替。</p>}
    <p className="data-note">來源 {i.source.id}：{i.source.status}；最後成功 {dateLabel(i.source.last_success)}。</p>
    {i.gaps.length>0&&<ul className="indicator-gaps">{i.gaps.map(g=><li key={g}>{g}</li>)}</ul>}
    {i.observations.length>0&&<details><summary>期別、來源與修訂明細</summary><div className="table-scroll"><table><thead><tr><th>原期別／起迄</th><th>數值與單位</th><th>修訂</th><th>來源</th></tr></thead><tbody>{i.revisions.map(r=><tr key={r.id}><th>{r.original_period}<small>{r.period_start} — {r.period_end}</small></th><td>{r.value} {r.currency||'%'}<small>{r.scope}{!r.valid&&`；不適用：${r.invalid_reason}`}</small></td><td>{r.revision}</td><td><a href={r.url} target="_blank" rel="noreferrer">官方文件 ↗</a><small>發布 {r.published_at?dateLabel(r.published_at,r.published_precision):'未知'}；出表 {r.reported_at?dateLabel(r.reported_at,'day'):'未提供'}</small><details><summary>必要原文摘錄</summary><blockquote>{r.raw_excerpt}</blockquote></details></td></tr>)}</tbody></table></div></details>}
  </article>)}</section>;
}

export function CommercialProgress({theme,data}:{theme:Theme;data:AssessmentResponse}){
  return <section className="commercial-progress"><h2>商業化里程碑核對</h2><p className="data-note">預期時間保留原精度；時間經過、合作或數值上升不會自動確認。</p>{theme.milestones.map((m,index)=>{const review=data.assessment?.milestone_reviews.find(r=>r.milestone_id===m.id);return <article key={m.id||index}><div><h3>{m.event}</h3><p>預期 {m.date}｜{review?({confirmed:'已確認',contradicted:'已被反證',unconfirmed:'尚未確認'})[review.state]:'尚無核對紀錄'}</p></div>{review&&<><p>{review.note}</p><p className="data-note">核對 {review.reviewed}；實際發生 {review.occurred||'日期未確認'}</p>{review.evidence_ids.length>0&&<details><summary>核對依據與適用範圍</summary><Evidence evidence={data.assessment!.evidence.filter(e=>review.evidence_ids.includes(e.id))} sources={data.evidence_sources}/></details>}</>}</article>})}</section>;
}
