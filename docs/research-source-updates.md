# 來源到期更新與恢復

新版研究環境的更新入口使用 `research.source_refresh_jobs`；研究發布仍走獨立 jobs 與 Git 流程。來源更新只增加營收、事件、指標觀測與擷取狀態，不改寫 Markdown、正式供應關係或 active research release。

## 操作

Owner 在 `/admin` →「來源健康」開啟「來源能力」，可看宣告頻率、可取／可衍生指標、歷史限制及最近實際結果。「更新一次」先保存 durable job，再嘗試派送 Prefect；同一來源已有等待、執行或退避作業時回原作業，不另開請求。人工維護來源不提供自動更新。更新後只重讀該列，不清除已載入的來源分頁。

背景服務關閉時作業會等待，網站繼續讀既有資料。既有 scheduler profile 的 `official-information/hourly` 每小時檢查到期來源；公告預設 1 小時，月營收／SEC 營收／技術文件預設 24 小時。`source-updates/refresh` 執行單次作業，`source-reconciliation/minute` 每分鐘補派到期或失聯作業，每次最多 50 筆。部署／flow/task 不額外重試 HTTP。這些 deployment 需先完成登錄並有 worker 才會執行，預覽 `research_lab.py up` 不會自行啟動 scheduler。

必要時可在已驗證的隔離 Compose writer 服務執行：

```text
python -m app.source_updates --source twse-revenue
python -m app.source_updates --job <job-uuid>
```

第一個命令為指定來源排入單次更新，再處理其已到期作業；第二個續跑原作業。不要在 host 設定 bootstrap DSN，也不要指向舊專案。一般批次仍可用 `python -m app.ingest`；research writer 環境會轉到相同 durable 流程。自動恢復需主機、DB、Prefect 與 worker 恢復，停機期間沒有持續擷取保證。

## 重試與故障

- 每個 URL 首次加最多三次重試，暫時網路錯誤／5xx 使用 1／4／16 秒加 jitter；作業最多 800 次請求。預算在請求前寫入 DB，重啟、重派不重設。
- 429 解析秒數或 HTTP 日期的 `Retry-After`，保存來源及提供者退避；未提供有效時間預設 15 分鐘。長等待不縮短，worker 直接結束本輪，之後再續跑。SEC 三個官方 hostname 共用 provider backoff 與既有 2 req/s gate。
- 403、格式改變、空外殼停止當輪。單一來源資料交易回滾，保留最後有效數值與最後成功時間；其他來源仍可執行。程序在資料提交後中斷時會續跑同 job，利用既有營收與事件 identity 去重。
- URL 限於註冊主機、HTTPS、公開 IP，重新導向逐次核對；20 秒、解壓後 25 MiB 界線。沒有任意網址代理。來源能力與實際成功分開，不因註冊或 HTTP 200 就宣稱已取得數值。

## 營收期間及事件分類

公司財報已於 2026-10-23 移除；TWSE／TPEx 月營收與 SEC revenue 成功後只投影為題材代理指標，不再寫入 canonical 財務。發行人範圍取公司表中的台股代號，穩定公司映射固定使用作業開始讀到的同一 release。

公司 Markdown 仍可選填 `financial-reporting`（完整欄位規則以 `industry-map/README.md` 為準），但目前不驅動任何程式，以下為原用途紀錄。它記錄來源族、信心、查核日及證據；財年須同時附 `fiscal-year-end`、`calendar-valid-from`、`calendar-valid-to`。只有 `well-supported` 且適用期間涵蓋該報表，才可用 12-31 年結推導台灣季度摘要的實際日期。未知、已失效、其他年結均保留原列與缺口，可改用附實際期間的官方補錄；不為了讓圖表有值而替公司補猜設定。設定沿用草稿、驗證及發布，不另建第二套管理來源。

官方發布標 `official`；媒體標 `report`，含匿名／傳聞關鍵詞則為 `rumor`。此分類說明資訊性質，不是自動查證結果。事件主體 `direct`、內容公司提及 `mention`、環節／題材背景 `background` 各自保存，傳聞不加入正式研究圖。

## API 與驗證

| 方法與路徑 | 行為 |
|---|---|
| GET `/api/admin/sources/{source_id}` | Owner 查能力宣告、最近結果、最近 job 與健康 |
| POST `/api/admin/sources/{source_id}/refresh` | Owner＋CSRF／Origin；202 回持久作業，人工來源 422 |
| GET `/api/admin/source-jobs/{job_id}` | Owner 查狀態、最早續跑時間、請求次數與結果 |

全部 `no-store`，不提供給私人讀者入口。`python scripts/research_lab.py pg-check --suite source-updates` 使用獨立測試 DB、離線 HTTP 與真實程序中斷；`frontend/tests/source-updates.spec.ts` 的畫面使用明示合成 API，代理授權邊界使用實際應用。測試不等於已啟動正式排程或已核對全部公司財年。
