# 研究服務的備份與還原

## 每日備份

在部署目錄執行（見 [部署目錄與防護](research-deployment.md#部署目錄與防護)）：

```powershell
cd C:\Users\User\industryflow-prod
.venv\Scripts\python.exe scripts\research_lab.py backup --secondary "D:\backups\industryflow-research" --keep-days 30
```

`backup` 屬於會改變正式服務的動作：與部署、回退共用 `deployments/.lock`，並經過同樣的四項防護。部署或回退正在進行時，備份最多等 30 分鐘（工作排程單次上限是 1 小時）；防護不通過就拒絕，並在 `backup-log.jsonl` 記一筆 `refused: …`。`deploy` 與 `rollback` 開始前也會做一份同格式的備份（含第二份副本），資料夾名稱寫進部署紀錄。

每份備份先寫入 `<時間>.partial`，全部完成並核對後才改名；第二份副本同樣處理。備份被中止（例如工作排程逾時）時留下的 `.partial`，由下一次備份在持有 lock 時清除；`--backup latest` 與 30 天清理都不把它當成備份。

Windows 工作排程器的 `IndustryFlow Research Daily Backup`：每天 03:30 以部署目錄的 `.venv\Scripts\python.exe` 執行上列命令。腳本用絕對路徑，「開始位置」設為部署目錄且不加引號（加引號會讓「開始位置」失效）。錯過的時段（關機、休眠）在下次可執行時補跑，單次上限 1 小時，同時只跑一份。它只在 Boris 登入時執行，因為 Docker Desktop 依附使用者工作階段；Docker 沒啟動時備份會失敗並記錄，不會產生半套備份。

2026-10-21 到正式環境切換前，排程在開發 checkout `C:\Users\User\openspec_pjt` 執行；切換時改寫成部署目錄（[部署與回退](research-deployment.md)）：

```powershell
$action = New-ScheduledTaskAction -Execute C:\Users\User\industryflow-prod\.venv\Scripts\python.exe `
  -Argument 'C:\Users\User\industryflow-prod\scripts\research_lab.py backup --secondary D:\backups\industryflow-research --keep-days 30' `
  -WorkingDirectory C:\Users\User\industryflow-prod
Set-ScheduledTask -TaskName "IndustryFlow Research Daily Backup" -Action $action
Start-ScheduledTask -TaskName "IndustryFlow Research Daily Backup"   # 手動觸發一次，再核對 backup-log.jsonl 與 D: 的副本
```

移除排程：

```powershell
Unregister-ScheduledTask -TaskName "IndustryFlow Research Daily Backup"
```

每份備份是一個以 UTC 時間命名的資料夾（例如 `20261018T214852Z`），主副本在部署目錄的 `backups/research/`（Git 忽略；切換時從開發 checkout 逐檔核對 SHA-256 複製過來），第二份在 `D:\backups\industryflow-research`。C 槽與 D 槽是兩顆不同的實體 SSD（Intel 與 Kingston），第二份複製後逐檔核對 SHA-256。

| 檔案 | 內容 |
|---|---|
| `database.dump` | `industry_research` 的 `pg_dump -Fc`，以二進位直接寫檔，不經文字轉碼 |
| `prefect.dump` | Prefect server 自己的 `prefect` 資料庫（同一個 cluster），`pg_dump -Fc --exclude-table-data=log --exclude-table-data=events --exclude-table-data=event_resources`。這三張觀測資料表只留 schema、不帶資料：沒有其他表以 foreign key 指向它們，合計占資料庫四分之三以上，`log` 的內容也已由各 flow 的報告與 `source_refresh_jobs` 記錄。其餘全部保留：遷移版本、deployments、work pools、排程、flow run 與 task run 的狀態歷史、concurrency limits、blocks、variables。2026-10-30 起才有 |
| `roles.sql` | `pg_dumpall --roles-only --no-role-passwords`：角色與成員關係，不含密碼 |
| `git.bundle` | managed Git 的 `bundle --all`，含 release、job 與 `research/published` 等全部 refs |
| `assets.tar` | 內容定址資產目錄；檔名即內容 SHA-256 |
| `manifest.json` | 建立時間、耗時、各檔 SHA-256 與大小、啟用中的 release（ID、代數、內容 hash、commit）、`public` 與 `research` 每張表的筆數與內容 md5、Git refs；運行中 API 容器的 image ID（`api_image`）與提交（`api_revision`）、資料庫遷移版本（`alembic_version`）；`prefect`：Prefect 自己的遷移版本（`alembic_version`）、`deployment`、`work_pool`、`flow_run` 的筆數，以及只排除資料的表（`excluded_table_data`）；是否為回退邊界（`rollback_boundary`），以及原因：收縮遷移（`contract_revisions`）或 Prefect 版本改變（`prefect_boundary`）。欄位只增不改，較舊的 manifest 沒有 `api_revision`、`prefect` 等欄位 |

- **一致性**：`industry_research` 傾印前後各算一次全表筆數與內容 md5；兩次不同就重做，最多 3 次。這樣清單記錄的就是傾印當下的狀態，還原時可以逐表比對。
- **`prefect` 的一致性**：Prefect 每分鐘都有 flow run 寫入，前後比對會一直不同，所以改用同一個 snapshot：一個 psql session 以 `REPEATABLE READ READ ONLY` 匯出 snapshot、在其中查詢 manifest 的 `prefect` 欄位，再讓 `pg_dump --snapshot` 匯入它。manifest 記的筆數因此正好是 `prefect.dump` 的內容，演練還原後可以逐項比對。傾印檔先寫在 db 容器的 `/tmp/prefect-backup.dump`，讀出後刪除；`pg_dump` 失敗時整份備份失敗。
- **結果紀錄**：成功與失敗都記在 `backups/research/backup-log.jsonl`。失敗時只刪除該次未完成的資料夾。
- **保留**：兩處都保留 30 天。只會刪除名稱符合時間格式、有 `manifest.json`、且不是回退邊界的完整備份資料夾，其他檔案不碰。回退邊界是含收縮遷移、或改變 Prefect 版本那次部署的部署前備份（`rollback_boundary: true`），不自動刪除，由 Boris 手動清理；manifest 讀不出來的資料夾也保留。

**不在備份內**：`.env.research` 的祕密（DB 密碼、session secret）要另外以受保護的方式保存，例如放在加密的隨身碟或密碼管理器。DB 傾印本身含 owner 的 Argon2id 密碼 hash，所以備份資料夾也要視為敏感資料。

## 還原演練

演練使用獨立的 Compose project `industryflow-research-drill`（`compose.research-drill.yaml`），可以從任何 checkout 或 worktree 執行：

- **環境**：自己的 DB、Git 與資產 volume，web 綁 `127.0.0.1:3016`、API 綁 `127.0.0.1:8016`。
- **祕密**：放在 `INDUSTRYFLOW_DRILL_HOME`（預設 `%USERPROFILE%\industryflow-drill`）的 `.env.research-drill`，與 checkout 無關。`setup` 只產生新的演練祕密，不讀正式的 `.env.research`；線上來源更新需要的 SEC 聯絡字串以 `setup --sec-user-agent` 傳入；env 檔已由其他動作建立時，同一個指令會補寫或取代它。錯誤輸出同時遮蔽演練與正式祕密。
- **image**：以備份 manifest 記錄的基準提交（`api_revision`）從 `git archive` 建置或重用（[建置與 image 版本](research-deployment.md#建置與-image-版本)）。manifest 較舊、沒有這個欄位時，以 `--baseline-commit` 指定當時正式 image 的提交。因為用的是基準 image，待合併提交的新遷移不會讓還原失敗。
- **隔離**：沒有排程，不會自動抓取來源；也不啟動 Prefect server，所以還原的 `prefect` 資料庫不會被寫入。不動正式服務與原服務，演練前後都會比對兩者的容器指紋。

```powershell
python scripts/research_drill.py setup                       # 第一次：在 INDUSTRYFLOW_DRILL_HOME 產生演練祕密
python scripts/research_drill.py restore --backup latest      # 從空 volume 開始，計時並核對；也可給備份資料夾路徑
python scripts/research_drill.py owner                        # 演練用 owner：只在演練 DB 內換成演練密碼
python scripts/research_drill.py down                         # 只移除演練 project 的容器與 volume
```

`--backup latest` 選部署目錄（`INDUSTRYFLOW_PROD_HOME`，預設 `%USERPROFILE%\industryflow-prod`）`backups/research/` 下最新一份有 `manifest.json` 的備份。它只讀備份檔案，不讀部署目錄的 `.env.research`。

`restore` 依序執行下列步驟，報告存在 `.work/research-drill/restore-<時間>.json`，並記下基準提交（之後的 `rollback-rehearsal` 預設回到它）：

1. 核對備份各檔的 hash，依 manifest 決定基準提交，建置或重用它的 image。
2. 啟動空 DB，先套用角色，再以 `pg_restore --exit-on-error` 還原，最後由 `research_roles` 設定演練用登入密碼。
3. 備份含 `prefect.dump` 時，在演練 cluster 建立 `prefect` 資料庫，以 `pg_restore --exit-on-error` 還原。較舊的備份沒有這個檔案：不建立資料庫，報告記 `prefect_restored: false` 並在 `prefect_note` 註明原因，不算失敗。
4. 以 `clone --mirror` 還原 managed Git，並移除指向 bundle 的 remote 設定。
5. 解開資產。
6. 啟動 API 與 web。
7. 逐項核對：全表筆數與內容 md5、啟用中的 release、API 實際提供的 release、Git refs、資產內容 hash 與數量、遷移版本（manifest 有記錄時）、`/next` 能否開啟；還原了 `prefect` 時，再核對它的遷移版本與三項筆數（`prefect_match`，不符時 `prefect_differing` 逐項列出備份與還原的值）。

合併前的預演部署、預演回退與分支程式的 PostgreSQL 檢查也在這個環境進行，見 [合併前演練](research-deployment.md#合併前演練)。

## 2026-10-19 演練結果

| 項目 | 結果 |
|---|---|
| 備份 | `20261018T214852Z`，耗時 59 秒；DB 3.5 MB、Git bundle 3.2 MB、資產 14 個；release `4969dd12…`（第 2 代） |
| 第二份 | D 槽副本 5 個檔案 SHA-256 全部相符 |
| 還原 | 從空 volume 到核對完成 **52.1 秒**：DB 可用 4.9 秒、DB 還原 13.2 秒、Git 與資產 17.0 秒、服務啟動 26.2 秒 |
| 核對 | 59 張表筆數與內容 md5 全部相同（含財務觀測、修訂、歷史與發布紀錄）；兩個 release 與啟用中版本一致；4 個 Git ref 一致；14 個資產內容 hash 正確；`/next` 回 200 |
| 隔離 | 原服務與預覽的容器指紋在演練前後相同 |
| 排程 | 已由工作排程器實際觸發一次並成功（見下方紀錄） |

**RPO**：每日備份時，最壞情況會遺失最近 24 小時內的變更，加上一次備份的耗時（約 1 分鐘）。若主機在 03:30 關機，排程會在下次開機後補跑，關機期間沒有新資料，所以不會擴大遺失。RPO 24 小時的目標以排程頻率達成。

**RTO**：實測 52 秒，遠低於 2 小時目標。實際事故還要加上判斷與決策時間。

以上是個人部署的驗收量測，不是可用性保證。

## 事故時保留新版資料的回復程序

原則：不覆寫現有 volume，先保全最新狀態，再在獨立環境還原與比對。研究內容可由 Git 重建，動態數據可由官方來源重新取得，兩者分開處理。

1. **先備份現況**：即使預覽已損壞，只要 DB 或 Git 還能讀，就先執行一次 `research_lab.py backup`。這份保存的是事故當下最新的資料，例如備份之後才發布的 release 與草稿。
2. **在演練環境還原**：用最近一份正常的備份執行 `research_drill.py restore`，確認核對全部通過，並記下它的 release 與時間。
3. **比對差異**：拿第 1 步的備份與第 2 步的資料比對。
   - **研究 release**：比對 `manifest.json` 的 `active_release` 與 `git_refs`。較新的 release 若仍在第 1 步的 Git bundle 裡，就從那個 commit 建立新草稿並重新發布，不要直接改 DB。
   - **營收指標與事件**：較新的部分由來源單次更新重新取得。
4. **切換**：演練環境（3016）可以先暫時作為服務使用，研究服務的 volume 保留不刪，供事後比對。要把資料併回 3010 時，先停止研究服務的 web 與 API，再依 `research-lab.md` 的方式還原到新 DB，核對後才啟動。任何步驟都不使用 `git reset` 回復資料，也不刪除原 volume。
5. **研究還原與資料庫還原分開**：只是內容發布錯誤時，用管理介面的 release 還原（`/api/admin/releases/{id}/restore`）回到前一版即可，不需要還原整個 DB。

## 事故時還原 `prefect` 資料庫

Prefect server 啟動時會遷移自己的 `prefect` 資料庫，而且不使用 downgrade。所以要回到 Prefect 升版之前的版本時，`rollback` 一律拒絕，訊息指出要還原的回退邊界備份：回退目標之後第一個回退邊界的部署前備份，它同時含 `industry_research` 與 `prefect`（[部署與回退](research-deployment.md#回退)）。`prefect` 資料庫毀損時也用這個程序，備份改用最近一份正常的每日備份。

1. **停止正式服務**：`research_lab.py stop`，含排程。Prefect server 運行時不能替換它的資料庫。
2. **先在演練環境還原並核對**：
   ```powershell
   python scripts/research_drill.py down
   python scripts/research_drill.py restore --backup C:\Users\User\industryflow-prod\backups\research\<邊界備份>
   ```
   報告的 `prefect_restored` 要是 `true`，`checks` 全部相符。
3. **改名保留現有的 `prefect`，不刪除**，符合「不覆寫現有資料，先保全最新狀態」：
   ```powershell
   docker exec industryflow-research-db-1 psql -U industry -d postgres -v ON_ERROR_STOP=1 -c "ALTER DATABASE prefect RENAME TO prefect_before_<UTC 時間>"
   ```
4. **新建空的 `prefect`，還原邊界備份的 `prefect.dump`**：
   ```powershell
   docker exec industryflow-research-db-1 psql -U industry -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE prefect"
   docker cp <邊界備份>\prefect.dump industryflow-research-db-1:/tmp/prefect.dump
   docker exec industryflow-research-db-1 pg_restore -U industry -d prefect --exit-on-error /tmp/prefect.dump
   docker exec industryflow-research-db-1 rm /tmp/prefect.dump
   ```
5. **`industry_research`**：看 Prefect 升版那筆部署紀錄。
   - `alembic_before` 等於 `alembic_after`（升版沒有帶遷移）：不必還原，舊版程式可以直接用現有資料。
   - 不相等：舊版的遷移鏈不認得較新的版本，下一步的 `deploy` 會拒絕。同樣把 `industry_research` 改名保留、新建，以邊界備份的 `database.dump` 還原；邊界之後的研究內容與數據依上一節第 3 步比對、補回。
6. **以舊版 image 接手**：`stop` 之後沒有 app 容器在運行，所以可以部署邊界之前運行的提交：
   ```powershell
   .venv\Scripts\python.exe scripts\research_lab.py deploy --commit <邊界之前運行的提交>
   .venv\Scripts\python.exe scripts\research_lab.py scheduler-start
   ```
   舊版腳本以它自己的規則建置、initialize、替換並寫入部署紀錄，所以紀錄、checkout 與容器重新一致。`rollback` 在這裡不能用：它依部署紀錄判斷 Prefect 版本，資料庫還原後仍會拒絕。`scheduler-start` 後在 Prefect（http://127.0.0.1:4201）確認 deployments 與下一個排程。
7. 確認正常後，`prefect_before_<時間>`（與改名保留的 `industry_research`）由 Boris 決定何時刪除。經過記在 `docs/research-acceptance.md`。

**信心**：第 2 步已在演練環境實測（2026-10-30，見下方「`prefect` 傾印與還原驗證」）；第 3–7 步依腳本與 PostgreSQL 的行為推導，尚未在正式環境執行過。

## 排程實際執行紀錄

| 時間（UTC） | 觸發方式 | 結果 | 耗時 |
|---|---|---|---|
| 20261018T214852Z | 手動執行 | ok，D 槽副本相符 | 56.2 秒 |
| 20261018T215359Z | 工作排程器 `Start-ScheduledTask` | ok（LastTaskResult 0），D 槽副本相符 | 52.4 秒 |

下一次自動執行：2026-10-20 03:30（本機時間）。
