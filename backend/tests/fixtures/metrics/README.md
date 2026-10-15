# 真實指標摘錄 fixtures

此目錄只供離線 parser 測試，正式 API／ingestion 不讀取。

AAON 兩檔於 2026-10-14 一般 HTTPS GET 原公告（200），以最少必要原文短摘錄及原發布／季度資訊重排成 HTML。標籤與數字來自來源，HTML 結構是 normalized excerpt，不宣稱原頁完整快照。

- [2025 Q4](https://investors.aaon.com/investor-news/aaon-reports-fourth-quarter-and-full-year-2025-results-carries-record-backlog-into-2026)：當季 BASX 液冷 75.3 million USD，發布 2026-03-02；不使用 102.6 million 的 AAON Coil Products 混合收入。
- [2026 Q1](https://investors.aaon.com/investor-news/aaon-reports-first-quarter-2026-results-with-record-sales-and-backlog-robust-earnings-growth-and-raises-full-year-guidance)：當季 BASX 液冷 93.2 million USD，發布 2026-05-07；不使用 117.6 million 的混合收入。

累計／預估／缺標籤負例由 tests 明確合成，與真實來源樣本分開。

`tsmc-q2-2026.html` 的必要標籤、占比及期間來自 [TSMC 官方稿](https://pr.tsmc.com/japanese/news/3326)，2026-10-14 以 web open 讀到。一般 HTTP GET 回 403；此為已核對的 normalized text fixture，不能放入正式 DB 或表示 live adapter 取得成功。生產流程仍由官方季度索引與新聞稿實際 HTTP 回應取得值，取不到就保留缺口。
