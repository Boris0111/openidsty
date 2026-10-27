# Design

## Context

動機見 proposal.md 的 Why，requirements 見 `specs/platform-runtime/spec.md`。以下只列影響做法的現況。

- **compose project 名稱寫死**：`compose.research.yaml` 的 `name: industryflow-research` 讓 volume 以 project 命名，不以目錄命名。所以從任何目錄執行這份 compose，操作的都是同一組正式 volume 與容器。換目錄可以沿用同一份資料，但舊程式也能從任何 checkout 動到正式服務。
- **`research_lab.py` 以 `ROOT`（腳本所在 checkout）為根**：`.env.research`、`backups/research`、`.work/research-lab`、`public-snapshot/` 都相對於它。`check()` 在每個動作前執行，並可能經 `setup()` 追加祕密。
- **設定檢查寫死 `:dev`**：`validate_config()` 寫死 `industryflow-research-api:dev`／`web:dev`（`scripts/research_lab.py:81`、`:92`、`:95`）。唯一允許的 bind mount 是 db 的 `./docker/research-init.sql`，它的路徑解析到 compose 檔所在的 checkout。
- **`initialize` 會寫正式資料**：鏈為 `alembic upgrade head && research_roles && import_map && financial_indicators && source_links`。`import_map` 以 image 內建的 `industry-map/`、`data/` 覆寫 legacy `public.*` 資料表；內容有變時會追加 `theme_assessment_versions`，缺 `change_reason` 時 raise。API 以 `depends_on: initialize: service_completed_successfully` 等它完成。
- **遷移**：`0001`–`0017` 線性。只有 `0001`、`0006`、`0016` 有可用的 downgrade。`0009`（`DROP POLICY` 後重建）與 `0017`（刪 7 張表、view、function）是破壞性的。`env.py` 不處理未知 revision。
- **演練環境（`industryflow-research-drill`）**：
  - 有自己的 volume、port（3016／8016）與祕密，可以 `restore --backup` 正式備份，但沒有 `initialize` 與排程。
  - image 與正式共用 `:dev`，從不建置。
  - `setup()` 從 `ROOT/.env.research` 複製 `SEC_USER_AGENT`，所以在 worktree 裡會失敗。
  - `run()` 只遮蔽正式祕密。
- **`pg-check`／`rebuild-check` 碰得到正式環境**：
  - `pg-check` 在正式 cluster 上建立並保留 `industry_research_test`，以 superuser 執行分支程式。
  - `rebuild-check` 的 DB 交易會回滾，但仍會把資產檔寫進正式的 `research-assets` volume（`research_compile.py:320-328`）。
- **術語已被佔用**：`release`、`restore` 已用於研究內容（`research.research_releases`、`refs/research/releases/*`、`/api/admin/releases/{id}/restore`）。本設計一律用「部署（deployment）」與「image 版本」。
- **既有的 `up` 不換排程服務**：只重建 api、web，所以 prefect、worker 會停在舊 image（`docs/research-acceptance.md` 第十、十二節）。
- **Windows 換行轉換**：系統 `core.autocrlf=true`。從 working tree 建置的 image 帶 CRLF，與 git 內容不同。

## Goals / Non-Goals

**Goals:**
- 部署、回退與演練共用同一套建置、初始化與 smoke 程序，演練的結果能代表正式部署的結果。
- 所有防護都以「拒絕並說明」為預設，不在缺少資訊時猜測或自動修復。
- 維運腳本仍只用 Python 標準函式庫（加上既有的 PyYAML 測試依賴），不新增套件。
- 舊格式的部署紀錄與備份 manifest 只增加欄位，讓回退後的舊腳本仍讀得懂。

**Non-Goals:**
- 不做 image registry 或多主機部署；image 只存在本機 Docker。
- 不重做 alembic 遷移，也不提供 downgrade；回退只靠相容性與備份。
- 不處理原服務（project `industryflow`）的 compose 與 image。
- 不改動研究內容的發布與還原流程。

## Decisions

### D1：部署目錄是獨立 clone，固定在已部署的提交

