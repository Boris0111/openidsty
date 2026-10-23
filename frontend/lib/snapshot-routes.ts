/**
 * Public snapshot reads: map a normalized reader key to a snapshot file, or compute it from exported indexes.
 * The route table must agree with backend/app/public_snapshot.py (tests/static/route-cases.json checks both).
 * Search, directory and comparison only intersect, order and slice what the API exported; no query semantics live here
 * except search matching, which mirrors backend/app/research_search.py search_query and is checked by snapshot-parity.
 * No imports: node tests load this file directly.
 */
export type SnapshotLoad=(path:string)=>Promise<unknown|null>;
export type SnapshotResult={status:number;body:unknown};
export type Summary={id:string;kind:string;name:string;summary:string;reviewed:string|null};
export type Directory={release_id:string;schema_version:string;items:Summary[];filters:Record<string,Record<string,string[]>>};
export type SearchIndex={release_id:string;schema_version:string;entities:(Summary&{roles:string[]})[];aliases:[string,string,string][]};

const COLLECTIONS=['companies','products','themes','concepts','research','applications','roles','segments'];
const KINDS=['company','product','theme','concept','research','application','role','segment'];
const MARKETS=['TW','US','KR','JP','HK','DE','NL'];
const ID='[A-Za-z0-9][A-Za-z0-9._:-]{0,199}';
type Key=string|[string,string];
const ROUTES:[string,Key[]|null,string][]=[
  ['/api/industries',[],'legacy/industries.json'],
  ['/api/industries/(ai-server|semiconductor)/graph',[],'legacy/industries/{0}/graph.json'],
  ['/api/segments',[],'legacy/segments.json'],
  ['/api/segments/([a-z0-9-]+)',[],'legacy/segments/{0}.json'],
  ['/api/themes',[],'legacy/themes.json'],
  ['/api/themes/([a-z0-9-]+)',[],'legacy/themes/{0}.json'],
  ['/api/themes/([a-z0-9-]+)/assessment',[],'legacy/themes/{0}/assessment.json'],
  ['/api/technical-documents/('+ID+')',[['limit','10'],['offset','0']],'legacy/technical-documents/{0}.json'],
  ['/api/v2/manifest',[],'v2/manifest.json'],
  ['/api/v2/chains',['release_id'],'v2/chains.json'],
  ['/api/v2/chains',[['segment','segment-[a-z0-9-]+']],'v2/chains/{segment}.json'],
  ['/api/v2/graphs',[['depth','1'],'release_id',['root',ID]],'v2/graphs/{root}.json'],
  ['/api/v2/documents/('+ID+')/revisions/('+ID+')',['release_id'],'v2/documents/{0}/{1}.json'],
  ['/api/v2/('+COLLECTIONS.join('|')+')/('+ID+')',['release_id'],'v2/{0}/{1}.json'],
  ['/api/v2/resolve',null,'resolve'],
  ['/api/v2/search',null,'search'],
  ['/api/v2/compare',null,'compare'],
  ['/api/v2/('+COLLECTIONS.join('|')+')',null,'directory'],
];

export function snapshotRoute(key:string,release:string):['file',string]|['computed',string]|['release']|null{
  const url=new URL(key,'http://snapshot.invalid'),names=[...url.searchParams.keys()];
  if(new Set(names).size!==names.length)return null;
  const query=Object.fromEntries(url.searchParams);
  for(const [pattern,keys,target] of ROUTES){
    const match=new RegExp('^'+pattern+'$').exec(url.pathname);
    if(!match)continue;
    if(query.release_id!==undefined&&query.release_id.toLowerCase()!==release.toLowerCase())return ['release'];
    if(!keys)return ['computed',target];
    const wanted=keys.map(item=>typeof item==='string'?item:item[0]);
    if(names.length!==wanted.length||!wanted.every(name=>name in query)||keys.some(item=>typeof item!=='string'&&!new RegExp('^(?:'+item[1]+')$').test(query[item[0]])))continue;
    return ['file',target.replace(/\{(\w+)\}/g,(_,name:string)=>/^\d+$/.test(name)?match[Number(name)+1]:query[name])];
  }
  return null;
}

