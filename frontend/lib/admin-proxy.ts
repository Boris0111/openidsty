import {NextRequest} from 'next/server';
import {randomUUID} from 'node:crypto';

function failure(status:number,code:string,message:string) {
  return Response.json({code,message,request_id:randomUUID(),retryable:status===503},
    {status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
}

// Deliberately separate from the public GET proxy. Each admin resource opts in.
export async function proxySession(request:NextRequest) {
  const allowed=(process.env.RESEARCH_ADMIN_ORIGINS||'').split(',').filter(Boolean);
  if(!allowed.length)return failure(503,'admin-unavailable','管理入口尚未完成設定。');
  const host=request.headers.get('host');
  const origin=allowed.find(value=>{try{return new URL(value).host===host}catch{return false}});
  const supplied=request.headers.get('origin');
  if(!origin||(supplied&&supplied!==origin)||(request.method!=='GET'&&!supplied)||request.headers.get('sec-fetch-site')==='cross-site') {
    return failure(403,'admin-origin-denied','此來源無法使用管理入口。');
  }
  const headers=new Headers({'Origin':origin});
  for(const name of ['Content-Type','X-CSRF-Token','Sec-Fetch-Site']) {
    const value=request.headers.get(name);if(value)headers.set(name,value);
  }
  const cookies=(request.headers.get('cookie')||'').split(';').map(value=>value.trim())
    .filter(value=>/^(industryflow_owner|industryflow_login_csrf)=/.test(value));
  if(cookies.length)headers.set('Cookie',cookies.join('; '));
  const chunks:Uint8Array[]=[];let size=0;
  if(request.method==='POST'&&request.body) {
    const reader=request.body.getReader();
    while(true) {
      const {value,done}=await reader.read();if(done)break;
      size+=value.byteLength;
      if(size>8192){await reader.cancel();return failure(413,'body-too-large','登入資料超過大小限制。')}
      chunks.push(value);
    }
  }
  const body=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){body.set(chunk,offset);offset+=chunk.byteLength}
  try {
    const result=await fetch(`${process.env.API_ORIGIN||'http://127.0.0.1:8014'}/api/admin/session`,{
      method:request.method,headers,body:request.method==='POST'?body:undefined,
      cache:'no-store',redirect:'error',signal:AbortSignal.any([request.signal,AbortSignal.timeout(15000)])});
    const forwarded=new Headers({'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    for(const name of ['X-Request-ID','Retry-After']){const value=result.headers.get(name);if(value)forwarded.set(name,value)}
    for(const value of result.headers.getSetCookie())forwarded.append('Set-Cookie',value);
    return new Response(await result.arrayBuffer(),{status:result.status,headers:forwarded});
  }catch{return failure(503,'admin-unavailable','管理服務暫時無法連線，請稍後再試。')}
}
