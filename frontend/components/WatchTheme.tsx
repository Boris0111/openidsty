'use client';
import {useApi} from '@/lib/api';
import {useWatchlist} from '@/lib/watchlist';
import type {UpdatesResponse} from '@/lib/types';
export function WatchTheme({id}:{id:string}){
  const watch=useWatchlist(),api=useApi<UpdatesResponse>(`/api/theme-updates?ids=${encodeURIComponent(id)}`),item=api.data?.items[0];
  const followed=watch.saved.theme_ids.includes(id);
  return <div className="watch-theme"><button disabled={!watch.ready||(!followed&&!item?.available)} onClick={()=>followed?watch.remove(id):item&&watch.follow(item)}>{followed?'移除此裝置關注':'加入此裝置關注'}</button>{item?.available&&<small>目前 v{item.version_number??'未建立'}；指標取得 {item.available_indicator_count||0}／{item.indicator_count||0}；候選 {item.candidate_count||0}，發布日待確認 {item.unknown_date_count||0}。首次加入以此回應建立已讀基準。</small>}{api.error&&<small role="alert">更新摘要無法取得，請稍後重試。</small>}{watch.notice&&<p role="status" className="data-note">{watch.notice}</p>}</div>;
}
