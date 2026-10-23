# Tasks

## 1. 升級與離線驗證

- [ ] 1.1 先把 branch rebase 到最新的 `main`。若 PR #7 已 merge，就包含公開快照的腳本；若還沒 merge，在本 task 註明，1.3 改為不適用。接著執行 `npm install next@16.4.3 --save-exact`。驗證：
  - `package.json` 只有 `next` 那一行改變。
  - `npm ls next` 顯示 `16.4.3`。
  - `npm audit` 回報 0 個漏洞。
- [ ] 1.2 驗證：`npm run typecheck`、`npm run build`（standalone）、`npm run test:e2e:offline` 全部通過；若 PR #7 已 merge，再加上 `npm run test:unit`。
- [ ] 1.3 若 PR #7 已 merge，以合成快照執行 `node scripts/write-fixture-snapshot.mjs` 與 `npm run build:static`（含爬頁）。驗證：靜態頁面測試全部通過，並記錄建置時是否還出現 Next.js 的安全升級提示。
- [ ] 1.4 驗證：PR 的 CI 通過。

## 2. 正式服務

- [ ] 2.1 在主 checkout 切到這個 PR 的 commit（先徵得維護者同意），執行 `python scripts/research_lab.py up` 重建 api 與 web。驗證：
  - `docker exec industryflow-research-web-1` 中的 Next.js 版本是 16.4.3。
  - 讀者端 live E2E（`RESEARCH_E2E=1`）通過。
  - 地圖、題材、公司、搜尋頁抽查正常。

  結果記錄在 `docs/research-acceptance.md` 新的一節。

## Workflow follow-up

- tasks 全部勾完後在 branch 上 archive（`skip_specs`，沒有 spec 需要同步），再交給維護者 merge。
- merge 後，主 checkout 切回 `main` 並 pull，再執行一次 `research_lab.py up`。
- 公開網站不需要因為這個 change 重新部署；下次發布研究時，照 `docs/public-snapshot.md` 重建，就會用新版。
