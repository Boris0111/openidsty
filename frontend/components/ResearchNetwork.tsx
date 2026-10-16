'use client';
import {useEffect,useRef,useState} from 'react';
import cytoscape,{Core,StylesheetJson} from 'cytoscape';
import type {ResearchGraph} from '@/lib/research-api';

const kindNames:Record<string,string>={classification:'分類',capability:'產品能力','named-supply':'具名供應',partnership:'合作',competition:'競爭','segment-supply':'環節供應','segment-feedback':'需求回饋','demand-feedback':'需求回饋'};

export function ResearchNetwork({graph,onSelect}:{graph:ResearchGraph;onSelect:(id:string)=>void}) {
  const container=useRef<HTMLDivElement>(null),instance=useRef<Core|null>(null),select=useRef(onSelect);
  select.current=onSelect;
  const [selectedEdge,setSelectedEdge]=useState<string|null>(null);
  useEffect(()=>{
    if(!container.current)return;
    const positions=new Map<string,{x:number;y:number}>();
    if(graph.nodes.length<=8){
      const remaining=new Set(graph.nodes.map(node=>node.id)),levels:string[][]=[];
      while(remaining.size){
        const next=[...remaining].filter(id=>!graph.edges.some(edge=>edge.target===id&&remaining.has(edge.source)));
        if(!next.length)break;
        levels.push(next);next.forEach(id=>remaining.delete(id));
      }
      if(!remaining.size)levels.forEach((ids,level)=>ids.forEach((id,index)=>positions.set(id,{x:(index-(ids.length-1)/2)*172,y:level*88})));
      else graph.nodes.forEach((node,index)=>positions.set(node.id,{x:150*Math.cos(index*2*Math.PI/graph.nodes.length),y:110*Math.sin(index*2*Math.PI/graph.nodes.length)}));
    }
    const style:StylesheetJson=[
      {selector:'node',style:{label:'data(name)',shape:'round-rectangle',width:148,height:58,'background-color':'#fff','border-width':1.5,'border-color':'#8ba4ad','font-family':'Microsoft JhengHei, PingFang TC, sans-serif','font-size':16,'text-wrap':'wrap','text-max-width':'132px','text-valign':'center',color:'#16343a'}},
      {selector:'node[kind="company"]',style:{'background-color':'#e7f2f4','border-color':'#267a97'}},
      {selector:'node.center',style:{'border-width':3,'border-color':'#203d46'}},
      {selector:'edge',style:{'curve-style':'bezier','line-color':'#7a9099','target-arrow-color':'#7a9099','target-arrow-shape':'triangle',width:1.7}},
      {selector:'edge[kind="classification"]',style:{'line-style':'dotted','target-arrow-shape':'none','line-color':'#a9b8bd'}},
      {selector:'edge[kind="capability"]',style:{'line-style':'dashed','line-color':'#267a97','target-arrow-color':'#267a97',width:2.4}},
      {selector:'edge[kind="segment-feedback"],edge[kind="demand-feedback"]',style:{'line-style':'dashed','line-color':'#c14c38','target-arrow-color':'#c14c38'}},
      {selector:'edge:selected',style:{width:4,'line-color':'#16343a','target-arrow-color':'#16343a'}}
    ];
    const cy=cytoscape({container:container.current,style,elements:[...graph.nodes.map(node=>({data:node,position:positions.get(node.id),classes:node.id===graph.root?'center':''})),...graph.edges.map(edge=>({data:edge}))],
      layout:positions.size?{name:'preset',padding:12}:{name:'breadthfirst',directed:true,padding:32,spacingFactor:1.2},minZoom:.3,maxZoom:2.5,wheelSensitivity:.15});
    if(cy.zoom()>1.2){cy.zoom(1.2);cy.center()}
    instance.current=cy;setSelectedEdge(null);
    cy.on('tap','node',event=>select.current(event.target.id()));
    cy.on('tap','edge',event=>setSelectedEdge(event.target.id()));
    const observer=new ResizeObserver(()=>{const zoom=cy.zoom(),pan={...cy.pan()};cy.resize();cy.zoom(zoom);cy.pan(pan)});
    observer.observe(container.current);
    return()=>{observer.disconnect();cy.destroy();instance.current=null};
  },[graph]);
  const edge=graph.edges.find(edge=>edge.id===selectedEdge),names=new Map(graph.nodes.map(node=>[node.id,node.name]));
  useEffect(()=>{instance.current?.edges().unselect();if(selectedEdge)instance.current?.getElementById(selectedEdge).select()},[selectedEdge]);
  return <section className="rs-network" aria-labelledby="rs-network-title"><div className="rs-section-top"><h2 id="rs-network-title">從產品找到公司</h2><button onClick={()=>instance.current?.fit(undefined,32)}>重設圖形</button></div>
    <div className="rs-canvas" ref={container} role="img" aria-label="產品、公司與分類關係圖，亦可使用下方文字清單" data-testid="research-network"/>
    <p className="rs-legend"><span>虛線：產品能力</span><span>點線：分類</span></p>
    <div className="rs-node-list" aria-label="關聯研究文字清單">{graph.nodes.filter(node=>node.id!==graph.root).map(node=><button key={node.id} onClick={()=>onSelect(node.id)}>{node.name}</button>)}</div>
    {graph.edges.filter(edge=>edge.kind!=='classification').length>0&&<label className="rs-edge-picker">閱讀連線<select value={selectedEdge||''} onChange={event=>setSelectedEdge(event.target.value||null)}><option value="">選擇關係</option>{graph.edges.filter(edge=>edge.kind!=='classification').map(edge=><option key={edge.id} value={edge.id}>{names.get(edge.source)} — {names.get(edge.target)}（{kindNames[edge.kind]||'關係'}）</option>)}</select></label>}
    {edge&&<div className="rs-edge-reading" role="region" aria-label="連線說明"><h3>{kindNames[edge.kind]||'關係'}</h3><p>{edge.mechanism}</p><ul>{edge.conditions.map(condition=><li key={condition}>{condition}</li>)}</ul>{edge.claims.map(claim=><button key={claim.entity_id+claim.claim_id} onClick={()=>onSelect(claim.entity_id)}>閱讀{nameFor(claim.entity_id,names)}的產品證據</button>)}{edge.evidence_url&&<a href={edge.evidence_url} target="_blank" rel="noreferrer">閱讀原始來源</a>}</div>}
    {graph.truncated&&<p className="rs-limit">目前顯示這一段關係；可選擇公司或產品繼續探索。</p>}
  </section>;
}
function nameFor(id:string,names:Map<string,string>){return names.get(id)||'公司'}
