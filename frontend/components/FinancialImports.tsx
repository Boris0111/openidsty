'use client';
import {useRef,useState} from 'react';
type Api=<T>(path:string,method?:string,data?:unknown,revision?:number,idempotencyKey?:string,rawType?:string)=>Promise<T>;
type Item={company_id:string;label:string;period_start:string;period_end:string;basis:string;scope:string;currency:string;unit:string;share_class:string;raw_value:string;raw_unit:string;multiplier:string;value:string;previous_value:string|null;changed:boolean;locator:string;revision_note:string;supersedes:string|null};
type Batch={batch_id:string;payload_hash:string;status:string;document:{title:string;source_url:string;filed_at:string|null;source_as_of:string|null};items:Item[];result:{new_revisions:number;active_changes:number}|null};
const bases:Record<string,string>={monthly:'單月',quarterly:'單季',ytd:'年度累計',annual:'全年',instant:'期末'};
const scopes:Record<string,string>={consolidated:'合併',standalone:'個體','whole-filing-entity':'整個申報主體','issuer-summary-unspecified':'摘要未明列範圍'};

export function FinancialImports({api,busy,action}:{api:Api;busy:boolean;action:(operation:()=>Promise<void>)=>Promise<void>}){
  const [content,setContent]=useState('');const [format,setFormat]=useState('json');const [batch,setBatch]=useState<Batch>();
  const [error,setError]=useState('');
  const [checked,setChecked]=useState(false);const [reason,setReason]=useState('');const key=useRef('');const signature=useRef('');
  function invalidate(){setBatch(undefined);setChecked(false);key.current='';signature.current=''}
  function template(){const document={source_id:'',source_family:'',source_url:'',title:'',accession:'',filed_at:null};const row={company_id:'',metric_id:'revenue',period_start:'',period_end:'',basis:'annual',scope:'consolidated',unit:'amount',currency:'',raw_value:'',raw_unit:'',multiplier:'1',tag:'',locator:''};const csv={...Object.fromEntries(Object.entries(document).map(([key,value])=>['document_'+key,value??''])),...row};const content=format==='csv'?'\ufeff'+Object.keys(csv).join(',')+'\r\n'+Object.values(csv).join(',')+'\r\n':JSON.stringify({format:'official-financial-import-v1',document,rows:[row]},null,2);const link=globalThis.document.createElement('a');const url=URL.createObjectURL(new Blob([content],{type:format==='csv'?'text/csv;charset=utf-8':'application/json'}));link.href=url;link.download='official-financial-import-template.'+format;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
  function perform(operation:()=>Promise<void>){return action(async()=>{setError('');try{await operation()}catch(reason){setError(reason instanceof Error?reason.message:'財務操作未完成。')}})}
  async function load(file:File){if(file.size>1024*1024)throw new Error('財務匯入超過 1 MiB。');const bytes=await file.arrayBuffer();let text:string;try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes)}catch{text=new TextDecoder('big5',{fatal:true}).decode(bytes)}setContent(text);setFormat(file.name.toLowerCase().endsWith('.csv')?'csv':'json');invalidate()}
  async function preview(){const current=await api<Batch>('financial-imports','POST',content,undefined,undefined,format==='csv'?'text/csv':'application/json');setBatch(current);setChecked(false);key.current='';signature.current=''}
  async function confirm(){if(!batch)return;const data={payload_hash:batch.payload_hash,reason:reason.trim(),confirmed_official_source:checked};const current=JSON.stringify(data);if(current!==signature.current){key.current=crypto.randomUUID();signature.current=current}setBatch(await api<Batch>('financial-imports/'+batch.batch_id+'/confirm','POST',data,undefined,key.current))}
  return <div className="ra-financial-import"><h2>官方財務補錄</h2><p>先核對官方報表、期間與口徑，再預覽差異。預覽不會寫入財務數值；僅接受 JSON／CSV，不自動猜讀 PDF。</p>
    {error&&<p className="ra-error" role="alert">{error}</p>}
    <label>財務檔案（最多 1 MiB）<input type="file" accept=".json,.csv,application/json,text/csv" disabled={busy} onChange={event=>{const file=event.target.files?.[0];if(file)void perform(()=>load(file))}}/></label>
    <label>輸入格式<select value={format} disabled={busy} onChange={event=>{setFormat(event.target.value);invalidate()}}><option value="json">JSON</option><option value="csv">CSV</option></select></label>
    <button disabled={busy} onClick={template}>下載空白範本</button>
    <label>財務匯入內容<textarea className="ra-import-content" rows={10} value={content} spellCheck={false} disabled={busy} onChange={event=>{setContent(event.target.value);invalidate()}}/></label>
    <button disabled={busy||!content.trim()} onClick={()=>void perform(preview)}>驗證並預覽財務</button>
    {batch&&<section aria-label="財務匯入預覽"><h3>核對匯入差異</h3><p><a href={batch.document.source_url} target="_blank" rel="noreferrer">{batch.document.title}</a></p><p>申報日期：{batch.document.filed_at||'來源未提供'}{batch.document.source_as_of?'；提供者出表日：'+batch.document.source_as_of:''}</p>
      <div className="ra-table"><table><thead><tr><th>公司／指標</th><th>期間與範圍</th><th>原值與換算</th><th>既有值 → 匯入值</th><th>文件定位</th></tr></thead><tbody>{batch.items.map((item,index)=><tr key={index}><td>{item.company_id}<br/>{item.label}</td><td>{item.period_start} 至 {item.period_end}<br/>{bases[item.basis]||item.basis}，{scopes[item.scope]||item.scope}{item.share_class?'，股別 '+item.share_class:''}</td><td>{item.raw_value} {item.raw_unit}<br/>倍率 {item.multiplier}</td><td>{item.previous_value??'尚無數值'} → {item.value} {item.currency}<br/>{item.changed?'數值不同，將保存修訂':'數值相同，不新增修訂'}</td><td>{item.locator}{item.supersedes&&<p>指定修正：{item.revision_note}</p>}</td></tr>)}</tbody></table></div>
      <p>內容核對碼：<code>{batch.payload_hash}</code></p>
      {batch.status==='confirmed'?<p role="status">已完成入庫：新增 {batch.result?.new_revisions??0} 筆數值修訂，{batch.result?.active_changes??0} 筆目前值變更。</p>:<><label><input type="checkbox" checked={checked} disabled={busy} onChange={event=>setChecked(event.target.checked)}/>我已閱讀官方原文並核對以上數值、期間、幣別與定位</label><label>財務確認理由<textarea rows={3} maxLength={2000} value={reason} disabled={busy} onChange={event=>setReason(event.target.value)}/></label><button className="ra-primary" disabled={busy||!checked||!reason.trim()} onClick={()=>void perform(confirm)}>確認財務入庫</button><p>確認失敗可重試；若資料已有新修訂，請重新預覽。</p></>}
    </section>}
  </div>;
}
