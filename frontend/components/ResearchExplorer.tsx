'use client';
import {useEffect,useRef,useState} from 'react';
import {useRouter,useSearchParams} from 'next/navigation';
import Link from 'next/link';
import {useResearch,ResearchDetail,ResearchGraph} from '@/lib/research-api';
import {ResearchNetwork} from './ResearchNetwork';
import {ResearchDetailContent} from './ResearchDetailContent';
import {ResearchDirectory,directoryView,directoryNames,DirectoryView} from './ResearchDirectory';
import {mapReturn,directoryReturn} from '@/lib/research-navigation';
import {ResearchCompare} from './ResearchCompare';
import {ResearchEvents} from './ResearchEvents';
import {EventTabs} from './EventTabs';
import {useResearchManifest} from '@/lib/research-manifest';
import {refreshResearch,resetDynamicResearch} from '@/lib/research-cache';
import {ResearchReadStatus} from './ResearchReadStatus';
import {ResearchWatchButton,ResearchWatchlist} from './ResearchWatch';
import {ResearchChainIndex,ResearchChainStrip,ResearchChainView,ResearchCompanyChains} from './ResearchChain';

const collections:Record<string,string>={company:'companies',product:'products',segment:'segments',theme:'themes',role:'roles',concept:'concepts',application:'applications',research:'research'};
const serviceNames:Record<string,string>={compare:'公司比較',observations:'傳聞觀察',watchlist:'此裝置收藏'};

