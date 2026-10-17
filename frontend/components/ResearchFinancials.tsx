'use client';
import {useEffect,useRef} from 'react';
import {useSearchParams,useRouter} from 'next/navigation';
import {useResearch} from '@/lib/research-api';
import {NumberValue} from './Reading';
import {readableNumber} from '@/lib/display';
import {FinancialPage,FinancialValue,ObservationPage,metricNames,basisNames,seriesKey,seriesLabel,periodLabel,readTime,financialLimit} from '@/lib/research-financial';

function Trend({values}:{values:FinancialValue[]}){
  const rows=[...values].sort((a,b)=>a.period_end.localeCompare(b.period_end)||a.period_start.localeCompare(b.period_start));
  const numeric=rows.map(row=>Number(row.value)),times=rows.map(row=>Date.parse(row.period_end));
  if(numeric.some(value=>!Number.isFinite(value))||times.some(value=>!Number.isFinite(value)))return <p>這組數值請由下方原值表查閱。</p>;
  const min=Math.min(0,...numeric),max=Math.max(0,...numeric),range=max-min||1,start=times[0],duration=times.at(-1)!-start||1;
  const points=rows.map((row,index)=>({row,x:rows.length===1?260:40+(times[index]-start)/duration*440,y:145-(numeric[index]-min)/range*120}));
  const connect=(index:number)=>{if(!index||rows[index].basis==='instant'||rows[index].basis==='ytd'||rows[index].unit==='per-share'&&['unknown','unspecified',''].includes(rows[index].share_class))return false;return Date.parse(rows[index].period_start)-Date.parse(rows[index-1].period_end)===86400000};
  return <figure className="rf-trend"><svg viewBox="0 0 520 180" role="img" aria-label="同來源、同幣別與同申報口徑的目前頁面趨勢；原期間與精確數值見下表"><line x1="35" y1="150" x2="485" y2="150" stroke="#cbd8dc"/><text x="35" y="15" fontSize="12" fill="#526575">{readableNumber(max===0?'0':rows[numeric.indexOf(max)].value,rows[0].unit,rows[0].currency)}</text><text x="35" y="158" fontSize="12" fill="#526575">{readableNumber(min===0?'0':rows[numeric.indexOf(min)].value,rows[0].unit,rows[0].currency)}</text>{points.map((point,index)=><g key={point.row.observation_id}>{connect(index)&&<line x1={points[index-1].x} y1={points[index-1].y} x2={point.x} y2={point.y} stroke="#267a97" strokeWidth="2"/>}<circle cx={point.x} cy={point.y} r="4" fill="#267a97"><title>{periodLabel(point.row)}：{point.row.value} {point.row.currency}</title></circle></g>)}<text x="40" y="172" fontSize="12" fill="#526575">{rows[0].period_end}</text><text x="480" y="172" textAnchor="end" fontSize="12" fill="#526575">{rows.at(-1)!.period_end}</text></svg><figcaption>{rows.length===1?'目前只有一筆期間資料。':'各點保留原始期間；缺期、累計、期末與未核對股別的 EPS 不連線。'} 原值及來源可由表格選取。</figcaption></figure>;
}

function PeriodReading({value}:{value:FinancialValue}){
  return <>{value.period_start!==value.period_end&&<><span className="rf-date">{value.period_start}</span>{' ～ '}</>}<span className="rf-date">{value.period_end}</span><span className="rf-date">（{basisNames[value.basis]||'原始期間'}）</span></>;
}

export function FinancialValueReading({value}:{value:FinancialValue}){
  const limit=financialLimit(value.limitations);
  return <><strong><NumberValue value={value.value} unit={value.unit} currency={value.currency}/></strong><p><PeriodReading value={value}/></p>{value.derived&&<p>依原始觀測衍生</p>}{limit&&<p className="rs-scope-note">{limit}</p>}</>;
}

