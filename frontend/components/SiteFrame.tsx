'use client';
import {usePathname} from 'next/navigation';
import {Shell} from './Shell';
import {WatchlistProvider} from '@/lib/watchlist';

export function SiteFrame({children}:{children:React.ReactNode}) {
  const pathname=usePathname();
  if(pathname.startsWith('/next')) return <main id="main">{children}</main>;
  return <WatchlistProvider><Shell>{children}</Shell></WatchlistProvider>;
}
