// Synthetic public snapshot for the static build checks; the real snapshot comes from backend/app/public_snapshot.py.
import {createHash} from 'node:crypto';
import type {Segment,Theme,AssessmentResponse,EvidenceSource,GraphData,Industry,SegmentLink,TechnicalProfile} from '../../lib/types';
import type {ResearchDetail,ResearchGraph,ResearchSummary,ChainIndexItem,ResearchCitation} from '../../lib/research-api';

export const RELEASE='00000000-0000-4000-8000-000000000001';
const SCHEMA='research-v1',PUBLISHED='2026-10-20T17:43:56Z';
// Assets are content-addressed like the export: the file name is the sha256 of its bytes.
export const DIAGRAM='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40"><rect width="120" height="40" fill="#e8eef4"/><text x="10" y="25" font-size="12">取熱 → 排熱</text></svg>\n';
export const DIAGRAM_SHA=createHash('sha256').update(DIAGRAM).digest('hex');
const assetUrl=()=>`/snapshot/${RELEASE}/assets/${DIAGRAM_SHA}.svg`;
const envelope=<T,>(data:T)=>({release_id:RELEASE,schema_version:SCHEMA,data});

// Legacy map: two layers, four segments, one theme.
const layers:Record<string,string>={compute:'ai-server',thermal:'ai-server',odm:'ai-server',foundry:'semiconductor'};
const names:Record<string,string>={compute:'運算晶片',thermal:'散熱',odm:'ODM 組裝',foundry:'晶圓代工'};
const tickers:Record<string,{ticker:string;name_zh:string;role:string}[]>={
  compute:[{ticker:'2330.TW',name_zh:'台積電',role:'先進製程代工'}],thermal:[{ticker:'3017.TW',name_zh:'奇鋐',role:'冷板與散熱模組'}],
  odm:[{ticker:'3017.TW',name_zh:'奇鋐',role:'整機散熱配套'}],foundry:[{ticker:'2330.TW',name_zh:'台積電',role:'晶圓代工'}]};
const document={id:'ocp-cold-plate',definition:{title:'合成冷板規範',publisher:'合成標準組織','doc-kind':'formal-specification',
  versions:[{id:'v1',label:'1.0',url:'https://example.org/cold-plate',published:'2026-01-01',reviewed:'2026-10-01','read-scope':'第 3 節',
    'access-limitations':'公開文件',scope:'冷板介面',locators:[{id:'sec-3',section:'3 冷板介面',excerpt:'合成摘錄：冷板以快接頭連接。'}]}]}};
const profile:TechnicalProfile={'product-boundary':'冷板只涵蓋晶片端取熱。','adoption-conditions':['機櫃需支援液體分配'],bottlenecks:['快接頭交期'],
  'substitution-limits':['氣冷無法直接替換高功耗晶片'],claims:[{id:'cold-plate-interface',statement:'冷板介面依規範固定。',confidence:'well-supported',
    evidence:[{'document-id':document.id,'version-id':'v1',locator:'sec-3'}]}],'evidence-gaps':['供應商份額未公開'],reviewed:'2026-10-01'};
const theme:Theme={theme:'liquid-cooling',name_zh:'液冷',status:'scaling',checked:'2026-10-07',segments:['thermal','odm'],
  segments_detail:[{id:'thermal',name:'散熱',layer:'ai-server'},{id:'odm',name:'ODM 組裝',layer:'ai-server'}],beneficiaries:[],
  prose:'## 題材範圍\n\n合成題材研究，[冷板](/next?focus=product-cold-plate) 是主要產品。\n\n## 判斷依據\n\n請回到原始來源。',
  milestones:[{id:'rack-delivery',date:'2027-Q1',event:'整櫃液冷交付',evidence:'需有正式交付證據'}],'technical-profile':profile,
  assessment_summary:{available:true,summary:'冷板交付已有依據，份額仍待核對。',confidence:'inference',reviewed:'2026-10-07'}};