export function ObservationReading({company,release,id,onSelect}:{company:string;release:string;id:string;onSelect:(id:string|null)=>void}){
  const params=useSearchParams(),router=useRouter();const before=params.get('before_revision');
  const result=useResearch<ObservationPage>(`/api/v2/companies/${encodeURIComponent(company)}/financials/observations/${encodeURIComponent(id)}?`+new URLSearchParams({release_id:release,limit:'20',...(before?{before_revision:before}:{})}));
  function history(value:number|null){const next=new URLSearchParams(params);if(value)next.set('before_revision',String(value));else next.delete('before_revision');router.push('/next?'+next,{scroll:false})}
  const data=result.data?.data,value=data?.observation;
  const panel=useRef<HTMLElement>(null);
  useEffect(()=>{const trigger=document.activeElement;return()=>{if(trigger instanceof HTMLElement&&trigger.isConnected)trigger.focus({preventScroll:true})}},[]);
  useEffect(()=>{if(value){panel.current?.focus({preventScroll:true});panel.current?.scrollIntoView({block:'start',behavior:'auto'})}},[value?.observation_id]);
  return <section className="rf-observation" ref={panel} tabIndex={-1} aria-label="財務來源與修訂"><div className="rs-section-top"><h3>來源與數值修訂</h3><button onClick={()=>onSelect(null)}>關閉來源與修訂</button></div>{result.loading?<p role="status">正在讀取來源與修訂…</p>:result.error?<p role="alert">{result.error}</p>:value&&data&&<>
    <h4>{value.label}</h4><FinancialValueReading value={value}/><p>{seriesLabel(value)}</p><p>{data.active_observation_id===value.observation_id?'這是此期間的最新有效值。':'這筆是歷史數值；最新有效值不同。'} 修訂 {value.revision}</p>
    {data.active_observation_id!==value.observation_id&&<button onClick={()=>onSelect(data.active_observation_id)}>查看最新有效值</button>}
    <h4>原始依據</h4>{value.sources.length?value.sources.map((source,index)=><div className="rs-citation" key={index}><a href={source.source_url} target="_blank" rel="noreferrer">原始官方文件{value.sources.length>1?' '+(index+1):''}</a>{source.filed_at&&<span>申報日：{source.filed_at}</span>}{source.source_as_of&&<span>提供者彙整日期：{source.source_as_of}</span>}{source.accession&&<span>申報編號：{source.accession}</span>}{source.tag&&<span>申報欄位：{source.tag}</span>}<span>原值：{source.raw_value??'未提供'} {source.raw_unit}；倍率 {source.multiplier}</span>{typeof source.locator==='string'?<span>定位：{source.locator}</span>:source.locator&&<>{['page','section','label'].map(key=>typeof source.locator==='object'&&source.locator!==null&&['string','number'].includes(typeof (source.locator as Record<string,unknown>)[key])?<span key={key}>{({page:'頁碼',section:'章節',label:'欄位名稱'} as Record<string,string>)[key]}：{String((source.locator as Record<string,unknown>)[key])}</span>:null)}</>}</div>):<p>這筆數值未提供可公開查閱的原始文件定位。</p>}{value.sources_truncated&&<p>來源超過這次顯示範圍。</p>}
    {value.derived&&<section><h4>衍生依據</h4><p>{value.formula_version?.includes('gross-margin')?'毛利 ÷ 營收 × 100':value.formula_version?.includes('revenue-yoy')?'（本期營收 ÷ 同期營收 − 1）× 100':value.formula_version?.includes('ytd-difference')?'本期累計 − 前期累計':'依可追溯的原始觀測衍生。'}</p>{value.lineage.map(input=><div key={input.observation_id}><p>{input.label}</p><FinancialValueReading value={input}/><button onClick={()=>onSelect(input.observation_id)}>查閱這筆原始觀測</button></div>)}</section>}
    <h4>這個期間的修訂紀錄</h4><p>按數值修訂列出；晚到的舊申報不會自動成為最新有效值。</p><ul className="rf-history">{data.revisions.map(row=><li key={row.observation_id}><button onClick={()=>onSelect(row.observation_id)}>修訂 {row.revision}：<NumberValue value={row.value} unit={row.unit} currency={row.currency}/>{row.observation_id===data.active_observation_id?'（最新有效）':''}</button><span>{row.filed_at?'申報日 '+row.filed_at:row.source_as_of?'提供者彙整 '+row.source_as_of:'申報日期未提供'}</span></li>)}</ul>{before&&<button onClick={()=>history(null)}>回最新修訂清單</button>}{data.has_more&&<button onClick={()=>history(data.next_before_revision)}>更早的修訂</button>}
  </>}</section>;
}

