'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {PUBLIC_SNAPSHOT} from '@/lib/public-snapshot';
import {useResearchWatchlist,queryUpdates,isWatchKind,WATCH_LIMIT,IMPORT_LIMIT_BYTES,UpdateItem,UpdatesResult,WatchTarget,exportWatchlist,parseImport,ImportPreview,targetKey} from '@/lib/research-watchlist';

const kindNames:Record<string,string>={company:'公司',product:'產品',theme:'題材',research:'研究頁'};

/** The public snapshot has no update checks, so it offers no watchlist. */
export function ResearchWatchButton(props:{kind:string;id:string;name:string;release:string}){return PUBLIC_SNAPSHOT?null:<WatchButton {...props}/>}

function WatchButton({kind,id,name,release}:{kind:string;id:string;name:string;release:string}){
  const watch=useResearchWatchlist();const [busy,setBusy]=useState(false);const [message,setMessage]=useState('');
  if(!isWatchKind(kind))return null;
  const followed=watch.has(kind,id);
  async function toggle(){
    if(!isWatchKind(kind))return;
    if(followed){watch.remove(kind,id);setMessage('已移除收藏');return}
    setBusy(true);setMessage('');
    try{
      // Baseline = the release on screen; a newer release later shows as a research update.
      const result=await queryUpdates([{kind,id}],release);const item=result.data.items[0];
      if(watch.add({kind,id,name},item?.available?item:undefined))setMessage(item?.available?'已加入收藏':'已加入收藏；已讀基準待確認');
    }catch{if(watch.add({kind,id,name}))setMessage('已加入收藏；目前無法建立已讀基準，可稍後在收藏頁確認')}
    finally{setBusy(false)}
  }
  return <><button onClick={()=>void toggle()} disabled={!watch.ready||busy} aria-pressed={followed}>{followed?'移除收藏':'加入收藏'}</button>{message&&<span role="status">{message}</span>}{watch.notice&&<span role="status">{watch.notice}</span>}</>;
}

function Status({label,state,detail}:{label:string;state:'pending'|'changed'|'same';detail:string}){
  return <li data-state={state}><strong>{label}</strong><span>{detail}</span></li>;
}

type State='pending'|'changed'|'same';
const compare=(current:string|null|undefined,seen:string|null):State=>seen===null?'pending':current!==seen?'changed':'same';
const PENDING='待確認：尚未建立已讀基準';

function Card({target,item,href,onMark,onRemove}:{target:WatchTarget;item?:UpdateItem;href:(id:string)=>string;onMark:(item:UpdateItem)=>void;onRemove:()=>void}){
  // States compare the response on screen with the local baseline, so marking read updates immediately.
  const research=compare(item?.research?.token,target.seen.research);
  const values=item?.values?.applicable?compare(item.values.token,target.seen.values):null;
  const events=item?.events;
  const eventState:State=target.seen.events===null?'pending':events?.marker===target.seen.events?'same':'changed';
  const counts=events?[events.new_dated?`${events.new_dated} 則新事件（依發布日）`:'',events.new_undated?`${events.new_undated} 則新收錄，發布日未知，不代表剛發生`:''].filter(Boolean).join('；'):'';
  const pending=[research,values,eventState].includes('pending');
  return <article className="rs-watch-card"><div className="rs-watch-title"><h2>{item?.available===false?target.name:<Link href={href(target.id)}>{item?.name||target.name}</Link>}</h2><span>{kindNames[target.kind]}</span></div>
    {item?.available===false?<p className="rs-scope-note">目前無法開啟：{item.reason}</p>:item&&<ul className="rs-watch-status">
      <Status label="研究" state={research} detail={research==='pending'?PENDING:research==='changed'?'已發布研究有更新':'研究無變更'}/>
      {values&&<Status label="數值" state={values} detail={values==='pending'?PENDING:values==='changed'?'有效數值有新期或修訂':'數值無變更'}/>}
      {events&&<Status label="事件" state={eventState} detail={eventState==='pending'?PENDING:eventState==='changed'?counts||'有新事件':'沒有新事件'}/>}
    </ul>}
    {!item&&<p className="rs-scope-note">尚未取得這項收藏的更新摘要。</p>}
    <div className="rs-watch-actions">{item?.available&&<button onClick={()=>onMark(item)}>{pending?'以目前顯示建立已讀基準':'將目前顯示標為已讀'}</button>}<button onClick={onRemove}>移除收藏</button></div>
  </article>;
}

type Checked=ImportPreview&{retired:WatchTarget[];unchecked:boolean};

