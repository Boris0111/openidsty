'use client';
import {useEffect,useRef,useState} from 'react';
import {useRouter,useSearchParams} from 'next/navigation';
import Link from 'next/link';
import {useResearch,ResearchDetail,ResearchGraph,ResearchPage} from '@/lib/research-api';
import {ResearchNetwork} from './ResearchNetwork';
import {ResearchDetailContent} from './ResearchDetailContent';
import {ResearchDirectory,directoryView,directoryNames,DirectoryView} from './ResearchDirectory';
import {mapReturn,directoryReturn} from '@/lib/research-navigation';

const collections:Record<string,string>={company:'companies',product:'products',segment:'segments',theme:'themes',role:'roles',concept:'concepts',application:'applications',research:'research'};
const kindNames:Record<string,string>={company:'公司',product:'產品',segment:'環節',theme:'題材',role:'供應角色',concept:'術語',application:'應用',research:'研究'};
const initialFocus='product-cold-plate';
const firstFlow=new Set([initialFocus,'product-liquid-to-liquid-cdu','company-auras','company-vertiv','concept-liquid-cooling-loop','application-ai-rack-cooling','role-chip-heat-capture','role-coolant-distribution']);

function Search({release,href}:{release:string;href:(id:string)=>string}) {
  const [query,setQuery]=useState(''),[debounced,setDebounced]=useState('');
  const wrapper=useRef<HTMLDivElement>(null);
  useEffect(()=>{const timer=setTimeout(()=>setDebounced(query),200);return()=>clearTimeout(timer)},[query]);
  const result=useResearch<ResearchPage>(debounced.trim()?`/api/v2/search?q=${encodeURIComponent(debounced)}&release_id=${release}`:null);
  const items=query===debounced?result.data?.data.items:undefined;
  return <div className="rs-search" ref={wrapper}><label htmlFor="rs-search">搜尋公司、產品或術語</label><input id="rs-search" value={query} placeholder="例如：雙鴻、CDU、冷板" onChange={event=>setQuery(event.target.value)} aria-expanded={Boolean(query)} aria-controls={query?'rs-results':undefined} autoComplete="off" onKeyDown={event=>{if(event.key==='Escape')setQuery('');if(event.key==='ArrowDown'){event.preventDefault();wrapper.current?.querySelector<HTMLAnchorElement>('#rs-results a')?.focus()}}}/>
    {query&&<div className="rs-results" id="rs-results" aria-label="搜尋結果">{result.error?<p role="alert">{result.error}</p>:!items?<p role="status">搜尋中…</p>:items.length?items.map((item,index)=><Link key={item.id} href={href(item.id)} onClick={()=>setQuery('')} onKeyDown={event=>{const links=wrapper.current?.querySelectorAll<HTMLAnchorElement>('#rs-results a');if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();links?.[(index+(event.key==='ArrowDown'?1:-1)+(links.length||1))%(links?.length||1)]?.focus()}if(event.key==='Escape'){setQuery('');wrapper.current?.querySelector('input')?.focus()}}}><strong>{item.name}</strong><span>{kindNames[item.kind]}　{item.summary}</span></Link>):<p>找不到結果，請試公司代號或另一個產品名稱。</p>}</div>}
  </div>;
}

