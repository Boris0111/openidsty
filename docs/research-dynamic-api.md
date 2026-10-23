# 事件、觀察與公司比較 API

所有入口使用 `/api/v2`、reader role 及 published release 檢查，回 `{release_id,schema_version,data}`。事件與觀察的 `data.as_of` 是這次讀取時間，不是發布日或研究日期；未指定 release 時為 `no-store`；固定研究 release 時採 ETag 與最多 30 秒快取，304 保留原 `as_of`，詳見 [版本與快取](research-reading-cache.md)。指定研究 release 只固定公司身分與研究內容，不會將事件凍結於當時，也不會在讀取時擷取外部網站。

公司財報（財務觀測、修訂、財務比較與官方補錄）已於 2026-10-23 由 change `remove-company-financials` 移除；`/companies/{company_id}/financials` 不再存在。題材所需的公司營收只作為題材代理指標，見 [題材指標](theme-indicators.md)。

## 公司比較

`GET /compare?company_ids=company-auras,company-vertiv&release_id=...` 接受 2–4 家不同公司；選太少、太多或重複時回 422，任一公司不在指定 release 時回 404。回應的 `data.companies` 依序列出每家公司的摘要、供應角色、產品（含角色名稱）、商業模式、風險、主張與已知缺口；超過顯示範圍時以 `truncated` 明示。

比較只並列研究內容，不含任何財務數值、排名或口徑選擇。某公司缺少商業模式或風險段落時回 null，由介面明示「尚未完成深研」，不以其他公司內容代替。比較內容固定於研究 release，指定 release 時與其他研究內容一樣長期快取，新 release 使用不同快取 key；舊連結帶的 `basis` 參數會被忽略。

## 事件與獨立觀察

`GET /events` 提供 official／report；`GET /observations` 只提供 rumor。可依 `entity_id`、`source_id`、`source_nature`、`relevance`（direct／background／mention）、`period_from`／`period_to`、`include_unknown`、`limit`／`cursor` 與 `release_id` 篩選。向 events 要求 rumor 或向 observations 要求 official／report 回 422，避免默默混入。

只讀取連到該 published release 物件的 published 事件，不讓 private research 身分透過事件浮現。依真正 published_at／reported_at 排序，沒有日期者排在後面並回 null／`date_unknown=true`；不以 fetched_at 補成發布日。`include_unknown` 預設 true，即使有日期篩選仍保留明示未知項；若只要期間內確切事件，指定 false。來源名稱優先取指定 release 的已保存名稱。回必要摘要與外部 URL，不回 raw、抓取診斷或管理狀態。月營收更新仍會產生營收事件，與其他官方發布一樣出現在 events。

每事件最多 100 個相關物件；截斷明示。來源性質和 direct／mention／background 不互相替代：官方發布中的公司提及仍是 mention；匿名供應消息即使指向公司，仍只在觀察入口，不會成為正式供應圖。

既有事件可用 writer CLI `python -m app.source_links` 重新對應穩定 ID；每批最多 500，單次最多 100000，超過回 partial／last_id，以 `--after <last_id>` 續跑。重跑不新增事件、不改研究、不抓網站；新版 initializer 會執行這個索引維護，首次尚無研究 head 時略過。若發布後增加 legacy mapping，重跑此命令即可將既有事件對應到新版身分。未知／歧義公司不按名稱猜測。

## 驗證及界線

`python scripts/research_lab.py pg-check --suite research-dynamic` 使用真實 reader role 測公司比較（2–4 家、缺口、不含財務）、觀察分流、日期與分頁及未發布拒絕。既有事件索引另由 `source-updates` suite 驗證。
