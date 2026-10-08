# 官方資料來源與更新

執行 `docker compose run --rm ingestion python -m app.ingest` 更新全部來源；`--source twse-financials` 可只抓一個來源。來源 ID 與狀態見網站「來源狀態」或 `/api/sources`。程式不需要行情服務或 Claude key。

| 類型 | 實際介接 |
|---|---|
| TWSE | OpenAPI 重大訊息、月營收、一般業綜合損益表；失敗時嘗試官方 CSV |
| TPEx | OpenAPI `mopsfin_t187ap04_O`／`05_O`／`06_O_ci` |
| SEC | 維護檔有 CIK 的公司，各自 submissions 與 companyfacts |
| 台積電 IR | 季度索引與最近季度；未舉行活動標為預告，不標為已發布財報 |
| 台達電 IR | 具日期的法說簡報／逐字稿公開下載連結 |
| NVIDIA IR | 官方法說活動 RSS；外殼、封鎖或空 feed 如實顯示失敗 |
| 微軟 IR | 正文具發布日期的財報新聞稿，追蹤共用導覽列中的最新季度 |

來源 ID、提供者、端點、擷取設定及宣告範圍統一在 `industry-map/sources.yaml`，欄位見地圖唯一 Schema。`backend/app/registry.py` 讀取並依 CIK 展開 SEC 公司來源；manual 為研究入口，排程不擷取。verified 僅表示人工查核網頁可讀，runtime 的 status、last_attempt、last_success、error 與 fetch_meta 分開保存。

新增來源：科技新報 semiconductor／component／pcnotebook/伺服器／能源科技四個 RSS、Semiconductor Engineering RSS、TPCA 公開新聞稿、經濟部工業生產新聞稿、Census M3 最新完整月報及歷史先行報告索引、EIA Electric Power Monthly。僅有限摘錄，不發布免費範圍之外的正文。來源範圍涵蓋所有環節及題材，實際命中按內容規則判定。

首次執行 bounded 回補來源可提供的近 90 日，其後每小時由同一 Prefect deployment 更新最新頁；可手動強制回補：

```powershell
docker compose run --rm ingestion python -m app.ingest --backfill-days 90
docker compose run --rm ingestion python -m app.ingest --source technews-semiconductor --backfill-days 90
docker compose run --rm ingestion python -m app.ingest --reclassify
```

fetch_meta 記錄 requested_days、pages、cutoff_reached、oldest_observed、newest_observed、warnings 與 limit；backfill_meta 保留最近歷史回補，不被後續最新頁更新覆寫。科技新報 RSS 的 paged query 會轉向主 feed，回補使用免費分類列表 `/page/N/` 的發布標籤與公開摘錄，日常更新仍使用 RSS。重複回同頁或達頁數上限尚未觸及 90 日邊界時停止並標 partial；不能宣稱完整回補。Census 歷史索引僅記期別與原文件 URL，無發布日與數值；EIA 本輪只取得最新月報，歷史入口限制保留在報告。統計按 provider＋dataset＋period 去重，避免最新 URL 換期覆蓋前期；科技新報跨 feed 按 canonical URL 合併並保存 feeds。不同提供者不憑標題合併。

日期語意與覆蓋計數見 [industry-research](industry-research.md)。台灣出表日記 reported_at，TSMC／台達活動日記 activity_at；未知發布日維持 null，財報原始 Financial 欄位保留相容。

SEC 依 [官方存取規範](https://www.sec.gov/about/developer-resources) 要求可聯絡的 User-Agent。在 `.env` 設 `SEC_USER_AGENT=IndustryFlow 維護者實際email`；空值時標記 configuration_required，不冒用聯絡人。本程式所有 HTTP 以最多約 4 requests/s 執行，逾時 20 秒、最多兩次嘗試；不可用不影響其他來源。

損益表「季別 2」表示半年**累計**，不是第二季單季；TW 金額從千元轉為完整 TWD 元。SEC 財報以期間、原幣及 accession 分組，避免把不同申報版本的 EPS、營收拼在一起。YoY 只在同口徑期間可比較時衍生。原始資料與修正版本可由 DB 或事件 API 回查；新來源加入不能以欄名相似直接假定單位。

IR 收錄的是法說日期與官方文件連結／正文節錄，不宣稱 PDF 或影片已轉錄。TSMC datePublished 的 1970 占位值不得採用。只有活動預告或部分季度遭封鎖會明示 preview／partial。主要公司來自官方 issuer，提及公司與地圖 inference 分開。

`backend/tests/fixtures` 全是離線測試資料，runtime 不讀取該目錄。來源失敗時保留歷史資料與 last_success，last_attempt／error 另行更新；來源頁不 cache。