- `C:\Users\User\industryflow-prod` 是 GitHub origin 的獨立 `git clone`，平時 detached 在部署紀錄中運行的提交。
- 目錄內放：
  - 正式祕密 `.env.research`、備份 `backups/research`、`.work/research-lab`、公開快照輸出 `public-snapshot/`。
  - `deployments/`：`home.json` 是部署目錄標記，內容為絕對路徑與建立時間；`ledger.jsonl` 是部署紀錄；`.lock`。
  - 自己的 `.venv`。
- `.gitignore` 加入 `/deployments/`；其餘路徑已被忽略。
- **不選 git worktree**：worktree 的管理資料在開發 repo 的 `.git/worktrees`。Claude Code 與 `git worktree prune` 會在那裡清理，重新 clone 開發目錄也會讓正式環境失去 git。
- **不選「留在開發 checkout，只加 SHA tag」**：腳本、compose 檔、備份排程仍會跟著當下 branch 走，Why 的第 1、5 點不會解決。

### D2：正式操作的防護

- 會改變正式服務的動作（`deploy`、`rollback`、`scheduler-start`、`start`、`stop`、`seed-git`、`bootstrap`、`restore`、`backup`、`public-snapshot`），在取得 lock 後檢查四項，任一不符就拒絕並列出原因：
  1. `deployments/home.json` 存在，且路徑等於 `ROOT`。
  2. `git status --porcelain` 為空：不允許未提交修改，也不允許未追蹤檔案；被忽略的檔案不算。
  3. HEAD 等於部署紀錄中運行的提交（`deploy` 的過渡期例外，見 D6）。
  4. 每個運行容器的 `org.opencontainers.image.revision` 都等於部署紀錄。
- `status`、`check` 是唯讀動作，只回報不符之處，不拒絕。
- `check()` 不再呼叫 `setup()`。`setup()` 在 volume `industryflow-research_pg-data` 已存在時拒絕產生祕密，並提示從部署目錄執行。
- **不選環境變數開關**：任何開發 shell 都能設定它，等於沒有防護。

### D3：只從 `git archive` 建置，以提交標記

- 建置步驟：
  1. 以 `git -c core.autocrlf=false archive --format=tar <sha>` 產生建置內容。
  2. 由 Python 以 binary pipe 傳給 `docker build -f backend/Dockerfile -`；web 同樣用 `frontend/Dockerfile`。
  3. `.dockerignore` 對 tar context 仍然生效。
- tag：`industryflow-research-api:<sha12>`、`industryflow-research-web:<sha12>`。
- labels：
  - `org.opencontainers.image.revision`（完整 SHA）、`org.opencontainers.image.created`
  - `io.industryflow.alembic-head`、`io.industryflow.contract-revisions`（由 D8 計算）
  - `io.industryflow.prefect-version`（取自 `backend/runtime-constraints.txt`）
  - `io.industryflow.build=git-archive`
- 同名 tag 已存在且 labels 相符時直接重用；label 不符時拒絕，不覆蓋。所以演練建置不會移動正式在用的 tag。
- Dockerfile 不變，label 以 `--label` 注入。
- **不選從 checkout 建置**：會帶入 CRLF 與未追蹤檔案。
- **不選 BuildKit 的 git URL context**：私有 repo 需要在 build 時處理認證。
- **不經過 PowerShell 管線傳 tar**：PowerShell 5.1 會改寫二進位串流。

### D4：compose 檔不再建置，tag 由腳本注入

- `compose.research.yaml`、`compose.research-drill.yaml` 都移除 `build:`，改為 `image: industryflow-research-api:${RESEARCH_IMAGE_TAG:?use scripts/research_lab.py}`（web、reader 同樣處理）。
- `compose(*args, tag=...)`：先濾掉 host 的 `RESEARCH_*` 變數，再設定 `RESEARCH_IMAGE_TAG`。shell 環境的優先權高於 `--env-file`，所以任何檔案都無法覆寫 tag。
- `validate_config(config, tag)`：要求 tag 符合 `^[0-9a-f]{12}$`，且所有 app 服務、web、reader 的 image 一致。其餘既有檢查（DB URL、reader 權限、port、bind mount、volume、profile、重啟策略）不變。
- 例行操作（`backup`、`public-snapshot`、`start`）用部署紀錄中運行的 tag。
- **不選另一個狀態 env 檔**：又多一個可以手改、可能與實際不符的檔案。

