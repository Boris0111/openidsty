import { NextRequest } from 'next/server';
export const dynamic = 'force-dynamic';
export async function GET(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const {path} = await context.params;
  const allowed = ['industries','segments','themes','theme-updates','technical-documents','search','coverage','companies','compare','events','sources','health'];
  const publicV2 = ['manifest','catalog','chains','search','resolve','companies','products','themes','concepts','research','applications','roles','segments','documents','assets','graphs','impact','events','observations','compare'];
  if ((!allowed.includes(path[0]) && !(path[0]==='v2' && publicV2.includes(path[1]))) || path.some(part=>part==='.'||part==='..'||part.includes('/')||part.includes('\\'))) return Response.json({detail:'找不到 API'}, {status:404,headers:{'Cache-Control':'no-store'}});
  try {
    const origin = process.env.API_ORIGIN || 'http://127.0.0.1:8010';
    const url = `${origin}/api/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`;
    const conditional=request.headers.get('if-none-match');
    const result = await fetch(url, {cache:'no-store', signal:AbortSignal.timeout(15000),headers:conditional&&conditional.length<=4096?{'If-None-Match':conditional}:{}});
    const headers = new Headers({'Content-Type':result.headers.get('content-type') || 'application/json', 'Cache-Control':result.headers.get('cache-control') || 'no-store'});
    for(const name of ['ETag','Age','Vary','X-Request-ID','Retry-After','Content-Security-Policy','X-Content-Type-Options']) {
      const value=result.headers.get(name); if(value) headers.set(name,value);
    }
    const disposition = result.headers.get('content-disposition');
    if(disposition) headers.set('Content-Disposition',disposition);
    return new Response(result.status===304?null:await result.arrayBuffer(), {status:result.status,headers});
  } catch {
    return Response.json({detail:'資料服務暫時無法連線，請稍後重試'}, {status:503,headers:{'Cache-Control':'no-store'}});
  }
}

// The only reader POST: a side-effect-free favourites update summary. The body is never logged.
const UPDATES_LIMIT = 64 * 1024;
export async function POST(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const {path} = await context.params;
  const noStore = {'Cache-Control':'no-store'};
  if (path.join('/') !== 'v2/updates/query') return Response.json({detail:'找不到 API'}, {status:404,headers:noStore});
  if (!(request.headers.get('content-type') || '').startsWith('application/json')) return Response.json({code:'invalid-request',message:'查詢格式不正確，請確認條件。'}, {status:415,headers:noStore});
  const body = await request.arrayBuffer();
  if (body.byteLength > UPDATES_LIMIT) return Response.json({code:'invalid-request',message:'收藏更新查詢超過大小限制。'}, {status:413,headers:noStore});
  try {
    const origin = process.env.API_ORIGIN || 'http://127.0.0.1:8010';
    const result = await fetch(`${origin}/api/v2/updates/query`, {method:'POST', cache:'no-store', signal:AbortSignal.timeout(15000), headers:{'Content-Type':'application/json'}, body});
    const headers = new Headers({'Content-Type':result.headers.get('content-type') || 'application/json', ...noStore});
    for(const name of ['X-Request-ID','Retry-After','X-Content-Type-Options']) {const value=result.headers.get(name); if(value) headers.set(name,value)}
    return new Response(await result.arrayBuffer(), {status:result.status,headers});
  } catch {
    return Response.json({detail:'資料服務暫時無法連線，請稍後重試'}, {status:503,headers:noStore});
  }
}
