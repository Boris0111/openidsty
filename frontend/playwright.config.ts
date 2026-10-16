import {defineConfig,devices} from '@playwright/test';
export default defineConfig({
  testDir:'./tests', testIgnore:'**/offline/**', outputDir:'./test-results/live', fullyParallel:false, workers:1, timeout:30000,
  use:{baseURL:process.env.E2E_BASE_URL||'http://localhost:3010',trace:'retain-on-failure',screenshot:'only-on-failure'},
  projects:[{name:'chromium',use:{...devices['Desktop Chrome'],launchOptions:process.env.PLAYWRIGHT_CHROME?{channel:'chrome'}:{}}}],
  reporter:[['list'],['html',{open:'never'}]]
});