### D5：部署紀錄是只追加的 JSON Lines

- 每筆紀錄的欄位：
  - `schema_version`、`seq`、`kind`（`deploy`／`rollback`／`adopt`）、`outcome`（`succeeded`／`failed`）、`error`
  - `commit`、`tag`、各 image ID、`rebuilt`（image 是否為重建）
  - `alembic_before`、`alembic_after`、image 的 alembic head、該提交的遷移鏈與收縮遷移清單、Prefect 版本
  - `backup`（備份資料夾名稱）、`contract_boundary`（布林）
  - `services`：每個服務的 image ID 與 revision
  - `smoke`：每項檢查的結果
  - `started_at`、`finished_at`
- 部署、回退、每日備份共用 `deployments/.lock`，同一時間只有一個寫入者。
- 每日備份 manifest 加入運行中 api 容器的 image ID、revision 與 `alembic_version`。目前記錄的是 `:dev` tag 的 ID，可能與實際運行的不同。
- **不選存在資料庫**：還原備份會連部署紀錄一起倒退，失去還原之後的歷史。

### D6：`deploy --commit <sha>` 的順序

1. 取得 lock，檢查部署目錄標記與乾淨的 working tree，並執行既有的原服務互斥檢查（`exclusion_conflicts`）。
2. `git fetch origin`，要求 `<sha>` 在 `git rev-list --first-parent origin/main` 中。main 用 merge commit，只檢查「可達」會放行 PR 內部從未成為 main 的中間提交。
3. **由目標版本的腳本接手**：在部署目錄 `git checkout --detach <sha>`，再以相同參數重新執行目標版本的 `research_lab.py`。之後的步驟、compose 設定與檢查規則都與 image 同一版本。
4. 拒絕條件：
   - 目前資料庫的 alembic 版本不在目標的遷移鏈上，代表撤回了已部署的遷移。
   - Prefect 有執行中的 flow，除非加 `--force`。
   - 目標相對目前資料庫新增了收縮遷移，卻沒有加 `--allow-contract`。
5. 執行部署前備份（含第二份副本）。有收縮遷移時，該備份標記為回退邊界。
6. 依 D3 建置或重用 image。
7. `compose run --rm --no-deps initialize`（新 tag）。舊的 api、web 仍在服務。
8. initialize 成功後才替換服務：
   - 一律替換 `api`、`web`：`up -d --no-deps --wait api web`。
   - 排程啟用時，依序替換 `prefect`，執行一次 `deploy` 註冊 deployments，再替換 `worker`。
   - reader 正在運行時一併替換。
   - db 不在例行部署中重建。
9. smoke 檢查：
   - `/api/health` 正常。
   - `/api/v2/manifest` 的 release 等於資料庫中目前的 release。
   - `/next` 回應 200。
   - 每個運行容器的 image ID 與 revision 符合目標。
   - `alembic_version` 等於 image 的 head。
   - 容器的 `com.docker.compose.project.working_dir` 等於部署目錄。
10. 寫入部署紀錄。
- **initialize 失敗時**：部署目錄 checkout 回原提交，寫入失敗紀錄；舊服務始終未被替換。
- **smoke 失敗時**：寫入失敗紀錄，印出 D7 可執行的 `rollback` 指令，或說明為何只能還原備份。不自動回退（Boris 的決定）。
- **不選沿用 `up` 加 `depends_on`**：Compose 可能在得知 initialize 失敗前就重建 api，`import_map` 一失敗網站就停擺。
- **不選維持「initialize 成功後才 checkout」**：那樣 initialize 會以舊版的 compose 設定執行新版 image。

### D7：`rollback --to <seq>` 不重跑初始化

