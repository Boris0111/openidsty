# openidsty｜IndustryFlow 半導體與 AI 產業情報地圖

以產業探索為入口：選產業 → 理解環節 → 查看題材與近期事件 → 追溯來源。完整研究、監測訊號與風險直接呈現，公司提供定位與相關資訊。研究服務只在本機 loopback（127.0.0.1）提供；對外只公開不含伺服器的研究結構靜態快照（見 [公開研究快照](docs/public-snapshot.md)），不含事件與指標，不需帳號；股價、行情估值與 AI 摘要不在範圍內。

產業結構以 `industry-map/` Markdown 為唯一來源；FastAPI 將環節與題材全文匯入 PostgreSQL，另外保存媒體事件、官方背景統計與題材代理指標所需的公司營收（公司財報已移除）。Next.js／Cytoscape.js 提供介面；啟用 scheduler profile 後，Prefect 每小時更新免費公開來源，並在 Docker 重啟後自動恢復（見 [research-lab](docs/research-lab.md)）；版本化規則產生內容分類證據。Redis 與 Neo4j 尚未引入。

## 正式研究服務（2026-10-21 起）

2026-10-21 起，`http://127.0.0.1:3010` 由新版研究服務（Compose project `industryflow-research`，`compose.research.yaml`）提供；API 為 8010，Prefect 為 4201，唯讀入口為 3015。

正式服務只執行 `main` 第一父鏈上的提交：image 從 `git archive` 建置並以提交標記，所有會改變正式服務的操作都在獨立的部署目錄 `C:\Users\User\industryflow-prod` 執行，每次部署與回退都先備份並寫入部署紀錄。部署、回退與防護見 [research-deployment](docs/research-deployment.md)，啟停、排程與檢查見 [research-lab](docs/research-lab.md)，備份見 [research-backup](docs/research-backup.md)，切換紀錄見 [research-acceptance](docs/research-acceptance.md)。

```powershell
cd C:\Users\User\industryflow-prod
.venv\Scripts\python.exe scripts\research_lab.py status                  # 運行版本、部署紀錄與不一致之處
.venv\Scripts\python.exe scripts\research_lab.py deploy --commit <sha>   # 原服務仍在運行或 port 被占用時會拒絕
.venv\Scripts\python.exe scripts\research_lab.py rollback --to <seq>
.venv\Scripts\python.exe scripts\research_lab.py stop
```