export function ResearchExplorer() {
  const router=useRouter(),params=useSearchParams();
  const queryRelease=params.get('release_id'),focus=params.get('focus')||'',view=directoryView(params.get('view'));
  // Without a focus the reader starts from the supply-chain index.
  const chainsView=params.get('view')==='chains'||(!params.has('view')&&!focus);
  const from=mapReturn(params.get('from'));
  const serviceView=Object.hasOwn(serviceNames,params.get('view')||'')?params.get('view'):null;
  const navigation=new URLSearchParams(params);navigation.delete('release_id');
  const manifest=useResearchManifest(navigation.toString());
  const release=queryRelease||manifest.data?.release_id;
  const kind=focus.split('-')[0],collection=focus?collections[kind]:undefined;
  const detail=useResearch<ResearchDetail>(release&&!view&&!serviceView&&!chainsView&&collection?`/api/v2/${collection}/${encodeURIComponent(focus)}?release_id=${release}`:null);
  const graph=useResearch<ResearchGraph>(release&&!view&&!serviceView&&!chainsView&&collection?`/api/v2/graphs?root=${encodeURIComponent(focus)}&depth=1&release_id=${release}`:null);
  const panel=useRef<HTMLElement>(null),previous=useRef<string|null>(null);
  const [copied,setCopied]=useState('');
  useEffect(()=>{
    if(!queryRelease&&manifest.data){const next=new URLSearchParams(params);next.set('release_id',manifest.data.release_id);router.replace('/next?'+next+window.location.hash,{scroll:false})}
  },[queryRelease,manifest.data,params,router]);
  useEffect(()=>{
    const selection=view?'view:'+view:focus||'chains';
    if(previous.current&&previous.current!==selection&&!view){panel.current?.focus({preventScroll:true});if(window.matchMedia('(max-width:800px)').matches)panel.current?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'})}
    previous.current=selection;setCopied('');
  },[focus,view]);
  function viewHref(value:DirectoryView,filters:Record<string,string>={}){const query=new URLSearchParams({view:value,...(release?{release_id:release}:{}),...(from?{from}:{})});for(const [key,value] of Object.entries(filters))if(value)query.set(key,value);return '/next?'+query}
  const index=view?viewHref(view,Object.fromEntries(['market','role','category','cursor'].flatMap(key=>params.get(key)?[[key,params.get(key)!]]:[]))):directoryReturn(params.get('index'),release,from);
  function href(id:string){return '/next?'+new URLSearchParams({focus:id,...(release?{release_id:release}:{}),...(from?{from}:{}),...(index?{index}:{})})}
  function selectEdge(edge:string|null){const query=new URLSearchParams(params);if(edge)query.set('edge',edge);else query.delete('edge');router.push('/next?'+query,{scroll:false})}
  function serviceHref(value:string,extra:Record<string,string>={}){return '/next?'+new URLSearchParams({view:value,...(release?{release_id:release}:{}),...(from?{from}:{}),...extra})}
  function companyPanel(value:string){const query=new URLSearchParams(params);for(const key of ['metric','basis','financial_cursor','event_cursor','observation_id','before_revision','source_nature','relevance','period_from','period_to'])query.delete(key);query.set('panel',value);router.push('/next?'+query,{scroll:false})}
  const panelName=params.get('panel')==='observations'?'observations':'events';
  function navigate(id:string){router.push(href(id),{scroll:false});if(window.matchMedia('(max-width:800px)').matches)panel.current?.scrollIntoView({block:'start',behavior:'auto'})}
  const item=detail.data?.data;
  const companies=graph.data?.data.nodes.filter(node=>node.kind==='company'&&node.id!==focus&&graph.data?.data.edges.some(edge=>edge.kind==='capability'&&edge.source===node.id&&edge.target===focus))||[];
  const products=graph.data?.data.nodes.filter(node=>node.kind==='product'&&node.id!==focus)||[];
  const anchored=useRef<string|null>(null);
  useEffect(()=>{
    // A shared #company-data link lands on that section once the research above it has rendered.
    const key=focus+':'+release;
    if(window.location.hash!=='#company-data'||item?.kind!=='company'||anchored.current===key)return;
    if(!(graph.data||graph.error))return;
    anchored.current=key;
    document.getElementById('company-data')?.scrollIntoView({block:'start'});
  },[focus,release,item,graph.data,graph.error]);
  function adopt(){
    if(!manifest.data)return;
    const next=new URLSearchParams(params);next.set('release_id',manifest.data.release_id);
    resetDynamicResearch();
    for(const key of ['cursor','financial_cursor','event_cursor','edge','observation_id','before_revision','compare_company','compare_observation','index'])next.delete(key);
    const back=directoryReturn(params.get('index'),manifest.data.release_id,from);
    if(back){const target=new URL(back,window.location.origin);target.searchParams.delete('cursor');next.set('index',target.pathname+'?'+target.searchParams)}
    router.push('/next?'+next,{scroll:false});
  }
  useEffect(()=>{
    // Segments are read on the industry map (which lists their supply chains) and themes on their judgment pages.
    if(item?.kind==='segment'&&(from||item.legacy_return))router.replace(from||item.legacy_return!.url);
    if(item?.kind==='theme')router.replace('/themes/'+encodeURIComponent(item.id.replace(/^theme-/,'')));
  },[item,from,router]);
  const crumbs=item?.kind==='company'?[{label:'公司',url:viewHref('companies')}]:[{label:'產業地圖',url:'/'},
    ...(item?.trail||[]).map(step=>({label:step.name,url:step.kind==='segment'?(from||step.url||'/'):href(step.id)}))];
  const updated=Boolean(queryRelease&&manifest.data&&manifest.data.release_id!==queryRelease);
  const error=(!release?manifest.error:undefined)||detail.error||(params.has('view')&&!view&&!serviceView&&!chainsView?'找不到這個研究目錄，請從供應鏈或公司重新選擇。':!collection&&!view&&!serviceView&&!chainsView?'找不到這筆研究入口，請從搜尋或公司索引重新選擇。':undefined);
  const title=chainsView?'供應鏈':serviceView?serviceNames[serviceView]:view?directoryNames[view]:item?.kind==='application'?item.content.question||item.name:item?.name||'產業研究';
  const lead=chainsView?'從應用問題切入，依步驟找到產品，再看哪些公司有產品證據。':view?'從研究對象找到供應角色、條件與來源。':serviceView==='watchlist'?'查看你收藏的研究、數值與事件是否有實質更新。':item?.kind==='application'?item.summary:'閱讀角色、產品與可追溯的判斷依據。';
  return <div className="research-service">
    <div className="rs-content">{!view&&!serviceView&&item&&<nav className="rs-breadcrumb" aria-label="研究位置"><ol>{crumbs.map(crumb=><li key={crumb.url}><Link href={crumb.url}>{crumb.label}</Link></li>)}<li aria-current="page">{item.name}</li></ol>{index&&<Link href={index}>回原目錄</Link>}</nav>}<div className="rs-intro"><div><h1>{title}</h1><p>{lead}</p></div><div className="rs-page-actions"><div>{serviceView!=='watchlist'&&<button onClick={()=>{navigator.clipboard?.writeText(window.location.href).then(()=>setCopied('連結已複製')).catch(()=>setCopied('可複製網址列分享'))}}>分享這份研究</button>}<button onClick={refreshResearch} aria-busy={manifest.loading||manifest.refreshing}>檢查更新</button>{item&&release&&!view&&!serviceView&&!chainsView&&!detail.loading&&<ResearchWatchButton key={item.id} kind={item.kind} id={item.id} name={item.name} release={release}/>}</div><span role="status">{copied}</span></div></div>
    {(updated||manifest.refreshError||release&&manifest.error)&&<aside className="rs-update" aria-label="研究更新">{updated&&<><span>有新版研究可閱讀；目前仍保留你正在讀的版本。</span><button onClick={adopt}>載入新版研究</button></>}{(manifest.refreshError||release&&manifest.error)&&<span role="status">目前無法確認研究更新，已載入的內容保留。</span>}</aside>}
    {[detail,graph].some(result=>result.refreshError)&&<ResearchReadStatus state={{refreshError:'unavailable',refresh:refreshResearch}}/>}
    {error&&<div className="rs-error" role="alert"><p>{error}</p><button onClick={()=>window.location.reload()}>重新讀取</button><Link href="/">回產業地圖</Link></div>}
    {!release&&!error&&<p role="status">正在讀取研究…</p>}
    {chainsView&&release&&<ResearchChainIndex release={release} href={href}/>}
    {view&&release&&<ResearchDirectory key={view} view={view} release={release} href={href} indexHref={viewHref}/>}
    {serviceView==='compare'&&release&&<ResearchCompare release={release} href={href}/>}
    {serviceView==='observations'&&<EventTabs current="rumors"/>}{serviceView==='observations'&&release&&<ResearchEvents key="global-observations" release={release} rumors href={href}/>}
    {serviceView==='watchlist'&&<ResearchWatchlist href={href}/>}
    {!params.has('view')&&item?.chain&&<ResearchChainView chain={item.chain} href={href}/>}
    {!params.has('view')&&item&&item.kind!=='company'&&item.chains&&<ResearchChainStrip chains={item.chains} href={href}/>}
    {!params.has('view')&&release&&collection&&<div className="rs-workspace rs-single">
      <article className="rs-detail" ref={panel} tabIndex={-1} aria-label="選中研究內容" aria-busy={detail.loading}>
        {item?.kind==='company'&&<p className="rf-jump"><a href="#company-data">查看近期資訊</a></p>}
        {item?.kind==='company'&&item.chains&&<ResearchCompanyChains chains={item.chains} href={href}/>}
        {detail.loading?<p role="status">正在讀取這份研究…</p>:item&&<ResearchDetailContent key={release+':'+item.id} item={item} href={href} companies={companies} products={products} release={release}/>}
      </article>
      <div className="rs-network-area">{graph.data?<ResearchNetwork graph={graph.data.data} onSelect={navigate} selectedEdge={params.get('edge')} onEdge={selectEdge}/>:graph.error?<p role="alert">{graph.error}</p>:<p role="status">正在讀取關係…</p>}</div>
    </div>}
    {!params.has('view')&&item?.kind==='company'&&release&&<section className="rf-company-data" id="company-data"><div className="rs-section-top"><h2>{item.name}：近期資訊</h2><Link href={serviceHref('compare',{company_ids:item.id})}>比較這家公司</Link></div><nav className="rs-directory-tabs" aria-label="公司近期資訊">{Object.entries({events:'官方與報導',observations:'傳聞觀察'}).map(([key,name])=><button key={key} aria-pressed={panelName===key} onClick={()=>companyPanel(key)}>{name}</button>)}</nav><ResearchEvents key={item.id+':'+panelName} entity={item.id} release={release} rumors={panelName==='observations'} href={href}/></section>}
    </div>
  </div>;
}
