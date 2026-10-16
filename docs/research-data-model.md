# 研究資料模型與遷移

僅在 `compose.research.yaml` 的隔離 DB 執行 `alembic upgrade head`。`0007` 在 research namespace 建立版本、快照、身分、證據、財務修訂與管理工作表；`0008` 加強不可變內容與讀者列權限。舊 public 表、ticker 主鍵及 API 契約不改。SQLite 仍只測 legacy schema 到 0006；research 約束必須在 PostgreSQL 測試，不能以 SQLite 通過冒充。

公司 ID 與 kind 在全域 entities 固定，名稱、aliases、證券、角色與來源 metadata 隨 release 保存。Snapshot、分類、能力、關係端點、主張與證據全部含 release FK。固定文件 revision 及資產以不可變內容識別；只有 published release 引用的內容可由 reader 讀到。head 只接受 published release，發布後不能把該版改回 ready 或原地改內容；還原只切 head，保留歷史。

財務分成 raw facts、標準化 groups、observations、provenance 及 derivations。Raw fact 身分含 accession／tag／context；group 的唯一鍵含公司、來源族、metric、原始期間、basis、scope、unit／currency／股別，不含 accession。新值追加 revision；A → B → A 允許再次修訂，不能把回到舊值當重跑。相同值新申報只補來源的實際行為於財務 task 驗證。金額用 Numeric(38,10)，不沿用舊 Float 的精度假設。

`research_reader_login` 屬於 NOLOGIN research_reader，預設 read-only transaction，沒有研究 DML、草稿、jobs、session、audit、匯入批次或原始 payload 權限。RLS 隱藏 ready／未發布的研究及其文件、資產；writer 可建立候選投影，但不能 CREATE TABLE 或重寫 published snapshot。兩種 application role 均非 superuser／schema owner／BYPASSRLS。Bootstrap 只供 initializer 做 migration／role 佈建；祕密從忽略的環境檔提供，不作為 CLI argument。

Legacy API 暫時需要 public 表的 SELECT；原 API 的診斷路徑尚待私人網路 gateway 的 allowlist 隔離，不因此宣稱已可公開部署。reader 仍沒有新管理資料的 SELECT 權限。

驗證命令為 `python scripts/research_lab.py pg-check`，工具拒絕在 application DB 放 fixtures。測試涵蓋 composite FK、38 位 Decimal、revision 與 raw fact／job 唯一鍵、ready head 拒絕、匿名查詢角色無管理權限、未發布文件隱藏、published 內容不可修改。保留測試 DB 可供檢查，不刪除任何既有 volume。

程式回退不等於 DB 回退；migration downgrade 拒絕破壞性刪除。需要回復時用已核對備份還原到另一個獨立 DB，再核對版本、hash 與資料後選擇服務入口。
