import {defineConfig, devices} from '@playwright/test';

// The public static build in out/, served like the CDN; STATIC_SNAPSHOT_DIR names the snapshot the pages come from.
export default defineConfig({
  testDir: './tests/static',
  outputDir: './test-results/static',
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:3017',
    serviceWorkers: 'block',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{
    name: 'chromium',
    use: {...devices['Desktop Chrome'], launchOptions: process.env.PLAYWRIGHT_CHROME ? {channel: 'chrome'} : {}},
  }],
  webServer: {
    command: 'node scripts/serve-static.mjs --root out --port 3017',
    url: 'http://127.0.0.1:3017',
    reuseExistingServer: false,
    timeout: 30000,
  },
  reporter: [['list'], ['html', {outputFolder: 'playwright-report/static', open: 'never'}]],
});
