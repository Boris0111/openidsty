# 唯讀 API

Swagger 位於 http://localhost:8010/api/docs。API 僅提供 GET；初始化及資料更新使用 CLI。

| 路徑 | 內容 |
|---|---|
| `/api/industries` | 產業清單與各產業環節數 |
| `/api/industries/{id}/graph` | 全部環節與直接跨產業鄰居；nodes／edges |
| `/api/segments?industry=semiconductor` | 全部環節清單；可選產業，用於跨產業篩選 |
| `/api/segments/{id}` | 原地圖欄位、完整散文、題材 |
| `/api/themes`／`/api/themes/{id}` | 全文、checked、原狀態、預期里程碑、相關環節及直接事件 |
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
