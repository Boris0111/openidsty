import {test,expect} from '@playwright/test';

test.skip(!process.env.RESEARCH_E2E,'Use the isolated research preview explicitly');

test('本機 session challenge 透過獨立代理且不進公開快取',async({request})=>{
  const result=await request.get('/api/admin/session');
  expect(result.status()).toBe(200);
  expect(result.headers()['cache-control']).toBe('no-store');
  const payload=await result.json();
  expect(payload.authenticated).toBe(false);
  expect(payload.csrf_token).toMatch(/^[A-Za-z0-9_-]{43}$/);
  const cookies=result.headersArray().filter(header=>header.name.toLowerCase()==='set-cookie').map(header=>header.value);
  expect(cookies.some(value=>value.startsWith('industryflow_login_csrf=')&&value.includes('HttpOnly')&&value.includes('SameSite=strict')&&value.includes('Path=/api/admin'))).toBe(true);
  expect(result.headers()['x-request-id']).toBeTruthy();
});

test('代理拒絕跨站與匿名寫入，不回顯密碼',async({request,baseURL})=>{
  const marker='synthetic-never-save-this-password';
  const missing=await request.post('/api/admin/session',{data:{password:marker}});
  expect(missing.status()).toBe(403);
  const cross=await request.post('/api/admin/session',{data:{password:marker},headers:{Origin:'https://evil.example'}});
  expect(cross.status()).toBe(403);
  const csrf=await request.post('/api/admin/session',{data:{password:marker},headers:{Origin:baseURL!,'X-CSRF-Token':'wrong'}});
  expect(csrf.status()).toBe(403);
  expect(await csrf.text()).not.toContain(marker);
  const logout=await request.delete('/api/admin/session',{headers:{Origin:baseURL!}});
  expect(logout.status()).toBe(401);
  const hidden=await request.get('/api/admin/drafts');
  expect(hidden.status()).toBe(401);
});

test('登入 body 大小有限制，研究入口持續可讀',async({request,baseURL,page})=>{
  const result=await request.post('/api/admin/session',{data:'x'.repeat(8193),headers:{Origin:baseURL!,'Content-Type':'application/json'}});
  expect(result.status()).toBe(413);
  await page.goto('/next');
  await expect(page.locator('.rs-detail > h2')).toHaveText('液冷冷板');
  await expect(page.locator('body')).not.toContainText(/登入密碼|維護者登入|owner_configured|csrf_token/);
});
