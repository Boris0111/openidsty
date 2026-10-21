## Why

新版研究服務已合併 `main`、歸檔並通過最終閱讀驗收，2026-10-21 也已從主專案啟動、輪替祕密並重設 owner；但它仍跑在預覽 port `3014`／`8014`，讀者書籤、v1 題材收藏（瀏覽器 localStorage 依 origin 隔離）與舊連結都還在原服務 origin `127.0.0.1:3010`。正式切換檢查表第 7 步要求新版接手原 origin，這需要修改 port、origin allowlist 與工具檢查，屬程式變更，因此另立此 change。

## What Changes

- 新版研究服務（Compose project `industryflow-research`）改綁原服務的 port：web `3010`、API `8010`、Prefect `4201`；唯讀入口 reader gateway 維持 `3015`，還原演練維持 `3016`／`8016`。**BREAKING**：預覽網址 `3014`／`8014`／`4204` 停用，在 3014 存的收藏需以 JSON 匯出／匯入搬到 3010。
- 管理入口 origin／host allowlist（`RESEARCH_ADMIN_ORIGINS`、`RESEARCH_ADMIN_HOSTS`）同步改為 3010／8010；`scripts/research_lab.py` 的 port 檢查、`research_cli` 預設網址、開發啟動設定與相關測試常數一併更新。
- 新版與原服務（Compose project `industryflow`，`compose.yaml`）不得同時運行：啟動新版前若原服務任何容器在跑或 port 被占用，操作 MUST 拒絕並說明；回復時反向操作。
- 驗證同一 origin 下：舊 ticker 深連結、舊題材網址可解析，舊 `#candidates` 轉到「數據與追蹤」，v1 題材收藏首次開啟時遷移一次且保留 v1 原值。這些行為已在既有 specs 定義，本 change 只在新 origin 實測並記錄。
- 更新 README 與研究服務操作文件：3010 為正式入口，原 `compose.yaml` 成為回復用的舊版服務。

不在範圍：第 5 步私人網路（HTTPS reverse proxy、跨裝置讀取）；scheduler 啟用與 10-18 起的資料補抓（由切換流程另行執行）；刪除原服務的 image 或 volume。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `platform-runtime`：「新舊開發環境相互隔離」改為描述切換後的狀態：正式研究服務占用原 origin，與原服務互斥運行並可回復；預覽 port 停用。

## Impact

- 設定：`compose.research.yaml`（ports、admin origin／host、Prefect UI URL）、`.Codex/launch.json`
- 工具：`scripts/research_lab.py`（`PORTS`、`up` 的互斥檢查）、`backend/app/research_cli.py`（預設 base URL）
- 測試：`backend/tests/test_research_auth.py` 等的 origin 常數；live e2e 改以 `E2E_BASE_URL=http://127.0.0.1:3010` 執行
- 文件：`README.md`、`docs/research-lab.md`、`docs/research-owner.md`、`docs/research-reader-entry.md`、`docs/research-acceptance.md`（切換記錄）
- 執行環境：重建 `industryflow-research` 的 api／web 容器（volume 不變）；原服務 `industryflow` 保持停止
