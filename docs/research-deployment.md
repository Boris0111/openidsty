# 研究服務的部署與回退

正式研究服務（Compose project `industryflow-research`）只執行 `main` 第一父鏈上的提交，image 直接從版本控制內容建置，每次部署與回退都先備份並寫入部署紀錄。日常操作（啟動、停止、排程、讀者入口）見 [research-lab](research-lab.md)，備份與還原見 [research-backup](research-backup.md)。

用語：程式的發布稱為「部署（deployment）」或「image 版本」。「release」「restore」只指研究內容的版本（`research.research_releases`、`/api/admin/releases/{id}/restore`），兩者不混用。

## 部署目錄與防護

正式服務由獨立 clone `C:\Users\User\industryflow-prod` 運作，平時 detached 在部署紀錄中運行的提交。它不是 git worktree：worktree 的管理資料在開發 repo 的 `.git/worktrees`，`git worktree prune` 或重新 clone 開發目錄都會讓正式環境失去 git。開發 checkout `C:\Users\User\openspec_pjt` 不保有正式祕密。

| 部署目錄內的路徑 | 內容 |
|---|---|
| `.env.research` | 正式祕密。不在 Git 與備份內，另存一份受保護的副本（密碼管理器或加密隨身碟） |
| `backups/research/` | 每日與部署前備份，以及 `backup-log.jsonl` |
| `deployments/home.json` | 部署目錄標記：絕對路徑 `path`、建立時間，以及第二份備份位置 `secondary` |
| `deployments/ledger.jsonl` | 部署紀錄，只追加 |
| `deployments/.lock` | 部署、回退、備份與其他正式操作共用的 lock |
| `.work/research-lab/`、`public-snapshot/` | 操作報告與公開快照輸出 |
| `.venv/` | 部署目錄自己的 Python。`research_lab.py` 只用標準函式庫，venv 只為隔離 |

`deployments/` 被 `.gitignore` 忽略，其餘路徑原本就已忽略。建立部署目錄（只做一次）：

```powershell
git clone https://github.com/Boris0111/openidsty.git C:\Users\User\industryflow-prod
cd C:\Users\User\industryflow-prod
git checkout --detach <要部署的 main 提交>
python -m venv .venv
.venv\Scripts\python.exe scripts\research_lab.py init-home --secondary D:\backups\industryflow-research
```

`init-home` 只在獨立 clone（不是 worktree）且 HEAD 為 detached 時才建立標記，已存在時拒絕。

### 防護

Compose project 名稱固定為 `industryflow-research`，從任何目錄執行這份 compose，操作的都是同一組正式容器與 volume。所以防護放在腳本裡。

會改變正式服務的動作有 `deploy`、`rollback`、`adopt`、`start`、`stop`、`scheduler-start`、`reader-start`、`reader-stop`、`seed-git`、`bootstrap`、`restore`、`backup`、`public-snapshot`。它們取得 lock 後檢查四項，任一不符就拒絕並列出全部原因，不改變任何狀態：

1. `deployments/home.json` 存在，且路徑等於腳本所在的 checkout。沒有標記時，連 `deployments/` 與 lock 檔都不建立。
2. `git status --porcelain` 為空：不允許未提交修改，也不允許未追蹤檔案；被 `.gitignore` 忽略的檔案不算。
3. HEAD 等於部署紀錄中運行的提交。`deploy` 交接給目標版本的腳本後，改為要求等於目標提交。
4. 每個運行中 app 容器的 revision label 與 image ID 都等於部署紀錄（`db` 不比對）。`adopt` 紀錄沒有 revision，只比 image ID。`rollback` 只回報這一項、不拒絕，因為它正是用來把容器換回已知版本。

`status`、`check` 是唯讀動作，列出所有不符之處但不拒絕。`check` 不會產生或補寫 `.env.research`。

`setup` 只在需要產生祕密時查詢 Docker：volume `industryflow-research_pg-data` 已存在就拒絕，因為新祕密會和既有資料庫不符。

