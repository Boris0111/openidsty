const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),ts=require('typescript');
const source=ts.transpileModule(fs.readFileSync('lib/snapshot-routes.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const loaded={};vm.runInNewContext(source,{exports:loaded,URL,URLSearchParams});
// Values built inside the vm context have its own Array prototype; compare them as plain JSON.
const plain=value=>value===undefined?value:JSON.parse(JSON.stringify(value));
const routes=Object.fromEntries(Object.entries(loaded).map(([name,fn])=>[name,(...args)=>{const value=fn(...args);return value&&typeof value.then==='function'?value.then(plain):plain(value)}]));
const {release,cases}=JSON.parse(fs.readFileSync('tests/static/route-cases.json','utf8'));
const head={release_id:release,schema_version:'research-v1'};
const summary=(id,kind='company')=>({id,kind,name:id,summary:'',reviewed:null});
const query=value=>new URLSearchParams(value);

test('route table matches the cases the backend export is tested against',()=>{
  for(const [key,expected] of cases)assert.deepEqual(routes.snapshotRoute(key,release),expected,key);
});

const directory={...head,items:['company-a','company-b','company-c','company-d'].map(id=>summary(id)),
  filters:{market:{TW:['company-a','company-c','company-d'],US:[]},role:{'role-x':['company-c','company-d','company-b']},category:{'application-y':['company-d','company-a']}}};

test('directory filters intersect in directory order and page by the last id',()=>{
  const first=routes.directoryPage(directory,query('market=TW&role=role-x&limit=1'));
  assert.equal(first.status,200);
  assert.deepEqual(first.body.data,{items:[summary('company-c')],next_cursor:'company-c',has_more:true});
  const last=routes.directoryPage(directory,query('market=TW&role=role-x&limit=1&cursor=company-c'));
  assert.deepEqual(last.body.data,{items:[summary('company-d')],next_cursor:null,has_more:false});
  assert.deepEqual(routes.directoryPage(directory,query('market=TW&category=application-y')).body.data.items.map(item=>item.id),['company-a','company-d']);
  assert.deepEqual(routes.directoryPage(directory,query('market=US')).body.data,{items:[],next_cursor:null,has_more:false});
  assert.equal(routes.directoryPage(directory,query('')).body.data.items.length,4);
});

test('directory rejects what the API rejects and marks unexported filters',()=>{
  assert.equal(routes.directoryPage(directory,query('market=XX')).body.code,'invalid-market');
  assert.equal(routes.directoryPage(directory,query('limit=101')).status,422);
  assert.equal(routes.directoryPage(directory,query('cursor=company-z')).body.code,'invalid-cursor');
  assert.equal(routes.directoryPage(directory,query('role=role-unknown')).body.code,'not-in-snapshot');
});

const column=id=>({...head,data:{...summary(id),products:[],risks:null}});
const files={'v2/compare/company-a.json':column('company-a'),'v2/compare/company-b.json':column('company-b'),
  'v2/companies/company-a.json':{...head,data:summary('company-a')},'v2/directory/companies.json':directory,
  'v2/resolve.json':{release_id:release,keys:{'2330':{status:200,body:{...head,data:summary('company-a')}},
    AMBIGUOUS:{status:409,body:{code:'ambiguous-identity',message:'這個入口對應多個主體，請選擇公司。',candidates:[summary('company-a'),summary('company-b')]}}}}};
const load=async path=>Object.hasOwn(files,path)?files[path]:null;
const read=key=>routes.snapshotRead(key,release,load);

test('comparison keeps request order and the API input checks',async()=>{
  const pair=await read('/api/v2/compare?company_ids=company-b%2Ccompany-a&release_id='+release);
  assert.deepEqual(pair.body,{...head,data:{companies:[column('company-b').data,column('company-a').data]}});
  for(const ids of ['company-a','company-a,company-a','a,b,c,d,e'])
    assert.equal((await read('/api/v2/compare?'+query({company_ids:ids,release_id:release}))).body.code,'invalid-comparison',ids);
  assert.equal((await read('/api/v2/compare?'+query({company_ids:'company-a,company-z',release_id:release}))).status,404);
});

test('files, other releases and excluded data each answer distinctly',async()=>{
  assert.deepEqual(await read('/api/v2/companies/company-a?release_id='+release),{status:200,body:files['v2/companies/company-a.json']});
  assert.equal((await read('/api/v2/companies/company-z?release_id='+release)).body.code,'not-in-snapshot');
  assert.equal((await read('/api/v2/companies/company-a?release_id=11111111-1111-4111-8111-111111111111')).body.code,'release-not-in-snapshot');
  assert.equal((await read('/api/v2/events?release_id='+release)).body.code,'not-in-snapshot');
  const missing=await read('/api/coverage');assert.equal(missing.status,404);assert.equal(missing.body.detail,missing.body.message);
});

test('resolve answers tickers, ambiguity and research IDs like the API',async()=>{
  assert.equal((await read('/api/v2/resolve?key=2330&kind=company')).body.data.id,'company-a');
  assert.equal((await read('/api/v2/resolve?key=AMBIGUOUS&kind=company')).status,409);
  assert.equal((await read('/api/v2/resolve?key=company-b&kind=company')).body.data.id,'company-b');
  assert.equal((await read('/api/v2/resolve?key=9999&kind=company')).body.code,'entity-not-found');
  assert.equal((await read('/api/v2/resolve?key=x&kind=planet')).body.code,'invalid-kind');
});

const index={...head,entities:[{...summary('company-a'),roles:['晶圓代工']},{...summary('company-b'),roles:[]},{...summary('product-c','product'),roles:[]}],
  aliases:[['AMD','amd','company-a'],['AMDOCS','amdocs','company-b'],['Cold Plate','cold plate','product-c'],['台積','台積','company-b'],['台積電','台積電','company-a'],['臺積電','台積電','company-a']]};
const search=value=>routes.searchPage(index,query(value));

test('search mirrors exact, Chinese prefix or substring and English word matching',()=>{
  assert.equal(routes.normalize('  ＡＭＤ　 臺積電 '),'amd 台積電');
  assert.deepEqual(search('q=amd').body.data.items.map(item=>item.id),['company-a']);
  assert.deepEqual(search('q=plate').body.data.items.map(item=>[item.id,item.matched_aliases]),[['product-c',['Cold Plate']]]);
  // Two characters or fewer match a prefix; an exact alias always ranks first.
  assert.deepEqual(search('q=台積').body.data.items.map(item=>item.id),['company-b','company-a']);
  assert.deepEqual(search('q=積電').body.data.items,[]);
  const three=search('q=臺積電').body.data.items;
  assert.deepEqual(three.map(item=>[item.id,item.matched_aliases,item.roles]),[['company-a',['台積電','臺積電'],['晶圓代工']]]);
  assert.deepEqual(search('q=amd&kind=product').body.data.items,[]);
});

test('search pages, filters kinds and rejects empty or invalid input',()=>{
  const first=search('q=台&limit=1');
  assert.deepEqual([first.body.data.items[0].id,first.body.data.has_more],['company-a',true]);
  const second=search('q=台&limit=1&cursor='+first.body.data.next_cursor);
  assert.deepEqual([second.body.data.items[0].id,second.body.data.has_more],['company-b',false]);
  assert.equal(search('q=%20%20').body.code,'invalid-search');
  assert.equal(search('q=amd&kind=planet').body.code,'invalid-kind');
  assert.equal(search('q=amd&cursor=9-x').body.code,'invalid-cursor');
});
