# 題材判讀 change 驗收紀錄

Change：`add-evidence-based-theme-assessments`；2026-10-14 完整四階段驗收。此文件記錄實測，任務狀態仍以 OpenSpec CLI／tasks checkbox 為準。

## 乾淨 tracked checkout

由 Git index 匯出 `.work/final-clean-20261014/`，沒有既有 .next、.env 或未追蹤應用檔案。Python 3.12.10／Node.js 24.14.0；requirements 的鎖定直接依賴已核對，前端重新 npm ci。coverage 與 watchlist route 均由 git ls-files 確認受版本控制。

| 必要檢查 | 最終結果 |
|---|---|
| 地圖 full | 17 環節／7 題材／35 canonical 來源通過 |
| 驗證器自身 | 舊格式與新判讀合法；43 類失敗案例通過 |
| 後端離線 pytest | 131 passed；既有 Starlette TestClient deprecation warning 保留 |
| 前端 typecheck／production build | 乾淨來源通過，包含 coverage／watchlist |
| 離線 Playwright | 16 passed；獨立 3011 production server、503 後端、明確 browser interception |
| 還原 DB 獨立網站 live E2E | 7 passed；8011／3012，不使用 browser fixtures |
| Docker production build | API／web 通過，本機 8010／3010 使用新 image |
| OpenSpec | strict validate 通過，主 specs 尚未 sync／archive |
| GitHub Actions | 工作流已建立，等效本機檢查通過；未推送，不宣稱遠端 runner 已執行 |

Next.js CLI start 對 standalone 有啟動方式提示；離線 server 可正常服務，正式 Docker 使用 standalone server。fixtures 只在 pytest／browser interception，ingestion 不讀 tests fixtures。

## P0／P1：可靠性與可追溯判讀

來源診斷保留 exception cause 的 configuration、HTTP／403、timeout、解析錯誤與最後成功。SEC 真實聯絡設定缺少時不代填；原 IR 失敗不由替代入口掩蓋。重試快照見 [p0-source-retries](p0-source-retries.json)。

[12 筆真實 ODM 核對](odm-classification-audit.md) 修正夏普訂單漏失與村田 MLCC 誤命中，規則 v2。重分類 2,855 事件，identity／標題／URL／fetched checksum 及 147 財報保留；ODM 30／90 日變為 1／7。零近期直接事件、待設定與 HTTP 失敗各自列缺口。

七題材共 15 筆證據短摘錄、9 個支持／反向論點、8 條有條件傳導、21 個里程碑核對；原全文與 2026-10-07 基準保留。Micron 舊 PDF 403／轉向限制與官方搜尋摘錄核對方式見 [研究來源核對](theme-source-audit.md)，未宣稱重新讀過全文。三種遍歷、手足擴散與回路終止測試通過。

API 候選測試涵蓋台北日界、直接／非例行、preview／未來排除及未知發布日；不修改 authored 結論。題材、環節、事件入口相容；全部結構候選可展開，不截斷 API paths。

## P2：觀測、來源與商業化

0003 在 SQLite 與還原 PostgreSQL 通過，保留 2,855 事件／147 財報／95 公司／7 題材。Decimal 123.45678901 僅作隔離 migration QA，正式未載入。

正式取得 11 筆真實觀測：AAON 2025 Q4、2026 Q1、Q2 液冷產品收入，以及奇鋐／聯亞／台積電／台達各兩筆月營收投影。九項設定、各指標原期別與缺口見 [live 矩陣](theme-indicator-live-matrix.md)。AAON 回補有最多五頁／八份公告限制，不宣稱兩年完整；最新兩份每小時核對。TSMC 指標索引 403，SEC MU／AVGO／VRT 缺實際聯絡設定，不以 fixtures 補數。

測試涵蓋真實 parser 正反例、單月／單季／累計、幣別／範圍／分母、零值／未知值、追加修訂、fetched 不造修訂、百分點及不可比較原因。資料年齡 monthly 60 日／quarterly 180 日與 HTTP 健康分開；單筆不連線，至少兩筆同口徑值才呈現趨勢。商業化核對分開預期時間與證據，數值／日期不自動完成里程碑。

## P3：版本、更新 token 與此裝置關注

0004 在還原 DB 保留研究／事件／財報／觀測。七題材各一個初始版本；隔離液冷修改 v2、同內容重跑不追加、還原 v3 與原 semantic hash 相同，共九個版本。正式仍只有七個原研究基準，沒有隔離 QA 修改。

版本測試涵蓋排版、穩定 ID 次序、狀態／證據／條件／缺口／核對修改、原因缺失拒絕、非法匯入無部分寫入、inactive 404、分頁及跨題材 404。支持／反向證據 URL 可在 diff 中回溯，查核日與 recorded_at 分開。選取器 aria-label 修正後，手機鍵盤比較通過。

關注測試涵蓋首次基準、三類提示、伺服器較新但舊顯示回應標已讀、重新整理、移除再加入、未知日期、來源失敗、損壞及讀寫儲存被拒絕。公開 API 沒有個人寫入 endpoint；清單僅此裝置。操作見 [關注文件](theme-watchlist.md)。

## 更新、重啟與新安裝

還原 DB `industry_restore_20261014172701` 連續兩次 live 更新 AAON／TSMC／TWSE／TPEx，七題材版本、indicator_token、candidate_token 相同；AAON 與財務投影第二輪新增 0。失敗 TSMC 不阻止成功來源；保留 2,855 事件、147 財報、12 觀測（11 真實＋1 隔離 QA）、9 版本。

獨立 QA API／web 重啟，之後 PostgreSQL container 也重啟；API health 恢復，版本與兩類 token 保留。正式 DB 保持七個原基準及 11 真實觀測，沒有 QA indicator／研究。

空 DB `industry_assessment_empty_20261014` 從 migration 到 initialize 驗證：17 環節、7 題材／初始版本、9 指標設定／關聯、0 事件／財報／觀測。來源先註冊，指標設定及既有財報投影於 initialize 完成；不用等下一輪 hourly。未取得數據呈現 unavailable，沒有零值或假資料。

正式 Prefect hourly deployment（cron `7 * * * *`、concurrency 1）已由新 worker 實際執行，flow run `26142a8d-0ef7-4673-977b-1cb17847c201` 完成；run 95 於 15:15:57 UTC 結束，AAON success／0、TSMC HTTP 403、投影 success／0。PostgreSQL advisory lock 的重疊拒絕與釋放已實測。

備份：
- 0003 前 `industry-20261014-172615.dump`，SHA256 `A1A52D63C08CAE166E9C6D52EEAAB551735F77CEE0274603C96B06889B83EB4A`。
- 0004 前 `industry-20261014-182938.dump`，SHA256 `9138C9833A766DAD96460999F047354AFF0CCA599C5F8A9C7566457AD8727998`。

## 七題材真實走查

七頁都核對結論、成立條件、主要不確定性、下一確認點與證據連結；指標／商業化／版本／候選各自可辨識。桌機與手機截圖、鍵盤操作通過。完整結論／指標／來源限制見 [交付矩陣](theme-delivery-matrix.md)，原 30／90 日表保留於 [覆蓋報告](coverage-90d.md)。
