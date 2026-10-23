# Tasks

## 1. 基準與備份（修改前）

- [x] 1.1 （2026-10-23 02:27 UTC：7 家代理指標皆有最新觀測，台股 4 家為 2026-09 月營收，SEC 3 家為最近一季；代理觀測 25 筆；舊 `financials` 326 列；`kind='financials'` 事件 147 筆；v2 表 `financial_groups` 14,205、`financial_raw_facts` 29,505、`financial_observations` 14,991、`observation_provenance` 29,527、`financial_derivations` 2,486、`financial_metric_definitions` 13、`financial_import_batches` 0）唯讀查詢正式 DB，記錄 7 家代理指標公司（AVC、TSMC、Delta、Landmark、MU、AVGO、VRT）在題材指標中最新的觀測期別、數值與來源，以及 `research.financial_*` 7 張表與 `events` 中 `kind='financials'` 的筆數。結果存到 `.work/remove-company-financials/baseline.json`，並在本 tasks 摘要。
- [x] 1.2 （2026-10-23：備份 `20261023T022816Z`，主副本在主 checkout `backups/research/`，第二份在 `D:\backups\industryflow-research\`；manifest 中各財務表筆數與 1.1 一致）執行 `python scripts/research_lab.py backup`，確認備份資料夾的 `manifest.json` 含上述表的筆數與 SHA-256，並在本 tasks 記錄備份資料夾名稱。

## 2. 共用函式搬家（純重構，行為不變）

- [x] 2.1 （2026-10-23：本機全套 288 passed，失敗的 1 項是既有的 Windows managed-git 測試，與本 change 無關）新增 `backend/app/payloads.py`，把 `encoded`、`raw_payload`、`_json`、`decimal_text`、`decimal_value` 逐字搬過去；`source_http.py`、`source_updates.py`、`source_ingestion.py` 改從新模組 import。為 `payloads.py` 補單元測試，涵蓋 Decimal、非有限值拒絕、date、float 拒絕與巢狀結構，`pytest backend/tests` 全數通過。
- [x] 2.2 把 `as_of` 搬到 `research_v2.py`，`research_events.py`、`research_updates.py` 改從新位置 import。以 `pytest backend/tests` 確認行為不變，並以 grep 確認 `research_events.py` 不再 import `research_financials`（`research_updates.py` 只剩 `VALUES_SQL` 用的 `LATEST`，於 5.2 隨 `VALUES_SQL` 一併移除）。

## 3. 營收路徑改接（題材代理指標不中斷）

- [x] 3.1 `connectors.parse_tw` 只接受 `announcements` 與 `revenue`，傳入 `financials` 時明確報錯；`parse_sec_facts` 只解析 revenue tag，「是否保留」與「重編排序」只看 revenue。更新 `test_ingestion.py` 中 kind=financials 與 SEC 毛利／EPS 的斷言：改為測試報錯，並測試只輸出營收。
- [x] 3.2 （2026-10-23：在臨時、獨立的 PostgreSQL 容器上，以 worktree 的程式碼跑 `test_source_updates.py`，16 passed，重跑仍 16 passed；新增 `test_revenue_source_projects_theme_proxy_without_financial_store`。不使用 `research_lab.py pg-check`，因為它會以 worktree 的程式碼覆蓋正式服務的 `industryflow-research-api:dev` image）`source_ingestion.ingest_definition` 移除 TW 與 SEC 的財務分支，`revenue` 與 `sec-facts` 改走 `connectors.fetch_source`；營收來源成功後執行 `project_financials`，不再依賴 canonical。新增測試：以 `fixtures/tw-revenue.json` 與 SEC fixture 跑單一來源更新，確認代理指標出現對應期別的觀測，而且過程完全不讀寫任何 `research.financial_*` 表。
- [x] 3.3 （2026-10-23：`test_financial_indicators.py` 原本就只走舊營收路徑，不需修改，2 passed；`test_source_updates.py` 移除 `test_financial_imports` 依賴，改用自有的 `published_company` fixture，刪除季度財年測試，營收列依來源 id 計數）`test_financial_indicators.py`、`test_source_updates.py` 改用只有營收的 fixture，移除對 `result['financial']`、`financial_groups`、`financial_raw_facts`、`financial_observations` 的斷言，保留排程、重試與來源隔離的測試；`pytest backend/tests` 全數通過。

## 4. 公司比較拆分

- [ ] 4.1 新增 `backend/app/research_compare.py`：搬入 `company()` helper 與原 compare 的 `companies[]` 組裝，回應只含 `companies`；選 2 至 4 家不同公司的驗證照舊，傳入 `basis` 時忽略。在 `main.py` 改掛新 router。新增測試涵蓋：回應沒有 `metrics`／`basis`、超過 4 家被拒、缺風險時明示缺口、帶 `basis` 的舊網址仍可用。
- [ ] 4.2 `research_cache.py` 讓 `compare` 在指定 `release_id` 時歸入不可變類別；`test_research_cache.py` 的 compare 案例改為驗證長期快取，`/financials` 案例刪除。
- [ ] 4.3 前端 `ResearchCompare.tsx` 移除 basis 選單、「財務比較結果」、`ObservationReading` 與相關 import，說明文字改為比較業務、角色與產品；`frontend/lib/research-cache.ts` 把 `compare` 移出動態類別。`npm run typecheck` 通過。

## 5. 移除 backend 財務功能

- [ ] 5.1 刪除 `research_financials.py`、`financial_imports.py`、`financial_store.py`、`financial_core.py`、`financial_sec.py`、`financial_tw.py`，以及 `main.py` 對應的 router；舊 `company_detail` 不再查 `Financial`、回應不含 `financials`，刪除舊 `/api/compare`。以 `grep -rn "financial_\(core\|store\|sec\|tw\|imports\)\|research_financials" backend scripts` 確認只剩 `financial_indicators`。
- [ ] 5.2 `research_updates` 移除 `VALUES_SQL`，公司的 `values_token` 改為 `None`；`test_research_updates.py` 改為斷言公司數值不適用、題材指標 token 照舊。
- [ ] 5.3 `source_updates`：`interval` 與 `describe_capabilities` 移除 `financials`、`balance` 與財務指標；`sources.yaml` 刪除 `twse-financials`、`tpex-financials`、`twse-balance`、`tpex-balance`；`compose.research.yaml` 的 initialize 拿掉 `python -m app.financial_store definitions`；`verify_runtime.py` 改檢查營收列而非財務列。以 `python scripts/validate_map.py` 與 `scripts/research_lab.py check` 驗證。
- [ ] 5.4 刪除 `test_financial_core.py`、`test_financial_store.py`、`test_financial_tw.py`、`test_financial_sec.py`、`test_financial_imports.py`、`test_research_dynamic.py` 中的財務與比較案例（事件與觀察的案例移到保留的測試檔）；`test_sec_http.py` 改用不依賴 `storage` 的 PostgreSQL fixture；`test_map_api.py`、`test_research.py`、`test_research_publication.py` 中引用財務欄位或表的斷言改寫或移除。`research_pg_checks.py` 與 `research_lab.py` 移除 `financial-*` 套件。`pytest backend/tests` 全數通過。
- [ ] 5.5 腳本：`research_integration.py`、`research_load.py`、`research_scale.py`、`reading_ingestion_audit.py`、`reading_snapshot.py`、`restore-check.ps1` 移除對財務表與財務 endpoint 的讀寫；`research_load.py` 的負載組合改用 compare（不含 basis）與 events。每支腳本以 `--help` 或語法檢查（`python -m py_compile`）確認可載入。

## 6. migration 0017 與 PostgreSQL 驗證

- [ ] 6.1 新增 `backend/migrations/versions/0017_drop_company_financials.py`，依 design D4 的順序刪除 view、表與 `research.guard_financial_import()`，保留 `research.guard_immutable_row()`，downgrade raise。`test_research_postgres.py` 移除財務 lineage／引用的測試，新增「0017 之後 `research.financial_*` 不存在、reader 仍可讀已發布研究與事件」的測試。
- [ ] 6.2 演練環境：以 `research_drill.py restore <1.2 的備份>` 還原，接著 `research_drill.py migrate` 升級到 0017，`research_lab.py pg-check --suite all` 全數通過；再以 `research_drill.py offline-refresh --source twse-revenue` 確認代理指標更新，並與 1.1 的基準比對。結果記錄在本 tasks。

## 7. 前端移除

- [ ] 7.1 刪除 `ResearchFinancials.tsx`、`FinancialImports.tsx`、`Financials.tsx`、`lib/research-financial.ts`，其中 `readTime` 先搬到 `lib/display.ts` 並更新 `ResearchEvents.tsx`；`lib/types.ts` 移除 `Financial` 與 `Company.financials`。`npm run typecheck` 通過。
- [ ] 7.2 `ResearchExplorer.tsx`：
  - 公司區塊改名「近期資訊」，只留「官方與報導」「傳聞觀察」，預設開啟官方與報導。
  - 移除財務相關的 URL 參數與連結，保留 `#company-data` 錨點。
  
  `AdminOperations.tsx` 移除「財務補錄」分頁並改寫還原說明；`SourceActions.tsx` 移除財務指標與財務修訂顯示；`lib/admin-proxy.ts`、`app/api/[...path]/route.ts` 移除財務路徑，`publicV2` 保留 compare。以 grep 確認元件中不再出現「基本財務」「財務補錄」。
