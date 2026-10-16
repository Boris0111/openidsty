# 新研究讀取 API

Legacy `/api/*` 與新版 `/api/v2/*` 並存。新版使用獨立 reader pool、repeatable-read／read-only transaction；每次先選一個 published release，再將所有 SQL 固定在該版。沒有研究 head 時回 503，不回傳看似成功的空地圖。草稿及 ready／preparing release 不可透過 query parameter 取得。

| GET 路徑 | 行為 |
|---|---|
| `/api/v2/manifest` | active release、schema、published_at、generation；no-store |
| `/api/v2/catalog` | 應用／環節／角色／題材／產品／術語／研究分類，可分頁；分類邊最多 400，超限明示 links_truncated |
| `/api/v2/{companies,products,themes,concepts,research,applications,roles,segments}` | 目錄；limit 預設 50、最大 100，回 items／next_cursor／has_more；不依賴搜尋才找到物件 |
| 上列清單加 `/{entity_id}` | 中文名、全文、研究條件、主張與來源、相關分類；沒有動態財務、來源維護設定、raw payload 或技術待核對佇列 |
| `/api/v2/resolve?kind=company&key=3324.TW` | 穩定 ID／舊 ticker／PRIVATE／舊環節與題材 ID；未知 404，多候選 409，禁止按名稱相近自動合併 |
| `/api/v2/documents/{id}/revisions/{revision_id}` | 只讀被已發布研究引用的固定版本；回原 URL、文件性質、定位與必要摘錄，來源失效也保留已發布內容 |

除 manifest 外皆接受 `release_id=<UUID>`；省略只在請求開始時取 active release。每個成功回應為 `{release_id,schema_version,data}`，讀者頁應保存這個 release_id 後再請求其他物件，避免混版。

清單可以 `market=TW`、`role=role-...` 或 `category=...` 篩選。公司市場依 listing，未上市公司不捏造市場；role 同時支援新 offering 與既有 segment 基本索引，category 經分類子樹查詢。Cursor 綁定 release／collection／篩選；條件改變回 409，格式錯誤或 limit 超額回 422。SQL 使用索引、LIMIT 與參數綁定，不將完整名單載到 Python 後再篩選。

固定文件的 revision_id 使用不可變 hash；舊 manifest 的 version key 在同一 published release 內只有一個對應時亦可解析，回應帶正式 revision_id。`latest` 不解析；不能用新版本替代失效的舊引用。未被引用的 manifest 版本與未發布文件不提供讀者存取。

詳情的主張／證據與相關分類各有回應上限，超過時 `truncated=true` 明示；一般研究仍保留完整 Markdown。完整圖形遍歷、搜尋、財務及收藏更新依各自後續契約實作，沒有用空成功回應冒充功能。快取與 request coalescing 於對應 task 驗證；目前回應保守使用 no-store。

錯誤固定 `{code,message,request_id,retryable}`，中文 message 不揭露 SQL、連線或內部例外。歧義另回 candidates。`X-Request-ID` 與錯誤中的 request_id 一致；DB 不可用回 503／retryable=true／Retry-After，與正常無研究資料的情形分開。新錯誤契約不改舊成功 payload。

實際 PostgreSQL 契約命令：`python scripts/research_lab.py pg-check`。測試包含新舊 API 並存、分頁與篩選、錯誤格式、歧義、未發布拒絕及固定引用。此文件僅描述已實作介面；owner 管理 API 尚未開放。

## 圖形與影響推導

搜尋使用 `/api/v2/search`，詳細字詞邊界、候選及 SQL 查核見 [research-search](research-search.md)。

`GET /api/v2/graphs?root=company-...&scope=company` 回 typed nodes／edges；scope 為 application／segment／product／company／theme 的閱讀脈絡，省略依 root 決定，role／concept 走 product 脈絡。分類、能力、具名供應、合作、競爭、環節供應與需求回饋分開，保留方向、機制、條件、信心、來源或 claim 引用。候選企業關係預設排除。Offering 只畫 capability，不因產品相容而轉為 named-supply。

depth 預設 1、最大 3；max_nodes 預設 200、最大 500；max_edges 預設 400、最大 1000。每一層及 induced links 皆在 SQL LIMIT 下查詢，BFS 記錄已訪問節點，真實回路不刪除且能終止。達數量或深度界線回 `truncated`／`truncation_reasons`，另給 continue_from 與文字目錄入口，不把結果假裝成全圖。

`GET /api/v2/impact?segment_id=segment-thermal&mode=all` 提供 linear／theme／sibling／all。三者皆保留可閱讀理由及完整 steps，每步標 inference；共同下游的 via 不是具名客戶交易。depth 計推導步驟，題材或 sibling 一步可透過 via 表達實際兩條結構連結。預設 depth=1 就涵蓋液冷經 ODM 找到 PCB 的手足路徑。經不同機制抵達同環節時保留各自理由，但節點只展開一次，避免循環擴張。

Impact 的節點／路徑限制與 graph 相同。來源拓樸最多讀 500 環節及 500 題材，各路徑最多列 100 公司，超過均明示截斷並提供公司清單連結；可繼續分頁閱讀。這些是研究結構路徑，不代表經濟因果或投資受惠已被證實。
