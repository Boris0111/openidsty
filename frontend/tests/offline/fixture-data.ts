// Synthetic browser-only responses. Never imported by app code or ingestion.
import type {Page} from '@playwright/test';
import type {Theme, Source, InfoEvent, Coverage, Segment, Company, AssessmentResponse} from '../../lib/types';

export const source: Source = {
  id: 'offline-source', name: '離線測試來源', url: 'https://example.invalid/source',
  status: 'configuration_required', last_attempt: null, last_success: null, error: '尚未設定聯絡資訊',
  new_count: 0, data: {adapter: 'manual'},
};
export const event: InfoEvent = {
  id: 1, title: '離線樣本：液冷設備需求', body: '此資料僅用於瀏覽器流程測試。',
  ticker: null, kind: 'industry_news', lifecycle: 'published', source_id: source.id,
  published_at: '2026-10-08T00:00:00Z', published_precision: 'day', reported_at: null,
  activity_at: null, date_semantics: 'publication', period: null, basis: null, routine: false,
  rules_version: 'offline', segments: [{id: 'thermal', relevance: 'direct', evidence: [{term: '液冷', matched: '液冷', excerpt: '離線測試摘錄'}]}],
  themes: [{id: 'liquid-cooling', relevance: 'direct', evidence: []}],
  fetched_at: '2026-10-09T00:00:00Z', url: 'https://example.invalid/article', mentioned: [],
};
export const theme: Theme = {
  theme: 'liquid-cooling', name_zh: '液冷', status: 'validating', checked: '2026-10-07',
  prose: '## 題材範圍\n\n離線研究樣本，保留查核基準。\n\n## 判斷依據\n\n請回到原始來源。',
  segments: ['thermal'], segments_detail: [{id: 'thermal', name: '散熱', layer: 'ai-server'}],
  beneficiaries: [], milestones: [{date: '2027-Q1', event: '驗證交付', evidence: '需有正式交付證據'}], events: [event],
};
export const assessment: AssessmentResponse = {
  available: true, status: theme.status, checked: theme.checked, current_version_id: null,
  evidence_sources: {[source.id]: {id: source.id, name: source.name, url: source.url, reachability: 'unverified', checked: '2026-10-09', runtime: []}},
  source_warnings: [{source_id: source.id, kind: 'unverified', message: '離線樣本原文件待確認'}],
  candidates: [event], candidate_count: 1, unknown_date_count: 1,
  undated_candidates: [{...event, id: 2, title: '離線樣本：發布日未知', published_at: null, published_precision: 'unknown'}],
  assessment: {
    summary: '產品交付已有依據，供應商份額仍待核對。', confidence: 'inference', reviewed: '2026-10-07',
    evidence: [{id: 'shipment', source_id: source.id, url: source.url, excerpt: 'Synthetic browser-only evidence.', period: '離線樣本 2026 Q2，產品交付口徑', published: null}],
    claims: [{id: 'product-shipment', stance: 'supporting', statement: '只支持具名產品交付，不代表全部供應商受惠。', confidence: 'well-supported', evidence_ids: ['shipment']}],
    conditions: ['需具名採購與料號適配'], gaps: ['候選公司份額尚未核實'],
    next_checks: [{question: '是否有量化產品收入？', evidence_required: '分產品財報及交付紀錄'}],
    paths: [{id: 'thermal-odm', steps: [{from: 'thermal', to: 'odm', type: 'downstream'}], mechanism: '整機採購需實際交付', direction: 'mixed', conditions: ['實際平台採購'], claim_ids: ['product-shipment']}],
    milestone_reviews: [],
  },
};
theme.assessment_summary = {available: true, summary: assessment.assessment!.summary, confidence: 'inference', reviewed: '2026-10-07'};
const names: Record<string, string> = {compute: '運算晶片', thermal: '散熱', odm: 'ODM 組裝', foundry: '晶圓代工'};
const segment = (id: string): Segment => ({
  segment: id, name_zh: names[id], layer: id === 'foundry' ? 'semiconductor' : 'ai-server',
  prose: '## 環節定義\n\n離線供應角色樣本。\n\n## 技術變數\n\n設備規格。\n\n## 傳導鏈\n\n採購條件。\n\n## 風險\n\n未取得資料。',
  companies: [{ticker: '2330.TW', name_zh: '台積電', role: '離線定位樣本'}],
  kpis: ['交付進度'], signals: ['官方揭露'], upstream: [], downstream: [],
  themes_detail: [theme], neighbors: [], events: [event],
});
export const coverage: Coverage = {
  as_of: '2026-10-09T00:00:00Z', window_start: '2026-07-11T00:00:00Z', rules_version: 'offline',
  counting: '離線樣本只計直接分類。', rows: [
    {id: 'odm', kind: 'segment', name: 'ODM 組裝', layer: 'ai-server', research_available: true, checked: null,
      configured_sources: 1, successful_sources: 0, last_updated: null, direct_30d: 0, direct_90d: 1,
      background_90d: 0, unknown_date: 0, routine_90d: 0, company_mentions_90d: 0, samples: [],
      gaps: ['近 30 日尚無直接事件'], sources: [source]},
    {id: theme.theme, kind: 'theme', name: theme.name_zh, layer: null, research_available: true, checked: theme.checked,
      configured_sources: 1, successful_sources: 0, last_updated: null, direct_30d: 1, direct_90d: 1,
      background_90d: 0, unknown_date: 0, routine_90d: 0, company_mentions_90d: 0, samples: [event],
      gaps: ['來源待設定'], sources: [source], assessment_available: true, assessment_checked: '2026-10-07'},
  ],
};
const company: Company = {
  ticker: '2330.TW', name: '台積電', aliases: ['臺積電'], financials: [], events: [], mentioned_events: [],
  roles: [{segment: 'foundry', segment_name: '晶圓代工', layer: 'semiconductor', role: '離線定位樣本'}],
};

