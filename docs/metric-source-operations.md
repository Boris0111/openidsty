# 直接指標來源操作

來源設定以 `industry-map/sources.yaml` 為準。AAON 首次最多五個索引頁、八份季度結果、近兩年；索引排除 conference-call 預告。TSMC 最多八個季度頁及八份官方新聞稿。每小時只核對最新兩份；沿用 OfficialHttp 的限速、逾時／重試與 PostgreSQL 防重疊鎖。HTTP 成功而無明確產品欄位，仍是資料缺口。

```powershell
docker compose run --rm --no-deps ingestion python -m app.ingest --source aaon-earnings-metrics
docker compose run --rm --no-deps ingestion python -m app.ingest --source tsmc-node-metrics
# 明確重新檢查來源可提供的一年歷史；不是保證完整一年
docker compose run --rm --no-deps ingestion python -m app.ingest --source aaon-earnings-metrics --backfill-days 365
```

首次成功或部分可讀的受限回補保存 backfill_meta 與完成時間；部分歷史缺欄位不會每小時重抓八篇。需要修復解析時，先以有 URL／原期間的真實樣本補測試，再明確回補。未能取得任何值則 failed，保留舊觀測與最後成功日。來源出錯不阻止其他來源，代理投影另記結果。

修訂核對 `indicator_observations` 的 identity、revision、content_hash、original_period、scope、currency、raw_excerpt；不直接覆寫舊值。同樣內容重跑不追加，fetched 不作數值更新。資料年齡以 period_end 計，與 last_success 的 HTTP 時間分開；過舊也繼續可讀。

2026-10-14 的真實取得範圍、未取得項目與重跑結果見 [live 矩陣](theme-indicator-live-matrix.md)。TSMC 索引回 HTTP 403，SEC 未設定實際聯絡資訊；保留缺口。fixtures 只供離線測試，正式 ingestion 不讀 fixtures。
