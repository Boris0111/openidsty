'use client';
import {useEffect,useState} from 'react';

type Api=<T>(path:string)=>Promise<T>;
type Gap={status:string|null;reason:string};
type Counts={not_researched:number;not_public:number;not_obtained:number;not_applicable:number;unclassified:number};
type Entity=Counts&{entity_id:string;kind:string;name:string;reviewed:string|null;research_depth:string|null;claims:number;implied_not_researched:boolean;gaps:Gap[]};
type Total=Counts&{kind:string;entities:number;basic_companies:number};
type Entities={release_id:string;totals:Total[];items:Entity[];has_more:boolean;next_cursor:string|null;counting:string};
type Version={version_id:string;label:string|null;reviewed:string|null;read_scope:string|null;locators:{id:string;section:string|null}[]};
type Candidate={observation_id:number;official_version:string|null;fetched_at:string;status:string;reason:string|null};
type Document={id:string;title:string;doc_kind:string;adopted:Version[];review_counts:Record<string,number>;candidates:Candidate[];citations:{claim_id:string;version_id:string;locator:string}[]};
type Scope={id:string;kind:'segment'|'theme';name:string;research_available:boolean;direct_30d:number;direct_90d:number;background_90d:number;unknown_date:number;company_mentions_90d:number;routine_90d:number;gaps:string[];technical_reviewed:string|null;technical_gaps:string[];technical_documents:Document[];assessment_candidates:{baseline:string|null;dated_count:number;undated_count:number;samples:{id:number;title:string;published_at:string|null}[]}|null};
type Scopes={as_of:string;counting:string;review_note:string;rows:Scope[]};

const kinds:Record<string,string>={company:'公司',application:'應用',role:'供應角色',product:'產品',concept:'術語',research:'研究頁'};
const gapLabels:Record<string,string>={'not-researched':'未研究','not-public':'未公開','not-obtained':'未取得','not-applicable':'不適用',unclassified:'未分類'};
const reviewLabels:Record<string,string>={pending:'待核對',adopted:'已採納',rejected:'不採納','not-adopted':'不採納'};
const columns:[keyof Counts,string][]=[['not_researched','未研究'],['not_public','未公開'],['not_obtained','未取得'],['not_applicable','不適用'],['unclassified','未分類']];
function day(value:string|null){return value?new Intl.DateTimeFormat('zh-TW',{dateStyle:'short',timeZone:'Asia/Taipei'}).format(new Date(value)):'日期未知'}

