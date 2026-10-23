// Layout checks shared by offline specs. Wait for a settled layout instead of measuring one frame.
import {expect, type Page} from '@playwright/test';

// tolerance keeps each spec's original allowance in CSS pixels.
export async function expectNoHorizontalOverflow(page: Page, tolerance = 1) {
  await expect.poll(() => page.evaluate(slack => document.documentElement.scrollWidth <= innerWidth + slack, tolerance)).toBe(true);
}
