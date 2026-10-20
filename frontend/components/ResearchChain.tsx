'use client';
import Link from 'next/link';
import {useResearch,ChainIndexItem,ChainMembership,ChainProduct,ResearchChain} from '@/lib/research-api';
import {ResearchIllustrations} from './ResearchIllustrations';

// Every application is read with the same layout the liquid-cooling flow introduced: question, picture or steps,
// products by step with their evidenced companies, then the remaining products of the chain.

function ProductCard({product,href}:{product:ChainProduct;href:(id:string)=>string}){
  return <Link className="rs-chain-product" href={href(product.id)}><strong>{product.name}</strong>
    <span>{product.companies.length?'有產品證據：'+product.companies.map(company=>company.name).join('、'):'尚未核對公司的產品證據'}</span></Link>;
}

export function ChainSteps({steps,label}:{steps:{label:string;note?:string|null;here?:boolean}[];label:string}){
  return <ol className="rs-chain-steps" aria-label={label}>{steps.map((step,index)=><li key={index} aria-current={step.here?'step':undefined}>
    <strong>{step.label}</strong>{step.note&&<span>{step.note}</span>}</li>)}</ol>;
}

export function ResearchChainView({chain,href}:{chain:ResearchChain;href:(id:string)=>string}){
  return <section className="rs-chain" aria-label="供應鏈圖解與產品">
    <div className={chain.diagram?'rs-chain-top':'rs-chain-top rs-chain-text'}>
      {chain.diagram&&<div className="rs-chain-diagram"><ResearchIllustrations assets={chain.diagram.assets}/>
        <p className="rs-scope-note">功能示意。公司間的具名交易需另有來源，不能由流程相接推定。<Link href={href(chain.diagram.concept.id)}>讀懂{chain.diagram.concept.name}</Link></p></div>}
      <div>{!chain.diagram&&<p className="rs-scope-note">這條供應鏈尚無圖解，先以文字步驟說明交付順序。</p>}
        {chain.steps.length>0&&<ChainSteps steps={chain.steps} label="供應鏈步驟"/>}</div>
    </div>
    <div className="rs-chain-products">{chain.steps.filter(step=>step.products.length).map(step=><div key={step.label} className="rs-chain-step">
      <h3>{step.label}</h3>{step.products.map(product=><ProductCard key={product.id} product={product} href={href}/>)}</div>)}</div>
    {chain.other_products.length>0&&<div className="rs-chain-step rs-chain-other"><h3>這條供應鏈的其他產品</h3>
      {chain.other_products.map(product=><ProductCard key={product.id} product={product} href={href}/>)}</div>}
  </section>;
}

export function ResearchChainStrip({chains,href}:{chains:ChainMembership[];href:(id:string)=>string}){
  const [chain,...others]=chains;
  if(!chain)return null;
  return <aside className="rs-chain-strip" aria-label="所在供應鏈">
    <p><Link href={href(chain.id)}>{chain.name}</Link>{chain.question&&<span>{chain.question}</span>}</p>
    {chain.steps.length>0&&<ChainSteps steps={chain.steps} label={chain.name+'的步驟'}/>}
    <Link className="rs-chain-strip-full" href={href(chain.id)}>看完整圖解與產品</Link>
    {others.length>0&&<p className="rs-chain-also">也屬於：{others.map((other,index)=><span key={other.id}>{index>0&&'、'}<Link href={href(other.id)}>{other.name}</Link></span>)}</p>}
  </aside>;
}

export function ResearchCompanyChains({chains,href}:{chains:ChainMembership[];href:(id:string)=>string}){
  if(!chains.length)return null;
  return <section className="rs-company-chains" aria-label="所屬供應鏈與產品"><h2>所屬供應鏈與產品</h2><ul>{chains.map(chain=><li key={chain.id}>
    <Link href={href(chain.id)}>{chain.name}</Link>
    <span>{chain.products.length?'有產品證據：'+chain.products.map(product=>product.name).join('、'):'依既有環節角色列入，尚未核對產品證據'}</span>
  </li>)}</ul></section>;
}

export function ResearchChainIndex({release,href}:{release:string;href:(id:string)=>string}){
  const result=useResearch<{items:ChainIndexItem[]}>(`/api/v2/chains?release_id=${release}`);
  if(result.error)return <p role="alert">{result.error}</p>;
  const items=result.data?.data.items;
  if(!items)return <p role="status">正在讀取供應鏈…</p>;
  // One grid keeps chains of the same segment next to each other without one-card rows.
  const sorted=[...items].sort((a,b)=>(a.segments[0]?.name||'').localeCompare(b.segments[0]?.name||'','zh-Hant'));
  return <div className="rs-chain-cards rs-chain-index">{sorted.map(chain=><ChainCard key={chain.id} chain={chain} href={href(chain.id)}/>)}</div>;
}

export function ChainCard({chain,href}:{chain:ChainIndexItem;href:string}){
  const picture=chain.assets.find(asset=>asset.id.endsWith('-desktop'))||chain.assets[0];
  return <Link className="rs-chain-card" href={href}>
    {picture?<img src={picture.url} alt="" loading="lazy"/>:<span className="rs-chain-card-steps" aria-hidden="true">{chain.steps.join(' → ')}</span>}
    <small>{chain.segments.map(segment=>segment.name).join('、')}</small><strong>{chain.name}</strong><span>{chain.question||chain.summary}</span>
  </Link>;
}
