import {test} from '@playwright/test';
import {expectNoHorizontalOverflow} from '../offline/layout';
import {pages, visit} from './snapshot';

// Every page the snapshot can show must render from snapshot files alone.
for (const [kind, urls] of Object.entries(pages())) {
  for (const url of urls) test(`${kind} ${url}`, async ({page}) => {await visit(page, url)});
  if (urls.length) test(`${kind} on a phone ${urls[urls.length - 1]}`, async ({page}) => {
    await page.setViewportSize({width: 390, height: 844});
    await visit(page, urls[urls.length - 1]);
    await expectNoHorizontalOverflow(page);
  });
}