- 目標必須是部署紀錄中 `outcome=succeeded` 的一筆。image 已被清除時依 D3 從 archive 重建，並在紀錄中標記 `rebuilt`；pip、npm 建置不是逐位元組可重現，所以要明示。
- 拒絕條件：
  - 目標的 alembic head 新於資料庫目前版本。
  - (目標 head, 資料庫版本] 區間內有收縮遷移。舊版提交看不到較新的遷移檔，所以用**部署紀錄中各次遷移鏈的聯集**判斷。
  - 目標與目前的 Prefect 版本不同：Prefect server 會遷移自己的 `prefect` 資料庫。
- 步驟：
  1. 部署前備份。
  2. checkout 目標提交。
  3. 以目標 tag 執行 `up -d --no-deps` 替換運行中的服務；排程啟用時重跑一次 Prefect `deploy` 註冊。
  4. smoke 檢查，寫入紀錄。
- **不執行 initialize**：避開「Can't locate revision」，也避免 `import_map` 以舊內容改寫 legacy 資料表、追加不實的判讀版本，或因缺 `change_reason` 而失敗。
- **不選 alembic downgrade**：多數遷移的 downgrade 刻意 raise。
- **不選讓 `env.py` 容忍未知 revision**：會在正向部署時掩蓋真正的不一致。

### D8：`scripts/migration_rules.py` 分類遷移

- 只用標準函式庫，CI lint、建置 label、回退判斷三處共用。
- 以 `ast` 解析每個遷移的 `revision`、`down_revision`，只看 `upgrade()` 的內容；並讀取它引用的 `sql/*.sql`，先去除註解。
- 標示為破壞性的語句：
  - SQL：`DROP {TABLE|VIEW|COLUMN|FUNCTION|TYPE|SCHEMA|POLICY|TRIGGER|CONSTRAINT|SEQUENCE}`、`RENAME`、`ALTER COLUMN … TYPE`、`SET NOT NULL`、`ADD COLUMN … NOT NULL` 且沒有 `DEFAULT`、`TRUNCATE`、`DELETE FROM`、`REVOKE`（以字詞邊界比對，`revoked_at` 不算）。
  - Alembic：`op.drop_*`、`op.rename_table`，以及 `alter_column` 帶 `type_=`、`nullable=False` 或 `new_column_name=`。
- 命中的遷移必須在模組層宣告其中一項：
  - `CONTRACT = '<原因>'`
  - `EXPAND_REVIEWED = '<前一版不受影響的理由>'`
- 同時檢查：遷移鏈線性、只有一個 head、4 位數 revision 等於檔名前綴。
- `0009`、`0017` 標為 `CONTRACT`，只加標記，不改 schema 行為。
- **限制**：新增 trigger、constraint、policy 這類語意上的破壞，lint 抓不到，要靠 D10 的預演回退。
- **不選 squawk 等外部工具**：看不到 `.sql` 檔與 `op.execute` 字串裡的 SQL，也會新增依賴。

### D9：expand／contract 規則

- 移除結構分兩步：
  1. 先部署「不再使用該結構」的版本（擴充）。
  2. 之後的部署才放入刪除它的收縮遷移。
- 收縮遷移的部署前備份就是回退邊界：要回到更早的版本，只能從那份備份還原到演練環境，核對後再依 `docs/research-backup.md` 的事故程序處理。
- 已合併的遷移檔不得刪除或改寫，撤回一律以新的遷移進行。
- 規則寫入 `docs/research-deployment.md`，並修正 `docs/research-lab.md:27` 等處「schema 都是 additive」的過時描述。

### D10：演練環境承接合併前驗證

