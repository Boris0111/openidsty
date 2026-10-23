const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');

const python=fs.readFileSync(path.join(__dirname,'../../backend/app/public_snapshot.py'),'utf8');
const keys=name=>[...new RegExp(name+' = \\{([^}]*)\\}','s').exec(python)[1].matchAll(/'([a-z_]+)'/g)].map(match=>match[1]).sort();

test('leak rules match the export',async()=>{
  const leaks=await import('../scripts/snapshot-leaks.mjs');
  assert.deepEqual([...leaks.FORBIDDEN_KEYS].sort(),keys('FORBIDDEN_KEYS'));
  assert.deepEqual([...leaks.ASSESSMENT_FORBIDDEN_KEYS].sort(),keys('ASSESSMENT_FORBIDDEN_KEYS'));
});

test('leak scan reports fields, API paths and secrets like the export does',async()=>{
  const {leakFindings,environmentSecrets}=await import('../scripts/snapshot-leaks.mjs');
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'snapshot-leaks-'));
  const write=(relative,value)=>{fs.mkdirSync(path.dirname(path.join(root,relative)),{recursive:true});fs.writeFileSync(path.join(root,relative),value)};
  write('v2/resolve.json',JSON.stringify({keys:{X:{status:409,body:{candidates:[]}}}}));
  write('legacy/themes/t/assessment.json',JSON.stringify({candidates:[]}));
  write('legacy/segments/b.json',JSON.stringify({events:[]}));
  write('legacy/themes/c.json',JSON.stringify({link:'/api/events'}));
  write('index.html','<p>token-0123456789</p>');
  write('.env.research','RESEARCH_SESSION_SECRET=token-0123456789\nOTHER=plain\n');
  const secrets=environmentSecrets(path.join(root,'.env.research'));
  assert.deepEqual(secrets,['token-0123456789']);
  assert.deepEqual(leakFindings(root,secrets).filter(line=>!line.startsWith('.env')),['index.html: secret value','legacy/segments/b.json: forbidden field events',
    'legacy/themes/c.json: private API path','legacy/themes/t/assessment.json: forbidden field candidates']);
  fs.rmSync(root,{recursive:true,force:true});
});
