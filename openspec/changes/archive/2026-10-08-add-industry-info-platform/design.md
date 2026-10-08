# Design

## Context

動機與功能契約見 proposal 與四個 delta specs。現有 repo 僅有 Markdown 地圖及 Python 驗證器，另有尚未提交的既有地圖成果，必須保留。新工作一律在本 repo；舊 financeinfost 僅用來檢視 parser 與中文別名問題。

本機 Node.js 24、Python 3.12 與 Docker 可用；3000／8000／5432 已被其他專案使用。來源網頁可讀不代表自動擷取成功，TWSE OpenAPI 已出現 DNS 問題。

## Goals / Non-Goals

**Goals:** 提供可實際啟動的資訊網站，維持來源、查證與資料缺口的語意；流程失敗不使公開 API 失效。

**Non-Goals:** 不建行情、交易、帳號、業務 Redis cache、Neo4j 或 LLM 呼叫。候選關係可以人工維護，AI 探勘留待摘要階段。

## Decisions

### 應用層與產業結構分離

後端使用 FastAPI、SQLAlchemy、Alembic；PostgreSQL 保存環節投影、去重公司、公司環節角色、關係、事件、財報、來源狀態與每輪更新紀錄。Markdown 是環節／題材的來源；匯入前執行既有驗證器，失敗不更新投影。原始來源 JSON 保存於資料庫，財報指標採具期間、幣別及 basis 的欄位。SQLite 僅用於離線單元測試，不作執行期資料庫替代。

### 官方來源優先

首批 connector 為台灣上市／上櫃官方公告、營收／損益資料，SEC submissions／companyfacts，及現有來源表的台積電、台達電、NVIDIA、微軟 IR 入口。JSON／CSV parser 與 HTTP 抓取分離，官方不可用時只回報狀態，不發布 fixtures。SEC User-Agent 由維護者設定；直接 IR 來源只收已發布文件，未來活動僅記錄為預告。來源依官方文件 ID／來源 URI 去重，財報以公司、期間、口徑與來源版本辨識；重述資料可更新並保留原始來源。

### 圖形與公司關係

Next.js App Router 提供公開頁面；Cytoscape.js 只在 client component 執行。產業圖顯示所選 layer 所有環節與直接跨 layer 鄰居，依 position 提供方向感而不砍回路。公司圖為中心的一跳 induced subgraph，保留鄰居間已知關係；供應箭頭從 supplier 指向 customer，partner 依記錄顯示單／雙向。顏色按相對中心公司的上下游及策略合作區分，候選用虛線；high／medium／low 對應大／中／小節點，unknown 使用固定小節點。grade 與 evidence／review status 分離，不由 tier 或連結數代替。

公司關係與 aliases 由版本控制的維護檔匯入；已確認關係須有可回查來源、理由與查核時間。公開站不提供寫入端點。初始關係採少量可驗證例子，不宣稱覆蓋全部公司；未知關係顯示資料缺口。

### API 與介面

唯讀 `/api/industries`、`/api/industries/{id}/graph`、`/api/segments/{id}`、`/api/companies`、`/api/companies/{ticker}`、`/api/companies/{ticker}/graph`、`/api/compare`、`/api/events`、`/api/events/{id}`、`/api/sources` 與 `/api/health`。圖輸出 nodes／edges 與中心／layer 中介資料，`include_candidates` 預設 false。所有公司連結以 URL-encoded ticker 識別。事件原文提及與結構推導公司分離，遍歷輸出路徑類型與 inference 標籤。

介面以白色、藍灰底及深藍文字為基底，圖形採供應藍、需求橘、策略合作紫；字體使用系統繁中 sans-serif 與清楚的數字字級。主畫面是大面積圖＋環節詳情側欄，其他元素安靜支援研究。公司頁固定顯示角色、基本財報、關係圖與事件；比較支援二至四家並列，保留期間與幣別。文字清單作為鍵盤及小螢幕可用的替代導覽。

### 執行環境

Compose project 使用獨立名稱與 volumes，web 3010、API 8010、Prefect 4201 均預設綁定 loopback，PostgreSQL 不發布 port。單一 PostgreSQL cluster 使用獨立 app／Prefect databases；一次性 migration／import 成功後再啟動 API 與流程。Prefect 單機 server 使用預設訊息機制，worker 接 process pool，每小時部署 concurrency limit 1；資料庫 advisory lock 防止手動執行與排程重疊。公開部署可透過 Caddy TLS reverse proxy，只公開網站與唯讀 API。

## Risks / Trade-offs

- 官方端點阻擋、逾時或格式改變 → 有界逾時與重試、來源狀態、fixtures；先證明取得實際資訊，UI 不填假資料。
- 財報年度、單季與累計混用 → period／basis／currency 明確記錄；只有同口徑輸入才計算 YoY／gross margin。
- 供應流與事件影響混淆 → 供應邊與 inference 路徑分開；原圖的雙向宣告不畫成雙向供應。
- 圖形資訊過密 → 一跳公司圖、類型／候選切換、可讀清單；先以現有圖與擴充測試資料驗證。
- 快取延遲 → 第一版採短時間 HTTP cache，來源狀態不 cache；公開頁面不得靠 rebuild 才更新資訊。

## Migration Plan

先新增獨立應用資料庫，執行 Alembic 與地圖匯入；不搬移舊專案資料。正式部署前備份 app database，還原驗證使用獨立資料庫。回滾停止本專案 Compose 或退回前一 image，保留 volumes 與 Markdown，無須刪除既有地圖。
