import {NextRequest} from 'next/server';
import {randomUUID} from 'node:crypto';

function failure(status:number,code:string,message:string) {
  return Response.json({code,message,request_id:randomUUID(),retryable:status===503},
    {status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
}

// Deliberately separate from the public GET proxy. Each admin resource opts in.
export async function proxyAdmin(request:NextRequest,path:string[]) {
  const resource=path.join('/');
  const uuid='[0-9a-fA-F-]{36}';
  const permitted=resource==='session'?['GET','POST','DELETE']:resource==='drafts'?['GET','POST']:['drafts/render-document','drafts/asset-upload'].includes(resource)?['POST']:new RegExp(`^drafts/${uuid}$`).test(resource)?['GET','PATCH']:new RegExp(`^drafts/${uuid}/(export|document|diff|preview)$`).test(resource)?['GET']:new RegExp(`^drafts/${uuid}/(import|validate)$`).test(resource)?['POST']:new RegExp(`^drafts/${uuid}/assets/[0-9a-f]{64}$`).test(resource)?['GET']:[];
  if(!permitted.includes(request.method))return failure(404,'admin-resource-not-found','找不到這項管理功能。');
  const allowed=(process.env.RESEARCH_ADMIN_ORIGINS||'').split(',').filter(Boolean);
  if(!allowed.length)return failure(503,'admin-unavailable','管理入口尚未完成設定。');
  const host=request.headers.get('host');
  const origin=allowed.find(value=>{try{return new URL(value).host===host}catch{return false}});
  const supplied=request.headers.get('origin');
  if(!origin||(supplied&&supplied!==origin)||(request.method!=='GET'&&!supplied)||request.headers.get('sec-fetch-site')==='cross-site') {
    return failure(403,'admin-origin-denied','此來源無法使用管理入口。');
  }
  const headers=new Headers({'Origin':origin});
  for(const name of ['Content-Type','X-CSRF-Token','Sec-Fetch-Site','If-Match']) {
    const value=request.headers.get(name);if(value)headers.set(name,value);
  }
  const cookies=(request.headers.get('cookie')||'').split(';').map(value=>value.trim())
    .filter(value=>/^(industryflow_owner|industryflow_login_csrf)=/.test(value));
  if(cookies.length)headers.set('Cookie',cookies.join('; '));
  const chunks:Uint8Array[]=[];let size=0;
  if(['POST','PATCH'].includes(request.method)&&request.body) {
    const reader=request.body.getReader();
    while(true) {
      const {value,done}=await reader.read();if(done)break;
      size+=value.byteLength;
      if(size>(resource==='session'?8192:resource==='drafts/asset-upload'?10*1024*1024:5*1024*1024)){await reader.cancel();return failure(413,'body-too-large','資料超過大小限制。')}
      chunks.push(value);
    }
  }
  const body=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){body.set(chunk,offset);offset+=chunk.byteLength}
  try {
    const result=await fetch(`${process.env.API_ORIGIN||'http://127.0.0.1:8014'}/api/admin/${resource}${request.nextUrl.search}`,{
      method:request.method,headers,body:['POST','PATCH'].includes(request.method)?body:undefined,
      cache:'no-store',redirect:'error',signal:AbortSignal.any([request.signal,AbortSignal.timeout(60000)])});
    const forwarded=new Headers({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    for(const name of ['Content-Type','Content-Disposition','Content-Security-Policy','ETag','X-Request-ID','Retry-After']){const value=result.headers.get(name);if(value)forwarded.set(name,value)}
    for(const value of result.headers.getSetCookie())forwarded.append('Set-Cookie',value);
    return new Response(await result.arrayBuffer(),{status:result.status,headers:forwarded});
  }catch{return failure(503,'admin-unavailable','管理服務暫時無法連線，請稍後再試。')}
}

export function proxySession(request:NextRequest){return proxyAdmin(request,['session'])}
