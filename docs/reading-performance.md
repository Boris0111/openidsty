# 讀取效能基準

本 change 目標：10 位同時讀取者，暖機 60 秒、正式至少 300 秒，各 endpoint 類別至少 100 樣本；各常用 API p95 < 500ms，coverage p95 < 1000ms，非預期錯誤 0。這是本機驗收目標，尚非容量保證。

## 固定條件

| 項目 | 本次條件 |
|---|---|
| 主機 | ASUS ROG Strix G513QE、AMD Ryzen 9 5900HX、16 logical CPU、16,540,921,856 bytes RAM；Windows |
| Docker | Desktop Engine 29.2.1、Linux containers；16 CPU、8,009,220,096 bytes RAM 配額；與正式服務共用主機，背景負載是限制 |
| PostgreSQL | 16.15-trixie，獨立 container／database，還原相同 dump；沒有 worker 寫入 |
| API baseline | `sha256:e2a5c2caa050f23e5f319c75116e6ff1599518793c493260dc2a482b89f3b511`；Uvicorn 預設單一 process，SQLAlchemy 預設 QueuePool 5／overflow 10，pool_pre_ping |
| web baseline | `sha256:b1ccd14e0d1d8a1f0bc1495d1d537f862d38894a78e7def651602e99517832aa`；Next.js standalone production build |
| 路徑 | 本機負載腳本 → `127.0.0.1:3013/api` → Next.js proxy → isolated API:8000 → isolated PostgreSQL；非 browser 記憶體命中 |
| 快照 | `industry-20261015-235419.dump`；SHA256 與還原紀錄見 [驗收](industry-reading-verification.md) |
| 快取 | 直接 HTTP 每次 GET；proxy fetch no-store；baseline API 原本有 public max-age=30 headers，urllib 不保存 HTTP cache |
| 查詢分布 | 固定循環：兩產業 graph、17 segment、7 theme／assessment／indicators、全部題材 updates、coverage；10 reader 的起點錯開 |
| 新文件 API | baseline N/A；實作後另外跑 `--documents`，不更動既有 endpoint mix |

## 重跑

```powershell
.\scripts\start-reading-lab.ps1 -BackupFile .\backups\industry-20261015-235419.dump
.\.venv\Scripts\python.exe scripts/reading_load.py --origin http://127.0.0.1:3013 --output .work/reading/baseline.json
# 改善後同一環境、相同 DB 快照重跑，再單獨量測新資源
.\.venv\Scripts\python.exe scripts/reading_load.py --origin http://127.0.0.1:3013 --output .work/reading/after.json
.\.venv\Scripts\python.exe scripts/reading_load.py --origin http://127.0.0.1:3013 --documents --output .work/reading/documents.json
```

腳本只有 GET，先由真實 API 讀取現有 ID，保存逐 URL 冷讀、正式各筆延遲／大小／HTTP 錯誤及每類 p50／p95／p99／throughput；樣本不足或減少併發／暖機／時間不能視為驗收。延遲包含讀完整個 JSON 回應。詳細 SQL 次數由同一 DB 快照內的診斷腳本另列，不以直接 backend timing 取代 proxy 路徑。

## 結果

2026-10-16 baseline：10 readers、60 秒暖機、正式 344.52 秒，共 4,160 筆；所有類別至少 100 筆、HTTP／JSON 解析錯誤 0。逐 URL 暖機前首讀與完整設定見 [量測摘要 JSON](reading-performance-baseline.json)；「首讀」為本輪每 URL 第一次取得，不代表清空 OS／PostgreSQL cache。初試 303.67 秒的 coverage／updates 樣本不足，只保留為本機 pilot，未取代此完整基準。完整量測期間沒有進行 build、E2E、外部 ingestion 或切換 app image；既有正式服務仍共用主機，另有輕量編修／驗證活動。

| API 類別 | 樣本 | p50 ms | p95 ms | p99 ms | 平均 bytes | 目標結果 |
|---|---:|---:|---:|---:|---:|---|
| graph | 199 | 210.41 | 390.83 | 510.61 | 4,361 | 通過 |
| segment | 1,669 | 482.63 | 822.04 | 995.87 | 27,093 | 未達 500ms |
| theme | 696 | 455.01 | 731.83 | 905.48 | 48,097 | 未達 500ms |
| assessment | 697 | 728.94 | 1,060.83 | 1,193.40 | 9,671 | 未達 500ms |
| indicators | 698 | 360.04 | 635.93 | 793.51 | 5,452 | 未達 500ms |
| theme-updates | 101 | 7,364.61 | 8,368.12 | 8,589.61 | 7,145 | 未達 500ms |
| coverage | 100 | 7,057.43 | 7,991.09 | 8,119.85 | 326,690 | 未達 1 秒 |
| technical-documents | N/A | — | — | — | — | 尚未存在 |

直接函式診斷（相同 DB 與固定 reference）顯示 coverage 執行 76 次 SQL、約 738ms；全部七題材 updates 116 次 SQL、約 837ms。此為無負載單次診斷，不能取代上表 proxy 端到端結果。實作前 coverage 全量載入 2,915 筆 Event 與全部分類；updates 重複組裝完整 assessment／indicators，再讀一次 token 集合。優先以 SQL 聚合、有界樣本與批次 token 摘要消除此成本；前端 cache 不會讓直接 HTTP benchmark 變快。