merge 前需要實機的驗證，從 PR 的 worktree 在演練環境進行（`scripts/research_drill.py`），不碰正式服務，見 [合併前演練](docs/research-deployment.md#合併前演練)。

下方「快速啟動」以後各節說明的是**原服務**（project `industryflow`，`compose.yaml`），現在只用於回復，**不可與研究服務同時啟動**，因為兩者使用同一組 port。回復步驟：

```powershell
cd C:\Users\User\industryflow-prod
.venv\Scripts\python.exe scripts\research_lab.py stop    # 只停止，研究服務的 volumes 保留
cd C:\Users\User\openspec_pjt
docker compose up -d                                     # 以原 image 與原資料回到 3010
```

## 快速啟動（Windows PowerShell，原服務）

需要 Docker Desktop（Linux containers）。第一次建置需要網路與數分鐘。以下命令只使用本專案 `industryflow` 的容器與 volumes，不會停止其他專案。

```powershell
cd C:\Users\User\openspec_pjt
.\scripts\setup-env.ps1
docker compose up -d --build
# 第一次立即取得資料；排程另於每小時第 7 分鐘執行
docker compose run --rm ingestion python -m app.ingest
```

| 入口 | 網址 |
|---|---|
| 網站 | http://localhost:3010 |
| API／Swagger | http://localhost:8010/api/docs |
| API health | http://localhost:8010/api/health |
| Prefect 管理介面（限本機） | http://localhost:4201 |

首次啟動會建立 app 與 Prefect 各自的 database、執行 Alembic、驗證並匯入地圖、註冊來源及 hourly deployment。PostgreSQL 不發布外部 port；`.env` 含隨機密碼且已忽略，不要提交。設定 SEC 前，在 `.env` 的 `SEC_USER_AGENT` 填「專案名稱＋維護者實際 email」，再 `docker compose up -d --force-recreate worker`。空值會顯示「待設定」；台灣與 IR 來源仍照常執行。

Linux 自架可複製 `.env.example` 成 `.env`，將 POSTGRES_PASSWORD 改成隨機十六進位密碼；其餘 Compose 命令相同。

```powershell
docker compose ps
docker compose logs --tail 80 api worker prefect
docker compose logs --tail 80 initialize deploy
# 停止，保留資料
docker compose down
# 再次啟動
docker compose up -d
```

`down` 不加 `-v`；刪除 volume 會刪除資料。其他專案已使用 3000／8000，本專案採 3010／8010。變更 port 可編輯 `.env`；網站 proxy 使用內部服務名稱，不依賴外部 port。

## 操作流程

桌機採完整產業圖與展開的研究側欄；手機預設環節清單與選中環節關係圖，可開啟全螢幕完整圖。選取寫入 URL，支援返回與分享；搜尋環節／題材／公司支援鍵盤。跨產業節點可展開，圖保留方向與真實回路。

題材頁提供研究全文、證據、查核日期與預期里程碑；已發布事件另列。公司頁保留名稱、代號、跨環節角色與相關事件，舊 `/compare` 導回產業探索並說明入口調整。企業關係資料保留；公司財報（含財務比較）已由 change `remove-company-financials` 以 migration `0017` 移除，公司比較改為只並列研究內容（`/next?view=compare`）。

「近期事件」優先呈現產業變化，可依產業／環節／題材／發布日期篩選，另行開啟例行財報／營收公告。事件詳情附分類命中詞、摘錄、規則版本與來源；影響推導以直接分類起算並標 inference。發布日未知保留缺口，出表日、活動日與取得時間分開。

「資料覆蓋」逐環節與題材列研究、設定來源、近 30／90 日直接事件及真實樣本，可下載矩陣。來源頁將註冊資訊、網頁可讀性與實際擷取狀態分開；成功擷取不表示已完整回補 90 日。最近驗收快照見 [近 90 日矩陣](docs/coverage-90d.md)，操作與限制見 [來源文件](docs/sources.md)。

## 前後端開發

最直接的方式是開啟容器 hot reload，修改 `frontend/` 或 `backend/app/` 即更新。

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up -d --build
```

回到 production build：

```powershell
docker compose up -d --build --force-recreate api web worker
```

若前端要在本機跑 Node.js 24（API 與 DB 保留 Docker）：

```powershell
docker compose up -d api prefect worker
docker compose stop web
cd frontend
npm.cmd ci
npm.cmd run dev
```

前端仍在 http://localhost:3010。`.Codex/launch.json` 提供前端與 Docker API 開發設定；前端 API_ORIGIN 預設 http://127.0.0.1:8010，可由環境變數改寫。瀏覽器僅使用同網域 `/api/`，不需要把 DB 或 SEC 直接公開。

Python 3.12 離線測試環境：

```powershell
cd C:\Users\User\openspec_pjt
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
$env:PYTHONUTF8 = '1'
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
```

後端 runtime 使用 PostgreSQL；SQLite 僅為 unit tests。API 容器的 reload 不會創建排程，排程僅在獨立 worker 執行。變更 flows 後重建 worker／deploy。

## 地圖與企業關係維護

改地圖前先讀 [唯一 Schema](industry-map/README.md)。修改後執行驗證；錯誤地圖不會覆蓋既有投影。

```powershell
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe scripts/validate_map.py
# 只撰寫 frontmatter 時；交付仍須全量通過
.\.venv\Scripts\python.exe scripts/validate_map.py --skip-prose
# 改驗證器時
.\.venv\Scripts\python.exe tests/run_validator_tests.py
# 將修改的地圖／公司研究檔匯入（也適用 production）
docker compose build api
docker compose run --rm initialize
# 更新使用新 image 的 API／worker
docker compose up -d api worker
```

公司 aliases、CIK、關係在 `data/company-research.yaml`；維護規則見 [company-research](docs/company-research.md)。業務關聯程度、證據型態與審核狀態分開，不以市值／tier 代替。結構有回路；影響遍歷包含上下游、題材及共同下游手足，皆標為 inference。

## 驗證

```powershell
# 網站必須已啟動
cd frontend
npm.cmd run typecheck
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
# 容器內也可驗證後端
docker compose exec -T api python -m pytest tests -q
# 至少一次 Prefect 更新完成後，驗證排程、PostgreSQL 與防重疊鎖
docker compose exec -T api python -m app.verify_runtime
```

測試 fixtures 只用於離線測試，不會被 runtime 載入。整合驗收記錄見 [verification](docs/verification.md)。

## 乾淨 checkout 與離線交付

`.github/workflows/verify.yml` 在 push／PR 使用 Python 3.12、Node.js 24 與鎖定依賴，檢查地圖、驗證器、後端離線測試、前端型別、node 單元測試、production build 與公開導覽，並以合成快照建置公開靜態版、逐頁瀏覽（`npm run build:static`、`npm run test:e2e:static`）。資料覆蓋頁必須存在於 Git；測試 `coverage` 產物只忽略根目錄及 frontend／backend／tests 的產物目錄，不能忽略 `frontend/app/coverage/`。

在新的 checkout（不複製 `.env`、`.next` 或未追蹤檔）執行下列流程；不需要啟動 Docker 或外部資料來源。套件與 Chromium 首次安裝需要網路，測試本身使用離線回應。

```powershell
# repo 根目錄；先依「Python 3.12 離線測試環境」安裝 backend/requirements.txt
$env:PYTHONUTF8 = '1'
git ls-files --error-unmatch frontend/app/coverage/page.tsx
.\.venv\Scripts\python.exe scripts/validate_map.py
.\.venv\Scripts\python.exe tests/run_validator_tests.py
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
cd ..\frontend
npm.cmd ci
npm.cmd run typecheck
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e:offline
```

離線 suite 使用獨立 config，啟動本次 build 於 `127.0.0.1:3011`，API_ORIGIN 指向不可用的本機位址；只在瀏覽器攔截必要 API。未知測試 API 會失敗，不借用現有 3010／8010 服務。回應檔僅位於 `frontend/tests/offline/`，正式 app／ingestion 不匯入，資料庫不載入。原 `npm.cmd run test:e2e` 仍只執行 live suite，需另行啟動真實服務；兩種驗證不可互相代替。P0 本機交付結果見 [本次驗收紀錄](docs/theme-assessments-verification.md)。

## 更新、備份與還原

```powershell
# 單次或單一來源更新
docker compose run --rm ingestion python -m app.ingest --source twse-revenue
# 強制嘗試公開歷史回補（逐來源記錄可取範圍與缺口）
docker compose run --rm ingestion python -m app.ingest --backfill-days 90
# 更新分類規則後重分類，不呼叫外部來源；initialize 也會執行
docker compose run --rm ingestion python -m app.ingest --reclassify
# 透過 Prefect worker 立即觸發整輪
docker compose exec -T worker prefect deployment run official-information/hourly
# 查來源健康
Invoke-RestMethod http://localhost:8010/api/sources
# 備份 app database（不含 Prefect 管理歷史）
.\scripts\backup.ps1
# 使用剛建立的 dump，在新的隔離 database 還原並核對筆數
.\scripts\restore-check.ps1 -BackupFile .\backups\industry-YYYYMMDD-HHMMSS.dump
```

備份腳本使用 pg_dump custom format，再由 docker cp 複製，避免 PowerShell 將二進位 dump 轉碼。還原腳本只建立 `industry_restore_<時間>`，不覆寫 app DB；確認後可用 `docker compose exec db dropdb -U industry <還原資料庫名>` 移除該驗證 DB。災難還原先停本專案 API／worker，保留現有 DB，將 dump 還原至新資料庫後，在 `.env` 設 `APP_DATABASE=industry_restore_<時間>`，再 `docker compose up -d`，讓 API／worker 使用新資料庫。不要用資料刪除取代備份。

## 自架公開部署

對外公開的只有研究結構的靜態快照：匯出、建置、比對與部署步驟見 [公開研究快照](docs/public-snapshot.md)。正式研究服務（`compose.research.yaml`）沒有公開 profile，只綁 127.0.0.1。本節以下是原服務（`compose.yaml`）的自架部署參考，目前未使用。

在有 Docker 的主機複製 repo 與安全保存的 `.env`，設定 PUBLIC_DOMAIN（自己的網域）及 ACME_EMAIL，讓 DNS 指向主機，開放 80／443；不要公開 5432、8010 或 4201。

```bash
docker compose --profile public up -d --build
```

Caddy 自動申請 TLS，僅代理網站及其唯讀 API。預設 localhost ports 仍供主機管理；Prefect UI 必須透過 SSH tunnel 或可信內網使用。若 80／443 已有 proxy，將其導至 web:3010 或 localhost:3010，不必啟動 Caddy。回滾可停止本專案 Compose 或回復前一版 image；地圖與 DB volumes 保留。

## 專案文件與 OpenSpec

| 路徑 | 用途 |
|---|---|
| `industry-map/` | 環節、題材、免費研究入口與唯一 Schema |
| `backend/` | API、migrations、connectors、Prefect flows 與 unit tests |
| `frontend/` | Next.js 與瀏覽器流程測試 |
| `data/` | 可審查的公司研究補充資料 |
| `docs/api.md`／`sources.md`／`frontend.md` | API 契約、來源設定與前端操作 |
| `compose.research.yaml` | 正式研究服務（web、API、Prefect、worker、唯讀入口）；不建置，image tag 由 `scripts/research_lab.py` 注入。操作見 [research-lab](docs/research-lab.md) |
| `compose.research-drill.yaml` | 演練環境：從正式備份還原、預演部署與回退、分支程式的 PostgreSQL 檢查 |
| `docs/research-deployment.md` | 正式服務的部署目錄與防護、image 版本、部署紀錄、部署與回退、遷移的擴充與收縮、合併前演練 |
| `compose.yaml`／`compose.dev.yaml` | 原服務的執行與 hot reload；原服務維持停止，不與研究服務同時運行 |

本 repo 已初始化 OpenSpec，無須再次 init。全域 CLI 是共用工具，規格在本 repo 的 `openspec/`；implementation 進度在各 change 的 tasks checkbox，不等於 planning artifacts 的完成數。

```powershell
openspec.cmd list
openspec.cmd status --change <name>
openspec.cmd instructions apply --change <name> --json
openspec.cmd validate <name> --type change --strict
```

新工作一律在此 repo；舊 `financeinfost` 只供參考。Codex 可用 `$openspec-propose`／`$openspec-apply-change`／`$openspec-archive-change`；歸檔須另行啟動。

題材判讀與指標：研究維護見 [theme-assessments](docs/theme-assessments.md)，指標／來源更新見 [theme-indicators](docs/theme-indicators.md) 與 [metric-source-operations](docs/metric-source-operations.md)。版本修改／還原見 [theme-version-operations](docs/theme-version-operations.md)，此裝置關注見 [theme-watchlist](docs/theme-watchlist.md)。七題材實測與缺口見 [交付矩陣](docs/theme-delivery-matrix.md)，驗收結果見 [驗證紀錄](docs/theme-assessments-verification.md)。initialize 在 migration、研究及來源註冊後匯入指標設定與既有營收投影；新安裝不用等待下一個 hourly 才看見指標設定。

技術研究與文件：Markdown／YAML 是編輯來源，驗證後原子匯入 PostgreSQL 供網站唯讀查詢；外部文件觀測與待核對候選不會自動改寫研究。維護與核對流程見 [technical-document-operations](docs/technical-document-operations.md)，實際已讀範圍見 [來源查核](docs/technical-source-audit.md)，全圖缺口見 [17 環節／7 題材矩陣](docs/technical-research-matrix.md)。連線閱讀與快取契約見 [frontend](docs/frontend.md)，量測結果及限制見 [reading-performance](docs/reading-performance.md)。

Docker 固定 Node 24.21.0，Python 的直接依賴與間接版本分別由 `backend/requirements.txt`、`backend/runtime-constraints.txt` 管理；新增的 PDF 解析器為 pypdf 6.20.1。更新執行環境時需重建 image 並重跑對應驗證及效能基準，避免把套件升版混入功能改善的比較。
