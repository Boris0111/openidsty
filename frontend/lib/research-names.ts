'use client';
import {useApi} from './api';
import type {SegmentLink,Theme} from './types';
export function useResearchNames(){
  const segments=useApi<SegmentLink[]>('/api/segments');
  const themes=useApi<Theme[]>('/api/themes');
  return Object.fromEntries([...(segments.data||[]).map(s=>[s.id,s.name]),...(themes.data||[]).map(t=>[t.theme,t.name_zh])]);
}
