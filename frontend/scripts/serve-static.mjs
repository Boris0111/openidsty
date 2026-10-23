// Serve the public build like Cloudflare Pages: /path → path.html or path/index.html, otherwise 404.html with 404.
// Usage: node scripts/serve-static.mjs [--root out] [--port 3017]
import {createServer} from 'node:http';
import {existsSync,readFileSync,statSync} from 'node:fs';
import path from 'node:path';

const argument=(name,fallback)=>process.argv.includes(name)?process.argv[process.argv.indexOf(name)+1]:fallback;
const root=path.resolve(argument('--root','out')),port=Number(argument('--port','3017'));
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.txt':'text/plain; charset=utf-8',
  '.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg','.gif':'image/gif','.ico':'image/x-icon','.woff2':'font/woff2'};

function file(pathname){
  const base=path.resolve(root,'.'+decodeURIComponent(pathname));
  if(base!==root&&!base.startsWith(root+path.sep))return null;
  for(const candidate of pathname.endsWith('/')?[path.join(base,'index.html')]:[base,base+'.html',path.join(base,'index.html')])
    if(existsSync(candidate)&&statSync(candidate).isFile())return candidate;
  return null;
}

createServer((request,response)=>{
  const {pathname}=new URL(request.url,'http://static.invalid');
  let found=null;
  try{found=file(pathname)}catch{found=null}
  const target=found||path.join(root,'404.html');
  response.writeHead(found?200:404,{'Content-Type':types[path.extname(target)]||'application/octet-stream','X-Content-Type-Options':'nosniff'});
  response.end(request.method==='HEAD'?undefined:readFileSync(target));
}).listen(port,'127.0.0.1',()=>console.log(`Serving ${root} on http://127.0.0.1:${port}`));
