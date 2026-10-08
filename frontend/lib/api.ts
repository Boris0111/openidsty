'use client';
import {useEffect, useState} from 'react';
export function useApi<T>(path:string) {
  const [revision,setRevision]=useState(0);
  const key=`${path}|${revision}`;
  const [state,setState]=useState<{key:string;data:T|null;error:string;loading:boolean}>({key:'',data:null,error:'',loading:true});
  useEffect(()=>{
    const controller=new AbortController();
    setState({key,data:null,error:'',loading:true});
    fetch(path,{signal:controller.signal,cache:'no-store'}).then(async r=>{
      const body=await r.json();
      if (!r.ok) throw new Error(typeof body.detail==='string'?body.detail:'資料暫時無法取得');
      if(!controller.signal.aborted)setState({key,data:body,error:'',loading:false});
    }).catch(e=>{if(!controller.signal.aborted)setState({key,data:null,error:e.message,loading:false})});
    return ()=>controller.abort();
  },[path,key]);
  return {...(state.key===key?state:{data:null,error:'',loading:true}),retry:()=>setRevision(v=>v+1)};
}
export const companyUrl=(ticker:string)=>`/companies/${encodeURIComponent(ticker)}`;
export const segmentUrl=(id:string,layer:string)=>`/?layer=${layer}&segment=${id}`;
export const themeStatus:Record<string,string>={emerging:'萌芽',validating:'驗證中',scaling:'擴張',mature:'成熟',fading:'降溫'};
export function dateLabel(value:string|null,precision='minute') {
  if(!value)return '尚未更新';
  if(precision==='day')return new Date(value).toLocaleDateString('sv-SE',{timeZone:'Asia/Taipei'});
  return new Date(value).toLocaleString('zh-TW',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',timeZone:'Asia/Taipei'});
}
export function eventDate(event:{published_at:string|null;published_precision:string;reported_at:string|null;activity_at:string|null}) {
  if(event.published_at)return `發布 ${dateLabel(event.published_at,event.published_precision)}`;
  if(event.reported_at)return `出表 ${dateLabel(event.reported_at,'day')}｜發布日未知`;
  if(event.activity_at)return `活動 ${dateLabel(event.activity_at,'day')}｜發布日未知`;
  return '發布日未知';
}
export const basisLabel:Record<string,string>={monthly:'單月',quarterly:'單季',ytd:'年度累計',annual:'全年'};
