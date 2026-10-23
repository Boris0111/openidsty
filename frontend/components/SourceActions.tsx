'use client';
import {useEffect,useState} from 'react';
type Api=<T>(path:string,method?:string,data?:unknown)=>Promise<T>;
type Job={job_id:string;status:string;available_at:string;requests:number;failure?:{message:string}|null};
type Detail={name:string;declared:{can_refresh:boolean;frequency_hours:number;history_limit:string;classification_limit:string};last_job:Job|null;last_result:Record<string,unknown>|null};
const statuses:Record<string,string>={queued:'等待背景服務',running:'正在擷取與核對',deferred:'依提供者要求稍後再試',success:'本輪已完成',partial:'已取得部分內容，仍有缺口',failed:'本輪未完成，既有資料保留'};

export function SourceActions({source,api,busy,action,onDone}:{source:{id:string;name:string;adapter?:string};api:Api;busy:boolean;action:(operation:()=>Promise<void>)=>Promise<void>;onDone:()=>Promise<void>}){
  const [job,setJob]=useState<Job>();const [detail,setDetail]=useState<Detail>();const [open,setOpen]=useState(false);const [error,setError]=useState('');
  const endpoint='sources/'+encodeURIComponent(source.id);
  function perform(operation:()=>Promise<void>){return action(async()=>{setError('');try{await operation()}catch(reason){setError(reason instanceof Error?reason.message:'來源操作未完成。')}})}
  async function read(){const result=await api<Detail>(endpoint);setDetail(result);if(result.last_job)setJob(result.last_job);setOpen(true)}
  useEffect(()=>{
    if(!job||!['queued','running','deferred'].includes(job.status))return;
    let active=true;const timer=setInterval(()=>{api<Job>('source-jobs/'+job.job_id).then(async result=>{if(!active)return;setJob(result);if(!['queued','running','deferred'].includes(result.status))await onDone()}).catch(reason=>{if(active)setError(reason.message)})},job.status==='deferred'?30000:5000);
    return()=>{active=false;clearInterval(timer)};
  },[job?.job_id,job?.status]);
  return <div className="ra-source-actions"><div className="ra-toolbar"><button disabled={busy||source.adapter==='manual'||!!job&&['queued','running','deferred'].includes(job.status)} onClick={()=>void perform(async()=>setJob(await api<Job>(endpoint+'/refresh','POST')))}>更新一次</button><button disabled={busy} onClick={()=>open?setOpen(false):void perform(read)}>{open?'收起來源能力':'來源能力'}</button></div>
    {error&&<p className="ra-error" role="alert">{error}</p>}
    {job&&<p aria-live="polite">{statuses[job.status]||'來源更新狀態已保存'}{job.status==='deferred'?'；最早 '+new Intl.DateTimeFormat('zh-TW',{dateStyle:'short',timeStyle:'short',timeZone:'Asia/Taipei'}).format(new Date(job.available_at)):''}{job.failure?'；'+job.failure.message:''}</p>}
    {open&&detail&&<section aria-label={source.name+'來源能力'}><p>宣告更新節奏：每 {detail.declared.frequency_hours} 小時。能力宣告與實際取得分開核對。</p><p>{detail.declared.history_limit}</p><p>{detail.declared.classification_limit}</p><button disabled={busy} onClick={()=>void perform(read)}>重新讀取能力與結果</button></section>}
  </div>;
}
