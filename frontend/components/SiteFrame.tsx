'use client';
import {usePathname} from 'next/navigation';
import {Shell} from './Shell';
import {ResearchWatchlistProvider} from '@/lib/research-watchlist';

export function SiteFrame({children}:{children:React.ReactNode}) {
  const pathname=usePathname();
  if(pathname.startsWith('/admin')) return <main id="main">{children}</main>;
  // Map, themes, events and /next research share one shell and one device watchlist.
  return <ResearchWatchlistProvider><Shell>{children}</Shell></ResearchWatchlistProvider>;
}
