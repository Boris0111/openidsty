'use client';
import Link from 'next/link';
import {useApi} from '@/lib/api';
import {useWatchlist} from '@/lib/watchlist';
import type {UpdatesResponse} from '@/lib/types';
import {Status} from '@/components/Status';
import {statusLabel} from '@/lib/display';
function Entries(){
  const watch=useWatchlist();const api=useApi<UpdatesResponse>(`/api/theme-updates?ids=${watch.saved.theme_ids.map(encodeURIComponent).join(',')}`);
  return <><button className="button" onClick={api.retry}>重新檢查更新</button><Status {...api}/>{api.data?.items.map(item=>{
    const seen=watch.saved.seen[item.theme_id];const version=Boolean(item.available&&(!seen||seen.version_id!==item.current_version_id));const indicators=Boolean(item.available&&(!seen||seen.indicator_token!==item.indicator_token));const candidates=Boolean(item.available&&(!seen||seen.candidate_token!==item.candidate_token));
    return <article key={item.theme_id} className="watch-card"><h2>{item.available?<Link href={`/themes/${item.theme_id}`}>{item.name}</Link>:'無法取得的題材'}</h2>{item.available?<><p>{item.assessment_summary||'判讀尚未整理'}</p><p className="data-note">目前 v{item.version_number??'未建立'}；原查核 {item.reviewed||'未提供'}。</p><div className="watch-updates"><Link href={`/themes/${item.theme_id}${seen?.version_id?`?from_version=${seen.version_id}`:''}#versions`}>{version?'判讀有更新':'判讀無變更'}</Link><Link href={`/themes/${item.theme_id}#indicators`}>{indicators?'指標新期／修訂':'指標無變更'}</Link><Link href={`/themes/${item.theme_id}#candidates`}>{candidates?'候選資訊有變化':'候選資訊無變更'}</Link></div><p>{item.pending_summary}</p><details><summary>指標期別與修訂摘要</summary>{item.indicator_summary?.map(i=><p key={i.id}>{i.name}（{i.kind==='direct'?'特定產品指標':'整體營收代理指標'}）：{i.period||'未取得'}；修訂 {i.revision??'—'}</p>)}</details>{Boolean(item.source_warnings?.length)&&<details><summary>來源取得警示（不計未讀）</summary>{item.source_warnings?.map((w,i)=><div key={i}><p>來源：{statusLabel(w.kind)}</p></div>)}<Link href="/sources">查看來源狀態</Link></details>}<button onClick={()=>watch.mark(item)}>將目前顯示標為已讀</button></>:<p className="empty">{item.reason}</p>}<button onClick={()=>watch.remove(item.theme_id)}>移除關注</button></article>;
  })}</>;
}
export default function Page(){const watch=useWatchlist();return <div className="page-content"><div className="page-heading"><h1>此裝置關注</h1><p>集中查看判讀、指標與待確認資訊。清單只保存在此裝置，沒有跨裝置同步。</p></div>{watch.notice&&<p role="status">{watch.notice}</p>}{!watch.ready?<p role="status">讀取此裝置清單…</p>:watch.saved.theme_ids.length?<Entries/>:<div className="empty"><p>尚未關注題材。</p><Link href="/themes">前往題材研究加入關注</Link></div>}</div>}
