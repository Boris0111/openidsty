# refocus-industry-explorer 整合驗收

> 2026-10-23 註記：公司財報已由 OpenSpec change `remove-company-financials` 移除；題材代理指標仍使用月營收與 SEC 營收。本文提及的財務資料、頁面與測試為當時紀錄，不再代表現況。

驗收日期：2026-10-08（Asia/Taipei）。資料快照基準：2026-10-08T10:28:00.111910+00:00。最新動態內容與來源健康仍以網站／API 當下回應為準。

## 交付

核心流程已改為選產業 → 理解環節 → 查看題材與近期事件 → 追溯來源。全部 17 環節與 7 題材全文、來源證據與查核基準可讀；每項都有自動來源設定與近 90 日直接分類樣本。公司採輕量模板，舊比較入口導回探索；財報／關係／比較 API 與歷史 DB 保留。

網站 http://localhost:3010；API 文件 http://localhost:8010/api/docs。完整數字與樣本見 [近 90 日矩陣](coverage-90d.md) 及 [JSON 快照](coverage-90d.json)，操作見 [前端文件](frontend.md)、[來源文件](sources.md) 與 [研究投影](industry-research.md)。本次 change 已於 2026-10-08 同步主 specs 並歸檔至 [變更紀錄](../openspec/changes/archive/2026-10-08-refocus-industry-explorer/proposal.md)。

## 驗證

| 檢查 | 結果 |
|---|---|
| 全量地圖驗證 | 17 環節、7 題材、23 筆來源宣告通過 |
| 驗證器自身測試 | 合法基準 full／skip-prose、27 類錯誤案例通過 |
| 後端完整測試 | 56 passed；涵蓋保留歷史的 migration、真實正反文章、全範圍分類、日期、跨 feed、期別、來源隔離及三種含回路遍歷 |
| TypeScript／production build | typecheck 與 Next.js Docker build 通過 |
| Playwright | 7 passed；全 17 環節／7 題材閱讀、實際 canvas 選取、相鄰高亮、14px 標籤、resize、URL／返回分享、防慢回應、重試、手機全螢幕、鍵盤搜尋、公司輕量頁、篩選及矩陣一致性 |
| 日期 UI | 日精度只顯示日期，按台北時區還原日期，避免 PostgreSQL UTC 正規化後退一天；發布／出表／活動／取得分開 |
| 執行環境 | PostgreSQL Alembic 0002、advisory lock、單一 hourly cron 與 concurrency 1 通過 |
| 重啟持久化 | 重啟本專案 DB／API／web／Prefect／worker 後，全部資料與分類關聯筆數一致 |
| OpenSpec | strict validate 通過；實作進度以 tasks checkbox 為準 |

視覺 QA 已檢視桌機研究、題材、覆蓋表、390px 手機閱讀與全螢幕圖；修正淡化程度、圖形控制遮擋及手機載入後閱讀定位。截圖位於 [screenshots](screenshots/)。Starlette TestClient 保留一則 httpx deprecation warning，不影響測試結果。

## 正式資料與實際回補

升級前已建立 `backups/industry-20261008-173224.dump`（pg_dump custom format，SHA256 `8913D8364105CCA8667A0C4148DCA749113F9A4A146C11030270EF09E17E6BD6`）。新增 migration 後重新匯入全文、正規化與分類原 122 筆事件，再以公開來源嘗試 90 日回補。初始化現在只重分類規則過期事件，手動全量重分類保留 fetched_at，不會把純分類處理當作擷取。

正式 DB：2624 筆事件、98 筆財務、95 家公司、5 筆既有企業關係；1336 筆環節分類、208 筆題材分類。未向 runtime 發布 fixtures。39 個註冊來源為 17 success、2 failed、18 configuration_required、2 manual；23 筆宣告包含 SEC 公司模板，故展開後來源數不同。

| 產業來源 | 本次歷史觀察 | 頁數／邊界 | 限制 |
|---|---|---|---|
| census-m3 | 2026-10-02T00:00:00+00:00 | 2／有限歷史 | 目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值 |
| eia-monthly | 2026-09-24T00:00:00+00:00 | 1／有限歷史 | 本輪僅最新公開月報；未取得歷史發布快照，保留回補缺口 |
| moea-industrial-production | 2026-07-23T16:00:00+08:00 | 5／已達 90 日 | 以官方列表最近六期發布為限；保留工業生產口徑 |
| semiengineering | 2026-07-10T07:01:43+00:00 | 35／已達 90 日 | 以公開 RSS／分類列表可取範圍為限；付費文章不擷取 |
| technews-components | 2026-07-10T16:04:00+08:00 | 49／已達 90 日 | 以公開 RSS／分類列表可取範圍為限；付費文章不擷取 |
| technews-energy | 2026-07-08T17:54:00+08:00 | 24／已達 90 日 | 以公開 RSS／分類列表可取範圍為限；付費文章不擷取 |
| technews-semiconductor | 2026-07-10T10:20:00+08:00 | 102／已達 90 日 | 以公開 RSS／分類列表可取範圍為限；付費文章不擷取 |
| technews-server | 2026-07-08T15:15:00+08:00 | 11／已達 90 日 | 以公開 RSS／分類列表可取範圍為限；付費文章不擷取 |
| tpca-news | 2026-04-23T00:00:00+08:00 | 1／已達 90 日 | 以公開消息列表及免費正文可取範圍為限 |

科技新報四分類、Semiconductor Engineering 與 TPCA 已觀察到超過 90 日的發布邊界，僅保存範圍內免費摘錄。RSS 與列表重疊不會誤判為同一頁；跨 feed canonical URL 合併，付費內容不擷取。經濟部取得近三期發布；Census 最新完整月報有發布日，歷史索引只保存期別且不推定發布日／PDF 數值；EIA 本次僅最新公開月報。統計按 provider＋dataset＋period 識別，不能當作純 AI 或公司訂單。

台積電／NVIDIA IR 實際 HTTP 403，既有資料仍保留；SEC 18 個公司來源仍待維護者真實 SEC_USER_AGENT，沒有以測試資料代替正式成功。網頁可讀性、宣告範圍與 runtime 成功分開。

## Prefect 與重跑

新版完整更新 run `486cbff1-bf10-4956-a175-42bf9061520e` 於 2026-10-08 10:12:24–10:13:00 UTC COMPLETED，37 個自動來源均已嘗試，新增筆數全部為 0。COMPLETED 不表示每個來源均成功，個別限制仍見來源狀態。

每小時 `7 * * * *`、deployment concurrency 1 與 PostgreSQL advisory lock 仍有效。重建 worker 時中斷的舊 run `01a11ae1-72a4-7e99-9c27-6bd111a3f84f` 及其 task 已標 CRASHED，保留中斷紀錄；沒有清除排程或歷史。維護時先確認當下 flow 執行完成，再重建 worker；initialize 的 `--only-stale` 避免啟動時反覆重分類全部資料。

## 判讀界線

原研究查核基準、可追溯來源與真實擷取結果為 well-supported；內容分類為可檢閱規則命中，不取代事實查核。三種影響路徑均為 inference，從 direct 環節開始；只有公司提及、例行財報、背景統計或未知發布日不會冒充直接事件。EIA／Census 歷史發布補齊、SEC live 存取與 IR 恢復保留 needs verification。