const error=(status:number,code:string,message:string):SnapshotResult=>({status,body:{code,message,detail:message,retryable:false}});
export const notInSnapshot=()=>error(404,'not-in-snapshot','公開版未收錄這項資料。');
const otherRelease=()=>error(404,'release-not-in-snapshot','這個連結指定的研究版本不在公開版內；公開版只收錄一個已發布版本。');
const envelope=(index:{release_id:string;schema_version:string},data:unknown):SnapshotResult=>({status:200,body:{release_id:index.release_id,schema_version:index.schema_version,data}});
function limitOf(value:string|null){
  if(value===null)return 50;
  return /^\d{1,3}$/.test(value)&&Number(value)>=1&&Number(value)<=100?Number(value):null;
}

/** Same as research_compile.normalize: NFKC, 臺→台, casefold and collapsed whitespace. */
export function normalize(value:string){return value.normalize('NFKC').replaceAll('臺','台').toLowerCase().split(/\s+/).filter(Boolean).join(' ')}

export function directoryPage(directory:Directory,params:URLSearchParams):SnapshotResult{
  const limit=limitOf(params.get('limit'));
  if(limit===null)return error(422,'invalid-request','查詢條件不正確。');
  const market=params.get('market');
  if(market&&!MARKETS.includes(market))return error(422,'invalid-market','市場條件不正確。');
  let items=directory.items;
  for(const name of ['market','role','category']){
    const value=params.get(name);
    if(!value)continue;
    const members=directory.filters[name]?.[value];
    if(!members)return notInSnapshot();
    const allowed=new Set(members);items=items.filter(item=>allowed.has(item.id));
  }
  const cursor=params.get('cursor');
  const start=cursor?items.findIndex(item=>item.id===cursor)+1:0;
  if(cursor&&start===0)return error(422,'invalid-cursor','分頁識別格式不正確。');
  const page=items.slice(start,start+limit),more=items.length>start+limit;
  return envelope(directory,{items:page,next_cursor:more?page[page.length-1].id:null,has_more:more});
}

export function searchPage(index:SearchIndex,params:URLSearchParams):SnapshotResult{
  const q=normalize(params.get('q')||''),kind=params.get('kind'),limit=limitOf(params.get('limit'));
  if((params.get('q')||'').length>100||limit===null)return error(422,'invalid-request','查詢條件不正確。');
  if(kind&&!KINDS.includes(kind))return error(422,'invalid-kind','研究類別不正確。');
  if(!q)return error(422,'invalid-search','請輸入公司、產品、代號或術語。');
  const chinese=/[㐀-鿿]/.test(q),short=[...q].length<=2;
  const escaped=q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  // PostgreSQL [:alnum:] is approximated by Unicode letters and numbers; snapshot-parity compares the real results.
  const boundary=new RegExp('(^|[^\\p{L}\\p{N}_])'+escaped+'([^\\p{L}\\p{N}_]|$)','u');
  const hits=new Map<string,{rank:number;aliases:string[]}>();
  for(const [alias,normalized,entity] of index.aliases){
    const exact=normalized===q;
    const matched=exact||(chinese?(short?normalized.startsWith(q):normalized.includes(q)):boundary.test(normalized));
    if(!matched)continue;
    const rank=exact?0:chinese&&short?1:2,hit=hits.get(entity)||{rank,aliases:[]};
    hit.rank=Math.min(hit.rank,rank);
    if(!hit.aliases.includes(alias))hit.aliases.push(alias);
    hits.set(entity,hit);
  }
  const order=new Map(index.entities.map((entity,position)=>[entity.id,position]));
  let rows=index.entities.filter(entity=>hits.has(entity.id)&&(!kind||entity.kind===kind))
    .map(entity=>({entity,...hits.get(entity.id)!})).sort((a,b)=>a.rank-b.rank||order.get(a.entity.id)!-order.get(b.entity.id)!);
  const cursor=params.get('cursor');
  if(cursor){
    const separator=cursor.indexOf('-'),rank=Number(cursor.slice(0,separator)),last=cursor.slice(separator+1);
    if(!['0','1','2'].includes(cursor.slice(0,separator))||!order.has(last))return error(422,'invalid-cursor','搜尋分頁識別不正確。');
    rows=rows.filter(row=>row.rank>rank||row.rank===rank&&order.get(row.entity.id)!>order.get(last)!);
  }
  const page=rows.slice(0,limit),more=rows.length>limit;
  const items=page.map(({entity,aliases})=>({id:entity.id,kind:entity.kind,name:entity.name,summary:entity.summary,reviewed:entity.reviewed,matched_aliases:aliases,roles:entity.roles}));
  return envelope(index,{items,has_more:more,next_cursor:more?page[page.length-1].rank+'-'+page[page.length-1].entity.id:null});
}

