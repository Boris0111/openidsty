# Proposal

## Why

公司財報功能沒有穩定的資料 API，資料庫累積的期數也不足以支撐「基本財務」頁與財務比較；繼續維護它只會增加程式、排程與規格的負擔。產品已重新定位為「有來源、標信心等級的產業結構地圖」（2026-10-23 決策），公司財報先剃除，日後找到替代資料再另提。題材指標仍需要公司揭露的營收作為證據，所以要保留最小的營收抓取，而不是連根拔除。

## What Changes

- **BREAKING** 移除公司財報的讀者功能：公司頁的「基本財務」分頁、財務觀測與修訂歷史、`/api/v2/companies/{id}/financials`（含 observations）、舊 `/api/companies/{ticker}` 的 `financials` 欄位、舊 `/api/compare`，以及前端 `Financials`、`ResearchFinancials` 元件。
- **BREAKING** 移除維護者的官方財務補錄：`/api/admin/financial-imports` 與後台「財務補錄」分頁。
- **BREAKING** 移除 v2 財務儲存：`financial_core`、`financial_store`、`financial_tw`、`financial_sec`、`financial_imports`、`research_financials` 模組，並以新 migration `0017` 刪除 `research.financial_*` 共 7 張表與其 view、RLS policy、trigger 與函式（執行前先備份）。
- **公司比較保留，但只比非財務內容**：業務模式、供應角色、產品、風險、判斷與缺口。改由新的 `research_compare` 模組提供 `/api/v2/compare`，不再接受 `basis`、不回傳 `metrics`；比較內容固定於研究版本，改依研究版本長期快取。
- **營收抓取縮減為題材 proxy 所需**：
  - 台股月營收（`twse-revenue`、`tpex-revenue`）與 SEC 營收（`sec-facts`）改走舊的 `connectors.parse_tw`／`parse_sec_facts`，只寫入舊 `financials` 表的營收欄位，`project_financials` 在營收來源成功後即投影到題材指標，不再依賴 v2 財務表。
  - 停止抓取季度損益與資產負債（`twse-financials`、`tpex-financials`、`twse-balance`、`tpex-balance`），並從 `sources.yaml` 移除；SEC 不再解析毛利、成本與 EPS。
- **營收事件照常記錄**：月營收更新仍產生事件並出現在事件流與「財報／營收」篩選；既有的財報類事件保留在資料庫，不刪除。只是不再有單獨呈現公司財務狀況的頁面或區塊。
- **連帶調整**：
  - 公司收藏的「數值」改為不適用（與產品相同），研究與事件更新照常追蹤。
  - 後台來源詳情不再列財務指標能力。
  - 共用函式搬出被刪除的模組：`as_of`、`encoded`、`raw_payload` 及其依賴的 `_json`、`decimal_text`、`decimal_value`。
  - 對應的測試、pg-check 套件、腳本與文件一併刪改。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `company-research`：移除「基本財務保留定義與修訂」；以非財務的公司比較取代「財務圖表與公司比較不得混用口徑」；公司頁不再顯示基本財務，業務曝險改說明不以公司營收代替產品收入。
- `official-information-ingestion`：移除「財務觀測可重現且不跨申報混用」與「來源能力限制與官方補錄」；更新節奏改為公告每小時、營收（題材 proxy）每日；其餘條文去掉「財報」字樣。
- `industry-explorer`：傳聞觀察、跨版本閱讀、供應鏈頁與數值呈現的條文去掉公司財務（「比較候選公司」屬讀者功能的條文不變，因公司比較保留）。
- `platform-runtime`：快取分類中「財務、含財務的比較」改為「指標」；公司比較歸入固定研究版本的內容；文件更新條文去掉「財報」。
- `data-coverage`：回補改為指標歷史；缺口情境改用營收代理指標。
- `research-publishing`：還原時保留的是事件與指標修訂。
- `research-watchlist`：更新摘要區分研究變更、有效指標修訂與新事件；公司不再有數值追蹤。
- `theme-assessments`：讀者可查看已公開的事件與指標。
- `theme-indicators`：寫明營收代理觀測的來源是台股月營收與 SEC 營收。
- `industry-map`：研究投影條文中「動態事件及財務」改為「動態事件及指標觀測」。

## Impact

- **backend**：刪除 6 個財務模組與其測試；新增 `research_compare.py`；修改 `main.py`、`source_ingestion.py`、`source_updates.py`、`source_http.py`、`research_events.py`、`research_updates.py`、`research_cache.py`、`connectors.py`、`ingest.py`、`research_pg_checks.py`、`verify_runtime.py`；新增 migration `0017`。
- **資料庫**：刪除 `research.financial_*` 7 張表與相關物件（不可逆，先備份）；舊 `financials` 表保留供題材 proxy；既有事件不動。
- **frontend**：刪除 `ResearchFinancials`、`FinancialImports`、`Financials`、`lib/research-financial.ts`；改寫 `ResearchCompare`、`ResearchExplorer`、`AdminOperations`、`SourceActions`、proxy allowlist、`research-cache.ts`、`types.ts` 與 CSS。
- **設定與腳本**：`compose.research.yaml` 的 initialize 指令、`sources.yaml`、`research_lab.py` 的 pg-check 套件、`research_integration.py`、`research_load.py`、`research_scale.py`、`restore-check.ps1`。
- **文件**：刪除 `docs/research-financial-*.md`，改寫約 20 份提及財務的文件；README 與 AGENTS.md 的「基本財報」字樣。
- **不動的部分**：題材 direct 指標（AAON、台積電 2nm）、題材 proxy 指標、事件與傳聞觀察、研究發布流程、`industry-map/companies/*.md` 的 `financial-reporting` front-matter（保留為公司資料，不再驅動任何程式）。
