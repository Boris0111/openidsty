# 技術研究與文件維護

研究以 `industry-map/` Markdown／YAML 編輯；正文保存解釋，frontmatter 保存可驗證結構，Git 留下原因與差異。PostgreSQL 是網站唯讀投影、動態資料與歷史的保存處。修改 DB 不會回寫研究，也不是另一個可獨立編輯的研究權威。

匯入先複製一份 authoring snapshot，驗證整份地圖、來源與固定文件引用，再在單一 transaction 更新投影。驗證或寫入失敗會 rollback，保留原研究及歷史。結構通過只表示引用與型別合法，內容仍需核讀原文件。重建研究投影不能取代事件、財報、觀測及歷史的 DB 備份。

1. 依 [唯一 schema](../industry-map/README.md) 編修研究、來源與 optional 文件 manifest；規範性質、公開摘要、版本及已讀章節分開記錄。
2. 執行 `python scripts/validate_map.py`；交付不能只用 skip-prose。修改 validator 時另跑 `python tests/run_validator_tests.py`。
3. 先備份 app DB，在隔離還原 DB 驗證，再使用既有 initialize／`python -m app.import_map` 匯入；網站沒有公開 review 或研究寫入 API。
4. 技術內容變動先列待核對。維護者或已獲授權的 agent 核讀後，將 adopted／no-impact、日期與原因寫入 manifest；只有研究本身需要改變才編修 Markdown。單純取得時間或「不影響原研究」不產生判讀新版本。

判讀原查核日與新技術研究查核日各自保存；若 assessment 實質改變，沿用 change_reason 與既有版本機制。來源 403、404、timeout、登入頁不會清除既有基準、必要摘錄或研究；不足資料留具體缺口，不用 fixtures 補正式資料。


目前 OCP／OIF 監測使用各來源宣告的一個官方索引（上限兩頁），只選冷板需求、OIF 3.2T CPO Module、CMIS 等指定系列，不爬其他連結。明列文件上限十份，HTML 2 MiB、文件 15 MiB、單次 HTTP 20 秒；來源設定可縮小上限。HTTP 重新導向逐跳核對官方 host。每日到期檢查整合在既有 hourly flow 與同一 advisory lock 中，API 不連外。UCIe／IEEE IRDS／JEDEC 目前採人工核對，不保證全文自動取得。

```powershell
docker compose run --rm initialize
# 本機手動略過每日到期時間，只核對指定來源；排程不使用此旗標
docker compose run --rm worker python -m app.ingest --source oif-technical --force-documents
```

正式採用前先在隔離還原環境執行相同指令並保存備份。文件表 migration 為 additive；舊應用回滾可保留新增表，不執行刪除歷史的 downgrade。

文件有三種彼此獨立的狀態：`doc-kind` 是文件性質，Source.status 是取得健康，TechnicalReview.status 才是 pending／adopted／no-impact。必要摘錄與固定版號在 manifest 維護；網站 `/technical-documents/<id>?version=<version-id>#locator-<locator-id>` 可回到原章節。歷史觀測有 limit／offset／total，移除定義只退役、不刪歷史。

內容正規化移除 HTML 導覽與 PDF 重複頁首頁尾、頁碼，統一空白；不以 ETag、取得時間或 bytes 差異單獨生成候選。官方未知版號維持 null，不合成版號。解析器更版先核對相同原 bytes；不能把演算法變動當正式新版。影像／加密／登入／無主體文件保留人工核對限制，不新增 OCR。

採納流程：先從唯讀 detail API 取得候選 content_hash 與 official_version，實際核讀變化與研究影響；若採納，將新固定版本／已讀章節加至 versions，再新增 reviews 的 adopted、version-id、reviewed、reason；若無影響則新增 no-impact 與原因。重新驗證並匯入。reviews 不可指向不存在的 runtime 觀測，匯入失敗整筆 rollback。更新 assessment 才沿用原 change_reason 與判讀版本機制；文件取得或核對本身不建立第四類 watchlist token。

固定版本不能刪除或改指向其他 URL／官方版號／內容。解析器校準須核對相同原 bytes，在同一版本保留 raw-hash，更新 parser-version、content-hash 與 normalization-note；此紀錄為已核對的解析基準，版本識別與官方版號不變，歷史觀測保留，不產生新候選。

人工基準觀測的 fetched_at 是匯入紀錄時間，與正式發布日及人工查核日分開；畫面以「觀測記錄」呈現。自動觀測的同欄位記錄取得時刻。必要已讀範圍不因存在完整 bytes／主體 hash 而擴張。


2026-10-16 預覽回饋後，一般閱讀已移除文件待核對清單及通用進階資訊；監測／核對資料仍由 API 及本機維護使用。當次 UI 驗收與後續修正請分別閱讀 [閱讀修正紀錄](reading-review-20261016.md)，舊畫面矩陣不代表修正後畫面。
