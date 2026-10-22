# 唯讀 API

Swagger 位於 http://localhost:8010/api/docs。API 僅提供 GET；初始化及資料更新使用 CLI。

| 路徑 | 內容 |
|---|---|
| `/api/industries` | 產業清單與各產業環節數 |
| `/api/industries/{id}/graph` | 全部環節與直接跨產業鄰居；nodes／edges |
| `/api/segments?industry=semiconductor` | 全部環節清單；可選產業，用於跨產業篩選 |
| `/api/segments/{id}` | 原地圖欄位、完整散文、題材 |
| `/api/themes`／`/api/themes/{id}` | 全文、checked、原狀態、預期里程碑、相關環節及直接事件 |
| `/api/themes/{id}/assessment` | 原判讀、證據來源、取得警示、查核後候選資訊與未知發布日缺口 |
| `/api/search?q=液冷` | 環節／題材／公司結果，含 kind、id、name、url |
| `/api/coverage`／`/api/coverage/report` | 24 項覆蓋及可下載 Markdown 近 90 日矩陣 |
| `/api/segments/{id}/impact?depth=3` | 上下游／題材／共同下游手足路徑，皆為 inference |
| `/api/companies?q=台積電` | ticker／名稱／aliases 搜尋 |
| `/api/companies/{ticker}` | 合併角色、財報、主體事件與獨立提及事件 |
| `/api/companies/{ticker}/graph?include_candidates=false` | 一跳 induced subgraph，保留鄰居間已知關係 |
| `/api/compare?tickers=NVDA,AMD` | 2–4 家不同公司；各筆財報保留原期間與幣別 |
| `/api/events?limit=30&offset=0&ticker=NVDA` | 分頁事件；kind、industry、segment、theme、date_from、date_to、include_routine、relevance 篩選 |
| `/api/events/{id}` | 事件、來源原始資料與結構推導路徑 |
| `/api/sources` | 最後嘗試／成功、錯誤、新增筆數及更新紀錄 |
| `/api/health` | DB 可連線與 map_ready |

未知識別碼回傳 404；無財報是空陣列，數字缺少是 null。金額以原幣完整元數保存，不跨幣別換算。期間 basis 包含 monthly、quarterly、ytd、annual。資料來源與 health 不 cache；其餘回應 max-age=30。ticker 使用 URL encoding，包含 `PRIVATE:` 公司。

事件預設隱藏 routine，已知發布日由新到舊、未知日置後；公司 API 保留例行資料。日期篩選為台北日界線的真正發布日（迄日含當日），不以出表／活動／取得時間補入。`relevance=direct` 預設只取有直接內容關聯的事件，background 只取背景，all 可讀取包含未分類的全部來源內容；明確 ticker 查詢保留公司主體資訊。`include_routine=true` 另加入例行資訊，仍不替財報建立 direct 分類。新增事件 kind 為 industry_news／official_stats。ticker、published_at 可為 null；published_precision 為 day／minute／unknown，reported_at／activity_at／fetched_at 分開。

事件 payload 提供 segments／themes 關聯（id、relevance、evidence），rules_version、period、basis、feeds。impact seeds 只含 direct 環節，不由公司全部角色生成。影響路徑只說明產業結構相連，不能證明影響方向或受惠。`upstream`／`downstream` 雙向宣告只生成一次供應箭頭。

coverage 可不 cache，每列有 research_available、configured_sources、successful_sources、direct_30d／direct_90d、background_90d、unknown_date、routine_90d、company_mentions_90d、samples、gaps。日期未知與預告不計直接 30／90 日；來源設定不等於事件實際覆蓋。舊財報、compare、公司 graph API 保留供既有消費端使用。

題材回應 additive 新增 assessment_summary（available、summary、confidence、reviewed），不移除舊欄位。assessment 查詢分開傳回 available、status／checked、authored assessment、evidence_sources 與 source_warnings；paths 在讀取時固定標 inference，不寫回 JSON。無 assessment 時回 available=false／assessment=null，原研究仍可讀；未知題材 404，POST 405。

