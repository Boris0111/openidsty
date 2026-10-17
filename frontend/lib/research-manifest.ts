'use client';
import {useEffect} from 'react';
import {useResearch} from './research-api';

export function useResearchManifest(navigation:string){
  const manifest=useResearch<{published_at:string;generation:number}>('/api/v2/manifest');
  useEffect(()=>{manifest.refresh()},[navigation,manifest.refresh]);
  useEffect(()=>{
    const timer=setInterval(()=>{if(document.visibilityState==='visible')manifest.refresh()},60000);
    return()=>clearInterval(timer);
  },[manifest.refresh]);
  return manifest;
}
