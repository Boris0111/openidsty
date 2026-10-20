import Link from 'next/link';

/** Official and reported events and the separate rumor watch share one 事件 entry, kept as distinct tabs. */
export function EventTabs({current}:{current:'official'|'rumors'}){
  return <nav className="event-tabs" aria-label="事件類型"><Link href="/events" aria-current={current==='official'?'page':undefined}>官方與報導</Link><Link href="/next?view=observations" aria-current={current==='rumors'?'page':undefined}>傳聞觀察</Link></nav>;
}
