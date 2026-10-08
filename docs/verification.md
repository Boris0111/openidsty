# 整合驗收記錄

目前研究介面與資料覆蓋驗收見 [refocus-industry-explorer](refocus-verification.md) 與 [近 90 日矩陣](coverage-90d.md)。下列為前一個 change 的歷史記錄，不代表現行介面或資料筆數。

驗收日期：2026-10-08（Asia/Taipei）。Change：`add-industry-info-platform`。以下為這次實際執行的結果，後續資料與來源狀態以網站／API 當下回應為準。

## 交付與入口

公開唯讀的產業總覽、環節詳細資料、2–4 家公司比較、固定公司頁、公司關係圖、官方事件及來源健康頁已提供。公司圖支援方向、供應／策略夥伴顏色、候選切換與節點跳轉；節點大小採明示的業務關聯程度。

| 入口 | 本機網址 |
|---|---|
| 網站 | http://localhost:3010 |
| API 文件 | http://localhost:8010/api/docs |
| API health | http://localhost:8010/api/health |
| Prefect 管理介面 | http://localhost:4201 |

Docker project 為 `industryflow`。PostgreSQL 只在 Docker 內部網路可達。既有 `valuflow` 的 3000／8000／5432／6379 服務在驗收前後維持運行，未被停止或替換。

## 結構與測試

| 檢查 | 結果 |
|---|---|
| `python scripts/validate_map.py` | full 通過：17 個環節、7 個題材、12 筆研究來源 |
| `python tests/run_validator_tests.py` | 合法基準 full／skip-prose 與 22 類錯誤案例全部通過 |
| `docker compose exec -T api python -m pytest tests -q` | 20 passed；離線 fixtures 僅用於測試 |
| 前端 typecheck／production build | 通過；Windows 本機與 Linux Docker build 均完成 |
| Playwright | 3 passed：實際 canvas 選節點、公司比較與跳轉、事件及失敗來源、窄螢幕鍵盤操作 |
| 瀏覽器視覺檢查 | 桌面公司圖與 390 px 產業頁截圖已檢視；修正圖中文字與箭頭重疊 |
| Compose | production、dev override 與 public profile 設定可解析 |

已實際啟動 `compose.dev.yaml`：Uvicorn reload 與 Next.js dev server 均 ready，主要頁面及 proxy health 回應 200；3 個 Playwright 流程在此模式亦通過（19.7 秒）。驗收完成後切回 production 模式。

後端覆蓋錯誤地圖不覆蓋投影、重複匯入、含回路的三種遍歷、跨環節公司去重、一跳鄰居間邊、中文 aliases／英文邊界、財務單位與累計口徑、缺值、修正版本、來源隔離及重跑一致性。Microsoft IR 的 mailto／分享 query／外部網域不得被當成財報頁，已有回歸案例。

Starlette TestClient 有一則 httpx deprecation warning；不影響上述通過結果。Windows 跑既有驗證器測試前須設 `$env:PYTHONUTF8 = '1'`，避免子程序輸出編碼造成錯誤訊息比對失敗。API JSON 明示 UTF-8，Windows PowerShell 的來源名稱已確認可正確顯示中文。

## 正式資料與來源限制

正式 PostgreSQL 已匯入 17 個環節、7 個題材、95 家公司、5 筆研究關係（4 筆 confirmed、1 筆 candidate），並經實際官方網路擷取保存 **110 筆事件、98 筆財務紀錄**。這些動態資料來自官方來源，未從 fixtures 發布。

共註冊 28 個 connectors；驗收快照為 8 個 success、2 個 failed、18 個 configuration_required：

| 來源 | 實際結果／限制 |
|---|---|
| TWSE／TPEx 各三個資料集 | 重大訊息、月營收、累計損益表解析成功；TPEx 重大訊息此次沒有地圖內公司的新增事件 |
| 台達電 IR | 取得 3 筆具日期的法說文件事件 |
| Microsoft IR | 取得 1 筆財報新聞稿；修正導覽連結判斷後，正式重跑 success 且新增 0 筆 |
| NVIDIA IR | 正式請求收到 HTTP 403，來源頁顯示 failed |
| 台積電 IR | 初次遇連線錯誤，最新排程請求收到 HTTP 403；來源頁顯示 failed，不以離線測試代替成功 |
| SEC（9 家公司，各 submissions／companyfacts） | 18 個 connectors 待提供維護者真實聯絡資訊的 SEC_USER_AGENT；未宣稱已取得 SEC 正式資料 |

重跑已成功的資料來源，新增筆數為 0；不同來源保持各自文件識別。失敗時保留歷史資料及最後成功時間，另記最後嘗試與原因。來源狀態及錯誤對網站使用者可見。

財務缺值維持 null，零值可顯示。台灣金額由千元換成完整 TWD，第二季損益表標為半年累計。事件保存來源連結及原始資料；IR 文件連結不等同 PDF／影片已轉錄。

## 排程、持久化與維護

`app.verify_runtime` 正式執行通過，確認 PostgreSQL、Alembic `0001`、非 fixtures 資料、啟用的唯一 hourly schedule `7 * * * *`、deployment global concurrency limit 1，以及 PostgreSQL advisory lock 的重疊阻擋。

Prefect process worker 已完成實際整輪更新；驗證 run ID 為 `7c8ece4c-895e-4489-9745-c81bbb254957`，entrypoint 為 `app.flows.official_information_flow`。COMPLETED 表示全部來源均已嘗試，個別來源成功與否仍以來源頁為準。API worker 不建立額外排程。

此外，2026-10-08 05:07（台灣時間）的自動排程已實際執行並 COMPLETED，run ID 為 `01a1182f-e35e-7d3a-9fcd-3cec667b5f05`，`auto_scheduled=true`；21:07:03–21:07:19 UTC 完成。全部來源的新增筆數均為 0，8 個成功、2 個 HTTP 403、18 個待設定，確認排程可在無手動觸發下運作。

已實際執行 `docker compose down`（未加 `-v`）及 `docker compose up -d`。重啟後事件仍為 110 筆、財務仍為 98 筆，網站、API、資料庫及 Prefect health 正常。

`scripts/backup.ps1` 已建立 pg_dump custom format 備份；`scripts/restore-check.ps1` 已在隔離資料庫 `industry_restore_20261008044237` 成功還原，核對 17 個環節、95 家公司、110 筆事件及 98 筆財務。原 app database 未覆寫。備份存於本機 `backups/`，不提交 Git。

Caddy public profile 的設定已透過 `caddy validate --config /etc/caddy/Caddyfile` 通過。此次未連接正式網域或公開網站；實際 DNS／TLS 申請仍需部署者依 README 設定自己的網域。

## 內容信心與下一階段

正式官網文件及目前成功的擷取結果為 well-supported；事件影響遍歷與 candidate 關係皆明示 inference。來源恢復、尚未設定的 SEC live 擷取及更多公司關係屬 needs verification。結構驗證不證明產業內容全部正確。

這版公司圖採少量可審查的官方證據，不能視為完整商業關係網。股價、價格衍生估值、帳號及 AI 摘要不在此次交付範圍；尚未加入 Redis 或 Neo4j。
