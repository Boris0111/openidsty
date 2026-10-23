'use client';
import {ResearchReadStatus} from './ResearchReadStatus';
import {useState,useEffect} from 'react';
import Link from 'next/link';
import {useRouter,useSearchParams} from 'next/navigation';
import Markdown from 'react-markdown';
import {useResearch,ResearchPage,ResearchSummary,ResearchClaim} from '@/lib/research-api';

type ComparePage={companies:(ResearchSummary&{roles:{segment_id:string;description:string}[];products:{product_id:string;name:string;role_name:string;conditions:string[]}[];risks:string|null;business_model:string|null;claims:ResearchClaim[];gaps:string[];truncated:boolean})[]};

export function ResearchCompare({release,href}:{release:string;href:(id:string)=>string}){
  const params=useSearchParams(),router=useRouter();
  const ids=(params.get('company_ids')||'').split(',').filter(Boolean);
  const [query,setQuery]=useState(''),[debounced,setDebounced]=useState('');
  useEffect(()=>{const timer=setTimeout(()=>setDebounced(query),200);return()=>clearTimeout(timer)},[query]);
  const options=useResearch<ResearchPage>(debounced.trim()?'/api/v2/search?'+new URLSearchParams({q:debounced,kind:'company',release_id:release,limit:'20'}):null);
  const valid=ids.length>=2&&ids.length<=4&&new Set(ids).size===ids.length;
  const result=useResearch<ComparePage>(valid?'/api/v2/compare?'+new URLSearchParams({company_ids:ids.join(','),release_id:release}):null);
  const single=useResearch<ResearchSummary>(ids.length===1?`/api/v2/companies/${encodeURIComponent(ids[0])}?release_id=${release}`:null);
  const [picked,setPicked]=useState<Record<string,string>>({});
  const names={...picked,...(single.data?{[single.data.data.id]:single.data.data.name}:{}),...Object.fromEntries(result.data?.data.companies.map(row=>[row.id,row.name])||[])};
  function update(changes:Record<string,string>){const next=new URLSearchParams(params);next.delete('basis');for(const [key,value] of Object.entries(changes))if(value)next.set(key,value);else next.delete(key);router.push('/next?'+next,{scroll:false})}
  return <section className="rf-compare" aria-label="公司比較"><ResearchReadStatus state={result}/><p>選擇 2–4 家公司，並列比較業務、供應角色、產品與風險。</p><div className="rf-filters"><label>搜尋加入比較的公司<input value={query} onChange={event=>setQuery(event.target.value)} placeholder="中文名稱或代號" maxLength={100}/></label></div>
    {query&&<div className="rf-compare-options" aria-label="可加入比較的公司">{options.error?<p role="alert">{options.error}</p>:query!==debounced||options.loading?<p role="status">正在搜尋公司…</p>:options.data?.data.items.length?options.data.data.items.map(row=><button key={row.id} disabled={ids.includes(row.id)||ids.length>=4} onClick={()=>{setPicked(previous=>({...previous,[row.id]:row.name}));update({company_ids:[...ids,row.id].join(',')});setQuery('')}}>加入{row.name}</button>):<p>沒有找到公司，請試名稱或完整代號。</p>}{options.data?.data.has_more&&<p>仍有更多結果，請輸入較完整的公司名稱。</p>}</div>}
    <ul className="rf-compare-selected" aria-label="已選公司">{ids.map((id,index)=><li key={id+index}><span>{names[id]||'已選公司 '+(index+1)}</span><button onClick={()=>update({company_ids:ids.filter((_,i)=>i!==index).join(',')})}>移除{names[id]||'第 '+(index+1)+' 家公司'}</button></li>)}</ul>
    {!valid&&<p role="status">請選擇 2–4 家不同公司。</p>}
    {result.error?<p role="alert">{result.error}</p>:result.loading?<p role="status">正在讀取公司比較…</p>:result.data&&<div className="rf-company-comparison">{result.data.data.companies.map(row=><article key={row.id}><h2><Link href={href(row.id)}>{row.name}</Link></h2><p>{row.summary}</p><h3>業務模式</h3>{row.business_model?<Markdown skipHtml components={{a:({href:destination,children})=>destination?.startsWith('/next?focus=')?<Link href={href(new URLSearchParams(destination.split('?')[1]).get('focus')||'')}>{children}</Link>:<a href={destination} target="_blank" rel="noreferrer">{children}</a>}}>{row.business_model}</Markdown>:<p>尚未完成業務模式深研，先保留已知角色。</p>}<h3>供應角色</h3><ul>{row.roles.map((role,index)=><li key={index}><Link href={href(role.segment_id)}>相關環節</Link>：{role.description}</li>)}</ul><h3>產品</h3>{row.products.length?<ul>{row.products.map((product,index)=><li key={index}><Link href={href(product.product_id)}>{product.name}</Link>：{product.role_name}</li>)}</ul>:<p>此公司尚未列出已核對的產品能力。</p>}<h3>風險與研究界線</h3>{row.risks?<Markdown skipHtml components={{a:({href:destination,children})=>destination?.startsWith('/next?focus=')?<Link href={href(new URLSearchParams(destination.split('?')[1]).get('focus')||'')}>{children}</Link>:<a href={destination} target="_blank" rel="noreferrer">{children}</a>}}>{row.risks}</Markdown>:<p>尚未完成風險深研。</p>}{row.gaps.map(gap=><p key={gap}>{gap}</p>)}{row.truncated&&<p>部分研究超過這次比較範圍，可開啟公司研究繼續閱讀。</p>}</article>)}</div>}
  </section>;
}
