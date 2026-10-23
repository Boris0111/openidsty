'use client';
import {useEffect} from 'react';
import Link from 'next/link';
import {useRouter,useSearchParams} from 'next/navigation';
import {useResearch,ResearchSummary} from '@/lib/research-api';

/** Old ticker URLs open the single new company research page; the legacy company API itself stays available. */
export function CompanyRedirect({ticker}:{ticker:string}){
  const router=useRouter();
  const result=useResearch<ResearchSummary>('/api/v2/resolve?'+new URLSearchParams({kind:'company',key:ticker}));
  const id=result.data?.data.id,release=result.data?.release_id;
  useEffect(()=>{if(id&&release)router.replace('/next?'+new URLSearchParams({focus:id,release_id:release})+window.location.hash)},[id,release,router]);
  if(result.error)return <div className="page-content"><div className="page-heading"><h1>無法開啟這家公司的研究</h1><p role="alert">{result.error}</p></div><p><Link href="/next?view=companies">前往公司索引</Link>，以名稱或代號重新尋找。</p></div>;
  return <div className="page-content"><p role="status">正在開啟公司研究…</p></div>;
}

/** `/companies?ticker=` works in both builds; static files cannot be named after every ticker. */
export function CompanyByTicker(){
  return <CompanyRedirect ticker={useSearchParams().get('ticker')||''}/>;
}
