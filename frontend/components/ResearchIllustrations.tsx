'use client';
import {useState} from 'react';
import type {ResearchDetail} from '@/lib/research-api';

function Illustration({asset,mobile}:{asset:ResearchDetail['assets'][number];mobile?:ResearchDetail['assets'][number]}){
  const [failed,setFailed]=useState(false);
  return <figure className="rs-illustration">{failed?<p role="status">圖解目前無法讀取，可先閱讀下方說明與來源。</p>:<picture>{mobile&&<source media="(max-width:800px)" srcSet={mobile.url}/>}<img src={asset.url} alt={asset.alt} loading="lazy" onError={()=>setFailed(true)}/></picture>}<figcaption>{asset.attribution}</figcaption></figure>;
}
export function ResearchIllustrations({assets}:{assets:ResearchDetail['assets']}){
  return <>{assets.filter(asset=>!asset.id.endsWith('-mobile')||!assets.some(other=>other.id===asset.id.replace(/-mobile$/,'-desktop'))).map(asset=><Illustration key={asset.url} asset={asset} mobile={asset.id.endsWith('-desktop')?assets.find(other=>other.id===asset.id.replace(/-desktop$/,'-mobile')):undefined}/>)}</>;
}