function Backup(){
  const watch=useResearchWatchlist();
  const [preview,setPreview]=useState<Checked>();const [message,setMessage]=useState('');const [busy,setBusy]=useState(false);
  function download(){
    const url=URL.createObjectURL(new Blob([exportWatchlist(watch.targets)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download=`industryflow-watchlist-${new Date().toISOString().slice(0,10)}.json`;
    document.body.append(link);link.click();link.remove();URL.revokeObjectURL(url);setMessage(`已匯出 ${watch.targets.length} 項收藏。`);
  }
  async function choose(file?:File){
    setPreview(undefined);setMessage('');
    if(!file)return;
    if(file.size>IMPORT_LIMIT_BYTES){setMessage('備份超過 1 MiB，未匯入；原清單保留。');return}
    setBusy(true);
    try{
      const parsed=parseImport(await file.text(),watch.targets);
      if(!parsed.preview){setMessage(parsed.error||'無法匯入；原清單保留。');return}
      // Targets missing from the published research are listed, not imported.
      let retired:WatchTarget[]=[];let unchecked=false;
      if(parsed.preview.fresh.length){
        try{const result=await queryUpdates(parsed.preview.fresh.map(({kind,id})=>({kind,id})));
          const gone=new Set(result.data.items.filter(item=>!item.available).map(item=>targetKey(item.kind,item.id)));
          retired=parsed.preview.fresh.filter(t=>gone.has(targetKey(t.kind,t.id)));}
        catch{unchecked=true}
      }
      setPreview({...parsed.preview,fresh:parsed.preview.fresh.filter(t=>!retired.includes(t)),retired,unchecked});
    }finally{setBusy(false)}
  }
  function confirm(){
    if(!preview)return;
    if(watch.merge(preview.fresh)){setMessage(`已合併 ${preview.fresh.length} 項；已存在的 ${preview.duplicates.length} 項保留此瀏覽器的已讀狀態。`);setPreview(undefined)}
    else setMessage(`合併後會超過 ${WATCH_LIMIT} 項上限，未匯入；原清單保留。`);
  }
  return <section className="rs-watch-backup" aria-label="備份與交換"><h2>備份與交換</h2>
    <p className="rs-scope-note">不同瀏覽器、裝置或不同網址（host／port）各有自己的收藏，不會自動同步；請在原處匯出 JSON，再到另一處匯入。備份只含研究身分、名稱與已讀基準，不含研究內容或任何登入資料，上限 1 MiB、{WATCH_LIMIT} 項。</p>
    <div className="rs-watch-toolbar"><button onClick={download} disabled={!watch.ready||!watch.targets.length}>匯出收藏 JSON</button>
      <label>匯入收藏備份<input type="file" accept="application/json,.json" disabled={!watch.ready||busy} onChange={event=>{void choose(event.target.files?.[0]);event.target.value=''}}/></label></div>
    {busy&&<p role="status">正在檢查備份…</p>}{message&&<p role="status">{message}</p>}
    {preview&&<div className="rs-watch-preview" aria-label="匯入預覽"><h3>匯入預覽（共 {preview.total} 項）</h3><ul>
      <li>新增 {preview.fresh.length} 項{preview.fresh.length>0&&`：${preview.fresh.map(t=>t.name).slice(0,10).join('、')}${preview.fresh.length>10?' 等':''}`}</li>
      <li>已存在 {preview.duplicates.length} 項，保留此瀏覽器的已讀狀態，不被備份覆寫</li>
      {preview.invalid.length>0&&<li>無法解析 {preview.invalid.length} 項，不匯入：{preview.invalid.map(item=>item.label).join('、')}</li>}
      {preview.retired.length>0&&<li>目前已發布研究找不到 {preview.retired.length} 項（可能已改名、合併或封存），不匯入：{preview.retired.map(t=>t.name).join('、')}</li>}
      {preview.unchecked&&<li>目前無法確認新項目是否仍在已發布研究中；匯入後可在清單中檢查並移除。</li>}
    </ul><div className="rs-watch-actions"><button onClick={confirm} disabled={!preview.fresh.length}>確認合併</button><button onClick={()=>setPreview(undefined)}>取消</button></div></div>}
  </section>;
}

export function ResearchWatchlist({href}:{href:(id:string)=>string}){
  const watch=useResearchWatchlist();
  const [result,setResult]=useState<UpdatesResult>();const [error,setError]=useState('');const [loading,setLoading]=useState(false);const [round,setRound]=useState(0);
  const signature=watch.targets.map(t=>t.kind+':'+t.id).join(',');
  useEffect(()=>{
    if(!watch.ready||!watch.targets.length)return;
    let active=true;setLoading(true);setError('');
    queryUpdates(watch.targets).then(data=>{if(active)setResult(data)}).catch(reason=>{if(active)setError(reason.message)}).finally(()=>{if(active)setLoading(false)});
    return()=>{active=false};
    // Marking read changes seen locally; it does not refetch, so the shown response stays the basis.
  },[watch.ready,signature,round]);
  const items=new Map(result?.data.items.map(item=>[item.kind+':'+item.id,item]));
  return <section className="rs-watchlist" aria-label="此裝置收藏">
    <p className="rs-scope-note">收藏只保存在這個瀏覽器與這個網址，最多 {WATCH_LIMIT} 項；不會跨瀏覽器或裝置同步，也不含研究全文，離線時仍需連線才能閱讀內容。更新只依各收藏自己的研究、有效數值與事件判定。</p>
    {watch.notice&&<p role="status">{watch.notice}</p>}
    {!watch.ready?<p role="status">正在讀取此瀏覽器的收藏…</p>:!watch.targets.length?<p>尚未收藏研究。可在公司、產品、題材或研究頁按「加入收藏」。</p>:<>
      <div className="rs-watch-toolbar"><button onClick={()=>setRound(value=>value+1)} aria-busy={loading}>檢查收藏更新</button>{loading&&<span role="status">正在檢查更新…</span>}</div>
      {error&&<p role="alert">{error} 已收藏的項目仍保留。</p>}
      {watch.targets.map(target=><Card key={target.kind+':'+target.id} target={target} item={items.get(target.kind+':'+target.id)} href={href}
        onMark={item=>watch.mark(item)} onRemove={()=>watch.remove(target.kind,target.id)}/>)}
    </>}
    {watch.ready&&<Backup/>}
  </section>;
}