// The export drops event candidates, version pointers and source runtime state from assessments.
type PublicAssessment=Omit<AssessmentResponse,'candidates'|'undated_candidates'|'candidate_count'|'unknown_date_count'|'current_version_id'|'evidence_sources'>&
  {evidence_sources:Record<string,Omit<EvidenceSource,'runtime'>>};
const assessment:PublicAssessment={available:true,status:theme.status,checked:theme.checked,
  evidence_sources:{'synthetic-source':{id:'synthetic-source',name:'合成官方來源',url:'https://example.org/source',reachability:'verified',checked:'2026-10-07'}},
  source_warnings:[{source_id:'synthetic-source',kind:'unverified',message:'合成原文件可讀性待確認'}],
  assessment:{summary:'冷板交付已有依據，份額仍待核對。',confidence:'inference',reviewed:'2026-10-07',
    evidence:[{id:'shipment',source_id:'synthetic-source',url:'https://example.org/source',excerpt:'Synthetic shipment note.',period:'2026 Q2',published:null}],
    claims:[{id:'shipment-claim',stance:'supporting',statement:'只支持具名產品交付。',confidence:'well-supported',evidence_ids:['shipment']}],
    conditions:['需具名採購'],gaps:['份額未核實'],next_checks:[{question:'是否有量化收入？',evidence_required:'分產品揭露'}],
    paths:[{id:'thermal-odm',steps:[{from:'thermal',to:'odm',type:'downstream'}],mechanism:'整機採購需實際交付',direction:'mixed',conditions:['實際平台採購'],claim_ids:['shipment-claim']}],
    milestone_reviews:[]}};
const segment=(id:string):Omit<Segment,'events'>=>({segment:id,name_zh:names[id],layer:layers[id],
  prose:'## 環節定義\n\n合成環節定義。\n\n## 技術變數\n\n規格。\n\n## 玩家格局\n\n合成。\n\n## 傳導鏈\n\n採購條件。\n\n## 監測指標\n\n交付。\n\n## 風險\n\n資料不足。',
  companies:tickers[id],kpis:['交付進度'],signals:['官方揭露'],upstream:id==='odm'?['thermal','compute']:[],downstream:['thermal','compute'].includes(id)?['odm']:[],
  themes_detail:['thermal','odm'].includes(id)?[theme]:[],neighbors:(id==='odm'?['thermal','compute']:['thermal','compute'].includes(id)?['odm']:[]).map(n=>({id:n,name:names[n],layer:layers[n]})),
  ...(id==='thermal'?{'technical-profile':profile}:{})});
const layerGraph=(layer:string):GraphData=>({layer,nodes:Object.keys(names).filter(id=>layers[id]===layer).map((id,i)=>({id,name:names[id],position:i+1,company_count:1,layer})),
  edges:layer==='ai-server'?[{id:'thermal-odm',source:'thermal',target:'odm',kind:'supply',direction:'forward',relation:{summary:'冷板供應整機',items:['冷板'],dependencies:[],conditions:['平台採用液冷'],confidence:'inference',evidence:[],gaps:['份額未公開'],reviewed:'2026-10-01'}},
    {id:'compute-odm',source:'compute',target:'odm',kind:'supply',direction:'forward'}]:[]});

// Research release: every collection holds at least one entity so each directory and detail route is exercised.
const row=(id:string,name:string,summary='合成研究'):ResearchSummary=>({id,kind:id.split('-')[0],name,summary,reviewed:'2026-10-01'});
const entities=[row('application-liquid-cooling','液冷供應鏈','熱怎麼送出去'),row('company-avc','奇鋐','散熱模組'),row('company-tsmc','台積電','晶圓代工'),
  row('concept-thermal-resistance','熱阻'),row('product-cold-plate','冷板'),row('research-cooling-notes','液冷研究筆記'),row('role-cold-plate-maker','冷板供應商'),
  row('segment-compute','運算晶片'),row('segment-foundry','晶圓代工'),row('segment-odm','ODM 組裝'),row('segment-thermal','散熱'),row('theme-liquid-cooling','液冷')];
