'use client';
import {useEffect,useState} from 'react';
import {useSearchParams} from 'next/navigation';
import {useApi,dateLabel} from '@/lib/api';
import {Status} from './Status';
import {confidenceLabel,fieldLabel,readingText,lifecycleLabel,displayName,readableNumber} from '@/lib/display';
import {useResearchNames} from '@/lib/research-names';

type Version={version_id:number;version_number:number;theme_id:string;reviewed:string|null;recorded_at:string;reason:string;payload?:unknown};
type History={current_version_id:number|null;total:number;versions:Version[]};
type Difference={from:Version;to:Version;changes:{path:string;kind:'added'|'removed'|'modified';before:unknown;after:unknown}[]};
const labels=fieldLabel;
function FieldValue({value,field='',names={}}:{value:unknown;field?:string;names?:Record<string,string>}){
  if(value===null||value===undefined)return <span>—</span>;
  if(['id','source_id','claim_ids','evidence_ids','milestone_id'].includes(field))return <span>引用已調整，請對照該論述的來源。</span>;
  if(typeof value==='string'){
    if(field==='excerpt'||field==='raw_excerpt')return <blockquote>{value}</blockquote>;
    if(/^https:\/\//.test(value))return <a href={value} target="_blank" rel="noreferrer">原始來源 ↗</a>;
    if(field==='confidence')return <span>{confidenceLabel[value as keyof typeof confidenceLabel]||'支持程度待確認'}</span>;
    if(field==='status')return <span>{lifecycleLabel[value]||'狀態待確認'}</span>;
    return <span>{names[value]||labels[value]||readingText(value,names)}</span>;
  }
  if(Array.isArray(value))return <ul>{value.map((v,i)=><li key={i}><FieldValue value={v} field={field} names={names}/></li>)}</ul>;
  if(typeof value==='object')return <dl>{Object.entries(value).filter(([k])=>!['id','source_id','claim_ids','evidence_ids','milestone_id'].includes(k)).map(([k,v])=><div key={k}><dt>{labels[k]||'欄位說明待補'}</dt><dd><FieldValue value={v} field={k} names={names}/></dd></div>)}</dl>;
  return <span>{typeof value==='number'&&field!=='date'&&field!=='year'?readableNumber(value):String(value)}</span>;
}
function Diff({id,from,to,names}:{id:string;from:number;to:number;names:Record<string,string>}){
  const api=useApi<Difference>(`/api/themes/${encodeURIComponent(id)}/assessment/compare?from_version=${from}&to_version=${to}`);
  return <><Status {...api}/>{api.data&&<div className="version-diff"><p>變更原因：{api.data.to.reason}</p><p className="data-note">查核 {api.data.to.reviewed||'未提供'}；記錄 {dateLabel(api.data.to.recorded_at)}。差異僅比較保存內容。</p>{api.data.changes.length===0?<p>兩版本的判讀內容相同。</p>:api.data.changes.map((d,i)=><article key={i}><h3>{d.path.split('.').map(k=>labels[k.replace(/\[.*?\]/g,'')]||'項目').join(' › ')} <small>{({added:'新增',removed:'移除',modified:'修改'})[d.kind]}</small></h3><div className="diff-columns"><div><h4>原版本</h4><FieldValue value={d.before} field={d.path.split('.').at(-1)?.replace(/\[.*?\]/g,'')} names={names}/></div><div><h4>比較版本</h4><FieldValue value={d.after} field={d.path.split('.').at(-1)?.replace(/\[.*?\]/g,'')} names={names}/></div></div></article>)}</div>}</>;
}
function HistoryContent({id,sharedFrom,sharedTo}:{id:string;sharedFrom:number;sharedTo:number}){
  const names=useResearchNames();
  const [offset,setOffset]=useState(0),[versions,setVersions]=useState<Version[]>([]),[selection,setSelection]=useState<{from:number;to:number}>({from:sharedFrom,to:sharedTo});
  const api=useApi<History>(`/api/themes/${encodeURIComponent(id)}/assessment/versions?limit=20&offset=${offset}`);
  const extraFrom=useApi<Version>(sharedFrom?`/api/themes/${encodeURIComponent(id)}/assessment/versions/${sharedFrom}`:null);
  const extraTo=useApi<Version>(sharedTo?`/api/themes/${encodeURIComponent(id)}/assessment/versions/${sharedTo}`:null);
  useEffect(()=>{if(!api.data)return;setVersions(previous=>offset===0?api.data!.versions:[...previous,...api.data!.versions.filter(v=>!previous.some(p=>p.version_id===v.version_id))]);if(sharedFrom&&!sharedTo)setSelection(v=>({...v,to:api.data!.current_version_id||0}));},[api.data,offset,sharedFrom,sharedTo]);
  const list=[...versions];for(const v of [extraFrom.data,extraTo.data])if(v&&!list.some(p=>p.version_id===v.version_id))list.push(v);
  const ready=selection.from>0&&selection.to>0&&selection.from!==selection.to&&[selection.from,selection.to].every(id=>list.some(v=>v.version_id===id));
  return <><Status {...api}/><Status {...extraFrom}/><Status {...extraTo}/>{api.data&&<><p>共 {api.data.total} 個保存版本。</p>{api.data.total===1?<p className="data-note">首次只保存目前研究基準，沒有虛構更早歷史。</p>:<div className="version-selectors">{(['from','to'] as const).map((field,index)=><label key={field}>{index?'比較版本':'原版本'}<select aria-label={index?'比較版本':'原版本'} value={selection[field]} onChange={e=>setSelection({...selection,[field]:Number(e.target.value)})}><option value={0}>請選擇版本</option>{list.map(v=><option key={v.version_id} value={v.version_id}>v{v.version_number}｜查核 {v.reviewed||'未知'}｜記錄 {dateLabel(v.recorded_at)}</option>)}</select></label>)}</div>}{ready&&<><Diff id={id} from={selection.from} to={selection.to} names={names}/><a href={`?from_version=${selection.from}&to_version=${selection.to}#versions`}>分享此版本比較</a><a href="#assessment">返回目前判讀</a></>}{versions.length<api.data.total&&<button onClick={()=>setOffset(v=>v+20)}>載入較早版本</button>}</>}</>;
}
export function AssessmentHistory({id}:{id:string}){
  const search=useSearchParams();const from=Number(search.get('from_version'))||0,to=Number(search.get('to_version'))||0;
  const [open,setOpen]=useState(Boolean(from||to));
  useEffect(()=>{if(from||to)setOpen(true);},[from,to]);
  return <section id="versions" className="assessment-history"><details open={open} onToggle={e=>setOpen(e.currentTarget.open)}><summary>判讀版本與差異</summary>{open&&<HistoryContent key={id} id={id} sharedFrom={from} sharedTo={to}/>}</details></section>;
}