lock 由作業系統持有（Windows 用 `msvcrt`、Linux 用 `fcntl`），程序結束或當掉時自動釋放，不會留下要手動刪除的 lock 檔。`deploy`、`rollback` 與其他動作拿不到 lock 就立刻拒絕；每日備份最多等 1 小時。

**開發 checkout 的 tombstone**：正式祕密搬到部署目錄後，開發 checkout 留一個值不合格式的 `.env.research`：

```text
# Production secrets moved to C:\Users\User\industryflow-prod (docs/research-deployment.md).
RESEARCH_POSTGRES_PASSWORD=moved-to-the-deployment-directory
```

舊版 `setup()` 讀到它會直接 raise「Invalid research environment」，新版的 `setup`、`check` 也拒絕。所以舊 branch 的 `research_lab.py up` 不會產生新祕密去重建正式容器。

## 建置與 image 版本

image 只從版本控制內容建置，不經過 working tree：

1. `git -c core.autocrlf=false archive --format=tar <sha>` 產生建置內容。不做換行轉換，也不含未追蹤檔案。
2. Python 以二進位 pipe 把 tar 傳給 `docker build -f backend/Dockerfile -`（web 用 `frontend/Dockerfile`）。不經過 PowerShell 管線，因為 PowerShell 5.1 會改寫二進位串流。`.dockerignore` 對 tar context 照樣生效。

tag 為提交前 12 碼：`industryflow-research-api:<sha12>`、`industryflow-research-web:<sha12>`。兩個 compose 檔都沒有 `build:`，image 寫成 `${RESEARCH_IMAGE_TAG:?…}`，由腳本設定；腳本會先濾掉 host 的 `RESEARCH_*` 變數，而 shell 環境的優先權高於 `--env-file`，所以任何檔案都改不了 tag。

| label | 內容 |
|---|---|
| `org.opencontainers.image.revision` | 完整提交 |
| `org.opencontainers.image.created` | 建置時間（UTC） |
| `io.industryflow.alembic-head` | 該提交的遷移 head |
| `io.industryflow.contract-revisions` | 收縮遷移清單，以逗號分隔 |
| `io.industryflow.prefect-version` | 取自 `backend/runtime-constraints.txt` |
| `io.industryflow.build` | 固定為 `git-archive` |

同名 tag 已存在且 label 相符（不比對 `created`）時直接重用；不符時拒絕，不覆蓋。所以演練建置不會移動正式在用的 tag。查看某個 image：

```powershell
docker image inspect industryflow-research-api:<sha12> --format '{{json .Config.Labels}}'
```

**保留**：Docker Desktop 的「Clean up」或 `docker image prune -a` 會刪掉不在運行的 image，包括回退目標。回退遇到 image 不存在時會從 archive 重建，並在紀錄標記 `rebuilt`（pip、npm 建置不是逐位元組可重現）。建議至少保留部署紀錄中最近 5 次成功部署的 image，實際數量看磁碟用量再定。

**2026-10-28 建置檢查**（task 2.3，提交 `2cbcaf4`）：api 與 web 共 202 秒，label 齊全（head `0017`、收縮 `0009,0017`、Prefect `3.8.8`）。image 內 `/workspace/industry-map/themes/800vdc.md` 沒有 CR，SHA-256 與 git blob 相同；舊的 `:dev` image 同一檔案有 136 個 CR。建置前後，正式服務 8 個容器的 ID、image 與啟動時間都不變。

## 部署紀錄欄位

`deployments/ledger.jsonl` 每行一筆 JSON，只追加、不改寫。不存在資料庫裡，因為還原備份會連紀錄一起倒退，失去還原之後的歷史。欄位只增不改：回退會 checkout 舊版腳本，舊腳本忽略它不認得的欄位。

