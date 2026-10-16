'use client';
import {useApi} from '@/lib/api';
import {useWatchlist} from '@/lib/watchlist';
import type {UpdatesResponse} from '@/lib/types';
export function WatchTheme({id}:{id:string}){
  const watch=useWatchlist(),api=useApi<UpdatesResponse>(`/api/theme-updates?ids=${encodeURIComponent(id)}`),item=api.data?.items[0];
  const followed=watch.saved.theme_ids.includes(id);
  return <div className="watch-theme"><button disabled={!watch.ready||(!followed&&!item?.available)} onClick={()=>followed?watch.remove(id):item&&watch.follow(item)}>{followed?'移除此裝置關注':'加入此裝置關注'}</button>{api.error&&<small role="alert">關注功能暫時無法使用，請重新整理後再試。</small>}{watch.notice&&<p role="status" className="data-note">{watch.notice}</p>}</div>;
}