- [ ] 7.3 CSS：依盤點移除 `.rf-series`、`.rf-trend*`、`.rf-table-wrap*`、`.rf-observation*`、`.rf-history*`、`.rf-metric-values*`、`.rf-comparison-metrics*`、`.rf-comparability`、`.rf-date`、`.financial-value`、`.ra-financial-import*`，保留事件與比較欄位使用的 selector；`npm run build` 成功，在 1440px 與 390px 檢查公司頁、比較頁與後台的畫面，截圖存到 `.work/remove-company-financials/`。
- [ ] 7.4 測試：
  - 刪除 `research-financial.spec.ts`、`financial-imports.spec.ts` 的財務案例，以及 offline `research-financial.spec.ts` 的財務案例；傳聞與事件案例移到保留的 spec。
  - 改寫 `research-cache.spec.ts`（offline 與 live）、`research-cache.node.cjs`、`research-dynamic.spec.ts`、`research-watchlist.spec.ts`（offline 與 live）與 `watchlist-fixture.ts`，改用事件或指標，公司數值改為不適用。
  - 各 fixture 移除 `/financials` 分支；`source-updates.spec.ts` 移除財務指標斷言。
  - 完整 `npm run test:e2e:offline` 通過。

## 8. 文件

- [ ] 8.1 刪除 `docs/research-financial-{acceptance,imports,metrics,sec,tw,reading}.md`；改寫 `docs/research-dynamic-api.md`，只保留事件與觀察；`docs/api.md` 移除財務 endpoint 與舊 compare；`docs/research-lab.md` 移除財務 pg-check 套件。以 `grep -rln "research-financial-" docs README.md AGENTS.md` 確認沒有指向已刪文件的連結。
- [ ] 8.2 更新 README.md、AGENTS.md（「基本財報」字樣），以及盤點列出的其餘文件（watchlist、reading-cache、navigation、source-updates、data-model、integration、backup、coverage、sources、verification、theme-indicators、frontend.md 等），寫成「題材代理指標使用月營收與 SEC 營收；公司財報已移除」。屬於歷史紀錄的文件，例如 `research-acceptance.md`、`research-performance.md`，只加註，不改寫。

