# 題材指標與修訂

定義在 `data/theme-indicators.yaml`，來源與自動擷取入口只在 `industry-map/sources.yaml` 宣告。定義檔只保存衡量對象／口徑，不放觀測數字。完整欄位見 [唯一 Schema](../industry-map/README.md)；既有財報 API 保留，指標以 PostgreSQL 新表另外保存。

首輪九項固定定義：AAON 液冷產品收入、台積電 2nm 晶圓營收占比為 direct；奇鋐、Micron、聯亞、台積電、Broadcom、台達與 Vertiv 的整體營收為 proxy。direct 仍僅代表具名公司的特定產品，不能升格成全市場滲透率；proxy 不能當題材專屬收入。amount 保留 USD／TWD，percent 的變化用百分點，不混為成長率。

原生日期分開：published_at 是可確認發布時間，reported_at 是出表時間，fetched_at 是取得時間；發布日未知留空。TW 月營收以既有官方出表日及完整 TWD 元數投影；SEC 單季必須有原財報起迄，不把財報年度改成曆年季度，年度／累計不當單季。

同指標、來源資料集／對象、期間與宣告的報告頻率口徑形成邏輯觀測。數值、單位／幣別及實際衡量範圍修訂會追加 revision；相同有效內容重跑不增加版本，也不以新的 fetched 時間表示數值已更新。官方更正後不再適用的範圍保存 valid=false 與理由，保留舊版本，但不把舊值冒充最新有效值。每個版本保留原始期別、URL、必要摘錄與 metadata。

## 0003 升級與初始投影

先備份，在隔離還原 DB 完成 migration 及筆數／數值核對後，再升級正式 DB。回退應用 image 並保留新增表，不做 destructive downgrade。

```powershell
./scripts/backup.ps1
./scripts/restore-check.ps1 -BackupFile ./backups/industry-YYYYMMDD-HHMMSS.dump
# 將下一行替換為 restore-check 實際輸出的隔離 DB 名稱
$env:APP_DATABASE = 'industry_restore_YYYYMMDDHHMMSS'
docker compose run --rm --no-deps ingestion alembic upgrade 0003
docker compose run --rm --no-deps ingestion python -m app.import_map
# 新公司 CIK／來源定義先由既有註冊／更新程序載入
docker compose run --rm --no-deps ingestion python -m app.ingest --reclassify --only-stale
docker compose run --rm --no-deps ingestion python -m app.financial_indicators
docker compose run --rm --no-deps ingestion python -m app.financial_indicators
Remove-Item Env:APP_DATABASE
```

代理投影不呼叫外部來源，重用既有 Financial。第二次通常 new_observations=0；這代表重跑一致，不能單憑零新增判定來源成功。只有目前題材關聯的定義參與投影，未關聯的歷史指標／觀測保留。SEC 尚未配置時，相應代理指標保持未取得，不生造零值；VRT 使用公開 CIK 1674101。手動定義與代理匯入共用更新鎖，若回 skipped_overlap，等待原輪次結束再執行。

monthly 距資料期末超過 60 日、quarterly 超過 180 日標示過舊，與 HTTP 健康分開。至少兩筆同單位／幣別／口徑的有效觀測才可連線比較；缺比較期或前期為零時不算增幅。實際零值保留，未知值不補零，不做匯率換算或插值。來源擷取與指標 API 的實測紀錄在相關任務完成後追加。

直接來源操作見 [metric-source-operations](metric-source-operations.md)；已取得與未取得期別見 [live 矩陣](theme-indicator-live-matrix.md)。