| 欄位 | 內容 |
|---|---|
| `schema_version`、`seq` | 格式版本（目前 `1`）與流水號 |
| `kind` | `deploy`、`rollback` 或 `adopt` |
| `outcome`、`error` | `succeeded`／`failed` 與錯誤訊息 |
| `commit`、`tag` | 完整提交與 image tag（提交前 12 碼；`adopt` 為 `pre-ledger`） |
| `images` | api 與 web 的 image ID |
| `built`、`rebuilt` | 這次實際建置的 image（重用時為空）；回退時 image 是否從 archive 重建 |
| `alembic_before`、`alembic_after` | 操作前後資料庫的遷移版本 |
| `alembic_head`、`migrations`、`contract_revisions` | image 的遷移 head、該提交的遷移鏈與收縮遷移清單 |
| `prefect_version` | image 的 Prefect 版本 |
| `backup`、`contract_boundary` | 操作前備份的資料夾名稱，以及它是否為回退邊界 |
| `replaced` | 服務是否已被替換。正在運行的版本是最後一筆 `replaced: true` 的紀錄 |
| `services` | 操作結束時每個運行容器的 container、image ID、revision 與 Compose working_dir |
| `smoke` | 每項 smoke 檢查的結果（見「部署」） |
| `fallback` | smoke 失敗時建議的回退指令，或只能還原備份的原因 |
| `rolled_back_to`、`drift_before` | 回退：目標紀錄的 `seq`，以及回退前與紀錄不符的容器 |
| `note` | `adopt`：說明它的 `commit` 是部署目錄的 checkout，不是 image 的來源 |
| `started_at`、`finished_at` | UTC 時間 |

## 部署

```powershell
cd C:\Users\User\industryflow-prod
.venv\Scripts\python.exe scripts\research_lab.py status                         # 先確認沒有不一致
.venv\Scripts\python.exe scripts\research_lab.py deploy --commit <main 上的提交>
```

避開每小時第 7 分鐘（`official-information/hourly` 的排程）。`deploy` 依序執行：

1. 取得 lock，檢查四項防護與原服務互斥：原服務在運行，或 port 被其他程式占用，就拒絕。
2. `git fetch origin`，要求提交在 `git rev-list --first-parent origin/main` 裡。main 用 merge commit，只檢查「可達」會放行 PR 內部從未成為 main 的中間提交。
3. 部署目錄 `git checkout --detach <提交>`，再以相同參數執行**目標版本**的 `research_lab.py`。之後的步驟、compose 設定與檢查規則都與 image 同一版本。上一版的腳本持有 lock 直到目標腳本結束；結束時若運行中的版本不是目標，就把部署目錄 checkout 回運行中的提交。
4. 拒絕條件，任一成立就拒絕，什麼都不改：
   - 資料庫目前的遷移版本不在目標的遷移鏈上，代表撤回或改寫了已部署的遷移。
   - Prefect 有 running 或 cancelling 的 flow run（仍在執行）。加 `--force` 才繼續，替換 worker 時會中斷它們。pending 的 run 還沒開始執行，不算忙碌，免得一筆卡住的提交擋住所有部署。
   - 目標相對目前資料庫新增收縮遷移，沒有加 `--allow-contract`。
   - db 容器不是從這個目錄建立的，沒有加 `--recreate-db`。只會在第一次部署發生，見下方「第一次部署」。
5. 部署前備份，含第二份副本（位置取自 `--secondary` 或 `home.json`）。有收縮遷移時，這份備份標記為回退邊界。
6. 依「建置與 image 版本」建置或重用 image。
7. 以新 tag 執行 `compose run --rm --no-deps initialize`：遷移、角色與地圖匯入。這時舊的 api、web 仍在服務。
8. initialize 成功後才替換服務：
   - 一律替換 `api`、`web`（`up -d --no-deps --wait`）。
   - 排程啟用時，依序替換 `prefect`、執行一次 `deploy` 註冊 deployments、再替換 `worker`。
   - reader 正在運行時一併替換。
   - db 不在例行部署中重建。
