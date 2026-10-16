import { NextRequest } from 'next/server';
export const dynamic = 'force-dynamic';
export async function GET(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const {path} = await context.params;
  const allowed = ['industries','segments','themes','theme-updates','technical-documents','search','coverage','companies','compare','events','sources','health'];
  if (!allowed.includes(path[0])) return Response.json({detail:'找不到 API'}, {status:404,headers:{'Cache-Control':'no-store'}});
  try {
    const origin = process.env.API_ORIGIN || 'http://127.0.0.1:8010';
    const url = `${origin}/api/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`;
    const result = await fetch(url, {cache:'no-store', signal:AbortSignal.timeout(15000)});
    const headers = new Headers({'Content-Type':result.headers.get('content-type') || 'application/json', 'Cache-Control':'no-store'});
    const disposition = result.headers.get('content-disposition');
    if(disposition) headers.set('Content-Disposition',disposition);
    return new Response(await result.text(), {status:result.status,headers});
  } catch {
    return Response.json({detail:'資料服務暫時無法連線，請稍後重試'}, {status:503,headers:{'Cache-Control':'no-store'}});
  }
}
