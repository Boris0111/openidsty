'use client';
import {useEffect,useState} from 'react';
import {useApi,dateLabel} from '@/lib/api';
import {Status} from './Status';

type Version={version_id:number;version_number:number;theme_id:string;reviewed:string|null;recorded_at:string;reason:string;payload?:unknown};
type History={current_version_id:number|null;total:number;versions:Version[]};
type Difference={from:Version;to:Version;changes:{path:string;kind:'added'|'removed'|'modified';before:unknown;after:unknown}[]};
const labels:Record<string,string>={assessment:'判讀',summary:'結論',confidence:'支持程度',reviewed:'查核日',status:'狀態',checked:'查核基準',claims:'論點',evidence:'證據',conditions:'條件',gaps:'缺口',milestone_reviews:'里程碑核對',next_checks:'下一確認點',paths:'傳導假設'};
function FieldValue({value}:{value:unknown}){
  if(value===null||value===undefined)return <span>—</span>;
  if(typeof value==='string')return /^https:\/\//.test(value)?<a href={value} target="_blank" rel="noreferrer">原始來源 ↗</a>:<span>{value}</span>;
  if(Array.isArray(value))return <ul>{value.map((v,i)=><li key={i}><FieldValue value={v}/></li>)}</ul>;
  if(typeof value==='object')return <dl>{Object.entries(value).map(([k,v])=><div key={k}><dt>{labels[k]||k}</dt><dd><FieldValue value={v}/></dd></div>)}</dl>;
  return <span>{String(value)}</span>;
}
function Diff({id,from,to}:{id:string;from:number;to:number}){
  const api=useApi<Difference>(`/api/themes/${encodeURIComponent(id)}/assessment/compare?from_version=${from}&to_version=${to}`);
  return <><Status {...api}/>{api.data&&<div className="version-diff"><p>變更原因：{api.data.to.reason}</p><p className="data-note">查核 {api.data.to.reviewed||'未提供'}；記錄 {dateLabel(api.data.to.recorded_at)}。差異僅比較保存內容。</p>{api.data.changes.length===0?<p>兩版本的判讀內容相同。</p>:api.data.changes.map((d,i)=><article key={i}><h3>{d.path.split('.').map(k=>labels[k]||k).join(' › ')} <small>{({added:'新增',removed:'移除',modified:'修改'})[d.kind]}</small></h3><div className="diff-columns"><div><h4>原版本</h4><FieldValue value={d.before}/></div><div><h4>比較版本</h4><FieldValue value={d.after}/></div></div></article>)}</div>}</>;
}
export function AssessmentHistory({id}:{id:string}){
  const [offset,setOffset]=useState(0),[versions,setVersions]=useState<Version[]>([]),[selection,setSelection]=useState<{id:string;from:number;to:number}|null>(null);
  const api=useApi<History>(`/api/themes/${encodeURIComponent(id)}/assessment/versions?limit=100&offset=${offset}`);
  useEffect(()=>{setVersions([]);setOffset(0);setSelection(null)},[id]);
  useEffect(()=>{if(!api.data)return;setVersions(previous=>offset===0?api.data!.versions:[...previous,...api.data!.versions.filter(v=>!previous.some(p=>p.version_id===v.version_id))]);if(offset===0){const list=api.data.versions;const query=new URLSearchParams(window.location.search);const from=Number(query.get('from_version'));setSelection({id,from:list.some(v=>v.version_id===from)?from:list[1]?.version_id||list[0]?.version_id||0,to:api.data.current_version_id||0})}},[api.data,id,offset]);
  const ready=selection?.id===id&&selection.from>0&&selection.to>0;
  return <section id="versions" className="assessment-history"><h2>判讀版本與差異</h2><Status {...api}/>{api.data&&<><p>目前版本 {versions.find(v=>v.version_id===api.data!.current_version_id)?.version_number||'未建立'}；共 {api.data.total} 個保存版本。</p>{api.data.total===1&&<p className="data-note">首次只保存目前研究基準，沒有虛構更早歷史。</p>}{ready&&<><div className="version-selectors"><label>原版本<select aria-label="原版本" value={selection!.from} onChange={e=>setSelection({...selection!,from:Number(e.target.value)})}>{versions.map(v=><option key={v.version_id} value={v.version_id}>v{v.version_number}｜查核 {v.reviewed||'未知'}｜記錄 {dateLabel(v.recorded_at)}</option>)}</select></label><label>比較版本<select aria-label="比較版本" value={selection!.to} onChange={e=>setSelection({...selection!,to:Number(e.target.value)})}>{versions.map(v=><option key={v.version_id} value={v.version_id}>v{v.version_number}｜查核 {v.reviewed||'未知'}｜記錄 {dateLabel(v.recorded_at)}</option>)}</select></label></div><Diff id={id} from={selection!.from} to={selection!.to}/><a href="#assessment">返回目前判讀</a></>}{versions.length<api.data.total&&<button onClick={()=>setOffset(v=>v+100)}>載入較早版本</button>}</>}</section>;
}