9. smoke 檢查（下表）。
10. 寫入部署紀錄。

initialize 失敗時，舊服務始終沒被替換：部署紀錄寫入 `outcome: failed`、`replaced: false`，部署目錄 checkout 回原提交。

| smoke 項目 | 通過條件 |
|---|---|
| `health` | `/api/health` 回 200 |
| `release` | `/api/v2/manifest` 的 release 等於資料庫 `research.release_head` |
| `next` | `http://127.0.0.1:3010/next` 回 200 |
| `containers` | 每個運行中 app 容器的 image ID 與 revision 都等於目標，且 api、web 都在 |
| `alembic` | 資料庫的遷移版本等於 image 的 head；回退時則要求維持回退前的版本 |
| `working_dir` | 每個容器的 `com.docker.compose.project.working_dir` 等於部署目錄 |

## smoke 失敗時

部署紀錄標記 `outcome: failed`、`replaced: true`，新服務留在原地，**不自動回退**（Boris 的決定）。指令會印出下一步，同樣寫進紀錄的 `fallback`：

- **可以回退**：印出可直接執行的 `python scripts/research_lab.py rollback --to <seq>`，目標是前一個成功版本。
- **不能回退**（例如這次部署套用了收縮遷移）：說明原因，並指出要還原的部署前備份。依 [research-backup](research-backup.md) 的事故程序，先在演練環境還原核對。
- **前一筆是 `adopt`**：沒有可回退的 image 版本，依下方「回到 pre-ledger image」處理。

先判斷問題再動手：`status` 列出每個容器的版本與不一致之處，紀錄的 `smoke` 欄位指出哪一項失敗。

## 回退

```powershell
.venv\Scripts\python.exe scripts\research_lab.py status                  # 找出要回去的 seq
.venv\Scripts\python.exe scripts\research_lab.py rollback --to <seq>
```

目標必須是部署紀錄中 `outcome: succeeded` 的 `deploy` 或 `rollback`。`rollback` 依序執行：

1. 取得 lock，檢查標記、乾淨的 working tree 與 HEAD。容器與紀錄不一致時不拒絕，只記在 `drift_before`。
2. 拒絕條件：
   - 目標的遷移 head 新於資料庫目前的版本。
   - (目標 head, 資料庫版本] 之間有收縮遷移。舊提交看不到較新的遷移檔，所以用**部署紀錄中各次遷移鏈的聯集**判斷。訊息會指出最近一次的回退邊界備份。
   - 目標與目前的 Prefect 版本不同：Prefect server 會遷移自己的 `prefect` 資料庫。
   - Prefect 有執行中的 flow run，除非加 `--force`。
3. 回退前備份。
4. image 已被清除時從 archive 重建，紀錄標記 `rebuilt: true`。
5. checkout 目標提交，以目標 tag `up -d --no-deps` 替換運行中的服務；排程啟用時重跑一次 Prefect `deploy` 註冊。
6. smoke 檢查，寫入紀錄。

**不執行 initialize**：這樣可以避開舊版 alembic 的「Can't locate revision」，也避免 `import_map` 以舊內容改寫 legacy 地圖表、追加不實的判讀版本，或因缺 `change_reason` 而失敗。代價是回退後 legacy 地圖表保留較新版本匯入的內容，所以**回退期間不產出公開快照**，免得混用新地圖資料與舊程式。

跨不過收縮遷移時，從回退邊界備份在演練環境還原、核對，再依 [research-backup](research-backup.md) 的事故程序處理。不使用 alembic downgrade：多數遷移的 downgrade 刻意 raise。

## 第一次部署（正式環境切換）

部署紀錄開始之前運行的容器，是在開發 checkout 以 `:dev` tag 建的。切換需要 Boris 同意並在場：

