# 研究資料模型與遷移

僅在 `compose.research.yaml` 的隔離 DB 執行 `alembic upgrade head`。`0007` 在 research namespace 建立版本、快照、身分、證據、財務修訂與管理工作表（財務表已由 `0017` 刪除）；`0008` 加強不可變內容與讀者列權限。舊 public 表、ticker 主鍵及 API 契約不改。SQLite 仍只測 legacy schema 到 0006；research 約束必須在 PostgreSQL 測試，不能以 SQLite 通過冒充。

公司 ID 與 kind 在全域 entities 固定，名稱、aliases、證券、角色與來源 metadata 隨 release 保存。Snapshot、分類、能力、關係端點、主張與證據全部含 release FK。固定文件 revision 及資產以不可變內容識別；只有 published release 引用的內容可由 reader 讀到。head 只接受 published release，發布後不能把該版改回 ready 或原地改內容；還原只切 head，保留歷史。

公司財務（raw facts、groups、observations、provenance、derivations 與官方補錄）已由 `0017_drop_company_financials` 刪除，downgrade 不重建；刪除前已完整備份。題材營收代理值另由 legacy 營收資料投影到指標表，見 [題材指標](theme-indicators.md)。以下保留原設計說明供歷史查閱：財務分成 raw facts、標準化 groups、observations、provenance 及 derivations。Raw fact 身分含 accession／tag／context；group 的唯一鍵含公司、來源族、metric、原始期間、basis、scope、unit／currency／股別，不含 accession。新值追加 revision；A → B → A 允許再次修訂，不能把回到舊值當重跑。相同值新申報只補來源的實際行為於財務 task 驗證。金額用 Numeric(38,10)，不沿用舊 Float 的精度假設。

`research_reader_login` 屬於 NOLOGIN research_reader，預設 read-only transaction，沒有研究 DML、草稿、jobs、session、audit、匯入批次或原始 payload 權限。RLS 隱藏 ready／未發布的研究及其文件、資產。`0016` 曾為財務 observations／provenance／derivations 加入逐列可見性檢查，已隨 `0017` 移除；reader 角色關閉 JIT 的設定保留。原因與量測見 [效能基準](research-performance.md)。writer 可建立候選投影，但不能 CREATE TABLE 或重寫 published snapshot。兩種 application role 均非 superuser／schema owner／BYPASSRLS。Bootstrap 只供 initializer 做 migration／role 佈建；祕密從忽略的環境檔提供，不作為 CLI argument。

Legacy API 暫時需要 public 表的 SELECT；原 API 的診斷路徑尚待私人網路 gateway 的 allowlist 隔離，不因此宣稱已可公開部署。reader 仍沒有新管理資料的 SELECT 權限。

驗證命令為 `python scripts/research_drill.py pg-check --commit <sha>`，工具拒絕在 application DB 放 fixtures。測試涵蓋 composite FK、38 位 Decimal、revision 與 raw fact／job 唯一鍵、ready head 拒絕、匿名查詢角色無管理權限、未發布文件隱藏、published 內容不可修改。保留測試 DB 可供檢查，不刪除任何既有 volume。

程式回退不等於 DB 回退；migration downgrade 拒絕破壞性刪除。需要回復時用已核對備份還原到另一個獨立 DB，再核對版本、hash 與資料後選擇服務入口。

## 初始化編譯與重建

`research_drill.py rebuild-check --commit <完整commit>` 從 Git archive 取得該提交的研究路徑，驗證完整 Schema 後編譯，拒絕非研究路徑、symlink、重複路徑與超限檔案。編譯結果含完整 Markdown、17 環節、7 題材、95 公司、所有 legacy 映射與固定文件引用；內容不依賴執行時間、網路狀態或當前來源健康。相同 commit／內容 hash 對應相同 release UUID；重跑核對實際 snapshot 內容，而非只相信儲存的 hash。

舊判讀、指標定義／觀測、技術文件／觀測／核對保留原 DB 歷史與日期，另建立 release-scoped legacy_history 映射；動態觀測仍由 DB 備份負責，不回寫靜態 Markdown。舊關係保留原 reason、URL、checked 與 confirmed／candidate，遷移不升級信心。來源註冊表的顯示 metadata 固定在 release，runtime 健康不回頭覆寫。

重建檢查只讀 application DB 的歷史，在 `industry_research_test` 的 rollback-only transaction 內匯入所需父資料與原始歷史、建立投影、再次重建並核對。成功或失敗均 rollback，fixtures 不進 application DB。只含目前 Git commit 而沒有 DB 備份，無法還原動態事件／指標歷史；完整恢復需同時保留兩者。

投影的寫入方式也在這裡核對（2026-11 起，`speed-up-draft-preview-and-editor`）：`project()` 平常把每張表的列累積起來，依 `research_compile.PROJECTION_ORDER`（foreign key 由上而下）整批送出；`immediate=True` 則像以前一樣逐列寫入。重建檢查在既有斷言之前，先在 savepoint 內以逐列方式投影並記下每張投影表的列數與 md5，rollback 後再以批次方式投影，兩邊必須相同；兩次都使用從 application DB 複製來的真實舊歷史，所以 legacy_history 也一併比對。報告 JSON 新增：

- `projection_tables`：每張投影表的 `rows` 與 `md5`（release 的列；entities、documents、document_revisions、assets 為整張表），依主鍵排序後計算，由 `research_compile.projection_tables()` 產生，`backend/tests/test_projection_writer.py` 用同一個函式。
- `writer_equivalent`：兩種寫法的版本識別、內容 hash 與上述各表都相同時為 `true`；不同時檢查直接失敗，不會寫出報告。

`research_lab.py bootstrap` 是本機維護者的一次性初始化操作：第一份研究發布在單一 DB 交易完成，已有 head 就拒絕替換，並在開發 repo 留 `refs/research/releases/<uuid>` 保護內容 commit。日常編輯／後續發布改走尚待實作的 owner／managed-clone 流程；這不是繞過管理授權的讀者上傳 API。資產保存於獨立 research-assets volume，API 僅唯讀掛載。
