// Same rules as backend/app/public_snapshot.py leak_findings; tests/snapshot-leaks.node.cjs keeps the key lists equal.
import {readdirSync,readFileSync,statSync} from 'node:fs';
import path from 'node:path';

export const FORBIDDEN_KEYS=['events','undated_candidates','candidate_count','unknown_date_count','runtime','history','last_attempt','last_success','current_version_id','list_url'];
// In an assessment `candidates` are event candidates; an ambiguous resolve lists company candidates, which is public.
export const ASSESSMENT_FORBIDDEN_KEYS=['candidates'];
const TEXT=new Set(['.json','.html','.js','.txt','.css','']);

function files(root){
  return readdirSync(root,{withFileTypes:true}).flatMap(entry=>{
    const full=path.join(root,entry.name);
    return entry.isDirectory()?files(full):[full];
  }).sort();
}

/** Every forbidden field, private API path or secret value under a snapshot or build directory. */
export function leakFindings(root,secrets=[]){
  const findings=[],values=secrets.filter(value=>value&&value.length>=8);
  for(const file of files(root)){
    const name=path.basename(file),extension=path.extname(file);
    if(!TEXT.has(extension)&&name!=='_headers'||!statSync(file).isFile())continue;
    const text=readFileSync(file,'utf8'),where=path.relative(root,file).split(path.sep).join('/');
    if(extension==='.json'){
      const forbidden=new Set([...FORBIDDEN_KEYS,...(name==='assessment.json'?ASSESSMENT_FORBIDDEN_KEYS:[])]);
      const walk=value=>{
        if(Array.isArray(value))value.forEach(walk);
        else if(value&&typeof value==='object')for(const [key,item] of Object.entries(value)){if(forbidden.has(key))findings.push(`${where}: forbidden field ${key}`);walk(item)}
      };
      walk(JSON.parse(text));
      if(text.includes('"/api/'))findings.push(`${where}: private API path`);
    }
    for(const value of values)if(text.includes(value))findings.push(`${where}: secret value`);
  }
  return findings;
}

/** Secret values from the research service's env file, when this checkout has one. */
export function environmentSecrets(file){
  try{
    return readFileSync(file,'utf8').split(/\r?\n/).filter(line=>!line.startsWith('#')&&line.includes('='))
      .map(line=>line.split('=',2)).filter(([key])=>/PASSWORD|SECRET|TOKEN/.test(key)).map(([,value])=>value.trim()).filter(Boolean);
  }catch{return []}
}
