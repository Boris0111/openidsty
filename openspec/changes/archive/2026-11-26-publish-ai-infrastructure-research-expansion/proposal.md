# AI 基礎設施研究發布提案

## Why

已歸檔的 `expand-ai-infrastructure-research` 通過演練部署、研究發布及桌機與 iPhone 走讀，待交付正式研究與公開站。現行研究 release 的來源清單仍含四筆已從 `main` 移除、並在正式資料庫標為 `retired` 的財報來源，需在本次發布補齊同步。

## What Changes

- 在隔離環境補驗來源清單，確認移除四筆退役項目後，三方向研究內容與已走讀版本一致。補記驗收證據並修正失效的歸檔連結。
- 通過最終 PR CI 後合併研究擴充與發布準備紀錄，依正式服務 runbook 部署合併提交。
- 從最新正式研究整合已驗收的內容與來源差異，依現有草稿流程發布，再由同一正式 release 建置、驗證與部署公開快照。

## Capabilities

### New Capabilities

無。

### Modified Capabilities

無。沿用 `platform-runtime`、`research-publishing` 與 `public-research-snapshot` 現行契約，這次交付的是研究資料、部署及驗收紀錄。`.openspec.yaml` 設定 `skip_specs: true`。

## Impact

- GitHub `main`、正式研究服務的 image 與部署紀錄、正式研究的 active release，以及 Cloudflare Pages `industryflow` 的 production deployment。
- 研究矩陣、驗收紀錄、研究草稿與公開快照。適用既有 API、Schema、排程及權限設定。
