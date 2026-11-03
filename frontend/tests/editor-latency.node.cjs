// Pure parts of scripts/research_editor_latency.cjs; the drill run itself is the live measurement.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const latency=require('../../scripts/research_editor_latency.cjs');

test('nearest-rank percentile matches research_draft_bench.py',()=>{
  const values=Array.from({length:100},(_,index)=>index+1);
  assert.equal(latency.percentile(values,50),50);
  assert.equal(latency.percentile(values,95),95);
  assert.equal(latency.percentile([30,10,20],50),20);
  assert.equal(latency.percentile([7],95),7);
  assert.equal(latency.percentile([],95),null);
});

test('interactions are grouped by interactionId and assigned to the key whose window they start in',()=>{
  const starts=[100,300,500];
  const entries=[
    {name:'keydown',interactionId:11,startTime:101,duration:48},{name:'keyup',interactionId:11,startTime:180,duration:24},
    {name:'keypress',interactionId:11,startTime:102,duration:56},
    {name:'input',interactionId:0,startTime:103,duration:400}, // not an interaction: ignored
    {name:'keydown',interactionId:12,startTime:502,duration:104000},
  ];
  assert.deepEqual(latency.keyLatencies(starts,entries),[56,null,104000]);
});

test('a key never pressed has no window and does not shorten the previous one',()=>{
  const entries=[{name:'keydown',interactionId:3,startTime:150,duration:900},{name:'keydown',interactionId:4,startTime:700,duration:32}];
  assert.deepEqual(latency.keyLatencies([100,null,600],entries),[900,null,32]);
});

test('entries under 16 ms are recorded as <16 and counted as 16; timeouts are failures counted at least as the timeout',()=>{
  const keys=[{key:0,latency_ms:null,timed_out:false},{key:1,latency_ms:24,timed_out:false},{key:2,latency_ms:null,timed_out:true},
    {key:3,latency_ms:200000,timed_out:true},{key:4,latency_ms:40,timed_out:false}];
  const summary=latency.summarize(keys,180000);
  assert.deepEqual(summary.values,['<16',24,'timeout','timeout',40]);
  assert.equal(summary.below_threshold,1);
  assert.equal(summary.timeouts,2);
  assert.equal(summary.count,5);
  assert.equal(summary.max_ms,200000);
  assert.equal(summary.p50_ms,40);
  const fast=latency.summarize([{key:0,latency_ms:null,timed_out:false},{key:1,latency_ms:null,timed_out:false}],180000);
  assert.equal(fast.p95_ms,16);assert.equal(fast.timeouts,0);
});

test('trace events fall into script, style/layout, paint, GC and other',()=>{
  assert.equal(latency.category('FunctionCall'),'script');
  assert.equal(latency.category('v8.callFunction'),'script');
  assert.equal(latency.category('UpdateLayoutTree'),'style_layout');
  assert.equal(latency.category('Layout'),'style_layout');
  assert.equal(latency.category('LocalFrameView::performLayout'),'style_layout');
  assert.equal(latency.category('Blink.Style.UpdateTime'),'style_layout');
  assert.equal(latency.category('Paint'),'paint');
  assert.equal(latency.category('Blink.PrePaint.UpdateTime'),'paint');
  assert.equal(latency.category('Blink.CompositingInputs.UpdateTime'),'paint');
  assert.equal(latency.category('PaintArtifactCompositor::Update'),'paint');
  assert.equal(latency.category('GetSelectionOffsets'),'other'); // native text editing stays visible in other_top
  assert.equal(latency.category('MinorGC'),'gc');
  assert.equal(latency.category('V8.GC_SCAVENGER'),'gc');
  assert.equal(latency.category('EventDispatch'),'other');
  assert.equal(latency.category('SpellCheckRequester::requestCheckingFor'),'other');
});

test('long main-thread tasks are split by self time and the other bucket names its events',()=>{
  const main={pid:1,tid:7},other={pid:2,tid:9};
  const events=[
    {ph:'M',name:'thread_name',...main,args:{name:'CrRendererMain'}},
    {ph:'M',name:'thread_name',...other,args:{name:'CrRendererMain'}},
    // 120 ms task: 60 ms script (with a 10 ms GC inside), 30 ms layout, 10 ms paint, 20 ms task self time.
    {ph:'X',name:'RunTask',...main,ts:0,dur:120000},
    {ph:'X',name:'FunctionCall',...main,ts:1000,dur:60000},
    {ph:'X',name:'MinorGC',...main,ts:20000,dur:10000},
    {ph:'B',name:'Layout',...main,ts:70000},{ph:'E',name:'Layout',...main,ts:100000},
    {ph:'X',name:'Paint',...main,ts:100000,dur:10000},
    {ph:'X',name:'RunTask',...main,ts:200000,dur:30000}, // under 50 ms: not a long task
    {ph:'X',name:'RunTask',...other,ts:0,dur:60000}, // another renderer with less task time
    {ph:'X',name:'RunTask',...main,ts:300000,dur:80000},
    {ph:'X',name:'SpellCheckRequester::requestCheckingFor',...main,ts:300000,dur:70000},
  ];
  const summary=latency.traceSummary(events);
  assert.equal(summary.main_thread,'1:7');
  assert.equal(summary.long_tasks,2);
  assert.equal(summary.total_ms,200);
  assert.deepEqual(summary.by_category_ms,{script:50,style_layout:30,paint:10,gc:10,other:100});
  assert.deepEqual(summary.other_top[0],{name:'SpellCheckRequester::requestCheckingFor',ms:70});
  assert.deepEqual(summary.other_top[1],{name:'RunTask',ms:30});
  assert.deepEqual(summary.longest[0],{start_ms:0,duration_ms:120,by_category_ms:{script:50,style_layout:30,paint:10,gc:10,other:20}});
  assert.deepEqual(latency.traceSummary([]),{main_thread:null,long_tasks:0,total_ms:0,by_category_ms:{},other_top:[],longest:[]});
});

test('arguments and the drill password',()=>{
  assert.equal(latency.parseArgs(['--help']).help,true);
  const args=latency.parseArgs(['--draft','d','--path','industry-map/x.yaml','--label','before-x','--trace']);
  assert.equal(args.mode,'raw');assert.equal(args.keys,30);assert.equal(args.interval,150);assert.equal(args.timeout,180000);
  assert.equal(args.origin,'http://127.0.0.1:3016');assert.equal(args.trace,true);
  assert.throws(()=>latency.parseArgs(['--draft','d','--path','p','--label','a/b']),/label/);
  assert.throws(()=>latency.parseArgs(['--draft','d','--path','p','--label','x','--mode','rich']),/mode/);
  assert.throws(()=>latency.parseArgs(['--path','p','--label','x']),/--draft/);
  const folder=fs.mkdtempSync(path.join(os.tmpdir(),'latency-'));const file=path.join(folder,'.env.research-drill');
  fs.writeFileSync(file,'RESEARCH_SESSION_SECRET=x\r\nDRILL_OWNER_PASSWORD=a=b\r\n');
  assert.equal(latency.drillPassword(file),'a=b');
  fs.writeFileSync(file,'RESEARCH_SESSION_SECRET=secret-value\n');
  assert.throws(()=>latency.drillPassword(file),error=>!error.message.includes('secret-value'));
  fs.rmSync(folder,{recursive:true,force:true});
});
