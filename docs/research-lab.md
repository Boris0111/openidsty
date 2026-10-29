# 研究服務的啟動與維運

2026-10-21 起這是正式研究服務。正式環境切換後，所有會改變正式服務的指令都在部署目錄 `C:\Users\User\industryflow-prod` 以它自己的 `.venv` 執行；開發 checkout 不保有 `.env.research`，從那裡執行會被拒絕。部署、回退、部署紀錄與防護見 [部署與回退](research-deployment.md)。此獨立 Compose 不讀原 `.env`，也不啟動原 project；`start` 不啟動 Prefect 或抓取 worker。

研究服務與原服務（project `industryflow`）共用 3010／8010／4201，兩者不可同時運行；原服務的 worker 同樣抓官方來源，同時運行會重複抓取。會啟動、替換或回退正式服務的 `deploy`、`rollback`、`start`、`scheduler-start`、`reader-start`，在改變任何狀態前偵測原服務有容器在運行，或 port（含 reader 的 3015）被其他程式占用時，會拒絕並列出占用者，但不會自動停止任何服務。`restore`（從原服務匯入）刻意不檢查：它的來源就是運行中的原服務資料庫，而且只啟動不對外發布 port 的 db。`stop` 會一併停止 reader、scheduler、web 與 API，釋放全部共用 port。

```powershell
cd C:\Users\User\industryflow-prod
.venv\Scripts\python.exe scripts\research_lab.py status            # 每個容器的提交、遷移版本與部署紀錄，列出不一致之處
.venv\Scripts\python.exe scripts\research_lab.py check             # 祕密格式與 Compose 規則；唯讀
.venv\Scripts\python.exe scripts\research_lab.py deploy --commit <main 上的提交>
.venv\Scripts\python.exe scripts\research_lab.py rollback --to <seq>
.venv\Scripts\python.exe scripts\research_lab.py stop
.venv\Scripts\python.exe scripts\research_lab.py start
.venv\Scripts\python.exe scripts\research_lab.py scheduler-start
# 首次還原：只讀既有 reading DB，寫入新版獨立 DB；非空目標拒絕覆寫。
.venv\Scripts\python.exe scripts\research_lab.py restore
# 首份實際研究流程備妥並提交後，才建立 application DB 的第一份研究 release。
.venv\Scripts\python.exe scripts\research_lab.py bootstrap --commit <完整commit>
```