const byId=Object.fromEntries(entities.map(entity=>[entity.id,entity]));
const collection:Record<string,string>={application:'applications',company:'companies',concept:'concepts',product:'products',research:'research',role:'roles',segment:'segments',theme:'themes'};
const citation:ResearchCitation={document_id:'document-cold-plate',revision_id:'rev-1',title:'合成冷板說明',url:'https://example.org/cold-plate',document_kind:'normative',
  published:'2026-01-01',reviewed:'2026-10-01',scope:'冷板介面',read_scope:'第 3 節',access_limitations:null,locators:[{id:'sec-3',section:'3',excerpt:'合成摘錄。'}],
  locator:'sec-3',applicable_period:'2026',stance:'supporting'};
const chainItem:ChainIndexItem={id:'application-liquid-cooling',name:'液冷供應鏈',summary:'熱怎麼送出去',question:'熱怎麼送出去？',
  segments:[{id:'segment-thermal',name:'散熱'}],steps:['取熱','排熱'],assets:[{id:'diagram-cooling',url:assetUrl(),alt:'液冷步驟圖',attribution:'合成圖解'}]};
function detail(entity:ResearchSummary):ResearchDetail{
  const base:ResearchDetail={...entity,markdown:`## 研究內容\n\n${entity.name}的合成研究，相關：[冷板](/next?focus=product-cold-plate)。`,content:{},
    claims:[{id:'claim-'+entity.id,statement:entity.name+'的合成主張',confidence:'inference',conditions:['合成條件'],reviewed:'2026-10-01',evidence:[citation]}],
    related:entities.filter(other=>other.id!==entity.id).slice(0,2),assets:[],truncated:false,
    trail:entity.kind==='company'?[]:[{id:'segment-thermal',kind:'segment',name:'散熱',url:'/?layer=ai-server&segment=thermal'}]};
  if(entity.kind==='application')return {...base,chain:{question:'熱怎麼送出去？',steps:[{label:'取熱',note:null,products:[{id:'product-cold-plate',name:'冷板',companies:[{id:'company-avc',name:'奇鋐'}]}]},{label:'排熱',note:null,products:[]}],
    other_products:[],diagram:{concept:{id:'concept-thermal-resistance',name:'熱阻'},assets:chainItem.assets}}};
  if(entity.kind==='product'||entity.kind==='role')return {...base,chains:[{id:chainItem.id,name:chainItem.name,question:chainItem.question,steps:[{label:'取熱',here:true},{label:'排熱',here:false}],products:[{id:'product-cold-plate',name:'冷板'}]}]};
  if(entity.kind==='company')return {...base,content:{roles:[{segment_id:'segment-thermal',description:'散熱角色'}],listings:[{ticker:entity.id==='company-tsmc'?'2330.TW':'3017.TW',market:'TW'}]}};
  if(entity.kind==='segment')return {...base,legacy_return:{url:'/?layer='+layers[entity.id.slice(8)]+'&segment='+entity.id.slice(8),label:'回到「'+entity.name+'」產業地圖'}};
  return base;
}
function graph(entity:ResearchSummary):ResearchGraph{
  const nodes=[entity,byId['company-avc'],byId['product-cold-plate']].filter((node,i,all)=>all.findIndex(other=>other.id===node.id)===i);
  return {root:entity.id,nodes,edges:[{id:'capability:avc-cold-plate',source:'company-avc',target:'product-cold-plate',kind:'capability',mechanism:'產品能力',conditions:['不指認交易'],claims:[]}].filter(edge=>nodes.some(n=>n.id===edge.source)&&nodes.some(n=>n.id===edge.target)),truncated:false,continue_from:[]};
}
const markets=['TW','US','KR','JP','HK','DE','NL'];
const directory=(kind:string)=>{
  const items=entities.filter(entity=>entity.kind===kind);
  const filters:Record<string,Record<string,string[]>>={};
  if(kind==='company'){
    filters.market=Object.fromEntries(markets.map(market=>[market,market==='TW'?['company-avc','company-tsmc']:[]]));
    filters.role=Object.fromEntries(entities.filter(e=>e.kind==='role'||e.kind==='segment').map(e=>[e.id,e.id==='role-cold-plate-maker'||e.id==='segment-thermal'?['company-avc']:e.id==='segment-foundry'?['company-tsmc']:[]]));
  }
  if(['company','product','role'].includes(kind))filters.category={'application-liquid-cooling':kind==='company'?['company-avc']:items.map(item=>item.id)};
  return {release_id:RELEASE,schema_version:SCHEMA,items,filters};
};
const column=(id:string)=>envelope({...byId[id],roles:[{segment_id:'segment-thermal',description:'散熱角色'}],
  products:id==='company-avc'?[{company_id:id,product_id:'product-cold-plate',name:'冷板',role_id:'role-cold-plate-maker',role_name:'冷板供應商',conditions:['合成'],n:1}]:[],
  risks:'集中風險。',business_model:'合成業務模式。',claims:[],gaps:[],research_depth:'basic',truncated:false});
