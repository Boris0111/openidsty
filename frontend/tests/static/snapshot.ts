// Reads the snapshot the public build was made from, so the crawl covers every page that snapshot can show.
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {expect, type Page} from '@playwright/test';

export const FIXTURE_RELEASE = '00000000-0000-4000-8000-000000000001';
const folder = process.env.STATIC_SNAPSHOT_DIR || path.join(__dirname, '../../.static-fixture', FIXTURE_RELEASE);
export const read = <T>(relative: string): T => JSON.parse(readFileSync(path.join(folder, relative), 'utf8'));
export const manifest = read<{release_id: string; published_at: string}>('manifest.json');

/** Every public page this snapshot can render, grouped by page kind (the first of each kind is checked on a phone too). */
export function pages(): Record<string, string[]> {
  const segments = read<{id: string; layer: string}[]>('legacy/segments.json');
  const themes = read<{theme: string}[]>('legacy/themes.json');
  const entities = read<{entities: {id: string; kind: string}[]}>('v2/search.json').entities;
  const companies = entities.filter(entity => entity.kind === 'company').map(entity => entity.id);
  const resolve = read<{keys: Record<string, {status: number}>}>('v2/resolve.json').keys;
  const research = (kind: string) => entities.filter(entity => entity.kind === kind).map(entity => '/next?focus=' + encodeURIComponent(entity.id));
  return {
    map: ['/', ...segments.map(segment => `/?layer=${segment.layer}&segment=${segment.id}`)],
    themes: ['/themes', ...themes.map(theme => `/themes/${theme.theme}`)],
    directories: ['/next', ...['segments', 'applications', 'roles', 'products', 'companies', 'themes', 'concepts'].map(view => '/next?view=' + view)],
    compare: ['/next?view=compare', ...(companies.length > 1 ? ['/next?view=compare&company_ids=' + encodeURIComponent(companies.slice(0, 2).join(','))] : [])],
    ...Object.fromEntries(['application', 'company', 'product', 'role', 'concept', 'research', 'segment', 'theme'].map(kind => [kind, research(kind)])),
    tickers: Object.entries(resolve).filter(([, value]) => value.status === 200).map(([key]) => '/companies?' + new URLSearchParams({ticker: key})),
  };
}

const PROBLEMS = /公開版未收錄|目前無法|研究版本不一致|找不到這|無法開啟|請稍後重試/;

/** Open a page and require it to read entirely from the snapshot: no API call, no missing file, no error text. */
export async function visit(page: Page, url: string) {
  const problems: string[] = [];
  page.on('request', request => {if (new URL(request.url()).pathname.startsWith('/api/')) problems.push('API request ' + request.url())});
  page.on('response', response => {if (new URL(response.url()).pathname.startsWith('/snapshot/') && response.status() >= 400) problems.push(`${response.status()} ${response.url()}`)});
  page.on('pageerror', error => problems.push('page error ' + error.message));
  await page.goto(url);
  await expect(page.getByText(/正在讀取|正在開啟/)).toHaveCount(0, {timeout: 15000});
  await page.waitForLoadState('networkidle');
  await expect(page.locator('main')).not.toContainText(PROBLEMS);
  await expect(page.locator('footer')).toContainText('不構成投資建議');
  await expect(page.locator('footer')).toContainText(new Date(manifest.published_at).toLocaleDateString('sv-SE', {timeZone: 'Asia/Taipei'}));
  const navigation = page.getByRole('navigation', {name: '主要導覽'});
  await expect(navigation.getByRole('link', {name: '事件'})).toHaveCount(0);
  await expect(navigation.getByRole('link', {name: '收藏'})).toHaveCount(0);
  expect(problems).toEqual([]);
}