`up` 已不再建置或替換服務，只會提示改用 `deploy`。分支程式的 PostgreSQL 契約檢查（`pg-check`）與研究重建檢查（`rebuild-check`）已移到演練環境（`scripts/research_drill.py`），見 [合併前演練](research-deployment.md#合併前演練)。

網站為 http://127.0.0.1:3010，API 為 http://127.0.0.1:8010，Prefect 為 4201（2026-10-21 切換前的預覽使用 3014／8014／4204）。`.env.research` 存放隨機且互不相同的 DB／session 祕密，被 Git 及 Docker build 忽略，不複製正式憑證。`setup` 只在正式 DB volume 不存在時產生祕密；volume 已存在時拒絕，因為新祕密會和既有資料庫不符。`check` 只顯示安全摘要，不輸出 Compose 內含憑證的完整 JSON，也不產生或補寫祕密。

所有 app 服務使用 `industryflow-research-api:<sha12>`，web 使用 `industryflow-research-web:<sha12>`：tag 是部署紀錄中運行的提交，由腳本注入，compose 檔本身不建置（[建置與 image 版本](research-deployment.md#建置與-image-版本)）。DB volume 與 network 由 `industryflow-research` 命名。沒有固定 container_name、host network、external volume、Docker socket 或可寫的原專案 bind mount。啟動前檢查 ports；停止不刪除 volumes。

`restore` 使用原始 binary stream 保存 pg_dump，避免 PowerShell 轉碼。來源預設 `industryflow-reading-db`／`industry_reading`；目標固定為新版 `industry_research`，拒絕非空目標。報告在 `.work/research-lab/restore.json`，逐表比對筆數與內容 hash，並比對原服務 container ID、image、啟動時間、restart、mount、port 未改變；報告不含憑證。

初始化執行資料庫遷移（擴充與收縮的規則見 [部署與回退](research-deployment.md#遷移擴充與收縮)）、佈建 reader／writer login 及既有研究匯入。`setup` 為四個不同用途產生獨立隨機祕密，舊設定只補缺少的新 key、不改已存在的值（正式 DB 已存在時同樣拒絕補寫）。API 的 legacy pool 與新版 reader pool 使用 reader login；管理另用明列 writer pool，背景寫入使用 writer，僅 initializer 持有 bootstrap 權限。Owner 設定與 session 操作見 [research-owner](research-owner.md)，草稿／發布見 [research-drafts](research-drafts.md)、[research-publication](research-publication.md)，可選的唯讀入口見 [research-reader-entry](research-reader-entry.md)。不要手動對研究服務使用原 compose.yaml。

`pg-check`（`research_drill.py pg-check --commit <sha>`）以該提交的 image，只在演練環境的 DB server 建立／遷移 `industry_research_test`，使用真實 reader／writer 連線執行 PostgreSQL 契約；合成 fixtures 不進任何 `industry_research`，也不碰正式的 DB cluster 與 volume。參見 [研究資料模型與遷移](research-data-model.md)。

`pg-check` 在整輪遷移／測試期間持有獨立 advisory lock，避免不同測試程序共用 head／owner 而互相干擾。預設執行全部；診斷時可使用 `--suite admin-read`、`--suite publication-restart` 或 `--suite publication-interfaces` 執行特定流程，結果不能冒充完整回歸。這些 lock 與測試資料均不更改 application head。

## 排程與重開機

排程（Prefect、deployments、worker）在 `scheduler` profile，要明確啟用：

```powershell
.venv\Scripts\python.exe scripts\research_lab.py scheduler-start
```

它先做原服務互斥檢查（原服務仍在運行或 4201 等共用 port 被占用時拒絕，什麼都不啟動），再依序啟動 `prefect`、執行一次 `deploy` 註冊 deployments、再啟動 `worker`，都使用部署紀錄中運行的 image。之後的 `deploy` 與 `rollback` 會一併替換運行中的排程服務。

`db`、`api`、`web`、`prefect`、`worker` 都是 `restart: unless-stopped`：Docker 或主機重開機後會自動回到運行狀態，不必再執行上面的指令。`deploy` 是一次性服務，不會重跑；deployments 與排程存在 Prefect 的資料庫，重啟後仍在。`research_lab.py check` 會拒絕缺少此設定的排程服務。重啟策略在建立容器時生效，compose 檔的修改會在下一次 `deploy` 替換容器時套用。

重開機後確認排程已恢復：

```powershell
.venv\Scripts\python.exe scripts\research_lab.py status
docker ps -a --filter label=com.docker.compose.project=industryflow-research --format "table {{.Names}}\t{{.Status}}"
```

`status` 的 services 應有 `prefect` 與 `worker`，`problems` 為空；`docker ps` 中 `deploy` 為 Exited (0)。接著在 Prefect（http://127.0.0.1:4201）看到下一個整點第 7 分鐘出現 `official-information/hourly` 的 flow run。Docker Desktop 依附使用者登入，所以「重開機後自動恢復」實際上是「登入並啟動 Docker Desktop 後自動恢復」。

- **暫停排程**：重開機不會關掉排程，要明確執行 `research_lab.py stop`（停止全部並釋放共用 port），或只停排程：`docker stop industryflow-research-worker-1 industryflow-research-prefect-1`。被手動停止的容器重開機後維持停止；恢復時執行 `scheduler-start`。
- **原服務只能 stop，不要 up**：原服務（project `industryflow`）的容器同樣是 `unless-stopped`。它們目前是被停止的狀態，所以重開機不會回來；但若對原服務重新 `up`，之後每次重開機它都會與研究服務搶 3010／8010／4201，而且開機時由 Docker 直接啟動、不經過互斥檢查。

來源排程／單次更新可用 `--suite source-updates` 驗證持久重試、來源隔離與重啟，操作及限制見 [source updates](research-source-updates.md)。僅啟動 web／API 不會開始自動擷取。

讀者事件／觀察／公司比較可用 `--suite research-dynamic`；契約見 [dynamic API](research-dynamic-api.md)。

每日備份、第二份副本與獨立還原演練見 [備份與還原](research-backup.md)；`backup` 只在部署目錄執行，`scripts/research_drill.py` 只操作演練 project。

首條實際讀取預覽位於 `/next`，首份 release 已建立，不要為了重建 UI 再初始化或刪除 DB。瀏覽器走讀命令（在 frontend 執行）：

```powershell
$env:PLAYWRIGHT_CHROME='1'
$env:RESEARCH_E2E='1'
$env:E2E_BASE_URL='http://127.0.0.1:3010'
npx playwright test tests/research-service.spec.ts
```
