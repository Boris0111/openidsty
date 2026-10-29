# Design

## Context

動機見 proposal.md 的 Why。以下是影響做法的現況，數字為 2026-10-29 在正式環境以唯讀查詢量得。

- **`prefect` 資料庫和研究資料庫在同一個 PostgreSQL cluster**：
  - 由 db 容器的初始化腳本 `docker/research-init.sql` 建立。Prefect server 透過 `PREFECT_API_DATABASE_CONNECTION_URL` 使用它，並以自己的 alembic 遷移管理 schema；目前版本 `d4a7e1c93f52`，Prefect 3.8.8。
  - 資料庫大小 786 MB：`event_resources` 305 MB、`events` 300 MB、`flow_run_state` 76 MB、`flow_run` 51 MB、`log` 43 MB。
  - 內容：5 個 deployments、1 個 work pool、17,561 筆 flow run、112,951 筆 log。
  - 完整 `pg_dump -Fc` 為 60 MiB、17 秒；排除 `log` 的資料為 55 MiB、13 秒。
- **備份**：`backup()` 傾印 `industry_research`（前後比對全表筆數與 md5，最多重試 3 次）、角色、managed Git 與資產，manifest 列出各檔 SHA-256。主副本與第二份副本先寫入 `.partial` 再改名。
- **回退邊界**：只有含收縮遷移的部署會把部署前備份標為 `rollback_boundary`。`rollback` 遇到 Prefect 版本不同時一律拒絕，但沒有任何備份可以把 `prefect` 資料庫還原到升級前。
- **演練**：drill compose 的 db 沒有掛載初始化腳本，所以沒有 `prefect` 資料庫，也不啟動 Prefect server。
- **互斥檢查**：`exclusion_conflicts()` 只在 `deploy`（上一版腳本，交接前）、`start`、`reader-start` 呼叫。

## Goals / Non-Goals

**Goals:**
- 讓「回不了舊版 Prefect 就還原備份」成為真的可行的路徑，並在演練環境驗證。
- 備份體積與耗時增加有界，不因 Prefect 的觀測資料而膨脹。
- 互斥規則套用在每個會讓研究服務的排程或 API 接手共用 port 的動作上。

**Non-Goals:**
- 不在演練環境啟動 Prefect server 或排程；只驗證資料庫還原的完整性。
- 不設定 Prefect 自己的保留期限（events、logs 的清理）。這屬於另一個維運議題，見 Open Questions。
- 不處理正式 Prefect 中卡住的 run，那由 Boris 決定。

## Decisions

### D1：`prefect.dump` 只帶排程狀態，不帶觀測資料

- 以 `pg_dump -Fc --exclude-table-data=log --exclude-table-data=events --exclude-table-data=event_resources` 傾印 `prefect` 資料庫。三張表的 schema 照樣保留，只是不帶資料。
- 保留的是升降版後回復排程所需的一切：schema 與 alembic 版本、deployments、work pools、排程、flow run 與 task run 的狀態歷史、concurrency limits、blocks、variables。
- 被排除的三張表：
  - 沒有其他表以 foreign key 指向它們，空表還原後 Prefect 照常運作；
  - 它們是可遺失的觀測資料，`log` 的內容也已由各 flow 的報告與 `source_refresh_jobs` 記錄；
  - 合計占資料庫的四分之三以上。
- **不比對前後筆數**：`industry_research` 的重試規則（前後兩次 inventory 相同才接受）不適用，因為 Prefect 每分鐘都有 flow run 寫入。`pg_dump` 本身在單一 snapshot 內，一致性已足夠。
- manifest 新增 `prefect`：`alembic_version`，以及 `deployment`、`work_pool`、`flow_run` 的筆數，都在傾印前查詢。欄位只增不改；較舊的 manifest 沒有它。
- **apply 時補充：查詢與傾印共用 snapshot**。查詢與 `pg_dump` 若各自取 snapshot，中間 Prefect 新增一筆 flow run，D3 的筆數核對就會誤報不符。所以由一個 psql session 以 `REPEATABLE READ READ ONLY` 匯出 snapshot、在其中查詢，再以 `\!` 執行 `pg_dump --snapshot` 匯入同一個 snapshot；`pg_dump` 失敗時以 PostgreSQL 16 的 `SHELL_ERROR` 讓 psql 失敗。已在一次性容器實測：查詢與傾印之間持續寫入時，還原的筆數仍等於查詢值。manifest 另記 `excluded_table_data`。
- **不選完整傾印**：60 MiB × 30 天 × 兩份副本約 3.6 GB，而且 `events` 會隨時間持續成長。
- **不選只在部署前備份傾印**：每日備份也要能在事故後回復排程，例如 Prefect 資料庫毀損時。

### D2：Prefect 升版的部署前備份是回退邊界

- `deploy_target()` 比較目標與目前紀錄的 `prefect_version`。不同時，部署前備份以 `rollback_boundary` 標記，部署紀錄記下 `prefect_boundary: true`。
- `latest_boundary()` 同時考慮收縮邊界與 Prefect 邊界。
- `rollback_refusals()` 在 Prefect 版本不同時改寫拒絕訊息：指出最近一次的 Prefect 邊界備份，並指向 `docs/research-backup.md` 的事故程序。
- **不選允許跨 Prefect 版本回退後自動降級 `prefect`**：Prefect 的 downgrade 未經驗證，與 D7「不使用 downgrade」的原則一致。
- **apply 時調整：指出回退目標之後的第一個邊界，而非最近一次**。`latest_boundary()` 改為 `first_boundary()`，收縮與 Prefect 的拒絕訊息都用它。只有一個邊界時兩者相同；跨越多個邊界時（例如先收縮遷移、再升級 Prefect，要回到收縮之前），最近一次的邊界備份已經包含較早的改變，還原它回不去。`fallback()` 同樣取上一個成功版本之後的第一個邊界。

