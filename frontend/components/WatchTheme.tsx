'use client';
import {useResearchManifest} from '@/lib/research-manifest';
import {ResearchWatchButton} from './ResearchWatch';

/** Theme pages use the same device watchlist as the research pages; the baseline is the release now published. */
export function WatchTheme({id,name}:{id:string;name:string}){
  const manifest=useResearchManifest('theme:'+id);
  const release=manifest.data?.release_id;
  if(!release)return manifest.error?<small role="alert">收藏功能暫時無法使用，請重新整理後再試。</small>:null;
  return <div className="watch-theme"><ResearchWatchButton kind="theme" id={'theme-'+id} name={name} release={release}/></div>;
}
