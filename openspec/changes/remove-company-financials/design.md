# Design

## Context

動機見 proposal.md 的 Why，行為要求見 `specs/` 下 10 份 delta。以下是 2026-10-23 盤點時確認、會影響做法的現況。

### 保留的營收路徑目前依賴要刪的模組
- 正式研究 runtime 的 `source_ingestion.ingest_definition`（`:49-118`）中：
  - TW 的 `revenue`、`financials`、`balance` 三種 kind 都先經 `financial_tw.parse_taiwan` 和 `persist_taiwan`。
  - 只有 canonical 解析成功的發行人，才會再由舊 `connectors.parse_tw` 產生 `Financial` 列（`:56-86`）。
- SEC `sec-facts` 先經 `financial_sec.parse_companyfacts` 和 `persist_sec`，再回傳 `connectors.parse_sec_facts`（`:87-99`）。
- `project_financials` 只在 `if canonical` 分支內執行（`:110-116`）。
- **結論**：直接刪掉 `financial_tw`、`financial_sec`，題材的營收代理指標會悄悄停止更新。
- `project_financials`（`financial_indicators.py:33`）本身只讀舊 `Financial` 表的 revenue、currency、period、basis、時間、url、raw，不讀 v2 表，也不讀 gross_margin、eps。
- 代理指標的來源（`data/theme-indicators.yaml`）：
  - `twse-revenue`：AVC、TSMC、Delta
  - `tpex-revenue`：Landmark
  - `sec-facts`：MU、AVGO、VRT

### 共用函式散在要刪的模組
- `research_financials.as_of`：被 `research_events.py:69`、`research_updates.py:108` 使用。
- `financial_store.encoded`、`raw_payload`：被 `source_http.py`、`source_updates.py` 使用。它們依賴 `financial_core._json`，`_json` 又依賴 `decimal_text`、`decimal_value`。
- `research_financials.LATEST`：只有 `research_updates.VALUES_SQL` 用到，表刪掉後就失去意義。

### 公司比較
`/api/v2/compare`（`research_financials.py:166`）同時組兩部分：
- `companies[]`：業務模式、角色、產品、風險、判斷、缺口，只依賴 `research_v2` 與 `research.company_offerings`。
- `metrics[]`：依賴 v2 財務表。

### 資料庫
- v2 財務物件分散在 `sql/0007`（7 張表與 grant）、`sql/0008`（RLS）、`0011`（索引與 trigger）、`0012`（欄位與索引）、`0013`（confirmation 欄位、函式、trigger）、`0015`（`financial_fact_citations` view）、`0016`（reader policy）。
- 最新 migration 是 `0016`，所以下一個是 `0017`。`0011`–`0013` 的 downgrade 都是直接 raise。

### 其他
- 營收事件：`connectors.parse_tw` 的 kind=revenue 會產生 `kind='financials'` 事件（`connectors.py:118`）；`classify.py:33`、`event_dates.py:17` 會處理這類事件。
- `registry.source_definitions` 用舊 `Company.cik` 展開 `per_company` 的 SEC 來源，新舊 runtime 都使用它（`source_updates.py:29`）。

## Goals / Non-Goals

**Goals：**
- 刪除公司財報的程式、表與介面，但讓題材代理指標的營收**不中斷**。
- 每一步都能獨立驗證；刪除不可逆的部分（DB）排在最後，且先備份、先在演練環境跑過。

**Non-Goals：**
- 不刪除舊 `financials` 表與其欄位。gross_margin、eps 之後只會是 null，不另做 schema 變更。
- 不刪除既有事件（包括季度財報事件）與 `Source` 列。歷史事件仍引用它們。
- 不改 `industry-map/companies/*.md` 的 `financial-reporting` front-matter 與其 schema 驗證。它保留為公司資料，不再驅動程式。
- 不新增公司財務的替代資料來源。

## Decisions

### D1：營收改走舊 connectors，v2 解析整條拿掉
- `source_ingestion` 移除 TW 與 SEC 的財務分支。
  - `revenue` 與 `sec-facts` 交給 `connectors.fetch_source`，和舊 `ingest.run_ingestion` 的路徑相同。
  - 發行人範圍用 `ingest_one` 既有的 `tracked`（公司表中的台股代號），不再用 `legacy_mappings` 加 `financial-reporting` 篩選。
- 營收來源成功、而且有新增或變動的 `Financial` 列時，就執行 `project_financials`。條件不再綁 canonical。
- `connectors.parse_tw`：
  - 只接受 `announcements` 與 `revenue`。`financials` kind 改為明確錯誤，避免設定殘留時默默產生資料。
- `parse_sec_facts`：
  - 只解析 revenue tag，去掉 gross_profit、cost、eps 與毛利推導。
  - 「是否保留這期」與「重編排序」只看 revenue。
- **不選：保留 `financial_tw` 只做解析。** 它的設計目標是 canonical 儲存，留著就等於留著半個財務系統；舊 connectors 已經能解析同一份 OpenAPI 資料，CI 也一直有測試。
- **風險**：canonical 路徑會依 `financial-reporting` 篩掉資料品質不足的發行人；改用 `tracked` 之後，篩選範圍可能變寬。
  - → 代理指標本身只投影 `theme-indicators.yaml` 列出的 7 家公司，其餘公司的營收列不會被讀者看到。apply 時比對切換前後這 7 家的代理觀測是否一致。

### D2：共用函式搬到中性模組
- 新增 `app/payloads.py`，放 `encoded`、`raw_payload`、`_json`、`decimal_text`、`decimal_value`，行為與原實作逐字相同。
- `as_of` 搬到 `research_v2.py`，和 `envelope` 等讀者回應工具放在一起。
- `LATEST` 隨 `research_financials` 刪除。
- **先搬家、再刪除**：搬家是純重構，測試應全部照舊通過，所以和功能變更分成兩步。

