# Tasks

## 1. Port 與 allowlist 改到原 origin

- [x] 1.1 修改 `compose.research.yaml`：web `127.0.0.1:3010`、API `127.0.0.1:8010`、Prefect `127.0.0.1:4201`（含 `PREFECT_UI_API_URL`）、reader 維持 3015；`RESEARCH_ADMIN_ORIGINS` 改為 `http://127.0.0.1:3010,http://localhost:3010`（api 與 web 兩處），`RESEARCH_ADMIN_HOSTS` 改為 `api:8000,127.0.0.1:8010,localhost:8010`。驗證：`python scripts/research_lab.py check` 輸出的 ports 為 3010／8010／4201／3015。
- [x] 1.2 更新 `scripts/research_lab.py` 的 `PORTS`、`backend/app/research_cli.py` 的預設 `--base-url`、`.Codex/launch.json` 的 port；更新 `backend/tests/test_research_auth.py` 等測試的 origin 常數。驗證：在 repo 根目錄執行 `grep -rnE "3014|8014|4204"`，排除歷史紀錄後沒有殘留；`python -m pytest -q backend/tests` 通過。

## 2. 與原服務互斥

- [x] 2.1 在 `research_lab.py` 的 `up`／`start` 加入互斥檢查：Compose project `industryflow` 若有運行中的容器即拒絕並列出名稱；不論既有 api 容器存不存在都探測 3010／8010，占用者不是本 project 時拒絕；不自動停止任何容器。為檢查邏輯加入單元測試（以假的 `docker ps` 輸出模擬原服務運行中、port 被他人占用、被自己占用三種情況）。驗證：測試通過，且在原服務停止的實機狀態下 `up` 可以正常執行。
- [x] 2.2 更新 `docs/research-lab.md`、`docs/research-owner.md`、`docs/research-reader-entry.md` 的網址與啟停說明，並在 `README.md` 標明 3010 為正式研究服務、`compose.yaml` 為回復用的原服務（附回復步驟、不可與研究服務同時啟動）。驗證：文件中的指令實際執行一次可用。

## 3. 切換到 3010 並驗收

- [x] 3.1 確認原服務沒有容器在運行後，執行 `python scripts/research_lab.py up` 重新建立 api／web 容器；確認 volume 名稱不變、active release 與切換前相同、`http://127.0.0.1:3010/next` 與 `http://127.0.0.1:8010/api/health` 回 200、3014／8014 已不再監聽。
- [x] 3.2 以 `E2E_BASE_URL=http://127.0.0.1:3010`（以及 `RESEARCH_E2E=1`）跑 live e2e，涵蓋讀者、管理登入／寫入 Origin 檢查，以及 `research-navigation.spec.ts` 的舊公司網址；reader gateway 跑 `research-reader-entry.spec.ts`。驗證：全部通過，失敗須修正後重跑。
- [x] 3.3 在 3010 手動或以腳本驗證：舊 ticker 深連結與舊題材網址可解析、`/themes/<id>#candidates` 停在「數據與追蹤」，以及同一 origin 的 v1 收藏（`industryflow.theme-watchlist.v1`）首次開啟時遷移一次、v1 原值保留、重新整理不重複遷移。驗證：結果記錄在 `docs/research-acceptance.md` 的切換紀錄。
- [x] 3.4 在 `docs/research-acceptance.md` 新增「2026-10-21 正式切換紀錄」：已完成的檢查表步驟（備份與演練、祕密輪替、owner 重設、origin 接手）、例外（第 5 步私人網路延後）、3014 收藏的匯出／匯入步驟，以及回復步驟。驗證：紀錄內每個數字都有對應的指令輸出。

## Workflow follow-up

- 切換流程另行執行：啟用 scheduler profile、補抓 10-18 起的資料、記錄 TWSE／TPEx 重大訊息 10-19／10-20 無法補回的缺口。
- 第 5 步私人網路之後另開 change。
- 完成後 archive 本 change，並同步 `platform-runtime` 主 spec。
