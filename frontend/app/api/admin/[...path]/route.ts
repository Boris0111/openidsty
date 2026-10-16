import {NextRequest} from 'next/server';
import {proxyAdmin} from '@/lib/admin-proxy';
export const dynamic='force-dynamic';
export const runtime='nodejs';
type Context={params:Promise<{path:string[]}>};
async function handler(request:NextRequest,context:Context){return proxyAdmin(request,(await context.params).path)}
export {handler as GET,handler as POST,handler as PATCH,handler as DELETE};
