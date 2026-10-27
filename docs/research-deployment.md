# 研究服務的部署與回退

正式研究服務（Compose project `industryflow-research`）只執行 `main` 第一父鏈上的提交，image 直接從版本控制內容建置，每次部署與回退都先備份並寫入部署紀錄。日常操作（啟動、停止、排程、讀者入口）見 [research-lab](research-lab.md)，備份與還原見 [research-backup](research-backup.md)。

用語：程式的發布稱為「部署（deployment）」或「image 版本」。「release」「restore」只指研究內容的版本（`research.research_releases`、`/api/admin/releases/{id}/restore`），兩者不混用。

## 遷移：擴充與收縮

每個資料庫遷移屬於下列其中一種：

| 種類 | 定義 | 回退 |
|---|---|---|
| 擴充（expand） | 前一版程式可以在新 schema 上運作：新增表、欄位（可為 null 或有 `DEFAULT`）、索引、view | 可以回退到前一版 image，不重跑初始化 |
| 收縮（contract） | 移除、改名、收窄既有結構，或刪除資料 | 不能跨越；只能還原備份 |

### 自動檢查

`scripts/migration_rules.py` 以 `ast` 讀每個遷移的 `upgrade()`（不看 `downgrade()`）及它引用的 `sql/*.sql`，先去除 SQL 註解再比對：

- SQL：`DROP {TABLE|VIEW|COLUMN|FUNCTION|TYPE|SCHEMA|POLICY|TRIGGER|CONSTRAINT|SEQUENCE}`、`RENAME`、`ALTER COLUMN … TYPE`、`SET NOT NULL`、沒有 `DEFAULT` 的 `ADD COLUMN … NOT NULL`、`TRUNCATE`、`DELETE FROM`、`REVOKE`。以字詞邊界比對，`revoked_at` 這類欄位名不算。
- Alembic：`op.drop_*`、`op.rename_table`，以及帶 `type_=`、`nullable=False` 或 `new_column_name=` 的 `alter_column`。

命中的遷移必須在模組層宣告其中一項，理由不可為空：

```python
CONTRACT = '<前一版為什麼會壞>'
EXPAND_REVIEWED = '<前一版為什麼不受影響>'
```

同時檢查遷移鏈線性、只有一個 head、4 位數 revision 等於檔名前綴。CI 以 `tests/test_migration_rules.py` 執行；本機可直接跑：

```powershell
python scripts/migration_rules.py                    # 檢查 working tree，有問題時 exit 1
python scripts/migration_rules.py --commit <sha>     # 某個提交的遷移鏈、head 與收縮清單
```

建置 image 時，head 與收縮清單寫進 label（`io.industryflow.alembic-head`、`io.industryflow.contract-revisions`）。比標記規則更早的提交（例如 `7ebbc68`）沒有 `CONTRACT` 標記，這時含破壞性語句但未標記的遷移一律視為收縮，所以判斷只會更嚴格，不會放寬。

目前的收縮遷移：

| revision | 內容 |
|---|---|
| `0009` | 先 `DROP POLICY` 再以較窄的條件重建 `research.legacy_history` 的讀者政策 |
| `0017` | 刪除公司財報的 7 張表、`financial_fact_citations` view 與 `guard_financial_import()` |

### 規則

1. **移除結構分兩步**：先部署「不再使用該結構」的版本（擴充），之後的部署才放入刪除它的收縮遷移。這樣在兩步之間，正在運行的版本永遠不依賴即將被刪的結構。
2. **收縮遷移要明確確認**：`deploy` 偵測到目標相對目前資料庫新增收縮遷移時，沒有 `--allow-contract` 就拒絕並列出它們。
3. **回退邊界**：含收縮遷移那次部署的部署前備份就是回退邊界，manifest 標記 `rollback_boundary`，30 天清理不刪除它（保存多久由 Boris 手動決定）。要回到邊界之前的版本，只能把那份備份還原到演練環境，核對後再依 [research-backup](research-backup.md) 的事故程序處理。`rollback` 跨越收縮遷移時一律拒絕。
4. **已合併的遷移不得刪除或改寫**：要撤回某個變更，新增一個遷移來做。改寫已部署的遷移會讓資料庫的實際 schema 與遷移鏈不一致，而 `deploy` 遇到「資料庫版本不在目標遷移鏈上」時會拒絕。

### 限制

lint 只看語法。新增 trigger、constraint、policy 這類語意上的破壞抓不到，例如新的 constraint 拒絕前一版會寫入的值。這類變更由合併前的回退預演（`research_drill.py rollback-rehearsal`）補足：預演失敗時，把該遷移改標為 `CONTRACT`。
