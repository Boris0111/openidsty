# 研究服務的啟動與維運

2026-10-21 起這是正式研究服務，在主專案 `C:\Users\User\openspec_pjt` 根目錄執行，不再使用 worktree。Python 可使用已安裝相同鎖定依賴的環境。此獨立 Compose 不讀原 `.env`，也不啟動原 project；`up` 預設不啟動 Prefect 或抓取 worker。

研究服務與原服務（project `industryflow`）共用 3010／8010／4201，兩者不可同時運行。`up`／`start` 偵測到原服務有容器在運行，或 port 被其他程式占用時，會拒絕並列出占用者，但不會自動停止任何服務。`stop` 會一併停止 reader、scheduler、web 與 API，釋放全部共用 port。

```powershell
python scripts/research_lab.py setup
python scripts/research_lab.py check
# 首次還原：只讀既有 reading DB，寫入新版獨立 DB；非空目標拒絕覆寫。
python scripts/research_lab.py restore
python scripts/research_lab.py up
python scripts/research_lab.py stop
python scripts/research_lab.py start
python scripts/research_lab.py pg-check
python scripts/research_lab.py rebuild-check
# 首份實際研究流程備妥並提交後，才建立 application DB 的第一份研究 release。
python scripts/research_lab.py bootstrap --commit <完整commit>
```

網站為 http://127.0.0.1:3010，API 為 http://127.0.0.1:8010，Prefect 為 4201（2026-10-21 切換前的預覽使用 3014／8014／4204）。`setup` 產生隨機且互不相同的 DB／session 祕密於被 Git 及 Docker build 忽略的 `.env.research`，不複製正式憑證。`check` 只顯示安全摘要，不輸出 Compose 內含憑證的完整 JSON。

所有 app 服務使用 `industryflow-research-api:dev`，web 使用 `industryflow-research-web:dev`；DB volume 與 network 由 `industryflow-research` 命名。沒有固定 container_name、host network、external volume、Docker socket 或可寫的原專案 bind mount。啟動前檢查 ports；停止不刪除 volumes。

`restore` 使用原始 binary stream 保存 pg_dump，避免 PowerShell 轉碼。來源預設 `industryflow-reading-db`／`industry_reading`；目標固定為新版 `industry_research`，拒絕非空目標。報告在 `.work/research-lab/restore.json`，逐表比對筆數與內容 hash，並比對原服務 container ID、image、啟動時間、restart、mount、port 未改變；報告不含憑證。

初始化執行 additive migrations、佈建 reader／writer login 及既有研究匯入。`setup` 為四個不同用途產生獨立隨機祕密，舊設定只補缺少的新 key、不改已存在的值。API 的 legacy pool 與新版 reader pool 使用 reader login；管理另用明列 writer pool，背景寫入使用 writer，僅 initializer 持有 bootstrap 權限。Owner 設定與 session 操作見 [research-owner](research-owner.md)，草稿／發布見 [research-drafts](research-drafts.md)、[research-publication](research-publication.md)，可選的唯讀入口見 [research-reader-entry](research-reader-entry.md)。不要手動對研究服務使用原 compose.yaml。

`pg-check` 僅在新版 DB server 建立／遷移 `industry_research_test`，使用真實 reader／writer 連線執行 PostgreSQL 契約；合成 fixtures 不進 `industry_research`。參見 [研究資料模型與遷移](research-data-model.md)。

`pg-check` 在整輪遷移／測試期間持有獨立 advisory lock，避免不同測試程序共用 head／owner 而互相干擾。預設執行全部；診斷時可使用 `--suite admin-read`、`--suite publication-restart` 或 `--suite publication-interfaces` 執行特定流程，結果不能冒充完整回歸。這些 lock 與測試資料均不更改 application head。

財務測試另有 `--suite financial-core`（含台灣實際樣本）、`--suite financial-sec`（SEC 官方／合成與跨程序限流）、`--suite financial-imports`（財務計算／storage／台美來源與 owner 補錄）。來源設定及官方核對見 [SEC adapter](research-financial-sec.md)，補錄操作見 [financial imports](research-financial-imports.md)。

## 排程與重開機

排程（Prefect、deployments、worker）在 `scheduler` profile，要明確啟用：

```powershell
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml --profile scheduler up -d
```

`db`、`api`、`web`、`prefect`、`worker` 都是 `restart: unless-stopped`：Docker 或主機重開機後會自動回到運行狀態，不必再執行上面的指令。`deploy` 是一次性服務，不會重跑；deployments 與排程存在 Prefect 的資料庫，重啟後仍在。`research_lab.py check` 會拒絕缺少此設定的排程服務。重啟策略在建立容器時生效，修改 compose 後要以上面的指令重建容器。

重開機後確認排程已恢復：

```powershell
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml --profile scheduler ps
```

`prefect` 與 `worker` 應為 running，`deploy` 為 exited (0)。接著在 Prefect（http://127.0.0.1:4201）看到下一個整點第 7 分鐘出現 `official-information/hourly` 的 flow run。Docker Desktop 依附使用者登入，所以「重開機後自動恢復」實際上是「登入並啟動 Docker Desktop 後自動恢復」。

- **暫停排程**：重開機不會關掉排程，要明確執行 `python scripts/research_lab.py stop`（停止全部並釋放共用 port），或只停排程：把上面指令的 `up -d` 換成 `stop prefect worker`。被手動停止的容器重開機後維持停止。
- **原服務只能 stop，不要 up**：原服務（project `industryflow`）的容器同樣是 `unless-stopped`。它們目前是被停止的狀態，所以重開機不會回來；但若對原服務重新 `up`，之後每次重開機它都會與研究服務搶 3010／8010／4201，而且開機時由 Docker 直接啟動、不經過 `up` 的互斥檢查。

來源排程／單次更新可用 `--suite source-updates` 驗證持久重試、來源隔離與重啟，操作及限制見 [source updates](research-source-updates.md)。僅啟動 web／API 不會開始自動擷取。

讀者財務／事件／觀察／比較可用 `--suite research-dynamic`；契約與可比較界線見 [dynamic API](research-dynamic-api.md)。

每日備份、第二份副本與獨立還原演練見 [備份與還原](research-backup.md)；`backup` 動作與 `scripts/research_drill.py` 只操作研究預覽與演練 project。

首條實際讀取預覽位於 `/next`，首份 release 已建立，不要為了重建 UI 再初始化或刪除 DB。瀏覽器走讀命令（在 frontend 執行）：

```powershell
$env:PLAYWRIGHT_CHROME='1'
$env:RESEARCH_E2E='1'
$env:E2E_BASE_URL='http://127.0.0.1:3010'
npx playwright test tests/research-service.spec.ts
```
