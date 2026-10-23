// Build the public static site from one exported snapshot, then verify it; any failure exits non-zero with no usable out/.
// Usage: npm run build:static -- --snapshot <public-snapshot/<release_id>> [--no-crawl]
import {cpSync,existsSync,mkdirSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {environmentSecrets,leakFindings} from './snapshot-leaks.mjs';

const frontend=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const argument=name=>process.argv.includes(name)?process.argv[process.argv.indexOf(name)+1]:undefined;
const snapshot=path.resolve(argument('--snapshot')||'');
const build=path.join(frontend,'.static-build'),out=path.join(frontend,'out');
// Routes that need a server or carry private data; the public build never contains them.
const EXCLUDED=['app/api','app/admin','app/coverage','app/sources','app/events','app/watchlist','app/technical-documents','app/compare','app/companies/[ticker]'];

function fail(message){rmSync(out,{recursive:true,force:true});console.error(message);process.exit(1)}
function run(command,args,options){
  const result=spawnSync(command,args,{stdio:'inherit',shell:process.platform==='win32',...options});
  if(result.status!==0)fail(`${[command,...args].join(' ')} failed (exit ${result.status})`);
}
function jsonFiles(root){
  return readdirSync(root,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?jsonFiles(path.join(root,entry.name)):entry.name.endsWith('.json')?[path.join(root,entry.name)]:[]);
}

if(!existsSync(path.join(snapshot,'manifest.json')))fail('Pass --snapshot <folder with manifest.json>, e.g. public-snapshot/<release_id>.');
const manifest=JSON.parse(readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
const release=manifest.release_id;
if(path.basename(snapshot)!==release)fail(`Snapshot folder must be named after its release ${release}.`);

// Every reference the reader can follow must exist inside the snapshot, or the public site would show gaps.
const missing=[];
const has=relative=>existsSync(path.join(snapshot,relative));
for(const file of jsonFiles(snapshot)){
  const text=readFileSync(file,'utf8'),where=path.relative(snapshot,file).split(path.sep).join('/');
  for(const [,asset] of text.matchAll(/"\/snapshot\/[0-9a-f-]{36}\/(assets\/[0-9a-f]{64}\.[a-z]+)"/g))if(!has(asset))missing.push(`${where}: ${asset}`);
  if(where.startsWith('v2/')&&!where.startsWith('v2/documents/'))
    for(const [,document,revision] of text.matchAll(/"document_id":"([^"]+)","revision_id":"([^"]+)"/g))if(!has(`v2/documents/${document}/${revision}.json`))missing.push(`${where}: document ${document}/${revision}`);
  if(where.startsWith('legacy/'))for(const [,document] of text.matchAll(/"document-id":"([^"]+)"/g))if(!has(`legacy/technical-documents/${document}.json`))missing.push(`${where}: technical document ${document}`);
}
if(missing.length)fail('Snapshot references missing files:\n'+[...new Set(missing)].slice(0,50).join('\n'));

// A fresh copy every time, except Next's build cache, which only speeds up rebuilds.
mkdirSync(build,{recursive:true});
for(const entry of readdirSync(build))if(entry!=='.next')rmSync(path.join(build,entry),{recursive:true,force:true});
for(const entry of existsSync(path.join(build,'.next'))?readdirSync(path.join(build,'.next')):[])if(entry!=='cache')rmSync(path.join(build,'.next',entry),{recursive:true,force:true});
rmSync(out,{recursive:true,force:true});
for(const item of ['app','components','lib','public','tsconfig.json','package.json','next-env.d.ts'])
  if(existsSync(path.join(frontend,item)))cpSync(path.join(frontend,item),path.join(build,item),{recursive:true});
for(const route of EXCLUDED)rmSync(path.join(build,route),{recursive:true,force:true});
writeFileSync(path.join(build,'next.config.ts'),"import type {NextConfig} from 'next';\n// Public static snapshot: no server, no image optimizer.\nconst config:NextConfig={output:'export',poweredByHeader:false,images:{unoptimized:true}};\nexport default config;\n");
run(process.execPath,[path.join(frontend,'node_modules/next/dist/bin/next'),'build'],{cwd:build,shell:false,env:{...process.env,NEXT_TELEMETRY_DISABLED:'1',
  NEXT_PUBLIC_SNAPSHOT_RELEASE:release,NEXT_PUBLIC_SNAPSHOT_PUBLISHED:manifest.published_at,STATIC_SNAPSHOT_DIR:snapshot}});
cpSync(path.join(build,'out'),out,{recursive:true});
cpSync(snapshot,path.join(out,'snapshot',release),{recursive:true});
// Cloudflare Pages allows one splat per rule, so the release segment of the asset rule is a named placeholder.
writeFileSync(path.join(out,'_headers'),`/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable
/snapshot/*
  Cache-Control: public, max-age=31536000, immutable
/snapshot/:release/assets/*
  Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; sandbox
`);

for(const route of ['api','admin','coverage','sources','events','watchlist','technical-documents','compare'])
  if(existsSync(path.join(out,route))||existsSync(path.join(out,route+'.html')))fail(`Excluded route ${route} is in the public build.`);
const findings=leakFindings(out,environmentSecrets(path.join(frontend,'..','.env.research')));
if(findings.length)fail('Public build contains private content:\n'+findings.slice(0,50).join('\n'));
if(!process.argv.includes('--no-crawl'))
  run(process.execPath,[path.join(frontend,'node_modules/@playwright/test/cli.js'),'test','--config','playwright.static.config.ts'],
    {cwd:frontend,shell:false,env:{...process.env,STATIC_SNAPSHOT_DIR:snapshot}});
console.log(`Public snapshot ${release} built in ${out}`);
