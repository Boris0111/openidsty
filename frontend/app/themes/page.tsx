'use client';
import Link from 'next/link';
import {useApi,themeStatus} from '@/lib/api';
import type {Theme} from '@/lib/types';
import {Status} from '@/components/Status';
import {confidenceLabel} from '@/components/Assessment';
import {WatchTheme} from '@/components/WatchTheme';
export default function Page(){
  const api=useApi<Theme[]>('/api/themes');
  return <div className="page-content"><div className="page-heading"><h1>題材研究</h1><p>從跨環節技術變化切入；狀態保留原始查核基準，近期事件持續更新。</p></div><Status {...api}/><div className="theme-list">{api.data?.map(t=><article key={t.theme}><div><h2><Link href={`/themes/${t.theme}`}>{t.name_zh}</Link></h2><span className="theme-status">{themeStatus[t.status]}</span></div><p>{t.assessment_summary?.summary||t.prose.split('## 題材範圍')[1]?.split('##')[0]?.trim().split('\n\n')[0].slice(0,200)}</p>{t.assessment_summary?.confidence&&<p className={`confidence ${t.assessment_summary.confidence}`}>{confidenceLabel[t.assessment_summary.confidence]}</p>}<small>狀態查核 {t.checked||'未提供'}　涵蓋 {t.segments.length} 個環節</small><WatchTheme id={t.theme}/></article>)}</div></div>
}
