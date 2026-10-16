# Docker 啟動失敗的唯讀診斷

查核於 2026-10-16 深夜至 2026-10-17（Asia/Taipei）。本輪只讀系統狀態及必要 log，不重啟 Docker／WSL、不改 ACL、不刪除 cache／volume 或重設環境。

## 已確認的事件

- 2026-10-16 23:41:25，`%LOCALAPPDATA%/Docker/log/vm/init.log` 記錄 BuildKit `filterHistoryEvents.func1`、`history.go:1074` 發生 nil pointer panic／SIGSEGV；23:41:26 服務以 code 2 結束，23:41:27 VM 準備關閉。這是本輪建置／建置歷史查詢期間發生的 Docker 內部崩潰；現有紀錄不能單獨辨識哪個客戶端請求觸發。
- `host/monitor.log` 記錄後續數次重新開啟 Desktop 都得到 `backend server is already running`；原 backend／build 程序仍是 2026-09-24 啟動的程序。Docker Desktop 狀態 stopped，docker-desktop WSL distro 為 Stopped。
- 同時反覆發生 backend log `.7` 改名為 `.8` 的 Access is denied。相關檔案的 ACL 均給目前使用者 FullControl，沒有發現明確 ACL 拒絕；殘留程序／檔案占用是推論，尚未辨識鎖持有者，不能宣稱已證實。
- WSL 2.6.3.0、核心 6.6.87.2，Ubuntu-24.04 仍 Running；WslService、vmcompute 皆 Running。沒有證據顯示整個 WSL 或 BIOS 虛擬化失效。
- 實體可用記憶體先前約 1.1 GiB，本輪約 2.17 GiB／總可用 15.4 GiB。已檢視的近期 VM logs 未見 OOM kill；記憶體壓力可能促成不穩定，但不能當成已確認根因。
- C 槽剩約 62.9 GiB，D 槽剩約 341.3 GiB；Docker data VHDX 存在、約 32.34 GiB。已檢視 log 未見 no-space／EXT4 I/O 錯誤；未驗證整個 VHDX 或資料庫完整性，因此不保證資料健康，也沒有資料已毀損的證據。

## 原因評估與來源

最強證據是 Docker 內部 BuildKit 的 build history 處理崩潰，繼而留下仍存活的 Windows backend，使重新開啟 UI 未產生完整重新啟動。log 輪替問題可能是額外阻礙或既有副作用，仍待完整結束程序後重測。

[Moby #52257](https://github.com/moby/moby/issues/52257) 回報相同函式與行號的 daemon crash；該 issue 指向 [Moby #52230](https://github.com/moby/moby/pull/52230) 的 BuildKit 更新。這支持已知實作缺陷的判斷，不代表僅憑 issue 已確認所有觸發條件，亦不把任意新版都視為已驗證修復。

建議先儲存工作、完整停止 Docker 殘留程序及 WSL 後再啟動；若不便逐一確認程序，重新啟動 Windows 是替代方式。這會中斷其他 WSL 工作及容器，需由使用者執行或明確授權。若同一 panic 重現，先保全資料及診斷，再評估帶修正的 Docker Desktop 更新；不先刪 build history、VHDX、volumes、unregister distro 或 factory reset。

依據：[Docker WSL 架構與條件](https://docs.docker.com/desktop/features/wsl/)、[官方故障排查](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/)。目前日誌顯示 Desktop 4.65.0；[官方 release notes](https://docs.docker.com/desktop/release-notes/#4650) 另記錄部分 4.56–4.65 Windows MSI 更新問題及移除資料的風險，因此不直接以解除安裝作為此輪修復步驟。

## 實作影響

`expand-industry-research-service` 仍為 11/52，task 4.1 未勾選。Owner/session 程式及測試已寫入功能 worktree；TypeScript 先前檢查通過，2 項不需 DB 的安全測試通過，10 項實際 PostgreSQL 情境尚未執行。新 image build 中斷，實際代理及讀者回歸尚待環境恢復；不以 skip 或已寫好程式視為完成。

原、新預覽皆逾時。此輪沒有操作原服務容器或其資料，但目前無法重新核對容器 fingerprint，不能將環境中斷說成原服務持續正常。恢復後先檢查資料與服務，再從 task 4.1 的 PostgreSQL／瀏覽器驗證繼續。

## 保存點與恢復順序（2026-10-17）

Boris 指示儲存目前工作進度。將首條流程回饋、導覽說明、尚未驗收的 owner/session 程式與測試、Docker 診斷一起保存到 `feat/expand-industry-research-service`；不將未驗證程式標為完成，也不合併 main。保存前最新 TypeScript 檢查通過，OpenSpec strict validation 與 Git diff 格式檢查通過。

接手者先讀根目錄 `AGENTS.md`，再執行 `openspec instructions apply --change expand-industry-research-service --json` 取得實際進度。環境恢復後：

1. 先用 `docker desktop status`、`docker ps` 核對 engine／容器；核對原 volume 與資料。完整主機重啟會改變 started_at，須記錄此中斷，不以舊 fingerprint 冒充重啟後服務未變。
2. 在新版 worktree 執行 `python scripts/research_lab.py pg-check`。它只在新版 server 的 `industry_research_test` 測試，先修正 owner/session 的真實 DB 失敗，再確認其他 PostgreSQL 回歸。避免使用 `docker buildx history ls` 作為健康檢查，此次 panic 發生於 build history 的處理路徑。
3. `python scripts/research_lab.py up` 只重建新版 image 與預覽，沒有重新 bootstrap 研究或刪除 DB 的需要；本機 owner 密碼仍未設定，合成測試不可寫入 application DB。
4. 在 frontend 設 `RESEARCH_E2E=1`、`PLAYWRIGHT_CHROME=1`、`E2E_BASE_URL=http://127.0.0.1:3014`，執行 `npx playwright test tests/research-owner.spec.ts tests/research-service.spec.ts`；再做所需回歸。
5. 4.1 的行為與實際驗證全部通過後，才核對 task checkbox 位置、勾選並重跑 apply instructions。接續 4.2 草稿／diff／預覽／CLI，之後依 tasks 交付；不要越過尚未完成的驗收。

此 Git 保存不包含 DB、VHDX、`.env.research`、`.work` 內的備份或原始 log；這些本機資料仍留在原處，不能將程式 commit 宣稱為資料庫備份。
