'use client';
import {useState} from 'react';
import type {TechnicalProfile} from '@/lib/types';
import {confidenceLabel} from '@/lib/display';
import {TechnicalEvidence} from './Relations';

function TechnicalClaim({claim}:{claim:TechnicalProfile['claims'][number]}){
  const [open,setOpen]=useState(false);
  return <article className="technical-claim"><p>{claim.statement}</p><span className={`confidence ${claim.confidence}`}>{confidenceLabel[claim.confidence]}</span>
    {claim.evidence.length>0&&<details open={open} onToggle={e=>setOpen(e.currentTarget.open)}><summary>查看這項說明的來源</summary>{open&&<TechnicalEvidence items={claim.evidence}/>}</details>}
  </article>;
}

export function TechnicalResearch({profile}:{profile?:TechnicalProfile}){
  if(!profile)return null;
  const facets=[
    ['adoption-conditions','導入前要滿足什麼條件？'],
    ['bottlenecks','什麼會卡住交付？'],
    ['substitution-limits','哪些方案不能直接替換？'],
  ] as const;
  return <section className="technical-research" aria-label="技術研究">
    <h2>導入條件與限制</h2><p>{profile['product-boundary']}</p>
    {facets.map(([key,label])=>profile[key].length>0&&<section key={key}><h3>{label}</h3><ul>{profile[key].map(value=><li key={value}>{value}</li>)}</ul></section>)}
    {profile.claims.length>0&&<section><h3>這些說明的依據</h3>{profile.claims.map(claim=><TechnicalClaim key={claim.id} claim={claim}/>)}</section>}
    {profile['evidence-gaps'].length>0&&<section><h3>目前還不能確認什麼？</h3><ul>{profile['evidence-gaps'].map(value=><li key={value}>{value}</li>)}</ul></section>}
    <p className="data-note">技術內容查核 {profile.reviewed}</p>
  </section>;
}
