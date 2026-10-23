'use client';
import {useResearchManifest} from '@/lib/research-manifest';
import {ResearchWatchButton} from './ResearchWatch';
import {PUBLIC_SNAPSHOT} from '@/lib/public-snapshot';

/** The public snapshot has no update checks, so it offers no watchlist. */
export function WatchTheme(props:{id:string;name:string}){return PUBLIC_SNAPSHOT?null:<ThemeWatch {...props}/>}

/** Theme pages use the same device watchlist as the research pages; the baseline is the release now published. */
function ThemeWatch({id,name}:{id:string;name:string}){
  const manifest=useResearchManifest('theme:'+id);
  const release=manifest.data?.release_id;
  if(!release)return manifest.error?<small role="alert">收藏功能暫時無法使用，請重新整理後再試。</small>:null;
  return <div className="watch-theme"><ResearchWatchButton kind="theme" id={'theme-'+id} name={name} release={release}/></div>;
}
