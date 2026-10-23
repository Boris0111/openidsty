import {PUBLIC_SNAPSHOT,SNAPSHOT_RELEASE} from './public-snapshot';
import {snapshotRead} from './snapshot-routes';

// Snapshot files never change under one release path, so one read per page load is enough.
const files=new Map<string,Promise<unknown|null>>();
function load(path:string){
  let pending=files.get(path);
  if(!pending){
    pending=fetch(`/snapshot/${SNAPSHOT_RELEASE}/${path}`,{credentials:'omit'}).then(response=>{
      if(response.status===404)return null;
      if(!response.ok)throw new Error('公開版資料暫時無法讀取，請重新整理。');
      return response.json();
    });
    files.set(path,pending);
    pending.catch(()=>files.delete(path));
  }
  return pending;
}

/** Reader GETs: the private API in the app, the exported snapshot in the public static build. */
export async function readerFetch(key:string,init?:RequestInit):Promise<Response>{
  if(!PUBLIC_SNAPSHOT)return fetch(key,init);
  const {status,body}=await snapshotRead(key,SNAPSHOT_RELEASE,load);
  if(init?.signal?.aborted)throw new DOMException('Aborted','AbortError');
  return new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json','Cache-Control':status===200?'public,max-age=86400':'no-store'}});
}
