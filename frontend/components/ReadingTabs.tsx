'use client';
import {useEffect,useRef,useState,type ReactNode} from 'react';

type ReadingTab={id:string;label:string;anchors?:string[];content:ReactNode};

// Keep the selected reading task small while preserving deep links and panel state.
export function ReadingTabs({label,tabs}:{label:string;tabs:ReadingTab[]}){
  const [active,setActive]=useState(tabs[0].id);
  const buttons=useRef<(HTMLButtonElement|null)[]>([]);
  const routes=tabs.map(t=>[t.id,...(t.anchors||[])].join(',')).join(';');
  useEffect(()=>{
    function followHash(){
      let hash=window.location.hash.slice(1);
      try{hash=decodeURIComponent(hash);}catch{/* Invalid shared fragments fall back to the first tab. */}
      const tab=tabs.find(t=>t.id===hash||t.anchors?.includes(hash));
      setActive(tab?.id||tabs[0].id);
      if(tab&&hash!==tab.id)requestAnimationFrame(()=>document.getElementById(hash)?.scrollIntoView({block:'start'}));
    }
    followHash();window.addEventListener('hashchange',followHash);
    return ()=>window.removeEventListener('hashchange',followHash);
    // Labels and content can change with API responses without resetting the reader's choice.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[routes]);
  function choose(index:number,focus=false){
    const tab=tabs[index];setActive(tab.id);
    window.history.replaceState(null,'',`${window.location.pathname}${window.location.search}#${tab.id}`);
    if(focus)buttons.current[index]?.focus();
  }
  return <div className="reading-sections">
    <div className="reading-tabs" role="tablist" aria-label={label}>{tabs.map((tab,index)=><button key={tab.id} ref={el=>{buttons.current[index]=el;}} id={`${tab.id}-tab`} role="tab" aria-selected={active===tab.id} aria-controls={tab.id} tabIndex={active===tab.id?0:-1} onClick={()=>choose(index)} onKeyDown={e=>{
      const next=e.key==='ArrowRight'?(index+1)%tabs.length:e.key==='ArrowLeft'?(index+tabs.length-1)%tabs.length:e.key==='Home'?0:e.key==='End'?tabs.length-1:null;
      if(next!==null){e.preventDefault();choose(next,true);}
    }}>{tab.label}</button>)}</div>
    {tabs.map(tab=><div key={tab.id} id={tab.id} role="tabpanel" aria-labelledby={`${tab.id}-tab`} tabIndex={0} hidden={active!==tab.id}>{tab.content}</div>)}
  </div>;
}