1. 建立部署目錄（見「部署目錄與防護」），`status` 應回報 `No deployment record yet`。
2. 複製 `.env.research` 與 `backups/research` 到部署目錄，逐檔核對 SHA-256；祕密另存受保護的副本。
3. `research_lab.py adopt`：把目前運行的 image 另標為 `industryflow-research-api:pre-ledger`、`industryflow-research-web:pre-ledger`，寫入第一筆 `adopt` 紀錄（容器、image ID、遷移版本、Prefect 版本）。`adopt` 只在部署紀錄為空時執行，不建置也不替換任何東西。在 `adopt` 與第一次部署之間，例行操作以 `pre-ledger` image 執行。
4. 避開整點 :07，執行 `deploy --commit <merge 提交> --recreate-db`。db 容器從部署目錄重建，bind mount `docker/research-init.sql` 改指向部署目錄；tag 改變也讓所有 app 容器重建，所以有一次短暫的全面停機。
5. 改寫備份排程（[research-backup](research-backup.md)）並手動觸發一次，再把這份備份還原到演練環境核對。
6. 開發 checkout 放入 tombstone `.env.research`（見「部署目錄與防護」），移除原本的祕密與 `backups/research`。

### 回到 pre-ledger image

第 4 步失敗，或切換後發現新腳本有問題時，用切換前的程式與 image 重建原容器。本 change 沒有新的遷移，資料庫不需要還原：

```powershell
cd C:\Users\User\openspec_pjt                         # 開發 checkout，先移除 tombstone、放回原本的 .env.research
git checkout --detach <切換前運行的提交>                 # 切換前的程式與 compose 檔（:dev、有 build:）
docker tag industryflow-research-api:pre-ledger industryflow-research-api:dev
docker tag industryflow-research-web:pre-ledger industryflow-research-web:dev
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml up -d --no-build --no-deps --force-recreate db api web
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml --profile scheduler up -d --no-build --no-deps prefect worker
```

`--no-build` 讓舊 compose 不從 working tree 重建，`--no-deps` 讓它不重跑 initialize。完成後在 `docs/research-acceptance.md` 記錄經過；部署目錄的紀錄保留，供下次切換參考。

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

## 合併前演練