### D3：比較拆成 `research_compare.py`
- 新模組提供 `GET /api/v2/compare?company_ids=...&release_id=...`。
- 內容搬自原 compare 的 `companies[]` 部分，加上 `company()` helper。
- 回應只有 `companies`，不再有 `basis`、`metrics`、`policy`、`as_of`。
- 傳入 `basis` 參數時忽略它，不報錯，讓舊的分享網址仍能開啟。
- `research_cache.py`：`compare` 從 30 秒的動態類別移到「指定研究版本即不可變」的類別。
- 前端 `ResearchCompare`：去掉 basis 選單、「財務比較結果」與 `ObservationReading`；說明文字改成「比較業務、角色與產品」。

### D4：migration 0017 一次刪除 v2 財務物件
- 依相依順序刪除：
  1. view `research.financial_fact_citations`
  2. 財務表上的 trigger 與 policy（隨 `DROP TABLE` 一併移除）
  3. 7 張表，由子到父：`observation_provenance`、`financial_derivations`、`financial_observations`、`financial_raw_facts`、`financial_import_batches`、`financial_groups`、`financial_metric_definitions`
  4. 函式 `research.guard_financial_import()`
- 共用的 `research.guard_immutable_row()` 保留。
- downgrade 直接 raise，與 `0011`–`0013` 一致。要復原就從備份還原。
- `compose.research.yaml` 的 initialize 拿掉 `python -m app.financial_store definitions`，`financial_indicators` 保留。
- **上線前的雙重保護**：
  1. `research_lab.py backup`，產生 `database.dump`、`git.bundle`、`assets.tar`、`manifest.json`。
  2. 用 `research_drill.py` 把這份備份還原到獨立的演練環境，在演練環境升級到 `0017`，跑 pg-check。
  3. 演練通過後，才對正式服務執行。

### D5：公司收藏的數值改為不適用
- `research_updates` 拿掉 `VALUES_SQL`，公司的 `values_token` 改回傳 `None`，與產品相同。
- 前端 `ResearchWatch` 在 `applicable=false` 時本來就會隱藏數值列。
- 收藏的儲存格式不變，舊的 `seen.values` 會被忽略，不會報錯。

### D6：營收事件照常、季度財報來源移除
- 月營收仍產生 `kind='financials'` 事件，事件頁的「財報／營收」篩選保留；既有季度財報事件也留在資料庫。
- `sources.yaml` 刪除 `twse-financials`、`tpex-financials`、`twse-balance`、`tpex-balance` 四筆。這些只為 v2 財務而設，沒有其他用途。
- `source_updates.interval` 與 `describe_capabilities` 拿掉 `financials`、`balance` 與財務指標描述。

### D7：前後端與文件同步移除
- 依盤點清單刪除元件、API、測試與文件，詳見 tasks。
- 公司頁的區塊改名為「近期資訊」，只留「官方與報導」「傳聞觀察」兩個分頁，預設開啟「官方與報導」。
- `#company-data` 錨點保留，舊的分享連結仍能定位到這個區塊。

## Risks / Trade-offs

- **[風險] 營收改走 `tracked` 之後，代理指標的期別或數值和切換前不同。**
  - → task 先記錄切換前 7 家公司代理觀測的最新期別與數值，切換後在演練環境與正式服務各比對一次；不一致就停下調查。
- **[風險] migration 0017 不可逆。**
  - → 先備份、先在演練環境升級並跑 pg-check，正式升級前需經維護者同意（AGENTS.md 規則）。
- **[風險] 被移除的 4 個來源在後台來源列表或覆蓋頁留下「從未更新」的殘影。**
  - → apply 時檢查 `/api/sources` 與覆蓋頁；若會誤導，就把這些來源標示為已停用，而不是刪除列。
- **[風險] 刪除 `test_financial_store.py` 後，`test_sec_http.py` 失去 `storage` fixture。**
  - → 改用既有的 PostgreSQL 連線 fixture，或在測試檔內建立最小的連線 fixture；只影響需要 PostgreSQL 的那一項測試。
- **[取捨] 季度財報事件的歷史保留，但不會再有新的。**
  - → 事件頁篩選名稱維持「財報／營收」，舊事件仍可讀。
- **[取捨] `financial-reporting` front-matter 不再被任何程式使用，但仍留在 26 份公司研究中。**
  - → 列為後續清理候選；改它需要走研究發布流程，不混入這個 change。

## Migration Plan

1. **備份**：`python scripts/research_lab.py backup`，確認 manifest 中 `research.financial_*` 的筆數。
2. **演練環境**：以 `research_drill.py` 還原這份備份，在演練環境的 image 上升級到 `0017`，跑 `research_lab.py pg-check --suite all`。
3. **正式服務**：依 AGENTS.md，在主 checkout 暫時切到 PR branch，經維護者同意後：
   1. 重建 api 與 web image。
   2. 執行 initialize，完成 alembic 升級到 `0017`。
   3. 重建 worker。
4. **驗證**：
   - 營收來源單次更新後，7 家代理觀測與切換前一致。
   - 財務 endpoint 回 404。
   - 公司比較只有研究內容。
   - 事件頁仍有營收事件。
5. **回滾**：
   - 程式：切回 `main` 重建容器。
   - DB：用第 1 步的備份還原。0017 沒有 downgrade。

## Open Questions

- 被移除的 4 個來源在管理端要「保留但標示停用」，還是「直接不列出」？取決於 apply 時 `/api/sources` 的實際呈現，不影響其他設計。
