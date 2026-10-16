# Design

## Context

動機與功能邊界見 [proposal](proposal.md)。本設計供 Boris 查核；建立 artifacts 不等於同意實作，所有 implementation tasks 保持未完成。

本次重新檢查的基準為 `026a484`：17 個環節、7 個題材、95 家不同公司、100 筆環節角色。公司頁實際僅呈現角色與事件；財報已有來源 connector，但舊表只保存 Float 型別的營收、年增、毛利率與 EPS。收藏為同 origin 的 localStorage，最多 20 個題材。Next proxy 目前只轉送 GET 且一律 no-store，正式 runtime 的研究來自建置時檔案，尚無管理登入或發布交易。

已確認的產品取捨為：研究加基本財務、AI／半導體全鏈、全鏈分類加核心深研、Boris 與既有 agent 維護、其他人唯讀、裝置收藏加備份、表單與檔案雙編輯、台美財務優先、同 repo 升級、新舊並存。本機加私人網路為第一版部署方式。

參考網站的用途限於服務設計：[Supply Chain Atlas](https://supply-chain-map.pages.dev/) 顯示公司關係、趨勢與術語圖解；[AI 產業地圖公司頁](https://aistockmap.com/c/2330/) 與[研究入口](https://aistockmap.com/influencer/) 將公司連到題材、產品定位與有頁碼的研究。2026-10-16 可讀公開／索引頁，未完成其登入功能或完整互動驗收；數量是網站自述，不能作為本專案事實資料或驗收基準。

## Goals / Non-Goals

**Goals:** 單一主機可維護的模組化系統；研究可追溯、可重建、可回復；完整供應角色可探索，核心公司有實質研究；正常讀取不等待外部來源；讀者介面只揭露與研究判斷相關的內容。

**Non-Goals:** 不建立多維護者協作平台、高可用叢集、公開網際網路服務、讀者帳號、模型 API 或交易工作台。資料庫故障可恢復，但不承諾故障期間全站離線可用。

## Decisions

### 1. 系統架構、組件與責任

沿用 Next.js／React、Cytoscape.js、FastAPI、PostgreSQL 16、Prefect，採同 repo 的模組化單體。API 與背景 worker 為可分別重啟的程序，共用資料庫與型別定義；不增 Redis、Neo4j、訊息中介或微服務。此規模先用有索引的關聯表及有界遍歷，量測後才調整基礎設施。

```text
Readers (private network) --> Read-only gateway --> Next.js reader UI
                                                        |
Owner (loopback) ----------> Next.js admin UI -----------+
                                                        v
                                                FastAPI
                                              /         \
                                     query modules    admin commands
                                          |                |
                                          v                v
                                     PostgreSQL <---- job records
                                          ^                |
                                          |                v
Official sources --> Prefect worker / adapters      publish worker
                                                           |
Agent / files --> draft import --> validation --> managed Git + assets
```

| 組件 | 責任與界線 |
|---|---|
| Reader UI | 應用／角色／產品／公司導覽、研究、比較、術語與收藏；Cytoscape 畫圖，文字清單提供同等入口 |
| Admin UI | 單一維護者登入；表單、Markdown、diff、預覽、驗證、發布、來源健康及稽核；不提供拖拉圖形編輯 |
| FastAPI query modules | 已發布研究、有界圖查詢、搜尋、財務與事件；使用只讀 DB role，回應不讀外網 |
| FastAPI admin commands | 身分、草稿及操作驗證；把發布／還原寫為作業，不在 HTTP 請求內長時間執行 |
| Prefect／worker | 延用單一 process worker；排程擷取與發布作業以 DB 鎖／狀態防重疊，作業能重試 |
| PostgreSQL | 研究讀取投影、事件、財務修訂、草稿、發布紀錄與管理 session；研究投影可由內容 commit 重建 |
| Managed Git／assets | 容器內獨立 clone 與 persistent volume，保存同專案的研究 commit、版本 refs 與內容定址資產；不掛載開發 repo 的 `.git` 或 Docker socket |

Reader gateway 只轉送明列的閱讀頁面、靜態資產、v2 GET 及無副作用的更新查詢 POST。`/admin`、`/api/admin`、legacy 診斷頁、DB 與 Prefect 不經私人網路入口暴露；管理身分驗證仍在 API 執行。第一版預設 loopback，私人網路分享須明確設定介面／allowlist；跨裝置走 HTTPS，不開公網 port forwarding。

### 2. 讀者流程與內容交付

入口為產業探索、題材、公司、術語／技術比較及此裝置收藏。全鏈先顯示應用與供應角色，再逐層展開產品及公司；不一次把全部公司和線塞入總覽。產品頁說明用途、規格界線、採用條件、瓶頸、替代限制、供應公司及引用；公司頁讀業務、產品、上下游、競爭、曝險、財務及風險。

能力關係與具名供應不同：`offers` 只代表公司提供某產品，`supplies` 必須有該客戶／產品的證據；`partners-with`、`competes-with`、`demand-feedback` 各自標示。公司同時出現於某題材不構成交易關係；傳聞為獨立觀察清單，正式圖預設不包含。

三種影響遍歷仍為線性上下游、題材橫向及共同下游手足。每種走法記錄已訪問節點並保留理由，不能為了分層排版刪掉真實回路；結構影響路徑永遠標為推論。分類父子樹另外驗證無環。

首批深研清單固定取自保存點以下 26 家；原分組是研究排程，不代表其中每個產品角色已查核正確。重新分類要有產品邊界依據，不能把滑軌等機構件誤稱電氣互連。

| 領域 | 公司識別（legacy） |
|---|---|
| 散熱 | `3017.TW`、`3324.TW`、`2421.TW`、`VRT`、`PRIVATE:boyd` |
| 電力 | `2308.TW`、`2301.TW`、`6282.TW`、`MPWR`、`VICR` |
| 互連 | `3533.TW`、`3665.TW`、`3023.TW`、`APH`、`2059.TW` |
| 網通 | `AVGO`、`MRVL`、`CRDO`、`ALAB`、`2345.TW`、`3081.TWO`、`4979.TWO` |
| 先進封裝 | `2330.TW`、`3711.TW`、`6239.TW`、`AMKR` |

全部 17 環節、7 題材及 95 家公司都保留。五領域以外 69 家先提供已知角色與來源，明示尚未深研部分。26 家逐一檢閱產品、業務、客戶／供應、競爭、風險與財務可取性；有依據的「未公開」可以完成查核，尚未研究的空模板不能算完成。未上市公司不要求取得不存在的公開財報。

顯示順序以研究問題為準：中文標題、產品交付與商業意義、關係與證據，再到數據／追蹤。正式規範或草案的差異只有在影響論述時解釋；來源維護清單、內部 ID、JSON、parser 版本與通用「進階資訊」不進一般閱讀。桌機／手機走查與 Boris 對閱讀順序的檢閱都是驗收，不用自動測試代替易讀性判斷。

### 3. Markdown 維護、雙編輯與發布資料流程

研究結論、條件與解釋使用 Markdown；可查詢的產品、公司、關係及引用放 YAML／frontmatter。既有 `industry-map/README.md` 延伸為唯一 Schema 規範，不另造相互競爭的欄位文件。新增 `industry-map/companies/`、`products/`、`applications/`、`concepts/` 與結構化關係資料；保留既有 segment/theme 檔及雙向上下游宣告。`data/company-research.yaml` 遷移為同一公司 registry 的輸入相容層，不永久維護第二份公司真實來源。

網站不在每次讀取時掃 Markdown。發布時驗證整份內容，編譯成 PostgreSQL 的已發布投影；事件、財報與擷取紀錄直接存在 DB。這保留 Git review 與 agent 編輯能力，也能做索引查詢與歷史修訂。

1. 表單保存草稿，或維護者透過既有 agent 修改匯出的研究檔案，再以 CLI 匯入草稿；兩者都帶 `base_release_id` 及草稿修訂號。
2. 草稿存在 DB；每次修改留下草稿修訂。CLI 的 export/import/validate/publish 使用相同管理契約，認證不放命令列、日誌或匯出檔；不提供從網站自動呼叫 agent 的承諾。
3. diff 比對基準發布版本，預覽使用相同 renderer 與 Schema；驗證必要欄位、引用、分類無環、既有上下游一致、關係證據、資產與允許路徑。
4. 發布請求建立持久 job，回 `202`，再提交到 Prefect 的 research-publication deployment；每分鐘的 reconciliation 補送仍在 queued 的 job，送出失敗不遺失 DB 作業。更新草稿檢查 `If-Match`，發布檢查基準 release；過期回 `409`，保留內容並要求整合，不自動覆寫。
5. Worker 在容器內 managed clone 的獨立 worktree 產生候選 Git commit，只允許研究路徑；以 `refs/research/releases/<release_id>` 保護該 commit。不能改應用程式、讀取祕密或操作開發中的 index。
6. 建立候選 release 的完整投影與內容定址資產，標為 ready；候選資料只有 owner preview 能查，讀者 API 必須驗證 release 已發布，不因猜中 release ID 而洩露草稿。
7. 使用 PostgreSQL transaction-level advisory lock 序列化啟用，重新檢查 base release、schema 與全部產物；同一交易切換 `release_head`、發布狀態與稽核。Git 及資產事先準備，沒有宣稱跨 Git／檔案／DB 的分散式原子交易。[鎖定語意](https://www.postgresql.org/docs/16/explicit-locking.html)
8. 發布成功後，持久同步作業讀取當前 head 再更新 managed clone 的 `research/published` branch，避免較舊 job 晚到把分支倒退。分支只是版本索引，正式讀取以 `release_head` 所指的 Git commit 為準；同步中斷可重做，舊 release 的 refs 不刪除。
9. GitHub 同步為維護者的備份／整合動作，預設不在網站存放可 push 程式碼的憑證，也不要求 GitHub 在線才能本機發布。備份需包含 managed clone 的發布 refs，不能只備份開發 worktree。
10. 還原選擇曾發布且 schema 相容的完整 release，走同樣授權、冪等及啟用交易；財務與事件不回退。重啟依 job 狀態與內容 hash 確認已完成步驟，不重複建立版本。

作業狀態為 queued → preparing → ready → published，失敗記 failed／可重試階段。提交、投影或啟用失敗時讀者仍看舊版；相同 idempotency key 加相同 payload 回原 job，key 相同但內容不同回 `409`。使用正規化內容 hash 去重，操作時間／來源健康不改變研究或收藏更新標記。

### 4. 事件、財務與來源資料流程

Prefect 每小時檢查到期來源，公告預設 1 小時、財務／月營收 24 小時；維護者可單次觸發，但不可繞過提供者限流。原始回應先做格式與大小驗證，再解析／主體對應／去重，最後以單一來源交易寫入有效觀測及修訂。讀取 API 不同步抓外部網站。HTTP 逾時上限 20 秒，暫時網路錯誤／5xx 最多重試 3 次（1／4／16 秒加 jitter），HTTP 與 Prefect 共用此重試預算，不能乘上多層重試；429 遵守 Retry-After 並延後來源，403 或 Schema 變更停止當輪重試，保留其他來源成果。

| 來源 | 已確認能力與首版處理 |
|---|---|
| TWSE／TPEx 月營收、損益與資產負債摘要 | 2026-10-16 已檢查兩站 OpenAPI Schema；可取得營收、損益、EPS 與負債總額等。查到的一般業摘要未含現金餘額／現金流量表，不能把全部欄位寫成已可自動取得 |
| SEC submissions／companyfacts | 無 API key，提供公司申報與標準 taxonomy 的公司整體 XBRL；不保證自訂 tag、產品分部或客戶收入。使用具聯絡資訊 User-Agent，本專案先限制總速率 2 req/s，低於官方目前 10 req/s 指引 |
| 官方財報／IR 文件 | 針對摘要缺少的 CFO、capex、現金或歷史，以維護者核對的檔案／表格匯入；必填來源與頁碼／標籤，不把一般 PDF 自動猜表承諾為全市場 parser |
| 日韓等其他市場與未上市公司 | 可研究產品及角色；財務先附官方來源人工補錄，未取得即留缺口 |
| 官方事件、具名媒體及傳聞 | 保存報導事實與來源，確定性及正式供應關係須經研究核對；不同提供者不僅靠相似標題自動合併 |

來源檢查依據：[TWSE Schema](https://openapi.twse.com.tw/v1/swagger.json)、[TPEx Schema](https://www.tpex.org.tw/openapi/swagger.json)、[SEC API 範圍](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)、[SEC 使用指引](https://www.sec.gov/about/developer-resources)。這些確認的是資料與文件能力，尚不是新版 adapter 已成功交付的證明。

財務以原幣呈現，保留原始期間及申報編號；顯示最多最近 8 季、3 年、台灣 36 個月，來源未提供的歷史標示缺口。預設合併報表；每家公司設定主要申報來源，其他來源保留，不以零散 tag 拼接報表。淨利主畫面採歸屬母公司／股東口徑，只有總淨利時另標範圍，不混作同一指標。

指標定義：營收、同口徑營收年增、毛利率、營業利益、淨利、基本 EPS、稀釋 EPS、CFO、購置不動產廠房設備的現金支出（capex，正值）、現金及約當現金、負債總額；基本／稀釋 EPS 分開，不把負債總額叫作有息負債。金額與比率均保留 Decimal，API 傳精確十進位字串。

只對同公司、幣別、會計範圍及相容申報期間衍生：營收 YoY 用同財季，毛利率用同期間毛利／營收。CFO／capex／可加總損益的單季可由同年度相容累計相減，保留輸入觀測與公式；EPS、比率及期末餘額不可相減。基本與稀釋 EPS、ADR 與普通股口徑不互換，不換匯估計缺值。來源重編追加 revision，先前有效值可追溯；抓取時間變化不新增 revision。

### 5. 資料庫架構

新表採 additive migration 建於 `research` schema；原有 `public` 表與主鍵保留，legacy API 先繼續讀原契約。身份／內容與動態觀測分開，不能只靠散文或無外鍵的 JSON 關係。第一版研究投影採每 release 完整 snapshot，省去增量發布一致性的複雜度；不可變內容與小規模歷史的儲存成本可接受，量測後才壓縮。

| 表群 | 主鍵／關聯與保存內容 |
|---|---|
| `entities` | 穩定英文 kebab-case `entity_id`、kind；所有 ID 帶 kind 前綴，如 `company-tsmc`、`theme-hbm4`、`product-hbm4`，避免跨類型同名碰撞，改名不改 ID；公司 `company_id` 即該 entity ID |
| `listings`、`source_identifiers` | release-scoped 公司 FK、市場／交易所、ticker、有效日期、CIK 等；舊 ticker／PRIVATE mapping 可解析，歧義不自動合併；擷取使用 active release 的映射 |
| `research_releases`、`release_head` | release UUID、Git commit、schema version、內容 hash、狀態與發布日；singleton head FK 指向正式完整版本 |
| `entity_snapshots`、`entity_aliases` | `(release_id, entity_id)`；中文名、摘要、Markdown、型別驗證 JSONB、semantic hash；alias 可對應多候選 |
| `taxonomy_links`、`company_offerings` | release-scoped 父子／應用及公司—產品—供應角色；公司能力不等於交易 |
| `relations` | `(release_id, relation_id)`；兩端 FK、型別、產品／應用 context、條件、有效期間與 claim FK；對稱關係去重，供應及需求回饋保持方向 |
| `research_claims`、`claim_evidence` | 主張、三種證據程度、條件、正反證與文件 revision／locator；不把行政 review 狀態當內容確定性 |
| `documents`、`document_revisions`、`assets` | 文件身分、版本／hash／URL／日期、合法摘錄與定位；資產以內容 hash 定址；沿用既有技術文件歷史映射 |
| `financial_metric_definitions`、`financial_observations`、`financial_derivations`、`financial_import_batches` | 定義與單位；公司、來源申報、tag、期間、basis、scope、currency、股別、`Numeric(38,10)`、revision、hash 與衍生 lineage；人工匯入保存預覽 payload hash、核對人／時間與確認結果 |
| 既有 `events`／`sources` 加 `event_entity_links`、`source_capabilities` | 延用事件去重及來源健康；新增穩定 entity 關聯、official/report/rumor 性質與版本化來源能力，不另複製所有事件 |
| `editor_drafts`、`draft_revisions`、`publish_jobs`、`audit_log` | 草稿基準／修訂、冪等鍵／payload hash、作業狀態與可恢復階段、發布／還原理由 |
| `admin_sessions` | 僅 owner 身分與 session hash／期限；與讀者查詢 role 隔離；無 readers／watchlists 表 |

Snapshot、關係兩端、claim 與 evidence 的 FK 都包含 release，禁止跨版引用。研究顯示的 listing、來源名稱與文件標題同樣取自該 release 或不可變 document revision，不能 join 會隨健康檢查改變的 metadata 後仍宣稱 immutable。財務 raw fact 以來源、文件申報及 tag/context 去重；標準化觀測群組另以公司、主要來源族、canonical metric、原始期間、basis、scope、unit/currency／股別識別，群組鍵不含申報編號。新申報的同組有效值改變才追加 revision；值相同但文件更新只追加來源關聯，不觸發未讀，預設依真正申報時間選最新有效資料。衍生值另存公式版本與輸入 ID，不與官方原值混淆。

主要索引為 `(release_id, kind)`、正規化 alias、關係兩端及 kind、公司／metric／period_end／revision、事件 entity／published_at／id、job idempotency key。最新值與 coverage 聚合在 SQL 執行，不載入全表到 Python。長名稱以 pg_trgm 輔助，[官方功能](https://www.postgresql.org/docs/16/pgtrgm.html) 只支持相似／子字串索引，不代替中文分詞；短中文名稱走確切 alias／前綴，英文提及遵守 token 邊界。

### 6. API 設計

舊 `/api/*` 保留本機相容。新讀者使用 `/api/v2`，維護使用 `/api/admin`；Next proxy 明列 namespace、method 及 path，不把任何 `/api` 一律轉送。研究頁先平行取得必要 profile／局部圖，共用同 key 的請求；財務歷史、事件與版本差異按頁面任務載入。

| Method／路徑 | 最小契約 |
|---|---|
| GET `/api/v2/manifest` | active release、schema、發布時間；無草稿資訊 |
| GET `/api/v2/catalog` | application／segment／theme／product 分類；接受 `release_id` |
| GET `/api/v2/search?q=...` | 中文／英文／ticker／產品／術語，回 kind、ID、中文名、角色及候選；q 最長 100 字 |
| GET `/api/v2/resolve?kind=company&key=...` | ticker／舊 ID 到穩定 ID；未知 404、歧義 409 及候選 |
| GET `/api/v2/{companies,products,themes,concepts,research}` | 可分頁、按市場／角色／分類篩選的目錄，不以搜尋取代完整可到達清單 |
| GET `/api/v2/{companies,products,themes,concepts,research}/{id}` | 固定 release 的研究、條件、引用與可到達關聯；不混入動態財務回應快取 |
| GET `/api/v2/documents/{id}/revisions/{revision_id}` | 只讀已發布主張實際引用的版本、locator 與合法摘錄，不回監測歷史或待核對佇列；legacy 引用頁解析至此資料 |
| GET `/api/v2/graphs?root=...&scope=...` | release、typed nodes／edges；scope 為 application／segment／product／company／theme，depth 預設 1、上限 3；預設 200 nodes／400 edges、上限 500／1000，超限回 truncated 與文字清單／繼續探索入口 |
| GET `/api/v2/impact?segment_id=...&mode=all` | linear／theme／sibling／all 的有界路徑與推論理由，保留三種遍歷 |
| GET `/api/v2/companies/{id}/financials` | metric、期間／basis／幣別與來源篩選；數值字串、source、原始期間、revision、derived／lineage 與缺口 |
| GET `/api/v2/events`、GET `/api/v2/observations` | entity／期間／來源性質篩選；正式事件與傳聞觀察分開 |
| GET `/api/v2/compare?company_ids=...` | 2–4 公司；profile 比較及各財務指標可比性原因，不捏造共同口徑 |
| POST `/api/v2/updates/query` | 至多 100 個 `{kind,id,seen}`，回研究／數值／事件更新摘要；無副作用、不保存個人清單，request body 不記錄於 access log |
| GET／POST／DELETE `/api/admin/session` | 同 origin 的登入狀態／CSRF challenge、owner 登入／登出；session cookie，無公開註冊 |
| POST／GET／PATCH `/api/admin/drafts`、`/drafts/{id}` | 建立／讀取／更新草稿，PATCH 須 If-Match；另有 `diff`、`preview`、`validate`、`import`／`export` 子資源 |
| POST `/api/admin/drafts/{id}/publish` | base release 加 Idempotency-Key，回 job ID 與 202；驗證失敗 422、基準衝突 409 |
| POST `/api/admin/releases/{id}/restore`、GET `/api/admin/jobs/{id}` | 發布版本還原／作業結果；還原需理由及冪等鍵 |
| POST `/api/admin/financial-imports`、POST `/financial-imports/{id}/confirm` | 正規化 JSON／CSV 先驗證並預覽；owner 核對官方來源、定位、期間、幣別與口徑後，帶 payload hash／冪等鍵確認入庫；缺少依據拒絕，不直接猜 PDF 數字 |
| GET `/api/admin/coverage`、`/sources`、`/audit`；POST `/sources/{id}/refresh` | 維護矩陣、健康、稽核及有界重試；限 owner |

清單採 cursor，預設 50、上限 100；財務另限制可查窗口／筆數。研究回應含 `release_id`、`schema_version`、`data`；動態回應含 `as_of`、真實資料期間與必要 freshness。錯誤統一 `code`、中文 `message`、`request_id`、`retryable`，未知 404、衝突 409、格式 422、限流 429、DB 不可用 503。管理資料不得從指定 draft／ready release 的讀取參數繞過授權。

時間以 UTC 儲存，UI 依台北顯示；只有日期的資料保留精度，不製造午夜或假發布時間。金額／比率回十進位字串與原單位，由 renderer 縮放成易讀金額；null 與有效零分開。

### 7. 快取策略與收藏資料

| 資料 | 策略 |
|---|---|
| manifest／任何未指定 release_id 的研究查詢 | no-store；頁面進入、導覽、手動更新及可見時每 60 秒檢查 manifest |
| 指定已發布 release 的 catalog／profile／graph／研究搜尋 | ETag 加 24h 快取；key 含 release、規範化參數及頁碼，發布後新 key，不做跨版本共用 |
| 固定 hash 的合法研究資產 | 僅發布後對讀者開放，長快取 immutable；同內容網址不覆寫，候選資產不直接掛在公開 static 目錄 |
| 動態財務／事件／含財務的公司比較 | ETag 加最多 30 秒快取，保留 as_of／實際期間；比較 key 含研究 release，ETag 含有效觀測 revision；歷史原始 revision 可長快取，預設 latest 不可 immutable |
| 更新查詢、admin、session、草稿預覽 | no-store；失敗回應不進成功快取 |
| 瀏覽器共用請求 | 沿用 request key、in-flight 合併、切換 generation guard 與完成項 LRU，上限 100；伺服器初版不加共享 cache service |

頁面 pin 一個 release，讀者接受新版後一起換頁面 context；manifest 更新不把新版邊線塞到舊公司頁。若引用帶明確 revision 失效，顯示該引用不可用，不偷偷換成最新版。歷史比較按需載入。

收藏 key 為 `industryflow.research-watchlist.v2`，最多 100 個 `{kind,id,seen}`。舊 `industryflow.theme-watchlist.v1` 只在同 origin 讀得到，遷移成功保存並驗證後仍保留舊 key 作備份；研究／指標的已讀 marker 可映射即保留，不可映射標為需要重新確認，不把全部更新自動標已讀。v1 candidate token 不沿用為維護佇列通知，新版只追蹤讀者可見的新事件。

匯出含 schema_version、匯出時間、目標與 seen；匯入上限 1 MiB、100 目標，先預覽後合併，既有目標以本機 seen 為準，無效／封存項逐一列出。超額或結構不安全拒絕整次覆寫；部分已存在但來源不可解析的目標可保留供移除／匯出。不同 host／port／瀏覽器透過備份交換，沒有自動同步；收藏不包含研究全文。

### 8. 安全性考量

- 單一 owner，安裝時本機設定密碼，Argon2id 保存密碼 hash；沒有註冊、重設密碼郵件或 reader account。遺失密碼由本機 CLI 重設並撤銷 session。
- Session 使用 256-bit 隨機 opaque token，DB 只留 hash；HttpOnly、SameSite=Strict，HTTPS 下 Secure cookie，伺服器閒置 30 分鐘／最長 8 小時到期；明列 loopback 開發 HTTP 例外，該 profile 不得綁私人網路。所有管理寫入驗證 Origin、CSRF token 與 owner；SameSite 不是 CSRF 的替代。[Session 依據](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- 讀者查詢 role 不能讀 session、草稿、稽核或寫資料；管理／worker 及 migration 使用不同權限。資料庫、Prefect、API 內部 port 不提供私人網路直連；gateway 拒絕 admin 及 legacy diagnostics。Host／Origin 採明列 allowlist，拒絕不相符的主機名稱及來源，降低 loopback 的 DNS rebinding 風險。
- 登入每 IP 每分鐘 5 次，超限暫停 15 分鐘；查詢設每 IP 每分鐘 120 次且回 429。只信任明列 proxy 的來源資訊，不能靠任意 X-Forwarded-For 繞過。
- 外部抓取只接受註冊來源、HTTPS 與固定 adapter；host allowlist、每次 DNS／連線及 redirect 驗證，封鎖 localhost、私有／link-local IP 與雲端 metadata。禁用自動跟隨 redirect，允許最多 3 次重新驗證；無任意網址代理。[SSRF 依據](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- Markdown 不執行原始 HTML／script；連結、圖片與 SVG 經 allowlist／消毒，圖解只使用管理資產，不允許 SVG script、外部資源、任意 iframe。匯入防路徑穿越、symlink 逃逸與超大解壓縮；研究草稿上限 5 MiB、單一研究資產 10 MiB；官方抓取 JSON／PDF另採來源上限、最高 25 MiB。
- 來源文字及 agent 輸出均是待驗證資料，不能成為可執行命令；web editor 不能改程式碼、`.env`、Git hooks 或 dependency files。
- 祕密留在各環境獨立 `.env`／受保護設定，禁止 commit、API 回應及 request body 日誌。讀者收藏備份不含登入憑證，解析 JSON 拒絕危險 key／型別；個人目標不作永久伺服器紀錄。

### 9. 故障處理與備份

| 故障 | 行為及恢復 |
|---|---|
| 外部來源 403／429／格式變更 | 保留最後有效資料與研究，局部標時間／缺口，詳細診斷留 admin；依來源退避，不刪資料或填零 |
| 發布 Git／asset／projection 失敗 | active head 不動，保留有 refs 的候選 commit 及 job；重試確認 hash 與已完成步驟 |
| 啟用完成但回應中斷 | 同 key 找到原 job 與 release；不重複發布或觸發未讀 |
| 併發編輯／發布 | revision 或 base 不符回 409；人工整合後重驗，無 last-write-wins |
| DB 不可用 | API 503；UI 保留已載入內容並顯示無法更新，owner 依 request_id 查日誌；不宣稱全站仍可離線查詢 |
| worker／主機重啟 | 恢復持久 jobs、補跑到期來源；DB 鎖隨交易結束釋放，單輪／單發布不重疊 |
| app／migration 有問題 | 切回原版 image／原服務，保留新版 volume；研究還原與資料庫還原分別操作，不以 git reset 回復資料 |

每日備份 app DB（pg_dump custom）、managed Git 的 refs／內容、合法資產與 active release manifest，保存 30 天；至少一份位於另一個儲存裝置。祕密另以受保護方式備份，不含在研究 bundle。備份需記錄成功時間與 hash，並以獨立 DB／Git／asset volume 演練還原。RPO 24 小時、RTO 2 小時為個人部署驗收目標，須測量後報告，尚非容量或可用性保證。

### 10. Git、worktree 與執行隔離

同 repo 維護，無 fork、無常設 develop。保存分支 `checkpoint/industry-reading-review-20261016` 指向 `026a484`；新版 `feat/expand-industry-research-service` worktree 位於 `C:/Users/User/openspec_pjt-research-service`。`main` 留在 `b613d53`，既有兩個 change 保留 completed／未歸檔；這次不 sync 主 specs。

後續 apply 才建立預覽執行設定：Compose project `industryflow-research`；image 明列 `industryflow-research-api:dev`、`industryflow-research-web:dev`，不能沿用原本固定的 `industryflow-api:local`／`industryflow-web:local`，並覆寫所有共用 api image 的 initialize、prefect、deploy、worker、ingestion 服務。network 與 pg／Git／asset volumes 全由該 project 命名，不使用原服務的 external volume 或固定 container_name。

預留 web `3014`、API `8014`、Prefect `4204`，均先綁 loopback；2026-10-16 檢查尚未占用，啟動前仍須再檢查，若衝突停止並明確報告，不接管既有 port。新 `.env` 產生獨立密碼；不複製正式 DB URL、session secret 或 writable bind mount。現有 `industryflow` 與 `industryflow-reading` 容器不停止、不重建。

需要動態歷史時，由現有備份還原到新版獨立 DB，核對遷移及資料筆數後才啟動新版 worker；同時運行多個環境不得超過來源總限流。純 UI／Schema 驗證預設不抓外網。維護 Git commit 及程式開發 branch 與 runtime 的 research/published 內容 refs 分開處理，不能讓網站發佈去改開發 worktree。

## Risks / Trade-offs

- [研究內容的維護量大於圖形程式量] → 固定 26 家深研與全鏈角色矩陣，先完成可閱讀的垂直流程，再逐項補證據；不以 UI 完成取代研究驗收。
- [免費來源無完整市場／歷史／產品收入] → 記錄能力、手動核對匯入、缺口與時間；不以來源註冊數宣稱全自動財務覆蓋。
- [檔案與網站編輯形成雙重來源] → 正式內容只能由 release 的 Git commit 重建，草稿必須帶基準；DB 動態數據與研究來源分工清楚。
- [版本 snapshot 有儲存成本] → 初期使用完整研究投影換取一致性，保留 append-only 歷史；依真實儲存量再考慮去重，不提前增加基礎設施。
- [小群服務依賴一台主機] → 停機明示、到期補跑與還原演練；不宣稱 24/7 或公開網站容量。

## Migration Plan

1. 先由 Boris 查核本 change 的功能、八項設計及來源限制；下一輪明確 apply 才開始程式與執行設定，避免把本次 Git 保存授權當成新系統實作授權。
2. 在新版 worktree 建立隔離 Compose、環境祕密及還原 DB；記錄原服務 image／volume／port 作比對，先不啟動抓取。
3. Additive 建 `research` schema、公司身分／listing mapping、release snapshot、financial observations、drafts／sessions／jobs；保留舊表、ticker 與 API。原始金額從 raw 官方欄位轉 Decimal；只有舊 Float 時標 legacy-import／原精度未知，直到官方重新取得，不捏造精度。
4. 遷移全部 17／7／95 研究及既有判讀、指標、技術文件歷史的來源映射，驗證三種遍歷；建立產品、應用與術語資料及首批 26 家研究。舊關係逐條保留來源／狀態，不能因遷移自動升級確定性。
5. 新 UI 暫置 `/next`、新 API `/api/v2`，原路徑與 API 維持相容；完成財務、收藏、後台及發布後，在隔離環境執行自動與人工驗收。不同 preview origin 的收藏透過匯出／匯入交換，不能讀另一個 port 的 localStorage。
6. Boris 驗收後才安排正式切換，保持原 origin 並一次遷移舊收藏；舊 ticker 深連結可解析。切換前做完整備份，新版採 additive schema，回復原 image／原服務時不執行 destructive downgrade。
7. 合併 main 與部署需依另行授權的交付範圍進行；歸檔另啟動，順序為 `add-evidence-based-theme-assessments`、`improve-industry-reading-and-technical-evidence`、本 change，避免未歸檔 delta 覆寫新版需求。

## 驗收與可行性判定

| 面向 | 必須提供的證據 |
|---|---|
| 研究內容 | 17 環節／7 題材／95 公司遷移無遺失，26 深研逐項人工查核；每個供應角色有產品邊界、公司及引用或有依據的缺口 |
| 使用流程 | 桌機 1440×1000、手機 390×844：從應用到產品／公司／關係來源，再比較與收藏；返回、分享、鍵盤、快速切換及溢出檢查；由 Boris 確認閱讀優先序 |
| 圖與搜尋 | 真實回路終止、液冷可經共同下游找到 PCB、三類路徑標推論；繁簡／臺台別名與英文邊界；同名不同公司不合併 |
| 財務 | 台灣上市／上櫃、美國及未上市樣本；零與缺值、單季／累計／年度／期末、重編、股別／EPS、原幣、不支援指標與官方補錄，皆保留來源 |
| 發布與安全 | 表單與檔案同結果、stale draft 409、重試冪等、Git／投影／啟用各階段中斷、還原不回退財務；匿名／CSRF／未發布 release／SSRF／惡意資產請求被拒絕 |
| 收藏 | v1 遷移、100 上限、匯出／合併、損壞／超額／儲存拒絕；重跑與來源健康不產生假更新，舊回應標已讀不吃掉較新內容 |
| 效能與恢復 | 真實資料及獨立測試 DB 的 300 公司／3,000 關係／100,000 財務觀測兩組；暖機 60 秒、10 人連續 5 分鐘，讀取比例 profile 35%、graph 25%、search 15%、financial 15%、coverage 10%，同時跑來源更新；記錄 p95、錯誤率、CPU／RAM、SQL、快取、版本與硬體，驗證 <500ms／coverage <1s；演練 RPO／RTO |

可行性結論：既有程式、容器與官方資料結構足以支持上述模組化擴展；財務不足以支援「所有公司全部指標自動完整取得」，因此已把來源能力、官方補錄及缺口納入首版行為。新 API 效能、發布恢復及 26 家內容品質仍須依 tasks 實作與驗證；本文件未將規劃目標宣稱為測得成果。
