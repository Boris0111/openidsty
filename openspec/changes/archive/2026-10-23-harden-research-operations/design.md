# Design

## Context

動機見 proposal.md 的 Why，行為要求見 `specs/platform-runtime/spec.md`。以下只列影響做法的現況。

**compose 現況**
- `compose.research.yaml` 中，`db`、`api`、`web` 都設了 `restart: unless-stopped`。
- `prefect`、`deploy`、`worker` 在 `scheduler` profile，三者都沒有 restart。
  - `deploy` 是一次性服務（`python -m app.deploy`），負責建立 work pool 與 deployments。
  - deployment 與排程存在 Prefect 的 PostgreSQL 資料庫中，所以重啟後不需要重跑 `deploy`。
- 原服務 `compose.yaml` 的常駐服務同樣設了 `unless-stopped`。切換後它們是被手動 stop 的狀態。

**`scripts/research_lab.py` 的 `validate_config`**
- 已經檢查 image、DB 權限、port bind 和 scheduler 是否為 opt-in，但沒有檢查 restart。
- 它需要 `docker compose config` 的輸出，所以無法在 CI 上跑。

**換行**
- 本機 `core.autocrlf=true`。
- `backend/tests/fixtures/**` 與 `tests/fixtures/**` 在 index 中是 LF，在工作區是 CRLF。
- `.gitattributes` 目前只處理 `docker/*.sh`、`*.sql` 和 `industry-map/assets/**`。

**CI（`.github/workflows/verify.yml`）**
- 依賴安裝只用了 `backend/requirements.txt`，而 `backend/Dockerfile` 另外套了 `-c runtime-constraints.txt`。
- 只跑 `backend/tests`，root `tests/` 只跑了 `run_validator_tests.py`。
- root `tests/` 的 30 個 unittest 已在本機離線通過（2026-10-23）。

## Goals / Non-Goals

**Goals：**
- 不改任何服務的啟動指令與依賴關係，只補上重啟策略。
- 讓「排程必須能自動恢復」成為不需要 Docker 也能檢查的規則。

**Non-Goals：**
- 不改 Prefect 的 worker 數量、concurrency 或 flow retry。
- 不處理排程停擺期間的資料回補。
- 不讓 Docker Desktop 脫離使用者登入；它在 Windows 上依附使用者工作階段，這屬於雲端搬遷 change 的範圍。
- 不改寫財報相關的文件段落，留給 `remove-company-financials`。

## Decisions

### D1：`prefect`、`worker` 用 `unless-stopped`，`deploy` 不設
- **`unless-stopped`**：與既有常駐服務一致，而且保留 `research_lab.py stop` 的語意。手動停止後，重開機也不會自己回來，這是把共用 port 還給原服務的前提。
- **不選 `always`**：重開機時會把手動停止的容器也拉起來，破壞上述互斥。
- **不選 `on-failure`**：daemon 重啟時不會恢復正常結束或被中斷的容器，無法滿足「重開機後恢復」。
- **`deploy` 不設 restart**：它是冪等的一次性工作，排程資料已經存在 Prefect DB；自動重跑沒有好處，失敗時反而會反覆重試。

### D2：啟動順序靠重試，不靠 `depends_on`
- `depends_on` 的 healthy 和 completed 條件只在 `docker compose up` 時生效；daemon 重啟容器時不會依序等待。
- worker 若在 Prefect API 或 DB 就緒前結束，交給重啟策略反覆重試即可，不另外寫等待腳本。
- 這點要在 apply 時用實際重啟演練驗證（見 Risks）。

### D3：防回歸分兩層
- **runtime 層**：`validate_config` 拒絕沒有 `unless-stopped` 的 `prefect`、`worker`，也拒絕替 `deploy` 設 restart。`up` 和 `check` 會在啟動前擋下。
- **CI 層**：在 root `tests/` 新增測試，直接用 PyYAML 解析 `compose.research.yaml` 檢查同樣的規則，不需要 Docker。
- **不採用**：只在 CI 呼叫 `docker compose config`。CI 沒有 Docker，而且多一個外部依賴。