- **tag**：`research_drill.py` 的 `compose()` 同樣注入 tag，來源是 `--commit`，或運行中演練 api 的 revision label。不另存狀態檔。
- **演練祕密**：移到 `INDUSTRYFLOW_DRILL_HOME`（預設 `%USERPROFILE%\industryflow-drill`）。`SEC_USER_AGENT` 改用 `--sec-user-agent` 傳入，或從部署目錄讀取一次。`research_scale.py`、`research_draft_bench.py` 改用 `research_drill.ENV_FILE`。
- **遮蔽**：`run()` 接受額外的遮蔽來源，錯誤輸出同時遮蔽正式與演練祕密。
- **新增或調整的指令**：
  - `restore --backup latest|<path>`：使用備份 manifest 記錄的**基準 image**（依它的 revision 建置或重用），所以 PR 的新遷移不會讓還原失敗。
  - `deploy-rehearsal --commit <sha>`：與 D6 相同的建置、initialize、替換與 smoke。報告列出每張表的列數與 md5 差異、遷移版本前後，以及 `theme_assessment_versions` 是否增加。
    - 演練的目的就是部署尚未合併的提交，所以**不檢查**主線第一父鏈與部署目錄（D2、D6 第 2 步）。
    - 收縮遷移、Prefect 忙碌等拒絕條件照樣適用。
    - 只操作 project `industryflow-research-drill`。
  - `rollback-rehearsal`：以 D7 的規則回到基準 image，報告相容性判斷與 smoke 結果。
  - `pg-check`、`rebuild-check`：從 `research_lab.py` 搬來，只連演練的 cluster 與 volume。
- **報告**：記錄 revision label 與執行時的 `worktree_dirty`。
- **`research_lab.py` 對應調整**：移除 `pg-check`、`rebuild-check`；`seed-git`、`bootstrap`、`restore` 不再建置，並受 D2 防護；`up` 改為提示使用 `deploy`。

### D11：備份排程與公開快照移到部署目錄

- **備份排程**「IndustryFlow Research Daily Backup」：
  - Python 改用部署目錄的 `.venv`；`research_lab.py` 只用標準函式庫，venv 只為隔離。
  - 腳本用絕對路徑，「開始位置」設為部署目錄。
  - 備份與部署共用 lock。
- **30 天清理**跳過標記為回退邊界的備份。
- **公開快照**：匯出、`npm ci`、`build:static`、一致性檢查與 wrangler 部署都在部署目錄進行，`--commit-hash` 用部署紀錄中運行的提交。

### D12：流程規則與本 change 的例外

- `AGENTS.md`「先驗證、再 merge」改寫為：
  - change 的 tasks（包含演練環境的實機驗證）全部勾完，並在 branch 上 archive 後，才交給 Boris merge。
  - 實機驗證從 PR 的 worktree 在演練環境進行，不切換主 checkout。
  - merge 後依 `docs/research-deployment.md` 部署，部署紀錄的 smoke 結果就是紀錄；只有正式環境才有的行為（例如重開機）在部署後核對，記錄在 `docs/research-acceptance.md`。
- **本 change 是例外**：它的首次部署就是正式環境切換，必須在 merge 之後才能進行。所以 tasks 分為 merge 前（1–7）與 merge 後切換（8）。切換完成後，以後續的 docs PR 記錄並 archive。

## Risks / Trade-offs

- **[風險] 舊程式仍可從任何 checkout 動到正式服務**：project 名稱固定，舊 branch 的 `research_lab.py up`（有 `build:`、`:dev`、會產生新祕密的 `setup`）會重建正式容器。祕密移出開發 checkout 後，這會變成密碼不符的停機。
  → 開發 checkout 留下一個值不合格式的 tombstone `.env.research`，讓舊版 `setup()` 直接 raise「Invalid research environment」。舊 branch 由 Boris 刪除。
- **[風險] db 的 bind mount 指向開發 checkout**（`./docker/research-init.sql`）。
  → 切換時從部署目錄重建 db。tag 改變也會重建所有 app 容器，所以安排一次短暫全面停機，避開每小時 :07 的資料更新。例行部署不碰 db。
- **[風險] CRLF 改為 LF**：第一個從 archive 建置的 image，會讓 `import_map` 把 legacy `segments`／`themes` 散文改寫成 LF。
  → 演練的 `deploy-rehearsal` 必須確認變動只在預期的表，且 `theme_assessment_versions` 不增加；若會增加，先在本 change 內處理比較方式，再進行切換。
