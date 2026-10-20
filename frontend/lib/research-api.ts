'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {acquireResearch,dynamicResearch,peekResearch,researchKey} from './research-cache';

export type ResearchEnvelope<T>={release_id:string;schema_version:string;data:T};
export type ResearchSummary={id:string;kind:string;name:string;summary:string;reviewed:string|null};
export type ResearchDocument={document_id:string;revision_id:string;title:string;url:string;document_kind?:string;published?:string|null;reviewed?:string|null;scope?:string|null;read_scope?:string|null;access_limitations?:string|null;locators?:{id?:string;section?:string;page?:string|number;excerpt?:string}[]};
export type ResearchCitation=ResearchDocument&{locator:string;applicable_period:string;stance?:string};
export type ResearchClaim={id:string;statement:string;confidence:string;conditions:string[];reviewed:string;evidence:ResearchCitation[]};
export type ResearchTrailItem={id:string;kind:string;name:string;url:string|null};
export type ResearchAsset={id:string;url:string;alt:string;attribution:string};
export type ChainProduct={id:string;name:string;summary?:string;companies:{id:string;name:string}[]};
/** An application read as a supply chain (only on application pages). */
export type ResearchChain={question:string|null;steps:{label:string;note:string|null;products:ChainProduct[]}[];other_products:ChainProduct[];
  diagram:{concept:{id:string;name:string};assets:ResearchAsset[]}|null};
/** Where a product, role, concept or company sits in each supply chain above it. */
export type ChainMembership={id:string;name:string;question:string|null;steps:{label:string;here:boolean}[];products:{id:string;name:string}[]};
export type ChainIndexItem={id:string;name:string;summary:string;question:string|null;segments:{id:string;name:string}[];steps:string[];assets:ResearchAsset[]};
export type ResearchDetail=ResearchSummary&{markdown:string;legacy_return?:{url:string;label:string}|null;trail?:ResearchTrailItem[];
  chain?:ResearchChain|null;chains?:ChainMembership[];content:{question?:string;definition?:string;purpose?:string;scope?:string;boundary?:string;adoption_conditions?:string[];bottlenecks?:string[];substitution_limits?:string[];comparisons?:{left:string;right:string;conditions:string[];limitations:string[]}[];related_ids?:string[];gaps?:string[];roles?:{segment_id:string;description:string}[];listings?:{ticker:string;market:string}[]};claims:ResearchClaim[];related:ResearchSummary[];assets:{id:string;url:string;alt:string;attribution:string}[];truncated:boolean};
export type ResearchGraph={root:string;nodes:ResearchSummary[];edges:{id:string;source:string;target:string;kind:string;mechanism:string;conditions:string[];claims:{entity_id:string;claim_id:string}[];evidence_url?:string}[];truncated:boolean;continue_from:string[]};
export type ResearchPage={items:ResearchSummary[];has_more:boolean;next_cursor:string|null};

export function useResearch<T>(path:string|null) {
  const key=path?researchKey(path):null;
  const [sequence,setSequence]=useState(0),force=useRef<string|null>(null);
  const [state,setState]=useState<{key:string|null;data?:ResearchEnvelope<T>;error?:string;refreshError?:string;loading:boolean;refreshing?:boolean;expires?:number}>({key:null,loading:false});
  const refresh=useCallback(()=>{force.current=key;setSequence(value=>value+1)},[key]);
  useEffect(()=>{
    if(!key)return;
    let active=true;
    const cached=peekResearch(key)?.payload as ResearchEnvelope<T>|undefined;
    setState(previous=>{const data=previous.key===key?previous.data||cached:cached;return {key,data,loading:!data,refreshing:Boolean(data)}});
    const forced=force.current===key;force.current=null;
    let handle:ReturnType<typeof acquireResearch>|undefined;
    try{
      handle=acquireResearch(key,forced);
      handle.promise.then(entry=>{if(active)setState({key,data:entry.payload as ResearchEnvelope<T>,loading:false,refreshing:false,expires:entry.ttl?entry.expires:Date.now()+30000})})
        .catch(error=>{if(active){const message=error instanceof Error&&error.message&&!/fetch|JSON|Unexpected|AbortError/i.test(error.message)?error.message:'目前無法更新資料，請稍後重試。';setState(previous=>({...previous,loading:false,refreshing:false,expires:Date.now()+30000,...(previous.data?{refreshError:message}:{error:message})}))}});
    }catch{setState(previous=>({...previous,loading:false,refreshing:false,...(previous.data?{refreshError:'目前無法更新資料，請稍後重試。'}:{error:'目前無法讀取資料，請稍後重試。'})}))}
    return()=>{active=false;handle?.release()};
  },[key,sequence]);
  useEffect(()=>{
    if(!key)return;
    const visible=()=>{if(document.visibilityState==='visible')setSequence(value=>value+1)};
    window.addEventListener('research:refresh',refresh);
    window.addEventListener('focus',visible);document.addEventListener('visibilitychange',visible);
    return()=>{window.removeEventListener('research:refresh',refresh);window.removeEventListener('focus',visible);document.removeEventListener('visibilitychange',visible)};
  },[key,refresh]);
  useEffect(()=>{
    if(!key||!dynamicResearch(key)||!state.expires||state.refreshing||document.visibilityState!=='visible')return;
    const timer=setTimeout(()=>{if(document.visibilityState==='visible')setSequence(value=>value+1)},Math.max(50,state.expires-Date.now()+25));
    return()=>clearTimeout(timer);
  },[key,state.expires,state.refreshing]);
  return {...(state.key===key?state:{key,loading:Boolean(key),data:undefined,error:undefined,refreshError:undefined,refreshing:false}),refresh};
}