### D4：fixtures 用 `-text`，不用 `eol=lf`
- 對 `backend/tests/fixtures/**`、`tests/fixtures/**` 設定 `-text`，與既有的 `industry-map/assets/** -text` 一致。checkout 出來的檔案就是 index 中的原始位元組，hash 測試才可靠。
- **不選 `eol=lf`**：它仍然把檔案當成文字來轉換。若 fixture 刻意包含 CRLF（例如模擬 HTTP 回應），內容會被改掉。
- index 中已經是 LF，所以不需要 `git add --renormalize`。只要讓現有 checkout 的工作區重新從 index 取出即可（見 Migration Plan）。

### D5：CI 與 Dockerfile 用同一條安裝指令
- 改成 `pip install -r backend/requirements.txt -c backend/runtime-constraints.txt`，與 `backend/Dockerfile` 完全相同。
- pip cache key 一併納入 constraints 檔。
- root `tests/` 改用 `python -m unittest discover -s tests -p "test_*.py"`，取代單獨執行 validator 測試，涵蓋 validator、research schema 與 lab 的互斥測試。

### D6：文件只修運維面，並以「現況」為準
- README 開頭與 AGENTS.md 改成描述現在的運作：研究服務、loopback、scheduler profile、重啟行為。
- 不預告後續 change，避免再次漂移。
- 已 archive 的 OpenSpec 範例指令改成不綁定特定 change 的寫法，例如 `openspec status --change <name>`。

## Risks / Trade-offs

- **[風險] Prefect server 或 worker 遇到 DB 未就緒時，可能卡住而不是結束，導致重啟策略不會觸發。**
  - → apply 時做一次實際重啟演練：重啟 Docker Desktop，確認 `prefect`、`worker` 都回到 running，並看到下一個整點的 flow run 被建立。如果卡住，再評估加 healthcheck，或讓 worker 失敗時結束。
- **[風險] 原服務若被重新 `docker compose up`，它的 `unless-stopped` 會讓它在每次重開機時都和研究服務搶 port。**
  - → `research-lab.md` 寫明「原服務只能 stop、不要 up」。`research_lab.py` 既有的互斥檢查仍會在 `up` 時拒絕。重開機時是 daemon 直接拉起容器、不經過這個檢查，所以這點只能靠操作規則。
- **[取捨] 重開機後排程自動恢復，代表維護者暫停排程時必須明確執行 `stop`，不能指望重開機來關掉排程。**
  - → 文件寫明暫停排程的指令。
- **[風險] 既有 Windows checkout 套用 `-text` 後，工作區仍是 CRLF，`git status` 卻因 stat 快取顯示乾淨，hash 測試照樣失敗。**
  - → Migration Plan 提供一次性的「刪除再取出」指令；執行前先確認 fixtures 沒有本機修改。
- **[取捨] SEC 那兩項 hash 測試會在 `remove-company-financials` 中隨 `test_financial_sec.py` 一起刪除。**
  - → 這次仍然修，因為規則保護的是所有 fixtures，不只這兩項。

## Migration Plan

1. 合併後，在主 checkout 先執行 `git status -- backend/tests/fixtures tests/fixtures`，確認這兩個目錄沒有本機修改。
2. 刪除工作區的這些 fixtures 後再取出：`git ls-files -z -- backend/tests/fixtures tests/fixtures | xargs -0 rm --`，接著 `git checkout -- backend/tests/fixtures tests/fixtures`。單純執行 `git checkout --` 不會改寫：git 依 stat 快取判定檔案未修改而略過（apply 時實測）。最後以 `git ls-files --eol` 確認為 `w/lf`。
3. 在研究服務目錄執行 `python scripts/research_lab.py check`，確認新的設定檢查通過。
4. 以 `--profile scheduler up -d` 重新建立 `prefect` 與 `worker` 容器。restart 是容器建立時的設定，既有容器不會自動套用。
5. 依 Risks 做一次重開機演練，結果記錄到 `docs/research-acceptance.md`。

**回滾**：移除 restart 設定後重新建立容器即可；DB、volume 和排程資料都不受影響。

## Open Questions

- ~~Prefect server 遇到 DB 暫時不可用時，會結束還是持續重試？~~ 已在 2026-10-23 的演練中回答：Docker 重啟後，`prefect` 與 `worker` 在同一秒啟動，RestartCount 都是 0。worker 約 20 秒後自行連上 Prefect，沒有結束，也沒有卡住，所以不追加 healthcheck。演練同時發現整點 run 延遲 26 分鐘（見 `docs/research-acceptance.md` 第八節），這個問題另案處理。
