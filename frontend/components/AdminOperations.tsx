'use client';
import {useEffect,useRef,useState} from 'react';
import {FinancialImports} from './FinancialImports';

type Api=<T>(path:string,method?:string,data?:unknown,revision?:number,idempotencyKey?:string,rawType?:string)=>Promise<T>;
type Job={job_id:string;status:string;stage:string;target_release_id?:string;failure?:{message:string;retryable:boolean}};
type Release={release_id:string;git_commit:string;published_at:string;reason:string};
type Releases={items:Release[];active_release_id:string;has_more:boolean;next_cursor:string|null};
type Source={id:string;name:string;url:string;status:string;last_attempt:string|null;last_success:string|null;error:string|null};
type Audit={audit_id:number;operation:string;recorded_at:string;detail:{reason?:string;git_commit?:string}};
type Page<T>={items:T[];has_more:boolean;next_cursor:string|number|null};
const statuses:Record<string,string>={queued:'等待背景處理',preparing:'準備研究與圖解',ready:'候選版本已備妥',published:'已完成',failed:'本次尚未完成'};
const stages:Record<string,string>={queued:'等待派送',git:'內容版本已保存',assets:'圖解已核對',projection:'候選資料已建立',complete:'正式版本已確認'};
function date(value:string|null){return value?new Intl.DateTimeFormat('zh-TW',{dateStyle:'short',timeStyle:'short',timeZone:'Asia/Taipei'}).format(new Date(value)):'尚無成功紀錄'}

