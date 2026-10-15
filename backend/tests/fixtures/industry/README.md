# 真實來源 fixtures

2026-10-08 從免費公開 RSS、TPCA 新聞稿、經濟部發布頁、Census M3 與 EIA 月報頁擷取。HTML 移除 navigation／script／style；XML 保留 feed 回應供 parser 測試。`classification-corpus.json` 為逐項檢閱的標題與有限摘錄，expected segments／themes 為人工設定，覆蓋全部環節與題材。負例含例行月營收及 CRAM 軟體新聞；英文邊界与缺乏語境另以合成反例測試。

Fixtures 僅供離線 tests；runtime 不讀取本目錄。資料發布時間依原始欄位，未知不補值；統計樣本檢驗期間／口徑，不以背景當直接事件。

`odm-audit.json` 為 2026-10-14 核對的 12 筆近 30 日真實事件摘錄，保存原 URL／發布日與人工理由。expected_odm 的 null 表示現有摘錄不足，測試不把它當負例。三篇另閱讀完整公開正文，記錄 full_article_checked；runtime 仍只使用原取得摘錄，不載入此 QA 檔。核對方法見 `docs/odm-classification-audit.md`。
# 科技新報歷史列表補充

`technews-category.html` 於 2026-10-08 擷取 https://technews.tw/category/semiconductor/page/2/ 的前三筆免費文章列表；去除圖片、分享控制與 script，保留原標題、發布標籤及公開摘錄。RSS 的 `paged` query 會轉向主 feed，因此歷史回補改走分類列表分頁。這些檔案只供離線測試。
