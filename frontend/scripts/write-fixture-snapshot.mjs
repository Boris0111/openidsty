// Write the synthetic snapshot (tests/static/fixture-snapshot.ts) in the export layout: <out>/<release>/...
// Usage: node scripts/write-fixture-snapshot.mjs [--out .static-fixture]
import {mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import ts from 'typescript';
import {leakFindings} from './snapshot-leaks.mjs';

const require=createRequire(import.meta.url);
const out=path.resolve(process.argv.includes('--out')?process.argv[process.argv.indexOf('--out')+1]:'.static-fixture');
const source=ts.transpileModule(readFileSync('tests/static/fixture-snapshot.ts','utf8'),
  {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const fixture={exports:{}};
new Function('require','module','exports',source)(require,fixture,fixture.exports);
const {RELEASE,DIAGRAM,DIAGRAM_SHA,fixtureFiles}=fixture.exports;

const root=path.join(out,RELEASE);
rmSync(root,{recursive:true,force:true});
for(const [relative,payload] of Object.entries(fixtureFiles())){
  mkdirSync(path.dirname(path.join(root,relative)),{recursive:true});
  writeFileSync(path.join(root,relative),JSON.stringify(payload));
}
mkdirSync(path.join(root,'assets'),{recursive:true});
writeFileSync(path.join(root,'assets',DIAGRAM_SHA+'.svg'),DIAGRAM);
const findings=leakFindings(root);
if(findings.length){console.error(findings.join('\n'));process.exit(1)}
console.log(root);