export async function installOfflineApi(page: Page) {
  const unexpected: string[] = [];
  await page.route('**/api/**', async route => {
    const url = new URL(route.request().url()), path = url.pathname;
    let data: unknown;
    if (path === '/api/industries') data = [{id: 'ai-server', name: 'AI 伺服器', segment_count: 3}, {id: 'semiconductor', name: '半導體', segment_count: 1}];
    else if (/^\/api\/industries\/[^/]+\/graph$/.test(path)) {
      const layer = path.split('/')[3], ids = layer === 'ai-server' ? ['compute', 'thermal', 'odm'] : ['foundry'];
      data = {layer, nodes: ids.map((id, i) => ({id, name: names[id], position: i + 1, company_count: 1, layer})), edges: layer === 'ai-server' ? [{id: 'thermal-odm', source: 'thermal', target: 'odm', kind: 'supply', direction: 'forward'}] : []};
    } else if (path === '/api/segments') data = Object.entries(names).map(([id, name]) => ({id, name, layer: id === 'foundry' ? 'semiconductor' : 'ai-server'}));
    else if (path.startsWith('/api/segments/') && names[path.split('/').at(-1)!]) data = segment(path.split('/').at(-1)!);
    else if (path === '/api/themes') data = [theme];
    else if (path === '/api/theme-updates') data = {items:[...new Set((url.searchParams.get('ids')||'').split(',').filter(Boolean))].map(id=>id==='liquid-cooling'?{theme_id:id,available:true,name:theme.name_zh,current_version_id:1,version_number:1,reviewed:theme.checked,assessment_summary:assessment.assessment!.summary,indicator_token:'i1',candidate_token:'c1',candidate_count:1,unknown_date_count:1,indicator_count:0,available_indicator_count:0,pending_summary:'1 則待納入判讀；1 則新收錄資訊發布日待確認（不代表新發生）',indicator_summary:[],source_warnings:[]}:{theme_id:id,available:false,reason:'題材已不可用'})};
    else if (path === '/api/themes/liquid-cooling') data = theme;
    else if (path === '/api/themes/liquid-cooling/assessment') data = assessment;
    else if (path === '/api/themes/liquid-cooling/indicators') data = {theme_id:theme.theme,as_of:'2026-10-14',indicators:[],gaps:['尚無指標設定']};
    else if (path === '/api/themes/liquid-cooling/assessment/versions') data = {current_version_id:1,total:1,versions:[{version_id:1,version_number:1,theme_id:theme.theme,reviewed:'2026-10-07',recorded_at:'2026-10-14T00:00:00Z',reason:'首次保存基準'}]};
    else if (path === '/api/themes/liquid-cooling/assessment/compare') data = {from:{version_id:1},to:{version_id:1,reason:'首次保存基準',reviewed:'2026-10-07',recorded_at:'2026-10-14T00:00:00Z'},changes:[]};
    else if (path === '/api/events') data = url.searchParams.get('date_from') === '2099-01-01' ? [] : [event];
    else if (path === '/api/events/1') data = {...event, source, impact: {confidence: 'inference', seeds: ['thermal'], paths: []}, raw: {offline: true}};
    else if (path === '/api/coverage') data = coverage;
    else if (path === '/api/sources') data = {sources: [source], last_run: null};
    else if (path === '/api/companies/2330.TW') data = company;
    else if (path === '/api/search') {
      const q = url.searchParams.get('q') || '';
      data = q.includes('積電') ? [{kind: 'company', id: '2330.TW', name: '台積電', url: '/companies/2330.TW'}] : q.includes('液冷') ? [{kind: 'theme', id: theme.theme, name: theme.name_zh, url: '/themes/liquid-cooling'}] : [];
    } else {unexpected.push(path); return route.fulfill({status: 404, json: {detail: '未宣告的離線測試 API'}});}
    await route.fulfill({json: data});
  });
  return unexpected;
}