export function ResearchExplorer() {
  const router=useRouter(),params=useSearchParams();
  const queryRelease=params.get('release_id'),focus=params.get('focus')||initialFocus,view=directoryView(params.get('view'));
  const from=mapReturn(params.get('from'));
  const manifest=useResearch<{published_at:string}>(queryRelease?null:'/api/v2/manifest');
  const release=queryRelease||manifest.data?.release_id;
  const kind=focus.split('-')[0],collection=collections[kind];
  const isFirst=firstFlow.has(focus)&&!view;
  const detail=useResearch<ResearchDetail>(release&&!view&&collection?`/api/v2/${collection}/${encodeURIComponent(focus)}?release_id=${release}`:null);
  const graph=useResearch<ResearchGraph>(release&&!view&&collection?`/api/v2/graphs?root=${encodeURIComponent(focus)}&depth=1&release_id=${release}`:null);
  const diagram=useResearch<ResearchDetail>(release&&isFirst?`/api/v2/concepts/concept-liquid-cooling-loop?release_id=${release}`:null);
  const panel=useRef<HTMLElement>(null),previous=useRef<string|null>(null);
  const [copied,setCopied]=useState('');
  const [diagramFailed,setDiagramFailed]=useState(false);
  useEffect(()=>{
    if(!queryRelease&&manifest.data){const next=new URLSearchParams(params);next.set('release_id',manifest.data.release_id);router.replace('/next?'+next,{scroll:false})}
  },[queryRelease,manifest.data,params,router]);
  useEffect(()=>{
    const selection=view?'view:'+view:focus;
    if(previous.current&&previous.current!==selection&&!view){panel.current?.focus({preventScroll:true});if(window.matchMedia('(max-width:800px)').matches)panel.current?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'})}
    previous.current=selection;setCopied('');
  },[focus,view]);
  function viewHref(value:DirectoryView,filters:Record<string,string>={}){const query=new URLSearchParams({view:value,...(release?{release_id:release}:{}),...(from?{from}:{})});for(const [key,value] of Object.entries(filters))if(value)query.set(key,value);return '/next?'+query}
  const index=view?viewHref(view,Object.fromEntries(['market','role','category','cursor'].flatMap(key=>params.get(key)?[[key,params.get(key)!]]:[]))):directoryReturn(params.get('index'),release,from);
  function href(id:string){return '/next?'+new URLSearchParams({focus:id,...(release?{release_id:release}:{}),...(from?{from}:{}),...(index?{index}:{})})}
  function selectEdge(edge:string|null){const query=new URLSearchParams(params);if(edge)query.set('edge',edge);else query.delete('edge');router.push('/next?'+query,{scroll:false})}
  function navigate(id:string){router.push(href(id),{scroll:false});if(window.matchMedia('(max-width:800px)').matches)panel.current?.scrollIntoView({block:'start',behavior:'auto'})}
  const item=detail.data?.data;
  const desktop=diagram.data?.data.assets.find(asset=>asset.id.endsWith('desktop'));
  const mobile=diagram.data?.data.assets.find(asset=>asset.id.endsWith('mobile'));
  const companies=graph.data?.data.nodes.filter(node=>node.kind==='company'&&node.id!==focus&&graph.data?.data.edges.some(edge=>edge.kind==='capability'&&edge.source===node.id&&edge.target===focus))||[];
  const products=graph.data?.data.nodes.filter(node=>node.kind==='product'&&node.id!==focus)||[];
  const error=manifest.error||detail.error||(params.has('view')&&!view?'找不到這個研究目錄，請從研究目錄重新選擇。':!collection&&!view?'找不到這筆研究入口，請從搜尋或公司索引重新選擇。':undefined);
  return <div className="research-service"><header className="rs-header"><Link className="rs-brand" href={href(initialFocus)}>IndustryFlow<span>產業研究</span></Link><nav aria-label="研究導覽"><Link href={href(initialFocus)} aria-current={isFirst?'page':undefined}>液冷供應鏈</Link><Link href={viewHref('segments')} aria-current={view&&view!=='companies'&&view!=='themes'?'page':undefined}>研究目錄</Link><Link href={viewHref('companies')} aria-current={view==='companies'?'page':undefined}>公司索引</Link><Link href={viewHref('themes')} aria-current={view==='themes'?'page':undefined}>題材研究</Link></nav>{release&&<Search release={release} href={href}/>}</header>
    <div className="rs-content">{!view&&<nav className="rs-breadcrumb" aria-label="研究返回"><Link href={index||viewHref('segments')}>回{index?'原目錄':'研究目錄'}</Link>{(from||item?.legacy_return)&&<Link href={from||item!.legacy_return!.url}>{from?'回到原來的產業地圖':item!.legacy_return!.label}</Link>}</nav>}<div className="rs-intro"><div><h1>{view?directoryNames[view]:isFirst?'AI 機櫃的熱，怎麼送出去？':item?.name||'產業研究'}</h1><p>{view?'從研究對象找到供應角色、條件與來源。':isFirst?'先分清楚產品交付，再看公司能做什麼，以及證據支持到哪裡。':'閱讀角色、產品與可追溯的判斷依據。'}</p></div><div className="rs-page-actions"><button onClick={()=>{navigator.clipboard?.writeText(window.location.href).then(()=>setCopied('連結已複製')).catch(()=>setCopied('可複製網址列分享'))}}>分享這份研究</button><span role="status">{copied}</span></div></div>
    {error&&<div className="rs-error" role="alert"><p>{error}</p><button onClick={()=>window.location.reload()}>重新讀取</button><Link href="/">開啟既有研究</Link></div>}
    {!release&&!error&&<p role="status">正在讀取研究…</p>}
    {view&&release&&<ResearchDirectory key={view} view={view} release={release} href={href} indexHref={viewHref}/>}
    {!params.has('view')&&release&&collection&&<div className={`rs-workspace ${isFirst?'':'rs-single'}`}>
      {isFirst&&<section className="rs-diagram" data-full-diagram={focus==='concept-liquid-cooling-loop'} aria-label="液對液系統與產品選擇"><div className="rs-section-top"><h2>同一套系統，不同交付角色</h2><Link href={href('concept-liquid-cooling-loop')}>讀懂兩個回路</Link></div>
        <div className="rs-mobile-schematic" aria-label="熱由冷板經 CDU 移向設施，兩側液體分離"><span>冷板<strong>晶片取熱</strong></span><b aria-hidden="true">→</b><span>CDU<strong>控制與換熱</strong></span><b aria-hidden="true">→</b><span>設施<strong>把熱排出</strong></span></div>
        {diagram.error||diagramFailed?<p className="rs-scope-note">圖解目前無法讀取，可先閱讀產品邊界及來源。</p>:desktop?<figure><picture>{mobile&&<source media="(max-width:800px)" srcSet={mobile.url}/>}<img src={desktop.url} alt={desktop.alt} onError={()=>setDiagramFailed(true)}/></picture><figcaption>功能示意。公司間的具名交易需另有來源，不能由水路相接推定。</figcaption></figure>:<p role="status">正在載入系統圖解…</p>}
        <div className="rs-product-choice" aria-label="選擇產品研究"><button aria-pressed={focus===initialFocus} onClick={()=>navigate(initialFocus)}><strong>冷板</strong><span>在晶片端取熱</span></button><button aria-pressed={focus==='product-liquid-to-liquid-cdu'} onClick={()=>navigate('product-liquid-to-liquid-cdu')}><strong>液對液 CDU</strong><span>控制回路，把熱交給設施</span></button></div>
        <p className="rs-scope-note">本輪走讀：雙鴻冷板與 Vertiv 液對液 CDU。這是已核對案例，並非完整供應商名單。</p>
      </section>}
      <article className="rs-detail" ref={panel} tabIndex={-1} aria-label="選中研究內容" aria-busy={detail.loading}>
        {detail.loading?<p role="status">正在讀取這份研究…</p>:item&&<ResearchDetailContent item={item} href={href} companies={companies} products={products}/>}
      </article>
      <div className="rs-network-area">{graph.data?<ResearchNetwork graph={graph.data.data} onSelect={navigate} selectedEdge={params.get('edge')} onEdge={selectEdge}/>:graph.error?<p role="alert">{graph.error}</p>:<p role="status">正在讀取關係…</p>}</div>
    </div>}
    </div><footer className="rs-footer"><p>研究依公開資料與原始條件判讀，產品能力、客戶交易與收入證據分開。</p><Link href="/">既有產業地圖、事件與財務</Link></footer>
  </div>;
}
