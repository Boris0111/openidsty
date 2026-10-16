'use client';
import type {ReactNode} from 'react';
import Link from 'next/link';
import Markdown from 'react-markdown';
import type {ResearchClaim,ResearchDetail,ResearchSummary} from '@/lib/research-api';

const kindNames:Record<string,string>={company:'公司',product:'產品',segment:'環節',theme:'題材',role:'供應角色',concept:'術語',application:'應用',research:'研究'};
const confidenceNames:Record<string,string>={'well-supported':'有明確證據支持',inference:'有條件推論','needs-verification':'仍待核實'};

function SourceClaims({claims}:{claims:ResearchClaim[]}) {
  if(!claims.length)return null;
  return <section className="rs-claims" aria-label="判斷與來源"><h3>這個判斷的依據</h3>{claims.map(claim=><article key={claim.id}>
    <span className="rs-confidence" data-confidence={claim.confidence}>{confidenceNames[claim.confidence]||'仍待核實'}</span><p>{claim.statement}</p>
    {claim.conditions.map(condition=><p className="rs-condition" key={condition}>{condition}</p>)}
    {claim.evidence.map((source,index)=><div className="rs-citation" key={source.revision_id+index}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><span>{source.applicable_period}</span></div>)}
  </article>)}</section>;
}

export function ResearchDetailContent({item,href,companies=[],products=[],onSelect}:{item:ResearchDetail;href:(id:string)=>string;companies?:ResearchSummary[];products?:ResearchSummary[];onSelect?:(id:string)=>void}) {
  function Internal({id,children}:{id:string;children:ReactNode}) {
    return onSelect?<button type="button" onClick={()=>onSelect?.(id)}>{children}</button>:<Link href={href(id)}>{children}</Link>;
  }
  const prose=<Markdown skipHtml components={{...(item.kind==='company'?{h2:({children}:{children?:ReactNode})=><h3>{children}</h3>,h3:({children}:{children?:ReactNode})=><h4>{children}</h4>}:{}),a:({href:destination,children})=>destination?.startsWith('/next?focus=')?<Internal id={new URLSearchParams(destination.split('?')[1]).get('focus')||item.id}>{children}</Internal>:<a href={destination} target="_blank" rel="noreferrer">{children}</a>}}>{item.markdown}</Markdown>;
  return <><div className="rs-detail-top"><span>{kindNames[item.kind]}</span>{item.reviewed&&<span>內容查核 {item.reviewed}</span>}</div><h2>{item.name}</h2><p className="rs-summary">{item.summary}</p>
    {item.content.listings&&item.content.listings.length>0&&<p className="rs-listings">{item.content.listings.map(listing=><span key={listing.ticker}>{({TW:'台灣',US:'美國'} as Record<string,string>)[listing.market]||listing.market}　{listing.ticker}</span>)}</p>}
    {item.content.boundary&&<section className="rs-boundary"><h3>交付邊界</h3><p>{item.content.boundary}</p></section>}
    {item.kind==='company'&&<div className="rs-prose">{prose}</div>}
    {item.content.adoption_conditions&&<section className="rs-conditions"><h3>採用前要核對</h3><ul>{[...item.content.adoption_conditions,...(item.content.bottlenecks||[])].map(condition=><li key={condition}>{condition}</li>)}</ul></section>}
    {item.content.substitution_limits&&<section><h3>替代與比較限制</h3><ul>{item.content.substitution_limits.map(condition=><li key={condition}>{condition}</li>)}</ul></section>}
    {companies.length>0&&<section className="rs-company-links"><h3>本輪有產品證據的公司</h3>{companies.map(company=><Internal key={company.id} id={company.id}><strong>{company.name}</strong><span>閱讀產品範圍與證據</span></Internal>)}</section>}
    {products.length>0&&<section className="rs-company-links"><h3>已核對的產品角色</h3>{products.map(product=><Internal key={product.id} id={product.id}><strong>{product.name}</strong><span>{product.summary}</span></Internal>)}</section>}
    <SourceClaims claims={item.claims}/>
    {item.content.gaps?.length?<section className="rs-gaps"><h3>判斷到哪裡為止</h3>{item.content.gaps.map(gap=><p key={gap}>{gap}</p>)}</section>:null}
    {item.kind!=='company'&&item.kind!=='product'&&<div className="rs-prose">{prose}</div>}
    {item.truncated&&<p>部分關聯超過單次顯示範圍，可透過目錄繼續閱讀。</p>}
  </>;
}