export function AdminCoverage({api}:{api:Api}){
  const [view,setView]=useState<'entities'|'scopes'>('entities');const [kind,setKind]=useState('');const [status,setStatus]=useState('');
  const [entities,setEntities]=useState<Entities>();const [scopes,setScopes]=useState<Scopes>();const [error,setError]=useState('');const [loading,setLoading]=useState(false);
  function entityPath(cursor?:string){const query=new URLSearchParams({...(kind?{kind}:{}),...(status?{status}:{}),...(cursor?{cursor}:{})});const encoded=query.toString();return 'coverage/entities'+(encoded?'?'+encoded:'')}
  useEffect(()=>{
    let active=true;setError('');setLoading(true);
    const pending=view==='entities'?api<Entities>(entityPath()).then(data=>{if(active)setEntities(data)}):api<Scopes>('coverage').then(data=>{if(active)setScopes(data)});
    pending.catch(reason=>{if(active)setError(reason.message)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false};
  },[view,kind,status]);
  async function more(){if(!entities?.next_cursor)return;const next=await api<Entities>(entityPath(entities.next_cursor));setEntities({...next,items:[...entities.items,...next.items]})}
  return <><h2>研究覆蓋</h2><p>維護者用來排定研究與核對工作。待核對候選、缺口分類與計數只在這裡呈現，讀者頁只保留影響主張的限制。</p>
    <nav aria-label="覆蓋檢視">{(['entities','scopes'] as const).map(value=><button key={value} aria-pressed={view===value} onClick={()=>setView(value)}>{value==='entities'?'研究缺口':'環節與題材'}</button>)}</nav>
    {error&&<p className="ra-error" role="alert">{error}</p>}{loading&&<p role="status">正在讀取覆蓋資料…</p>}
    {view==='entities'&&entities&&<>
      <div className="ra-table"><table><caption>已發布研究的缺口分類（各類物件合計）</caption><thead><tr><th>類型</th><th>物件</th>{columns.map(([,label])=><th key={label}>{label}</th>)}</tr></thead><tbody>{entities.totals.map(total=><tr key={total.kind}><th>{kinds[total.kind]||total.kind}</th><td>{total.entities}{total.kind==='company'&&<small>（basic {total.basic_companies}）</small>}</td>{columns.map(([field])=><td key={field}>{total[field]}</td>)}</tr>)}</tbody></table></div>
      <p className="ra-note">{entities.counting}</p>
      <div className="ra-toolbar"><label>類型<select value={kind} onChange={event=>setKind(event.target.value)}><option value="">全部</option>{Object.entries(kinds).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label><label>缺口<select value={status} onChange={event=>setStatus(event.target.value)}><option value="">全部</option>{Object.entries(gapLabels).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label></div>
      <div className="ra-table"><table><thead><tr><th>研究物件</th><th>深度／查核</th><th>缺口與理由</th></tr></thead><tbody>{entities.items.map(item=><tr key={item.entity_id}><td><a href={'/next?'+new URLSearchParams({focus:item.entity_id,release_id:entities.release_id})} target="_blank" rel="noreferrer">{item.name}</a><small>{kinds[item.kind]||item.kind}</small></td><td>{item.research_depth==='deep'?'深研':item.kind==='company'?'基本索引':'—'}<small>查核 {item.reviewed||'未提供'}；主張 {item.claims}</small></td><td>{item.implied_not_researched&&!item.gaps.some(gap=>gap.status==='not-researched')&&<p><strong>未研究</strong>　basic 公司尚未深研</p>}{item.gaps.map((gap,index)=><p key={index}><strong>{gapLabels[gap.status||'unclassified']}</strong>　{gap.reason}</p>)}{!item.gaps.length&&!item.implied_not_researched&&'無列出缺口'}</td></tr>)}</tbody></table></div>
      {!entities.items.length&&<p className="ra-note">這個篩選目前沒有研究物件。</p>}
      {entities.has_more&&<button disabled={loading} onClick={()=>void more().catch(reason=>setError(reason.message))}>載入更多研究物件</button>}</>}
    {view==='scopes'&&scopes&&<>
      <p className="ra-note">基準 {day(scopes.as_of)}。{scopes.counting}</p>
      <div className="ra-table"><table><thead><tr><th>環節／題材</th><th>直接事件 30／90 日</th><th>背景 90 日</th><th>未知發布日</th><th>公司提及 90 日</th><th>來源與事件缺口</th></tr></thead><tbody>{scopes.rows.map(row=><tr key={row.kind+row.id}><th>{row.name}<small>{row.kind==='theme'?'題材':'環節'}</small></th><td>{row.direct_30d}／{row.direct_90d}</td><td>{row.background_90d}</td><td>{row.unknown_date}</td><td>{row.company_mentions_90d}<small>例行 {row.routine_90d}</small></td><td>{row.gaps.join('；')||'有近期直接事件'}</td></tr>)}</tbody></table></div>
      <h3>技術文件核對與待納入判讀</h3><p className="ra-note">{scopes.review_note}</p>
      {scopes.rows.filter(row=>row.technical_documents.length||row.assessment_candidates||row.technical_gaps.length).map(row=><details key={row.kind+row.id} className="ra-coverage-scope"><summary>{row.name}：技術查核 {row.technical_reviewed||'未整理'}；待核對文件 {row.technical_documents.reduce((sum,doc)=>sum+(doc.review_counts.pending||0),0)}{row.assessment_candidates&&`；待納入判讀事件 ${row.assessment_candidates.dated_count}（未知日期 ${row.assessment_candidates.undated_count}）`}</summary>
        {row.technical_gaps.length>0&&<p><strong>技術面向缺口</strong>　{row.technical_gaps.join('；')}</p>}
        {row.technical_documents.map(doc=><section key={doc.id}><h4>{doc.title}</h4><p className="ra-note">性質 {doc.doc_kind}；核對 {Object.entries(doc.review_counts).map(([key,count])=>`${reviewLabels[key]||key} ${count}`).join('、')||'尚無紀錄'}</p>
          <ul>{doc.adopted.map(version=><li key={version.version_id}>已核對 {version.label||version.version_id}（查核 {version.reviewed||'未提供'}）：{version.locators.map(locator=>locator.section||locator.id).join('、')}<small>{version.read_scope}</small></li>)}</ul>
          {doc.citations.length>0&&<p>論述定位：{doc.citations.map(citation=>`${citation.claim_id} → ${citation.version_id}／${citation.locator}`).join('；')}</p>}
          {doc.candidates.length>0&&<ul>{doc.candidates.map(candidate=><li key={candidate.observation_id}>{reviewLabels[candidate.status]||candidate.status}：{candidate.official_version||'版本未標示'}（取得 {day(candidate.fetched_at)}）{candidate.reason&&<small>{candidate.reason}</small>}</li>)}</ul>}</section>)}
        {row.assessment_candidates&&<section><h4>查核基準 {row.assessment_candidates.baseline||'未提供'} 之後的直接事件</h4>{row.assessment_candidates.samples.length?<ul>{row.assessment_candidates.samples.map(event=><li key={event.id}><a href={'/events/'+event.id} target="_blank" rel="noreferrer">{event.title}</a><small>{day(event.published_at)}</small></li>)}</ul>:<p className="ra-note">目前沒有基準之後的直接事件。</p>}</section>}
      </details>)}</>}
  </>;
}