export function comparePage(columns:({release_id:string;schema_version:string;data:unknown}|null)[]):SnapshotResult{
  if(columns.some(column=>!column))return error(404,'company-not-found','找不到這家公司。');
  return envelope(columns[0]!,{companies:columns.map(column=>column!.data)});
}

export function compareIds(params:URLSearchParams){
  const value=params.get('company_ids')||'',ids=value.split(',');
  if(value.length>850||ids.length<2||ids.length>4||new Set(ids).size!==ids.length)return null;
  return ids;
}

/** Answer one reader GET from the snapshot: the same status and body the private API gives for this release. */
export async function snapshotRead(key:string,release:string,load:SnapshotLoad):Promise<SnapshotResult>{
  const route=snapshotRoute(key,release);
  if(!route)return notInSnapshot();
  if(route[0]==='release')return otherRelease();
  if(route[0]==='file'){const body=await load(route[1]);return body===null?notInSnapshot():{status:200,body}}
  const url=new URL(key,'http://snapshot.invalid'),params=url.searchParams;
  if(route[1]==='directory'){
    const directory=await load('v2/directory/'+url.pathname.split('/')[3]+'.json') as Directory|null;
    return directory?directoryPage(directory,params):notInSnapshot();
  }
  if(route[1]==='search'){
    const index=await load('v2/search.json') as SearchIndex|null;
    return index?searchPage(index,params):notInSnapshot();
  }
  if(route[1]==='compare'){
    const ids=compareIds(params);
    if(!ids)return error(422,'invalid-comparison','比較須選擇 2 至 4 家不同公司。');
    if(ids.some(id=>!new RegExp('^'+ID+'$').test(id)))return error(404,'company-not-found','找不到這家公司。');
    return comparePage(await Promise.all(ids.map(id=>load('v2/compare/'+id+'.json'))) as ({release_id:string;schema_version:string;data:unknown}|null)[]);
  }
  const kind=params.get('kind')||'',value=params.get('key')||'';
  if(!KINDS.includes(kind))return error(422,'invalid-kind','研究類別不正確。');
  if(kind!=='company'||!value)return notInSnapshot();
  const resolved=await load('v2/resolve.json') as {release_id:string;keys:Record<string,{status:number;body:unknown}>}|null;
  if(!resolved)return notInSnapshot();
  if(Object.hasOwn(resolved.keys,value))return resolved.keys[value];
  // A company's own research ID also resolves; every ticker and legacy key was exported above.
  const companies=await load('v2/directory/companies.json') as Directory|null;
  const company=companies?.items.find(item=>item.id===value);
  return company?envelope(companies!,company):error(404,'entity-not-found','找不到這個代號或研究入口。');
}
