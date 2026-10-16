'use client';
import Link from 'next/link';
import {useApi} from '@/lib/api';
import type {Theme,Classification} from '@/lib/types';

export function DirectThemes({links}:{links:Classification[]}) {
  const themes=useApi<Theme[]>('/api/themes');
  return <section className="event-theme-assessments"><h2>直接相關題材的判讀</h2><div className="theme-tags">{links.filter(t=>t.relevance==='direct').map(t=><Link key={t.id} href={`/themes/${t.id}#assessment`}>閱讀{themes.data?.find(theme=>theme.theme===t.id)?.name_zh||'名稱待補'}判讀</Link>)}</div></section>;
}