const aliases:[string,string,string][]=([['2330','2330','company-tsmc'],['3017','3017','company-avc'],['AVC','avc','company-avc'],['TSMC','tsmc','company-tsmc'],
  ['Cold Plate','cold plate','product-cold-plate'],['台積電','台積電','company-tsmc'],['奇鋐','奇鋐','company-avc'],['液冷','液冷','theme-liquid-cooling'],
  ['散熱','散熱','segment-thermal'],['冷板','冷板','product-cold-plate'],['臺積電','台積電','company-tsmc']] as [string,string,string][]).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);

/** Snapshot path → JSON payload, laid out exactly like an export of backend/app/public_snapshot.py. */
export function fixtureFiles():Record<string,unknown>{
  const files:Record<string,unknown>={};
  const segments:SegmentLink[]=Object.keys(names).map(id=>({id,name:names[id],layer:layers[id]}));
  files['legacy/industries.json']=[{id:'ai-server',name:'AI 伺服器',segment_count:3},{id:'semiconductor',name:'半導體',segment_count:1}] satisfies Industry[];
  for(const layer of ['ai-server','semiconductor'])files[`legacy/industries/${layer}/graph.json`]=layerGraph(layer);
  files['legacy/segments.json']=segments;
  for(const id of Object.keys(names))files[`legacy/segments/${id}.json`]=segment(id);
  files['legacy/themes.json']=[theme];files['legacy/themes/liquid-cooling.json']=theme;files['legacy/themes/liquid-cooling/assessment.json']=assessment;
  files[`legacy/technical-documents/${document.id}.json`]=document;
  files['v2/manifest.json']=envelope({published_at:PUBLISHED,generation:1});
  for(const entity of entities){
    files[`v2/${collection[entity.kind]}/${entity.id}.json`]=envelope(detail(entity));
    files[`v2/graphs/${entity.id}.json`]=envelope(graph(entity));
  }
  for(const kind of Object.keys(collection))files[`v2/directory/${collection[kind]}.json`]=directory(kind);
  files['v2/chains.json']=envelope({items:[chainItem]});
  for(const id of Object.keys(names))files[`v2/chains/segment-${id}.json`]=envelope({items:id==='thermal'?[chainItem]:[]});
  files['v2/documents/document-cold-plate/rev-1.json']=envelope(citation);
  for(const id of ['company-avc','company-tsmc'])files[`v2/compare/${id}.json`]=column(id);
  files['v2/search.json']={release_id:RELEASE,schema_version:SCHEMA,entities:entities.map(entity=>({...entity,roles:entity.kind==='company'?['合成角色']:[]})),aliases};
  files['v2/resolve.json']={release_id:RELEASE,keys:{'2330.TW':{status:200,body:envelope(byId['company-tsmc'])},'3017.TW':{status:200,body:envelope(byId['company-avc'])}}};
  files['manifest.json']={release_id:RELEASE,schema_version:SCHEMA,published_at:PUBLISHED,generation:1,counts:{companies:2}};
  files['export.json']={exported_at:PUBLISHED};
  return files;
}