export function ResearchFinancials({company,release,taiwan=false}:{company:string;release:string;taiwan?:boolean}){
  const params=useSearchParams(),router=useRouter();
  const metric=params.get('metric')||'revenue',basis=params.get('basis')||(taiwan?'monthly':'annual'),cursor=params.get('financial_cursor');
  const query=new URLSearchParams({release_id:release,metric,basis,limit:'100',...(cursor?{cursor}:{})});
  const result=useResearch<FinancialPage>(`/api/v2/companies/${encodeURIComponent(company)}/financials?${query}`);
  function change(key:string,value:string|null){const next=new URLSearchParams(params);if(key==='metric'||key==='basis')next.delete('financial_cursor');next.delete('observation_id');next.delete('before_revision');if(value)next.set(key,value);else next.delete(key);router.push('/next?'+next,{scroll:false})}
  function select(id:string|null){change('observation_id',id)}
  const groups=new Map<string,FinancialValue[]>();for(const row of result.data?.data.items||[]){const key=seriesKey(row);groups.set(key,[...(groups.get(key)||[]),row])}
  return <section aria-label="公司基本財務" id="company-financials"><h2>基本財務</h2><p>公司整體財務，不能直接代表特定產品或 AI 收入。</p><div className="rf-filters"><label>財務指標<select value={metric} onChange={event=>{change('metric',event.target.value)}}>{Object.entries(metricNames).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label><label>財務口徑<select value={basis} onChange={event=>change('basis',event.target.value)}>{Object.entries(basisNames).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label></div>
    {result.error?<p role="alert">{result.error}</p>:result.loading?<p role="status">正在讀取財務…</p>:result.data&&<><p className="rs-scope-note">讀取時間（台北）：{readTime(result.data.data.as_of)}。此時間不是申報日；來源的歷史範圍有限。</p>{result.data.data.source_selection_gap&&<p className="rs-scope-note">{result.data.data.source_selection_gap}</p>}{result.data.data.gaps.map(gap=><p key={gap} role="status">{gap}</p>)}
      {[...groups].map(([key,rows])=><section className="rf-series" key={key}><h3>{rows[0].label}</h3><p>{seriesLabel(rows[0])}</p><Trend values={rows}/><div className="rf-table-wrap"><table><thead><tr><th>原始期間與口徑</th><th>數值</th><th>來源與修訂</th></tr></thead><tbody>{rows.map(row=><tr key={row.observation_id}><th scope="row"><PeriodReading value={row}/></th><td><NumberValue value={row.value} unit={row.unit} currency={row.currency}/>{row.derived&&<span className="rf-row-note">衍生值</span>}</td><td><button onClick={()=>select(row.observation_id)} aria-label={`查閱 ${periodLabel(row)} 的來源與修訂`}>查來源與修訂</button></td></tr>)}</tbody></table></div></section>)}
      <div className="rs-directory-pages">{cursor&&<button onClick={()=>change('financial_cursor',null)}>回第一頁財務</button>}{result.data.data.has_more&&<button onClick={()=>change('financial_cursor',result.data!.data.next_cursor)}>下一頁財務</button>}</div>
    </>}{params.get('observation_id')&&<ObservationReading key={company+':'+params.get('observation_id')} company={company} release={release} id={params.get('observation_id')!} onSelect={select}/>}
  </section>;
}
