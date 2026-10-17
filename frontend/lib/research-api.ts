'use client';
import {useEffect,useState} from 'react';

export type ResearchEnvelope<T>={release_id:string;schema_version:string;data:T};
export type ResearchSummary={id:string;kind:string;name:string;summary:string;reviewed:string|null};
export type ResearchDocument={document_id:string;revision_id:string;title:string;url:string;document_kind?:string;published?:string|null;reviewed?:string|null;scope?:string|null;read_scope?:string|null;access_limitations?:string|null;locators?:{id?:string;section?:string;page?:string|number;excerpt?:string}[]};
export type ResearchCitation=ResearchDocument&{locator:string;applicable_period:string;stance?:string};
export type ResearchClaim={id:string;statement:string;confidence:string;conditions:string[];reviewed:string;evidence:ResearchCitation[]};
export type ResearchDetail=ResearchSummary&{markdown:string;legacy_return?:{url:string;label:string}|null;content:{definition?:string;purpose?:string;scope?:string;boundary?:string;adoption_conditions?:string[];bottlenecks?:string[];substitution_limits?:string[];comparisons?:{left:string;right:string;conditions:string[];limitations:string[]}[];related_ids?:string[];gaps?:string[];roles?:{segment_id:string;description:string}[];listings?:{ticker:string;market:string}[]};claims:ResearchClaim[];related:ResearchSummary[];assets:{id:string;url:string;alt:string;attribution:string}[];truncated:boolean};
export type ResearchGraph={root:string;nodes:ResearchSummary[];edges:{id:string;source:string;target:string;kind:string;mechanism:string;conditions:string[];claims:{entity_id:string;claim_id:string}[];evidence_url?:string}[];truncated:boolean;continue_from:string[]};
export type ResearchPage={items:ResearchSummary[];has_more:boolean;next_cursor:string|null};

export function useResearch<T>(path:string|null) {
  const [state,setState]=useState<{key:string|null;data?:ResearchEnvelope<T>;error?:string;loading:boolean}>({key:null,loading:false});
  useEffect(()=>{
    if(!path) return;
    const controller=new AbortController();
    setState({key:path,loading:true});
    fetch(path,{signal:controller.signal,cache:'no-store'}).then(async response=>{
      const payload=await response.json();
      if(!response.ok) throw new Error(payload.message||'研究目前無法讀取，請稍後重試。');
      if(!controller.signal.aborted) setState({key:path,data:payload,loading:false});
    }).catch(error=>{if(!controller.signal.aborted)setState({key:path,error:error.message,loading:false})});
    return ()=>controller.abort();
  },[path]);
  return state.key===path?state:{key:path,loading:Boolean(path),data:undefined,error:undefined};
}