## 相同快照的改善後結果

2026-10-16：60 秒暖機、正式 300.17 秒，10 readers，共 11448 筆，所有類別至少 100 筆且錯誤 0。核心 workload 與原 baseline 相同；測量期間沒有 build、E2E、外部 ingestion 或切換 image。僅有輕量編修及紀錄整理。既有正式服務仍共用主機。逐 URL 首讀、response bytes 與設定見 [改善後摘要](reading-performance-after.json)；首讀不是清空 DB／OS cache。

| API | baseline p95 ms | 改善後 p50／p95／p99 ms | 樣本 | 目標 |
|---|---:|---|---:|---|
| graph | 390.83 | 145.66／225.08／263.37 | 544 | < 500ms，通過 |
| segment | 822.04 | 232.74／341.13／404.45 | 4640 | < 500ms，通過 |
| theme | 731.83 | 223.26／332.92／387.60 | 1908 | < 500ms，通過 |
| indicators | 635.93 | 230.18／352.23／422.79 | 1907 | < 500ms，通過 |
| assessment | 1060.83 | 316.34／441.03／503.69 | 1906 | < 500ms，通過 |
| updates | 8368.12 | 274.78／372.93／420.77 | 272 | < 500ms，通過 |
| coverage | 7991.09 | 696.46／832.55／879.34 | 271 | < 1000ms，通過 |

這是上述主機、快照與工作負載的實測結果，不是所有資料規模與部署環境的容量保證。新增文件 API 另以 10 readers、60 秒暖機及至少 300 秒測量，不與原來不存在的 endpoint 製造改善比率。

第一輪改善後仍未達標：updates p95 約 1,097ms、coverage 約 1,675ms。profile 顯示每次判讀重新解析整份來源 YAML 是共用 CPU 的主要成本；改成讀已驗證的 DB 來源投影並在 request 內共用。authoring 權威仍在 repo；API 不讀取或改寫來源 YAML。保留本機 after-initial.json 作診斷，不把未達標輪次當正式達成結果。

## 查詢及一致性

coverage SQL 從 76 次降到 20 次，updates 從 116 次降到 7 次。coverage 以 COUNT DISTINCT 與 window top-3，指標以 identity 最新修訂及 indicator 期別排名；updates 僅讀 canonical token 所需欄位，不組裝歷史。沒有新增 Redis、圖資料庫或微服務，也沒有用 API cache 遮蔽讀取成本。

固定 reference 為 2026-10-15T16:00:00+00:00。所有既有 table 內容指紋、三類 token、原覆蓋指標及樣本順序皆一致；新建 8 份文件基準、8 筆觀測與 8 筆核對，來源從 53 增至 73（新增 canonical／人工技術入口）。證據見 [一致性紀錄](reading-query-verification.json)。

EXPLAIN ANALYZE 完整結果：[改善前](reading-query-plans-before.json)、[改善後](reading-query-plans-after.json)，[摘要](reading-query-plans.json)。0006 為分類 scope／relevance／event_id 的 covering indexes，讓查詢不需掃描分類證據 JSON 頁。原始 snapshot 的指標量小，不額外添加未量測必要性的 indicator 索引。這些單次 plan 的冷暖狀態不同，不能把全部 execution-time 差異歸因索引；容量判斷使用上方完整暖機 proxy workload。

專用空 PostgreSQL 的 migration、重複匯入、REPEATABLE READ 下同時寫入的計數／樣本與去重提及測試均通過。測試資料只存在 industry_empty_reading，測後移除，不進入正式 app 快照。


新增文件 API 獨立量測：同樣 10 readers、60 秒暖機、300.09 秒正式測量；列表 2,524 筆，p50／p95／p99 為 121.05／166.69／196.49ms；詳情 20,176 筆，為 132.03／177.06／211.29ms，均無錯誤且通過 500ms。見 [文件量測摘要](reading-documents-performance.json)。文件讀取實作與 8 份基準在後續事件卡片來源名稱修正中保持相同，未以不同內容的數據替代此結果。

量測最終版本使用與 baseline 相同的 Node 24.21.0 及 Python 直接／間接依賴，基底 image layers 一致；新 PDF 解析依賴僅 pypdf 6.20.1。曾隨浮動 tag／間接依賴裝到 Node 24.22.0、Pydantic 2.14.1 等，該輪只作診斷，未當最終同環境驗收。Dockerfile 與 runtime-constraints 固定此基準，更新時須明確重驗。

最後畫面走查補正事件卡片的來源名稱，source_id 與未知類型留在進階資訊（此面板後來已全站移除，識別碼只留在 API payload）；API additive 提供 source_name。segment 的鄰接環節與題材、theme 的環節名稱改為批次讀取，避免為名稱顯示增加逐筆查詢。coverage／assessment 共用已讀來源名稱，不新增其統計查詢；原 SQL 次數仍為 20／7。所有核心 endpoint 在此修正後重新以原備份快照量測，完整結果為上表。
