'use client';
import {useEffect,useRef,useState} from 'react';
import cytoscape,{Core,ElementDefinition,StylesheetJson} from 'cytoscape';
import type {GraphData} from '@/lib/types';

export function Network({graph,selected,onSelect,selectedRelation,onRelation,compact=false}:{graph:GraphData;selected?:string;onSelect:(id:string)=>void;selectedRelation?:string|null;onRelation?:(id:string)=>void;compact?:boolean}) {
  const container=useRef<HTMLDivElement>(null),cy=useRef<Core|null>(null),callback=useRef(onSelect);
  const [ready,setReady]=useState(false);callback.current=onSelect;
  const relationCallback=useRef(onRelation);relationCallback.current=onRelation;
  useEffect(()=>{
    if(!container.current)return;
    const elements:ElementDefinition[]=graph.nodes.map(({position,...n})=>({data:{...n,sequence:position,label:n.name.length>6?n.name.slice(0,Math.ceil(n.name.length/2))+'\n'+n.name.slice(Math.ceil(n.name.length/2)):n.name}}));
    elements.push(...graph.edges.map(e=>({data:e})));
    const styles:StylesheetJson=[
      {selector:'node',style:{shape:'round-rectangle',width:154,height:68,'background-color':'#ffffff','border-width':1.5,'border-color':'#94A3B8',label:'data(label)',color:'#182C3A','font-family':'Microsoft JhengHei, PingFang TC, sans-serif','font-size':17,'text-wrap':'wrap','text-valign':'center','text-halign':'center','text-max-width':'145px','overlay-opacity':0}},
      {selector:'edge',style:{width:1.5,'line-color':'#94A3B8','target-arrow-color':'#64748B','target-arrow-shape':'triangle','curve-style':'unbundled-bezier','control-point-distances':36,'control-point-weights':0.5,'arrow-scale':1.2,'overlay-opacity':0,opacity:0.75}},
      {selector:'edge[kind="demand-feedback"]',style:{'line-style':'dashed'}},
      {selector:'edge[kind="unreviewed"]',style:{'line-style':'dotted'}},
      {selector:'node[?external]',style:{'background-color':'#F7F8FA','border-style':'dashed',color:'#64748B'}},
      {selector:'node.selected',style:{'border-width':3,'border-color':'#2563EB','background-color':'#EAF1FF','font-weight':700}},
      {selector:'node.neighbor',style:{'border-color':'#2563EB','border-width':2}},
      {selector:'node.dimmed',style:{opacity:0.7}},
      {selector:'edge.dimmed',style:{opacity:0.18}},
      {selector:'edge.highlighted',style:{'line-color':'#2563EB','target-arrow-color':'#2563EB',width:2.5,opacity:1}},
      {selector:'edge.relation-selected',style:{'line-color':'#0D9488','target-arrow-color':'#0D9488',width:4,opacity:1}}
    ];
    const instance=cytoscape({container:container.current,elements,style:styles,minZoom:0.3,maxZoom:2.5,wheelSensitivity:0.2,layout:{name:'preset'}});
    if(compact){
      const neighbors=graph.nodes.filter(n=>n.id!==selected);
      instance.getElementById(selected||'').position({x:270,y:190});
      neighbors.forEach((n,i)=>{const angle=-Math.PI/2+2*Math.PI*i/Math.max(1,neighbors.length);instance.getElementById(n.id).position({x:270+230*Math.cos(angle),y:190+150*Math.sin(angle)})});
    }else if(window.matchMedia('(max-width:800px)').matches){
      [...graph.nodes].sort((a,b)=>(a.position||1)-(b.position||1)).forEach((n,i)=>instance.getElementById(n.id).position({x:(i%3)*185+90,y:Math.floor(i/3)*112+55}));
    }else{
      const groups=new Map<number,string[]>();
      graph.nodes.forEach(n=>{const group=n.external?0:n.position||1;groups.set(group,[...(groups.get(group)||[]),n.id])});
      [...groups.keys()].sort((a,b)=>a-b).forEach((group,col)=>groups.get(group)!.forEach((id,row)=>instance.getElementById(id).position({x:col*195+90,y:row*112+55})));
    }
    let fitted=container.current.clientWidth>0;
    if(fitted)instance.fit(undefined,35);
    const readable=()=>{instance.nodes().style('font-size',Math.max(17,14/instance.zoom()))};readable();
    instance.on('zoom',readable);
    instance.on('tap','node',event=>callback.current(event.target.id()));
    instance.on('tap','edge',event=>relationCallback.current?.(event.target.id()));
    cy.current=instance;setReady(true);
    const observer=new ResizeObserver(()=>{instance.resize();if(!fitted&&container.current&&container.current.clientWidth>0){instance.fit(undefined,35);fitted=true;readable()}});observer.observe(container.current);
    return ()=>{observer.disconnect();instance.destroy();cy.current=null;setReady(false)};
    // Selected changes only style the existing full graph; compact graph changes its node set.
  },[graph,compact]);
  useEffect(()=>{
    const instance=cy.current;if(!instance)return;
    instance.elements().removeClass('selected neighbor highlighted dimmed relation-selected');
    const node=instance.getElementById(selected||'');
    if(node.length){node.addClass('selected');node.neighborhood('node').addClass('neighbor');node.connectedEdges().addClass('highlighted');instance.elements().difference(node.closedNeighborhood()).addClass('dimmed')}
    const relation=instance.getElementById(selectedRelation||'');
    if(relation.length){relation.removeClass('dimmed').addClass('relation-selected');relation.connectedNodes().removeClass('dimmed')}
  },[selected,selectedRelation,ready,graph]);
  function zoom(ratio:number){const c=cy.current;if(c)c.zoom({level:c.zoom()*ratio,renderedPosition:{x:c.width()/2,y:c.height()/2}})}
  return <div className={`network-wrap ${compact?'local-network':'industry'}`}><div className="network" ref={container} role="img" aria-label={compact?'選中環節與相鄰供需關係圖':'完整產業供應鏈互動圖，亦可由環節清單操作'} data-testid={compact?'local-network':'network'} data-nodes={graph.nodes.length} data-edges={graph.edges.length}/><div className="graph-footer"><div className="graph-controls"><button aria-label="放大圖形" onClick={()=>zoom(1.25)}>＋</button><button aria-label="縮小圖形" onClick={()=>zoom(0.8)}>−</button><button onClick={()=>cy.current?.fit(undefined,35)}>重設視角</button></div><p className="graph-hint">選擇環節或連線查看說明</p></div></div>
}
