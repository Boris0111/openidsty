# 搜尋契約與 SQL 查核

`GET /api/v2/search?q=...` 支援公司、產品、術語及其他研究類別，q 長度 1–100；limit 預設 50、最大 100。空白查詢回 422；無符合資料回空 items。結果包含中文名、kind、穩定 ID、符合的 aliases 與供應角色，並保留 next_cursor／has_more。可用 kind 篩選，release_id 與 cursor 固定同一已發布版本。

Alias 以 NFKC、台／臺統一、大小寫與空白正規化索引；不修改正式名稱與公司 ID。中文一、二字採確切／前綴，三字以上可子字串；產品應維護讀者慣用短名，例如冷板。英文採 token 邊界，AMD 不命中 AMDOCS；上市代號亦可查。百分比及底線等輸入視為文字，不放大成 wildcard。確切 alias 優先，同 alias 的不同法律主體分列候選，不默默合併；跨市場同一 entity 只回一筆。

SQL 以 release-scoped normalized alias 搜尋、SQL 分組與 LIMIT 分頁，不載入全部公司後在 Python 比對。`0007` 建立 normalized btree pattern index 與 pg_trgm GIN；短中文不依賴 trigram。索引不是所有小資料查詢都必然選用，應以 planner 與實測判讀。

2026-10-16 使用 PostgreSQL 16.15、`dad167a` 的 119 個真實研究物件，在 test DB rollback-only transaction 中以 reader role 執行 EXPLAIN ANALYZE／BUFFERS。臺積電、台積、AMD 的 SQL execution time 分別為 0.592／0.327／0.471 ms；此小資料規模的 alias 分支選 sequential scan，snapshot join 使用主鍵。這不是 HTTP p95、併發容量或擴大資料驗收。完整 SQL／JSON plans 保存於 `.work/research-lab/rebuild-check.json`；重現命令 `python scripts/research_lab.py rebuild-check --commit dad167a94fafe9499702356fc8842d6f79b858ce`。

PostgreSQL 契約共 22 項通過，其中搜尋涵蓋台／臺、短中文、NVIDIA、ticker、AMD／AMDOCS、產品、術語、同名候選、未發布排除、wildcard 文字及分頁條件衝突。後續資料增加時再用實際 workload 決定查詢調整，不先新增搜尋服務。
