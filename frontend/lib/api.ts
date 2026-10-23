'use client';
import {useEffect,useState,useRef} from 'react';
import {subscribeRequest,requestKey,empty,type Snapshot} from './request-cache';
import {PUBLIC_SNAPSHOT} from './public-snapshot';
export function useApi<T>(path:string|null){
  const subscriptionRef=useRef<ReturnType<typeof subscribeRequest>|null>(null);
  const key=path?requestKey(path):'';const [state,setState]=useState<{key:string;value:Snapshot}>({key:'',value:empty});
  useEffect(()=>{
    if(!key)return;
    const subscription=subscribeRequest(key,value=>setState({key,value}));
    subscriptionRef.current=subscription;return ()=>{subscription.unsubscribe();if(subscriptionRef.current===subscription)subscriptionRef.current=null;};
  },[key]);
  const value=state.key===key?state.value:empty;
  return {data:value.data as T|null,error:value.error,loading:key?value.loading:false,retry:()=>subscriptionRef.current?.retry()};
}
// Static files cannot be named after tickers such as PRIVATE:shinko, so the public snapshot uses the query form.
export const companyUrl=(ticker:string)=>PUBLIC_SNAPSHOT?'/companies?'+new URLSearchParams({ticker}):`/companies/${encodeURIComponent(ticker)}`;
export const segmentUrl=(id:string,layer:string)=>`/?layer=${layer}&segment=${id}`;
export {lifecycleLabel as themeStatus} from './display';
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
