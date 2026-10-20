const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),ts=require('typescript');
const source=ts.transpileModule(fs.readFileSync('lib/research-cache.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const release='11111111-1111-4111-8111-111111111111';
const data=value=>({release_id:release,schema_version:'research-v1',data:{value}});
function environment(fetch){
  let now=1000;class Clock extends Date{static now(){return now}}
  const exports={};vm.runInNewContext(source,{exports,URL,AbortController,DOMException,queueMicrotask,Date:Clock,fetch,window:{dispatchEvent(){}},Event});
  return {...exports,advance:amount=>{now+=amount}};
}
function response(value,tag='"one"',control='public,max-age=86400'){return new Response(JSON.stringify(data(value)),{headers:{ETag:tag,'Cache-Control':control}})}
const path='/api/v2/companies/company-test?release_id='+release;

test('normalized identical requests share work; releasing one consumer preserves another',async()=>{
  let resolve,count=0,signal;
  const cache=environment((url,options)=>{count++;signal=options.signal;return new Promise(done=>resolve=done)});
  const a=cache.acquireResearch(cache.researchKey(path+'&limit=1'));
  const b=cache.acquireResearch(cache.researchKey('/api/v2/companies/company-test?limit=1&release_id='+release));
  a.release();await Promise.resolve();assert.equal(signal.aborted,false);assert.equal(count,1);
  resolve(response('shared'));assert.equal((await b.promise).payload.data.value,'shared');b.release();
});

test('completed cache is bounded to 100 and evicts the least recently used request',async()=>{
  let calls=0;const cache=environment(async()=>{calls++;return response('ok')});
  for(let i=0;i<100;i++)await cache.acquireResearch(path+'&item='+i).promise;
  await cache.acquireResearch(path+'&item=0').promise;
  await cache.acquireResearch(path+'&item=100').promise;
  await cache.acquireResearch(path+'&item=0').promise;assert.equal(calls,101);
  await cache.acquireResearch(path+'&item=1').promise;assert.equal(calls,102);
});

test('dynamic comparison caps freshness at 30 seconds, revalidates 304, and adopts revisions',async()=>{
  let count=0,revision=1;const seen=[];
  const cache=environment(async(url,options)=>{count++;seen.push(options.headers);return revision===1&&count>1?new Response(null,{status:304,headers:{ETag:'"one"','Cache-Control':'public,max-age=86400'}}):response(revision,revision===1?'"one"':'"two"')});
  const key='/api/v2/compare?release_id='+release+'&company_ids=company-a,company-b';
  await cache.acquireResearch(key).promise;cache.advance(29999);await cache.acquireResearch(key).promise;assert.equal(count,1);
  cache.advance(2);const same=await cache.acquireResearch(key).promise;assert.equal(same.payload.data.value,1);assert.equal(seen[1]['If-None-Match'],'"one"');
  revision=2;cache.advance(30001);assert.equal((await cache.acquireResearch(key).promise).payload.data.value,2);
  cache.resetDynamicResearch();await cache.acquireResearch(key).promise;assert.equal(count,4);
});

test('orphan cancellation cannot populate or overwrite a new generation of the same key',async()=>{
  const resolves=[];const cache=environment(()=>new Promise(done=>resolves.push(done)));
  const old=cache.acquireResearch(path);const rejected=assert.rejects(old.promise,{name:'AbortError'});
  old.release();await Promise.resolve();const next=cache.acquireResearch(path);
  resolves[0](response('old'));await rejected;resolves[1](response('new','"new"'));
  await next.promise;assert.equal((await cache.acquireResearch(path).promise).payload.data.value,'new');next.release();
});

test('no-store, unpinned, wrong-version and failed responses never enter success cache',async()=>{
  let count=0;const cache=environment(async()=>{count++;return response('ok','"one"','no-store')});
  await cache.acquireResearch(path).promise;await cache.acquireResearch(path).promise;assert.equal(count,2);
  const unpinned=environment(async()=>{count++;return response('ok')});
  await unpinned.acquireResearch('/api/v2/companies/company-test').promise;await unpinned.acquireResearch('/api/v2/companies/company-test').promise;assert.equal(count,4);
  let failed=true;const failure=environment(async()=>failed?new Response(JSON.stringify({message:'unavailable'}),{status:503}):response('recovered'));
  await assert.rejects(failure.acquireResearch(path).promise);failed=false;assert.equal((await failure.acquireResearch(path).promise).payload.data.value,'recovered');
  const mismatch=environment(async()=>new Response(JSON.stringify({...data('wrong'),release_id:'other'})));
  await assert.rejects(mismatch.acquireResearch(path).promise);assert.equal(mismatch.peekResearch(path),undefined);
  assert.throws(()=>cache.researchKey('/api/admin/session'));assert.throws(()=>cache.researchKey('https://evil.invalid/api/v2/companies'));
});

test('static data survives validation failure, retries failures, and never crosses releases',async()=>{
  let fail=false,calls=0;const cache=environment(async()=>{calls++;return fail?new Response('{}',{status:503}):response('original')});
  await cache.acquireResearch(path).promise;fail=true;
  await assert.rejects(cache.acquireResearch(path,true).promise);assert.equal(cache.peekResearch(path).payload.data.value,'original');
  await assert.rejects(cache.acquireResearch(path,true).promise);assert.equal(calls,3);
  assert.equal(cache.peekResearch(path.replace(release,'22222222-2222-4222-8222-222222222222')),undefined);
});