- **[風險] 回退後 legacy 地圖表保留較新內容**：只差擴充遷移時可以接受，但回退期間產出的公開快照會混用新地圖資料與舊程式。
  → `docs/research-deployment.md` 註明回退期間不產出公開快照。
- **[風險] image 清理刪掉回退目標**：Docker Desktop「Clean up」或 `docker image prune -a` 會刪掉它們。
  → D7 從 archive 重建並標記 `rebuilt`；文件列出保留最近幾版的建議。
- **[取捨] 演練環境只有一個實例**：port 與 project 固定，一次只能演練一個 PR，`down` 會清掉上一個。
  → 演練報告存在各自 PR 的 worktree；流程上一次只演練一個 PR。
- **[取捨] 正式環境才有的行為無法在 merge 前驗證**，例如排程重開機、Prefect 與 worker 在主機重啟後恢復。
  → 這類行為在 merge 後部署時核對並記錄，tasks 不以它阻擋 merge。
- **[風險] 部署紀錄與 manifest 格式演進**：回退會 checkout 舊腳本。
  → 欄位只增不改，`schema_version` 遞增時舊腳本忽略未知欄位。
- **[風險] Windows 環境**：二進位 tar 經 PowerShell 會損壞；工作排程的「開始位置」加引號會失效；部署目錄路徑太長時，`node_modules` 可能超過路徑長度限制。
  → 只用 Python 處理 pipe，排程用未加引號的短路徑。
- **[取捨] lint 只看語法**：語意上的破壞（新 trigger、constraint、policy）抓不到。
  → 由演練的預演回退補足，失敗時把遷移改標為收縮。

## Migration Plan

正式環境切換在 merge 後進行，需要 Boris 同意並在場。

1. **準備部署目錄**：`git clone` origin 到 `C:\Users\User\industryflow-prod`，`git checkout --detach <merge 提交>`，建立 `.venv`，寫入 `deployments/home.json`。
2. **搬移祕密與備份**：
   - 複製 `.env.research` 與 `backups/research`，逐檔核對 SHA-256。
   - 祕密另存一份受保護的副本（密碼管理器或加密隨身碟）。
3. **保留回復點**：把目前運行的 `:dev` image 另標為 `pre-ledger-api`／`pre-ledger-web`，並寫入一筆 `adopt` 紀錄，記錄目前容器、image ID 與 alembic 版本。
4. **首次部署**：避開整點，執行 `deploy --commit <merge 提交>`，從部署目錄重建包含 db 在內的所有容器。確認：
   - bind mount 與 `working_dir` label 都指向部署目錄。
   - smoke 通過，部署紀錄 `outcome=succeeded`。
5. **改寫備份排程**並手動觸發一次，核對 `backup-log.jsonl` 與 D: 的第二份副本。
6. **驗證新備份**：把這份新備份還原到演練環境，確認新部署目錄產生的備份可用。
7. **封住開發 checkout**：放入 tombstone `.env.research`，移除原本的祕密與備份。確認在開發 checkout 執行 `check` 會拒絕，且不產生祕密。
8. **收尾**：Boris 刪除本機舊 branch；以後續 docs PR 在 `docs/research-acceptance.md` 記錄切換，並 archive 本 change。

**切換失敗的回復**：

- **第 4 步失敗**：先在開發 checkout 移除 tombstone，放回原本的 `.env.research`，再以 `pre-ledger-*` image 重建原容器。本 change 沒有遷移，資料庫不需要還原。
- **切換後發現問題**：依 D7 回退；若問題出在新腳本，同樣用 `pre-ledger-*` image 回到切換前的狀態，並在部署紀錄寫入說明。

## Open Questions

- 本機 Docker 要保留最近幾版正式 image：先建議保留部署紀錄中最近 5 次成功部署，實際數量看磁碟用量再定。不影響 specs 或 tasks。
- 回退邊界備份要保存多久：先定為不自動刪除，由 Boris 手動清理。之後若改為固定期限，只改文件與清理條件。
