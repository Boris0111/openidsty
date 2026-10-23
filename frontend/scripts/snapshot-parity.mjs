// Compare the public snapshot's computed reads (search, directories, comparison, resolve) and stored files with the
// private API for the same release. Any difference is listed and exits non-zero.
// Usage: node scripts/snapshot-parity.mjs --snapshot <public-snapshot/<release_id>> [--api http://127.0.0.1:8010]
import {readFileSync,existsSync} from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import ts from 'typescript';

const argument=(name,fallback)=>process.argv.includes(name)?process.argv[process.argv.indexOf(name)+1]:fallback;
const snapshot=path.resolve(argument('--snapshot','')),api=argument('--api','http://127.0.0.1:8010');
const frontend=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=ts.transpileModule(readFileSync(path.join(frontend,'lib/snapshot-routes.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const routes={exports:{}};new Function('require','module','exports',source)(createRequire(import.meta.url),routes,routes.exports);
const {snapshotRead}=routes.exports;

const read=relative=>JSON.parse(readFileSync(path.join(snapshot,relative),'utf8'));
const load=async relative=>existsSync(path.join(snapshot,relative))?read(relative):null;
const {release_id:release}=read('manifest.json');
const counts={},mismatches=[];
let seed=20261023;const random=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
const pick=(items,n)=>{const copy=[...items],out=[];while(copy.length&&out.length<n)out.push(copy.splice(Math.floor(random()*copy.length),1)[0]);return out};

async function remote(key){
  const response=await fetch(api+key,{headers:{Accept:'application/json'}});
  return {status:response.status,body:await response.json().catch(()=>null)};
}
// A key the browser would send: the path plus its parameters sorted, as research-cache normalizes them.
function key(pathname,params){const query=new URLSearchParams(params);query.sort();return pathname+(query.size?'?'+query:'')}
async function local(requestKey){return snapshotRead(requestKey,release,load)}
function record(kind,label,expected,actual){
  counts[kind]=(counts[kind]||0)+1;
  const a=JSON.stringify(expected),b=JSON.stringify(actual);
  if(a!==b)mismatches.push(`${kind} ${label}\n  api:      ${a.slice(0,400)}\n  snapshot: ${b.slice(0,400)}`);
}
// Cursors differ by design (the API signs them, the snapshot uses the last id), so pages are compared as one list.
async function allPages(read,pathname,params){
  const items=[];let cursor=null,status=200,body=null;
  for(let page=0;page<50;page++){
    ({status,body}=await read(key(pathname,{...params,...(cursor?{cursor}:{})})));
    if(status!==200)return {status,code:body?.code};
    items.push(...body.data.items);
    if(!body.data.has_more)return {status,items};
    cursor=body.data.next_cursor;
  }
  return {status:'too-many-pages'};
}

const index=read('v2/search.json');
const queries=new Set();
for(const [alias,normalized] of index.aliases){
  queries.add(alias);
  const characters=[...normalized];queries.add(characters.slice(0,1).join(''));queries.add(characters.slice(0,2).join(''));
  for(const token of normalized.split(/[^\p{L}\p{N}]+/u))if(token)queries.add(token);
}
for(const q of [...queries].filter(q=>q.trim())){
  record('search',q,await allPages(remote,'/api/v2/search',{q,release_id:release}),await allPages(local,'/api/v2/search',{q,release_id:release}));
}
for(const q of pick([...queries].filter(q=>q.trim()),100))
  record('search-company',q,await allPages(remote,'/api/v2/search',{q,kind:'company',limit:'20',release_id:release}),await allPages(local,'/api/v2/search',{q,kind:'company',limit:'20',release_id:release}));

for(const collection of ['segments','applications','roles','products','companies','themes','concepts','research']){
  const directory=read(`v2/directory/${collection}.json`);
  const combos=[{}];
  for(const [name,values] of Object.entries(directory.filters))for(const value of Object.keys(values))combos.push({[name]:value});
  const names=Object.keys(directory.filters);
  for(let i=0;i<names.length;i++)for(let j=i+1;j<names.length;j++)
    for(const a of Object.keys(directory.filters[names[i]]))for(const b of Object.keys(directory.filters[names[j]]))combos.push({[names[i]]:a,[names[j]]:b});
  if(names.length===3)for(let n=0;n<200;n++)combos.push(Object.fromEntries(names.map(name=>[name,pick(Object.keys(directory.filters[name]),1)[0]])));
  for(const combo of combos)for(const limit of [undefined,'100']){
    const params={...combo,release_id:release,...(limit?{limit}:{})};
    record('directory',collection+' '+JSON.stringify(params),await allPages(remote,`/api/v2/${collection}`,params),await allPages(local,`/api/v2/${collection}`,params));
  }
}

const companies=index.entities.filter(entity=>entity.kind==='company').map(entity=>entity.id);
const groups=[[companies[0]],[companies[0],companies[0]],companies.slice(0,5)];
for(let n=0;n<300;n++)groups.push(pick(companies,2+Math.floor(random()*3)));
for(const ids of groups){
  const params={company_ids:ids.join(','),release_id:release};
  const [expected,actual]=[await remote(key('/api/v2/compare',params)),await local(key('/api/v2/compare',params))];
  record('compare',ids.join(','),{status:expected.status,body:expected.status===200?expected.body:expected.body?.code},{status:actual.status,body:actual.status===200?actual.body:actual.body?.code});
}

const resolveKeys=[...Object.keys(read('v2/resolve.json').keys),...companies,'NO-SUCH-TICKER'];
for(const value of resolveKeys){
  const params={kind:'company',key:value};
  const [expected,actual]=[await remote(key('/api/v2/resolve',params)),await local(key('/api/v2/resolve',params))];
  record('resolve',value,{status:expected.status,body:expected.status===200?expected.body:expected.body?.code},{status:actual.status,body:actual.status===200?actual.body:actual.body?.code});
}

for(const entity of index.entities){
  const collection={company:'companies',product:'products',theme:'themes',concept:'concepts',research:'research',application:'applications',role:'roles',segment:'segments'}[entity.kind];
  const detail=key(`/api/v2/${collection}/${entity.id}`,{release_id:release});
  const expected=(await remote(detail)).body;
  record('detail',entity.id,JSON.stringify(expected).replace(/\/api\/v2\/assets\/([0-9a-f]{64})\?release_id=[0-9a-f-]{36}/g,'ASSET:$1'),
    JSON.stringify((await local(detail)).body).replace(new RegExp(`/snapshot/${release}/assets/([0-9a-f]{64})\\.[a-z]+`,'g'),'ASSET:$1'));
  const graph=key('/api/v2/graphs',{root:entity.id,depth:'1',release_id:release});
  const remoteGraph=(await remote(graph)).body;delete remoteGraph.data.list_url;
  record('graph',entity.id,remoteGraph,(await local(graph)).body);
}

console.log(JSON.stringify({release,compared:counts,mismatches:mismatches.length},null,1));
if(mismatches.length){console.error(mismatches.slice(0,30).join('\n'));process.exit(1)}