export function AdminOperations({draft,dirty,busy,api,action}:{draft?:{draft_id:string;base_release_id:string;revision:number};dirty:boolean;busy:boolean;api:Api;action:(operation:()=>Promise<void>)=>Promise<void>}){
  const [tab,setTab]=useState<'publish'|'sources'|'history'|'financial'>('publish');const [reason,setReason]=useState('');
  const [job,setJob]=useState<Job>();const [releases,setReleases]=useState<Releases>();const [target,setTarget]=useState('');
  const [sources,setSources]=useState<Page<Source>>();const [audit,setAudit]=useState<Page<Audit>>();const [error,setError]=useState('');
  const keys=useRef(new Map<string,string>());
  function key(payload:unknown){const identity=JSON.stringify(payload);if(!keys.current.has(identity))keys.current.set(identity,crypto.randomUUID());return keys.current.get(identity)!}
  useEffect(()=>{
    let active=true;setError('');setTarget('');
    if(tab==='financial')return;
    const pending=tab==='sources'?api<Page<Source>>('sources').then(data=>{if(active)setSources(data)}):tab==='history'?api<Page<Audit>>('audit').then(data=>{if(active)setAudit(data)}):api<Releases>('releases').then(data=>{if(active)setReleases(data)});
    pending.catch(reason=>{if(active)setError(reason.message)});return()=>{active=false};
  },[tab,job?.status==='published'?job.job_id:null]);
  useEffect(()=>{
    if(!job||!['queued','preparing','ready'].includes(job.status))return;
    let active=true;const timer=setInterval(()=>{api<Job>('jobs/'+job.job_id).then(data=>{if(active){setJob(data);setError('')}}).catch(reason=>{if(active)setError(reason.message)})},3000);
    return()=>{active=false;clearInterval(timer)};
  },[job?.job_id,job?.status]);
  async function publish(){if(!draft)return;const payload={base_release_id:draft.base_release_id,revision:draft.revision,reason:reason.trim()};setJob(await api<Job>('drafts/'+draft.draft_id+'/publish','POST',payload,undefined,key({draft:draft.draft_id,...payload})))}
  async function restore(){if(!releases||!target)return;const payload={base_release_id:releases.active_release_id,reason:reason.trim()};setJob(await api<Job>('releases/'+target+'/restore','POST',payload,undefined,key({target,...payload})))}
  return <section className="ra-operations" aria-label="發布與維護"><nav aria-label="維護工作">{(['publish','sources','financial','history'] as const).map(value=><button key={value} aria-pressed={tab===value} onClick={()=>setTab(value)}>{({publish:'發布與還原',sources:'來源健康',financial:'財務補錄',history:'操作紀錄'})[value]}</button>)}</nav>
    {error&&<p className="ra-error" role="alert">{error}</p>}
    {tab==='financial'&&<FinancialImports api={api} busy={busy} action={action}/>}
    {tab==='publish'&&<><h2>發布與還原</h2><p>發布會核對完整研究後才切換版本。儲存草稿不會改變正式內容。</p><label>這次操作的理由<textarea rows={3} value={reason} maxLength={2000} onChange={event=>setReason(event.target.value)}/></label><div className="ra-toolbar"><button className="ra-primary" disabled={busy||dirty||!draft||!reason.trim()} onClick={()=>void action(publish)}>發布已儲存修訂{draft?' '+draft.revision:''}</button>{draft&&<span>依據草稿的正式基準發布；基準過期會拒絕覆寫。</span>}</div>
      {job&&<div className="ra-job" aria-live="polite"><h3>{statuses[job.status]||job.status}</h3><p>{stages[job.stage]||'背景作業處理中'}</p><p>作業 {job.job_id}</p>{job.failure&&<p>{job.failure.message}</p>}<div className="ra-toolbar"><button disabled={busy} onClick={()=>void action(async()=>setJob(await api<Job>('jobs/'+job.job_id)))}>重新查詢作業</button>{job.status==='failed'&&job.failure?.retryable&&<button disabled={busy} onClick={()=>void action(async()=>setJob(await api<Job>('jobs/'+job.job_id+'/retry','POST')))}>重試原作業</button>}{job.status==='published'&&job.target_release_id&&<a href={'/next?release_id='+encodeURIComponent(job.target_release_id)} target="_blank" rel="noreferrer">開啟這份已發布研究</a>}</div></div>}
      <details className="ra-restore"><summary>還原先前完整版本</summary><p>只切換研究內容；動態財務與事件歷史會保留。使用上方理由記錄這次還原。</p><label>選擇曾發布版本<select value={target} onChange={event=>setTarget(event.target.value)}><option value="">請選擇</option>{releases?.items.filter(item=>item.release_id!==releases.active_release_id).map(item=><option key={item.release_id} value={item.release_id}>{date(item.published_at)} · {item.reason.slice(0,70)}</option>)}</select></label><div className="ra-toolbar"><button disabled={busy||!target||!reason.trim()} onClick={()=>void action(restore)}>還原已選版本</button><button disabled={busy} onClick={()=>void action(async()=>{setReleases(await api<Releases>('releases'));setTarget('')})}>重新讀取正式版本</button>{releases?.has_more&&<button disabled={busy} onClick={()=>void action(async()=>{const next=await api<Releases>('releases?cursor='+encodeURIComponent(releases.next_cursor!));setReleases({...next,items:[...releases.items,...next.items]})})}>載入更早版本</button>}</div></details></>}
    {tab==='sources'&&<><h2>來源健康</h2><p>抓取失敗不會刪除已發布研究；這裡的成功時間是來源擷取時間。</p><div className="ra-table"><table><thead><tr><th>來源</th><th>最近成功（台北）</th><th>擷取狀態</th><th>診斷</th></tr></thead><tbody>{sources?.items.map(source=><tr key={source.id}><td><a href={source.url} target="_blank" rel="noreferrer">{source.name}</a></td><td>{date(source.last_success)}</td><td>{({ok:'已取得',success:'已取得',not_run:'尚未執行',failed:'擷取失敗',error:'擷取失敗',skipped:'本輪略過'} as Record<string,string>)[source.status]||source.status}</td><td>{source.error?<details><summary>查看原因</summary><p>{source.error}</p></details>:'無錯誤紀錄'}</td></tr>)}</tbody></table></div>{sources?.has_more&&<button disabled={busy} onClick={()=>void action(async()=>{const next=await api<Page<Source>>('sources?cursor='+encodeURIComponent(String(sources.next_cursor)));setSources({...next,items:[...sources.items,...next.items]})})}>載入更多來源</button>}</>}
    {tab==='history'&&<><h2>操作紀錄</h2><div className="ra-table"><table><thead><tr><th>時間（台北）</th><th>操作</th><th>理由／結果</th></tr></thead><tbody>{audit?.items.map(item=><tr key={item.audit_id}><td>{date(item.recorded_at)}</td><td>{({publish:'發布研究',restore:'還原研究',login:'登入',logout:'登出','draft-save':'儲存草稿','owner-setup':'設定維護者','owner-reset':'重設維護者'} as Record<string,string>)[item.operation]||item.operation}</td><td>{item.detail.reason||'已記錄'}{item.detail.git_commit&&<code> {item.detail.git_commit.slice(0,12)}</code>}</td></tr>)}</tbody></table></div>{audit?.has_more&&<button disabled={busy} onClick={()=>void action(async()=>{const next=await api<Page<Audit>>('audit?cursor='+audit.next_cursor);setAudit({...next,items:[...audit.items,...next.items]})})}>載入較早紀錄</button>}</>}
  </section>;
}
