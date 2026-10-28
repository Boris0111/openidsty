# Proposal

## Why

正式研究服務直接從開發 checkout `C:\Users\User\openspec_pjt` 運行（`docs/research-lab.md:3`），開發動作會直接改變正式環境：

- **image 由當下的 working tree 決定**：
  - `research_lab.py` 的 `up`、`seed-git`、`rebuild-check`／`bootstrap`、`pg-check` 都會 `compose build`（`scripts/research_lab.py:456`、`:403`、`:416`、`:442`），把當下 branch 連同未提交的修改，建到可變的 tag `industryflow-research-api:dev`／`web:dev`（`compose.research.yaml:4`）。
  - 演練環境也用同一個 tag。
  - image 不含 commit 資訊，事後無法得知正式服務跑的是哪個版本。
- **流程規則要求正式服務跑未 merge 的程式碼**：
  - `AGENTS.md:84` 規定 merge 前在主 checkout 切到 PR branch，對正式服務演練。
  - 2026-10-24 PR #9 因此在正式服務上跑了約 10 小時合併前的程式碼。
  - `docs/research-acceptance.md:374` 記錄過這段期間「`main` 的 alembic 不認得 `0017`」，不能從 `main` 重建。
- **image 內容與版本控制不同**：系統的 `core.autocrlf=true`。以 `industry-map/themes/800vdc.md` 實測，git 內容沒有 CR，正式 image 裡卻有 136 個 CR。
- **回退沒有定義**：
  - `0017_drop_company_financials` 刪了 7 張表，downgrade 會直接 raise。
  - 比 `0017` 舊的 image 在 `initialize` 時，會因為不認得 revision 而失敗（`compose.research.yaml:42`）。
  - 文件卻仍寫「schema 都是 additive」（`docs/research-acceptance.md:229`、`docs/research-lab.md:27`）。
- **祕密與備份綁在開發 checkout**：
  - `.env.research` 只有這一份，而且不在備份範圍（`docs/research-backup.md:29`）。
  - 每天 03:30 的備份排程執行的是當下 branch 的 `research_lab.py`。

地圖正要往廣度擴充，change 的數量會增加。在那之前，要先讓「正式環境只跑已合併的版本」成為機制，而不是靠人記得。

## What Changes

- **獨立的正式部署目錄**：
  - 正式服務改由獨立 clone `C:\Users\User\industryflow-prod` 運作，固定在已部署的 commit（detached）。
  - 正式祕密、備份、部署紀錄、公開快照輸出、備份排程的工作目錄都放在這裡。
  - 開發 checkout 不再保有 `.env.research`。
- **正式操作的防護**：
  - 會改變正式服務的動作，只在部署目錄、working tree 乾淨、HEAD 與部署紀錄一致時才執行。
  - `setup` 遇到正式資料庫 volume 已存在時，拒絕產生新祕密。
- **以 commit 標記的 image**：
  - 只從 `git archive` 建置（不經過換行轉換，也不含未追蹤檔案）。
  - tag 為 `industryflow-research-{api,web}:<sha12>`。
  - label 記錄 commit、alembic head、收縮遷移清單與 Prefect 版本。
  - 兩個 compose 檔移除 `build:`，image tag 由腳本注入。
- **部署與回退指令**：
  - `research_lab.py deploy --commit <sha>`：
    - 只接受 `origin/main` 第一父鏈上的 commit。
    - 先備份。
    - 新 image 的 `initialize` 成功後，才替換所有運行中的 app 服務。
    - 最後做 smoke 檢查，寫入部署紀錄。
    - smoke 失敗時只回報，並給出可以直接執行的回退指令，或說明為何只能還原備份。
  - `rollback --to <序號>`：
    - 不重跑 `initialize`。
    - 跨越收縮遷移或 Prefect 版本時拒絕。
  - 另新增 `status`、`scheduler-start`。
- **遷移分成擴充（expand）與收縮（contract）**：
  - 新增 `scripts/migration_rules.py` 與 CI 測試；有破壞性語句的遷移必須明確標記。
  - 既有的 `0009`（`DROP POLICY`）與 `0017` 標為收縮。
  - 含收縮遷移的部署需要明確確認，那次的部署前備份就是回退邊界，不會被 30 天清理刪除。