需要實機的合併前驗證，從 PR 的 worktree 在演練環境（project `industryflow-research-drill`，web 3016、API 8016）進行：不切換主 checkout，也不讓正式服務執行未合併的程式碼。演練與正式部署共用 `research_lab.py` 的建置、initialize、替換、smoke 與回退判斷，所以演練的結果代表正式部署的結果。演練祕密與還原細節見 [備份與還原](research-backup.md#還原演練)。

```powershell
cd <PR 的 worktree>
python scripts/research_drill.py down                                     # 清掉上一次演練
python scripts/research_drill.py restore --backup latest                   # 以備份的基準 image 還原正式資料
python scripts/research_drill.py deploy-rehearsal --commit <PR HEAD>
python scripts/research_drill.py rollback-rehearsal                        # 回到 restore 的基準 image
python scripts/research_drill.py pg-check --commit <PR HEAD> --suite all
python scripts/research_drill.py rebuild-check --commit <PR HEAD>          # PR 改了研究內容的編譯時
```

- **`deploy-rehearsal`**：與「部署」第 4–10 步相同的拒絕條件、建置、initialize、替換與 smoke（project 換成演練的，網址換成 8016／3016）。演練的目的就是部署尚未合併的提交，所以**不檢查**第一父鏈與部署目錄；收縮遷移要 `--allow-contract` 等拒絕條件照樣適用。報告 `.work/research-drill/deploy-rehearsal-<時間>.json` 列出每張變動表的列數與 md5 前後、遷移版本前後、`theme_assessment_versions` 的增減、提交與 `worktree_dirty`，以及 smoke 結果。
- **`rollback-rehearsal`**：以「回退」的規則回到 restore 的基準 image（或 `--commit` 指定的提交），不執行 initialize。報告判定 `expand-only`（列出中間的擴充遷移），或 `refused` 並列出原因；跨越收縮遷移時，訊息指向演練還原時用的那份備份。
- **`pg-check`、`rebuild-check`**：以該提交的 image 在演練的 `bootstrap` 服務執行。`industry_research_test` 建在演練的 DB cluster，`rebuild-check` 的資產只寫進演練的 volume，正式的 cluster 與 volume 都不碰。
- **`build --commit`**：只建 image，例如預先建好要演練回退的舊版本。
- **只有一個演練實例**：port 與 project 固定，一次只能演練一個 PR，`down` 會清掉上一個。報告存在各自 PR 的 worktree。
- **只有正式環境才有的行為**，例如排程在主機重開機後恢復，無法在 merge 前驗證。這類行為在 merge 後部署時核對，記錄在 [research-acceptance](research-acceptance.md)。

## 演練紀錄（2026-10-28，separate-research-production-deployment task 7）

從 PR #10 的 worktree 執行，沒有部署目錄標記，也沒有正式祕密。正式服務的指紋（容器 ID、image、狀態與啟動時間、DB 清單、`industry_research_test` 計數、volume、資產與 managed Git、`:dev` image）在每一步前後都相同。報告在該 worktree 的 `.work/research-drill/`。

| 步驟 | 結果 |
|---|---|
| 7.2 image | 基準 `7ebbc68e9a5b` 與 PR `fce6cbf10f14` 從 `git archive` 建置，labels 齊全，`industry-map` 的 Markdown 共 0 個 CR |
| 7.3 還原 | 備份 `20261027T193003Z`（manifest 沒有 `api_revision`）：不給 `--baseline-commit` 時先拒絕；以 `7ebbc68` 還原後全部核對相符，`/next` 200，RTO 52.7 秒（`restore-20261027T194619Z.json`） |
| 7.4 預演部署 | smoke 六項全過，遷移 `0017 → 0017`，`theme_assessment_versions` 7 → 7，61.0 秒。52 張表只有 `public.sources` 變動（7 列 `url`、83 列 `data.registry_url`），是 initialize 寫回 `sources.yaml` 形式的既有行為，下一次每小時更新會寫回。預期中的散文 CRLF → LF 沒有發生：`import_map` 以 `read_text()` 讀檔時已正規化換行，正式 DB 的散文本來就沒有 CR（`deploy-rehearsal-20261027T194912Z.json`） |
| 7.5 預演回退 | 回到 `7ebbc68`，沒有 initialize，smoke 六項全過，52 張表全部不變，判定 `expand-only`（`rollback-rehearsal-20261027T195309Z.json`） |
| 7.6 收縮遷移 | `6c0afd1^`（`5ceb9a62c4f7`，head `0016`）：回退被拒絕，訊息指出 `0017` 與回退邊界備份，演練容器不變（`rollback-rehearsal-20261027T195457Z.json`） |
| 7.7 `pg-check --suite all` | **待重跑**。第一次 157 passed、1 error：`scaled_tree` fixture 需要 image 內沒有的 `scripts/research_scale.py`（2026-10-24 起就存在），已修正；第二次因主機記憶體不足被中止 |
| 7.8 防護與遮蔽 | worktree 內 `deploy` 因沒有標記被拒絕、`setup` 因正式 volume 已存在被拒絕，狀態都沒變；故意失敗的演練步驟輸出中，連線字串的密碼為 `[REDACTED]`，演練祕密出現 0 次 |

**順帶發現（正式 Prefect，非本 change 造成）**：`research-publication-reconciliation/minute` 有一筆 flow run 自 2026-10-21 停在 PENDING／Submitting，這個 deployment 最後一次完成是 2026-10-22。`deploy` 原本把 PENDING 也算忙碌，會因此擋住所有部署；已改為只計 RUNNING 與 CANCELLING。那筆卡住的 run 要由 Boris 決定如何處理。