舊 assessment API 的 candidates 欄位只為本機相容保留：讀者入口（gateway）不轉送舊 `/api`，舊題材頁自 task 6.5 也不再顯示；維護者改由 `/api/admin/coverage` 的 `assessment_candidates` 查閱（見 [研究覆蓋](research-coverage.md)）。候選資訊只含直接分類、非例行、已發布的內容，真正發布日的台北日期必須晚於研究 reviewed，且時間不在未來。candidates 最多列 8 筆、candidate_count 保留總數；發布日期未知另列 unknown_date_count 與最多 8 筆 undated_candidates，不以 reported／activity／fetched 代替。current_version_id 在 P3 建立版本前為 null。evidence_sources 以 canonical ID 提供 registry 名稱與目前 runtime 狀態；source_warnings 不是重新查核結果。

coverage 題材 row 新增 assessment_available／assessment_checked，與全文研究分開；環節 row 不適用者為 null。indicator_count／available_indicator_count 及 indicator_gaps 分開保存指標設定與取得狀態；未設定時明示缺口，不以新聞或來源成功補值。Markdown report 保留原 30／90 日表，另附題材判讀／指標區塊。

GET /api/themes/{id}/indicators?limit=12（1–36）：Decimal 以字串回傳；同邏輯觀測只列最新修訂，revisions 保留歷史。比較同單位／幣別／範圍／口徑，amount 為增幅、percent 為百分點。unavailable 不補零，monthly 超過 60 日／quarterly 超過 180 日過舊。HTTP 失敗仍可讀舊值。indicator_count／available_indicator_count／indicator_gaps 加到題材覆蓋列；環節列不適用。

版本列表／詳情／compare 見 [版本操作](theme-version-operations.md)，皆為 GET。inactive 題材一般 API 回 404、列表／搜尋／覆蓋不列入；DB 歷史保留。

GET /api/theme-updates?ids=...：去重後最多 20 項，不存在／inactive 逐項回報；版本與兩種內容 token 獨立。只提供公開資料，無關注或已讀 POST／PUT endpoint，細節見 [theme-watchlist](theme-watchlist.md)。
# 環節關係擴充

`GET /api/industries/{layer}/graph` 保留原 `id=source:target`、source、target、direction 與全部原拓樸；環節 edge.kind 為 supply／demand-feedback／unreviewed。公司關係圖仍使用原 kind，與此分類分開。

環節 edge 新增 source_name／target_name、relation（summary、items、dependencies、conditions、confidence、evidence、gaps、reviewed）。舊檔沒有 metadata 時回傳 unreviewed 與具體缺口，不假定是已核實供應。`GET /api/segments/{sid}` 新增相同 edge 結構的 relations 陣列，包含上游與下游，供文字閱讀使用。

`upstream`／`downstream` 仍是拓樸權威；kind 不更動上下游、題材或共同下游手足遍歷，也不移除需求回饋環。來源端 frontmatter 是關係說明唯一存放處；任何結構邊都不證明特定公司之間已發生交易。


技術文件唯讀 API：`GET /api/technical-documents?segment=<id>&theme=<id>&limit=20&offset=0` 回傳 as_of、items、total、limit、offset（limit 1–50）。摘要區分 doc_kind、已核對 versions 與 pending_count。`GET /api/technical-documents/{id}?limit=10&offset=0` 回傳 definition（各固定版本與 locators）、runtime source 及有界 history。未知文件 404，超限 422；沒有公開 POST／review 寫入入口。歷史退役定義仍可讀。API／proxy 全部 no-store，讀取不呼叫外部來源。

指標修訂：`GET /api/themes/{tid}/indicators/{iid}/revisions?limit=20&offset=0`，limit 1–100，回傳 items／total／limit／offset，跨題材指標 404。原 indicators payload 的 revisions 改為最多 20 筆，另有 revisions_total、revisions_limit；畫面提供載入更多。最新值先按 identity／revision 排名，再取最多 limit 個期別，失效最新版不回退同 identity 舊修訂。coverage 使用一致 REPEATABLE READ 唯讀快照、共同 reference 及 SQL COUNT DISTINCT／window top-3，未知日、背景、提及與例行維持原計數語意。

事件 payload 另提供 optional source_name（目前來源顯示名稱），保留原 source_id。名稱在同次 request 內批次讀取並重用；舊資料沒有名稱時 UI 明示待補；原 source_id 保留在 payload 供核對，讀者介面不顯示逐事件識別碼。
