# 新研究服務的隔離預覽

在新版 worktree 根目錄執行，Python 可使用已安裝相同鎖定依賴的環境。此獨立 Compose 不讀原 `.env`，也不啟動原 project；預設不啟動 Prefect 或抓取 worker。

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

預覽為 http://127.0.0.1:3014，API 為 http://127.0.0.1:8014；Prefect 預留 4204。`setup` 產生隨機且互不相同的 DB／session 祕密於被 Git 及 Docker build 忽略的 `.env.research`，不複製正式憑證。`check` 只顯示安全摘要，不輸出 Compose 內含憑證的完整 JSON。

所有 app 服務使用 `industryflow-research-api:dev`，web 使用 `industryflow-research-web:dev`；DB volume 與 network 由 `industryflow-research` 命名。沒有固定 container_name、host network、external volume、Docker socket 或可寫的原專案 bind mount。啟動前檢查 ports；停止不刪除 volumes。

`restore` 使用原始 binary stream 保存 pg_dump，避免 PowerShell 轉碼。來源預設 `industryflow-reading-db`／`industry_reading`；目標固定為新版 `industry_research`，拒絕非空目標。報告在 `.work/research-lab/restore.json`，逐表比對筆數與內容 hash，並比對原服務 container ID、image、啟動時間、restart、mount、port 未改變；報告不含憑證。

初始化執行 additive migrations、佈建 reader／writer login 及既有研究匯入。`setup` 為四個不同用途產生獨立隨機祕密，舊設定只補缺少的新 key、不改已存在的值。API 的 legacy pool 與新版 reader pool 使用 reader login；管理另用明列 writer pool，背景寫入使用 writer，僅 initializer 持有 bootstrap 權限。Owner 設定與 session 操作見 [research-owner](research-owner.md)，草稿／發布見 [research-drafts](research-drafts.md)、[research-publication](research-publication.md)，可選的唯讀入口見 [research-reader-entry](research-reader-entry.md)。不要手動對此預覽使用原 compose.yaml，也不要提前啟用 scheduler profile。

`pg-check` 僅在新版 DB server 建立／遷移 `industry_research_test`，使用真實 reader／writer 連線執行 PostgreSQL 契約；合成 fixtures 不進 `industry_research`。參見 [研究資料模型與遷移](research-data-model.md)。

`pg-check` 在整輪遷移／測試期間持有獨立 advisory lock，避免不同測試程序共用 head／owner 而互相干擾。預設執行全部；診斷時可使用 `--suite admin-read`、`--suite publication-restart` 或 `--suite publication-interfaces` 執行特定流程，結果不能冒充完整回歸。這些 lock 與測試資料均不更改 application head。

財務測試另有 `--suite financial-core`（含台灣實際樣本）、`--suite financial-sec`（SEC 官方／合成與跨程序限流）、`--suite financial-imports`（財務計算／storage／台美來源與 owner 補錄）。來源設定及官方核對見 [SEC adapter](research-financial-sec.md)，補錄操作見 [financial imports](research-financial-imports.md)。

來源排程／單次更新可用 `--suite source-updates` 驗證持久重試、來源隔離與重啟，操作及限制見 [source updates](research-source-updates.md)。僅啟動 web／API 不會開始自動擷取。

首條實際讀取預覽位於 `/next`，首份 release 已建立，不要為了重建 UI 再初始化或刪除 DB。瀏覽器走讀命令（在 frontend 執行）：

```powershell
$env:PLAYWRIGHT_CHROME='1'
$env:RESEARCH_E2E='1'
$env:E2E_BASE_URL='http://127.0.0.1:3014'
npx playwright test tests/research-service.spec.ts
```