### D3：演練還原 `prefect` 並核對

- `research_drill.py restore` 遇到 manifest 列有 `prefect.dump` 時：
  1. 在演練 cluster 執行 `CREATE DATABASE prefect`；
  2. 以 `pg_restore --exit-on-error` 還原；
  3. 核對 `alembic_version` 與三項筆數和 manifest 相同。
- 報告加入 `prefect_restored` 與核對結果。沒有 `prefect.dump` 的舊備份記為 `prefect_restored: false`，原因為「這份備份早於 prefect 傾印」，不算失敗。
- 演練不啟動 Prefect，所以還原的資料庫不會被寫入，核對結果穩定。

### D4：事故時還原 `prefect` 的程序

- 寫入 `docs/research-backup.md`：
  1. `stop` 正式服務（含排程）；
  2. 先在演練環境還原邊界備份並核對；
  3. 在正式 cluster 把 `prefect` 改名保留（不刪除）；
  4. 新建空的 `prefect` 資料庫，以 `pg_restore` 還原邊界備份的 `prefect.dump`；
  5. 依既有程序處理 `industry_research`；
  6. 以舊版 image `scheduler-start`。
- 改名保留而不刪除，符合既有「不覆寫現有資料，先保全最新狀態」的原則。
- **apply 時補充第 5、6 步的實際做法**：
  - 第 6 步的「以舊版 image」由 `deploy --commit <邊界之前運行的提交>` 完成，再 `scheduler-start`。`stop` 之後沒有 app 容器，防護通過；舊版腳本建置、initialize、替換並寫入部署紀錄，紀錄與容器重新一致。`rollback` 依部署紀錄判斷 Prefect 版本，資料庫還原後仍會拒絕，不能用。
  - 第 5 步只在升版那次部署帶了遷移（`alembic_before` ≠ `alembic_after`）時才需要還原 `industry_research`：否則舊版腳本的 `deploy` 不會因遷移鏈拒絕，舊版程式可直接用現有資料。
  - 第 3–7 步尚未在正式環境執行過，文件標明信心。

### D5：互斥檢查涵蓋 `scheduler-start` 與 `rollback`

- **`scheduler-start`**：取得 lock、通過防護後，在啟動 `prefect` 之前呼叫 `exclusion_conflicts()`。
- **`rollback`**：在現行腳本中、判斷相容性時一併檢查，拒絕訊息和其他拒絕條件列在一起。檢查在備份與 checkout 之前，目標腳本不重複檢查。
- **`restore`（從原服務匯入）不檢查**：它的來源就是運行中的原服務資料庫，而且只啟動不對外發布 port 的 db。

### D6：`bootstrap` 以 `core.autocrlf=false` 取得內容

- 與 `build_images` 和演練的 `rebuild-check` 相同，`git -c core.autocrlf=false archive`。
- 不改 `seed-git`：它用 `git bundle`，傳的是 Git 物件本身，不經換行轉換。

## Risks / Trade-offs

- **[風險] 傾印的大小與耗時隨 flow run 歷史成長**：`flow_run_state` 每天增加。
  → manifest 的 `sizes` 已逐檔記錄；驗證時量測 `prefect.dump` 的大小與耗時並寫進文件。若超過 30 MiB，再評估 Prefect 的保留期限（Open Questions）。
- **[風險] Prefect 新版本改了表名**：`--exclude-table-data` 指名的表不存在時，pg_dump 不報錯，只是不排除。
  → 測試以傳入的參數為準；Prefect 升版的 change 需重新確認表名，寫在 `docs/research-deployment.md` 的 Prefect 升版注意事項。
- **[取捨] 排除 `log`、`events`**：還原後看不到 Prefect UI 中舊 run 的 log 與事件。
  → 研究資料與更新結果不依賴它們；事故時優先回復排程能力。
- **[風險] 還原 `prefect` 需要停機**：Prefect server 運行時不能替換它的資料庫。
  → 事故程序要求先 `stop`；只在跨 Prefect 版本回復時才需要。

## Migration Plan

1. merge 後依 `separate-research-production-deployment` 的部署程序 `deploy`。這次部署不改 Prefect 版本，也沒有遷移。
2. 手動觸發一次每日備份，核對 `prefect.dump` 的 SHA-256、manifest 的 `prefect` 欄位與第二份副本。
3. 把這份備份還原到演練環境，核對 `prefect` 的遷移版本與筆數。
4. 回退：本 change 不含資料庫遷移，可以 `rollback` 回前一版；較新的備份多出的 `prefect.dump` 不影響舊版腳本，因為 manifest 欄位只增不改。

## Open Questions

- Prefect 的保留期限：`events` 與 `event_resources` 合計約 605 MB。是否設定 `PREFECT_EVENTS_RETENTION_PERIOD` 或定期清理 flow run 歷史，另行決定，不影響本 change 的傾印方式。
- 正式 Prefect 中卡住的 run（`research-publication-reconciliation/minute`，自 2026-10-21 停在 PENDING／Submitting）：
  - 它不擋部署，因為忙碌只計 RUNNING 與 CANCELLING。
  - 但 deployment 的 `concurrency_limit=1` 可能因它而不再排入新的 run（最後一次完成在 2026-10-22）。
  - 清理方式由 Boris 決定。
