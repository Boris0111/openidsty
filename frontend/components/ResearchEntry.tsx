'use client';
import Link from 'next/link';
import {useSearchParams} from 'next/navigation';
import {useResearch,ResearchSummary} from '@/lib/research-api';
import {mapReturn} from '@/lib/research-navigation';

/** Legacy pages remain usable when v2 has not yet been initialized. */
export function ResearchEntry({kind,identity}:{kind:'segment'|'company';identity:string}){
  const params=useSearchParams();
  const result=useResearch<ResearchSummary>('/api/v2/resolve?'+new URLSearchParams({kind,key:identity}));
  if(!result.data)return null;
  const from=kind==='segment'?mapReturn('/?'+params):undefined;
  return <p><Link href={'/next?'+new URLSearchParams({focus:result.data.data.id,release_id:result.data.release_id,...(from?{from}:{})})}>閱讀{kind==='segment'?'產品與公司研究':'完整公司研究'}</Link></p>;
}