## 9. 整合驗證與歸檔

- [ ] 9.1 完整離線檢查：`python scripts/validate_map.py`、`python -m unittest discover -s tests -p "test_*.py"`、`pytest backend/tests`、`npm run typecheck`、`npm run build`、`npm run test:e2e:offline`、`openspec validate remove-company-financials --strict`，全部通過；push 後 CI 通過，並記錄 run ID。
- [ ] 9.2 正式服務實機驗證。依 AGENTS.md，在主 checkout 切到 PR branch，經維護者同意後進行：
  1. 再備份一次。
  2. 重建 api 與 web。
  3. initialize 升級到 0017。
  4. 重建 worker。

  驗證項目：
  - 營收來源單次更新後，7 家代理觀測與 1.1 基準一致，或新增的期別合理。
  - `/api/v2/companies/{id}/financials` 與 `/api/admin/financial-imports` 回 404。
  - 公司比較只有研究內容。
  - 事件頁仍有營收事件。
  - 公司收藏的數值顯示不適用。
  - 被移除的 4 個來源在後台的呈現不誤導（處理 design 的 Open Question）。

  結果記錄在 `docs/research-acceptance.md` 新的一節。
- [ ] 9.3 依 AGENTS.md 在 branch 上執行 `/opsx:archive`，同步 10 份主 spec，CI 通過後才交給維護者 merge。

## Workflow follow-up

- merge 後主 checkout 切回 `main` 並 pull；刪除 worktree 與 branch。
- 後續清理候選：`industry-map/companies/*.md` 的 `financial-reporting` front-matter，需走研究發布流程。