- **merge 前的實機驗證改在演練環境**：
  - `research_drill.py` 用最新正式備份還原基準狀態，再以 PR commit 的 image 預演部署與回退。
  - 分支程式的 PostgreSQL 契約檢查（`pg-check`）與重建檢查（`rebuild-check`）從 `research_lab.py` 移到演練環境，不再碰正式的資料庫 cluster 與 volume。
  - 演練祕密改放在 `INDUSTRYFLOW_DRILL_HOME`，可以從 worktree 執行，錯誤輸出會遮蔽演練祕密。
- **流程規則**：
  - 改寫 `AGENTS.md`「先驗證、再 merge」：merge 前的實機驗證在演練環境完成，不再切換主 checkout。
  - 正式部署在 merge 後依標準程序進行，以部署紀錄的 smoke 結果作為紀錄，不列為 change 的 task。
- **BREAKING（維運指令）**：
  - `research_lab.py up` 不再建置，改為提示使用 `deploy`。
  - `pg-check`、`rebuild-check` 從 `research_lab.py` 移除，`.env.research` 移出開發 checkout。
  - 依賴舊指令的文件一併改寫。
- **術語**：程式碼的發布稱為「部署（deployment）」或「image 版本」。「release」「restore」維持研究內容版本的原意，不混用。
- **不在範圍內**：
  - CI 加 PostgreSQL。
  - flaky 測試政策與 main 紅燈告警。
  - merge 關卡（分支保護）。
  - 異地備份。
  - 搬到雲端主機。
  - 原服務（project `industryflow`）的處理方式。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `platform-runtime`：新增 4 條 requirement，修改 2 條。
  - 新增：正式服務只執行已合併提交的版本化 image；部署與回退先備份並留有紀錄；資料庫遷移區分擴充與收縮；合併前實機驗證在演練環境進行。
  - 修改「開發與維護操作可驗證」：維護文件加入部署、回退與部署紀錄。
  - 修改「自動檢查與 runtime 一致」：維運腳本測試涵蓋部署、回退與遷移分類規則。
  - 「新舊開發環境相互隔離」文字不變。

## Impact

- **維運腳本**：
  - `scripts/research_lab.py`：新增 deploy、rollback、status、scheduler-start、防護與部署紀錄；修改 compose 注入、設定檢查、setup 與備份 manifest。
  - `scripts/research_drill.py`：image tag、演練目錄、祕密遮蔽，以及還原、預演、PG 檢查。
  - 新增 `scripts/migration_rules.py`。
  - `scripts/research_scale.py`、`research_draft_bench.py` 改用演練目錄的祕密路徑；`research_load.py` 改記演練實際運行的 image。
- **設定**：
  - `compose.research.yaml`、`compose.research-drill.yaml`：移除 `build:`，改用 tag 變數。
  - `.gitignore` 加入 `/deployments/`。
  - Dockerfile 不變，label 在建置時注入。
- **遷移**：`backend/migrations/versions/0009_*.py`、`0017_drop_company_financials.py` 只加收縮標記，`0016_reader_row_lookups.py` 只加 `EXPAND_REVIEWED` 標記，都不改 schema。
- **測試**：root `tests/` 新增遷移規則、建置、防護、部署、回退與演練環境的 unittest，不需要 Docker，在 CI 執行。`backend/tests/conftest.py` 讓需要 `scripts/research_scale.py` 的測試在 API image 內 skip（CI 從 checkout 照常執行），`pg-check --suite all` 才能在演練環境完整通過。
- **文件**：
  - 新增 `docs/research-deployment.md`。
  - 改寫 `AGENTS.md`、`README.md`、`docs/research-lab.md`、`research-backup.md`、`public-snapshot.md`、`research-owner.md`、`research-reader-entry.md`。
  - `research-acceptance.md` 的歷史段落只加註，不改寫。
- **營運**：
  - merge 後的首次部署就是正式環境切換：建立部署目錄、搬移祕密與備份、改寫備份排程、在部署目錄重建 db 容器，會有一次短暫的全面停機。這需要 Boris 同意並在場。
  - 本機舊 branch 由 Boris 刪除。
- **相依套件**：不新增。
