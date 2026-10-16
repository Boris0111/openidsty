import {defineConfig, devices} from '@playwright/test';

export default defineConfig({
  testDir: './tests/offline',
  outputDir: './test-results/offline',
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:3011',
    serviceWorkers: 'block',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{
    name: 'chromium',
    use: {...devices['Desktop Chrome'], launchOptions: process.env.PLAYWRIGHT_CHROME ? {channel: 'chrome'} : {}},
  }],
  webServer: {
    command: 'node node_modules/next/dist/bin/next start --hostname 127.0.0.1 --port 3011',
    url: 'http://127.0.0.1:3011',
    reuseExistingServer: false,
    timeout: 30000,
    env: {API_ORIGIN: 'http://127.0.0.1:9', NEXT_TELEMETRY_DISABLED: '1'},
  },
  reporter: [['list'], ['html', {outputFolder: 'playwright-report/offline', open: 'never'}]],
});
