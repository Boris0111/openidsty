import {test,expect} from '@playwright/test';
test.skip(!process.env.RESEARCH_E2E,'Use only the isolated research preview');

test('真實讀者代理可查財務、比較與既有事件，不取得管理 payload',async({request})=>{
  const manifest=await (await request.get('/api/v2/manifest')).json();
  const release=manifest.release_id;
  const financial=await request.get('/api/v2/companies/company-auras/financials',{params:{release_id:release}});
  expect(financial.status()).toBe(200);expect(financial.headers()['cache-control']).toContain('max-age=30');
  const values=await financial.json();expect(values.release_id).toBe(release);expect(values.data.as_of).toBeTruthy();
  if(values.data.items.length===0)expect(values.data.gaps.length).toBeGreaterThan(0);
  const compare=await request.get('/api/v2/compare',{params:{company_ids:'company-auras,company-vertiv',release_id:release}});
  expect(compare.status()).toBe(200);const compared=await compare.json();
  expect(compared.data.companies).toHaveLength(2);expect(compared.data.metrics.length).toBeGreaterThan(10);
  expect(compared.release_id).toBe(release);expect(compare.headers()['cache-control']).toContain('max-age=30');
  const events=await request.get('/api/v2/events',{params:{release_id:release,limit:3}});
  expect(events.status()).toBe(200);const current=await events.json();
  expect(current.data.items.length).toBeGreaterThan(0);
  for(const item of current.data.items){expect(['official','report']).toContain(item.source_nature);expect(item.raw).toBeUndefined();expect(item.fetched_at).toBeUndefined();expect(item.last_error_kind).toBeUndefined()}
  const observations=await request.get('/api/v2/observations',{params:{release_id:release,limit:3}});
  expect(observations.status()).toBe(200);
  for(const item of (await observations.json()).data.items)expect(item.source_nature).toBe('rumor');
  expect((await request.get('/api/v2/events?source_nature=rumor')).status()).toBe(422);
  expect((await request.get('/api/v2/companies/company-missing/financials')).status()).toBe(404);
});
