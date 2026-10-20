'use client';
import {useSearchParams} from 'next/navigation';
import {useResearch,ChainIndexItem} from '@/lib/research-api';
import {mapReturn} from '@/lib/research-navigation';
import {ChainCard} from './ResearchChain';

/** The map's segment panel opens that segment's supply chains, which keep the map selection as their way back. */
export function SegmentChains({segment}:{segment:string}){
  const params=useSearchParams();
  const result=useResearch<{items:ChainIndexItem[]}>('/api/v2/chains?'+new URLSearchParams({segment:'segment-'+segment}));
  const items=result.data?.data.items;
  // Without published research (or chains under this segment) the map still reads on its own.
  if(!items?.length)return null;
  const release=result.data!.release_id,from=mapReturn('/?'+params);
  return <section className="segment-chains" aria-label="這個環節的供應鏈"><h3>這個環節的供應鏈</h3><div className="segment-chain-cards">
    {items.map(chain=><ChainCard key={chain.id} chain={chain} href={'/next?'+new URLSearchParams({focus:chain.id,release_id:release,...(from?{from}:{})})}/>)}
  </div></section>;
}
