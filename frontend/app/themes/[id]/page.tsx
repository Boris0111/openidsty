import {readFileSync} from 'node:fs';
import path from 'node:path';
import {ThemeReading} from '@/components/ThemeReading';

/** The public static build pre-renders every exported theme; the app renders themes on request. */
export function generateStaticParams(){
  const folder=process.env.STATIC_SNAPSHOT_DIR;
  if(!folder)return [];
  return (JSON.parse(readFileSync(path.join(folder,'legacy/themes.json'),'utf8')) as {theme:string}[]).map(theme=>({id:theme.theme}));
}

export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <ThemeReading id={id}/>}
