# Proposal

## Why

正式研究服務在 2026-10-21 切換後，`compose.research.yaml` 的 `prefect` 與 `worker` 沒有 restart 設定。Docker 或主機重開機後，db、api、web 會自動回來，排程卻不會。TWSE／TPEx 的開放資料只提供當下快照，所以排程停擺的期間無法回補，10-15、10-16、10-19 的重大訊息已經因此遺失（`docs/research-acceptance.md:303`）。

同時，自動檢查與 runtime 之間有落差：
- CI 沒有套用 runtime 的鎖定依賴。
- root `tests/` 下有兩個測試檔不在 CI。
- 測試 fixtures 在 Windows 會被 checkout 成 CRLF，造成 hash 測試失敗。

README 與 AGENTS.md 也還在描述切換前的狀態，會誤導下一位接手的維護者或 agent。後續還有財報移除與靜態公開兩個 change，這些基礎要先穩住。

## What Changes

- **排程自動恢復**：`compose.research.yaml` 的 `prefect`、`worker` 加上與其他常駐服務一致的 `restart: unless-stopped`。`deploy` 是一次性服務，維持不重啟。
- **防止回歸**：`scripts/research_lab.py` 的設定檢查拒絕缺少 restart 的常駐排程服務，並加一個不需要 Docker 的 compose 靜態檢查測試。
- **固定 fixtures 換行**：`.gitattributes` 對 `backend/tests/fixtures/**` 停用換行轉換，讓 checkout 出來的 fixtures 與 git 中的內容逐位元組相同。
- **CI 與 runtime 用同一組依賴**：CI 安裝 Python 依賴時套用 `backend/runtime-constraints.txt`，與 `backend/Dockerfile` 一致。CI 另外執行 root `tests/` 下的 unittest。
- **文件對齊現況**：只修運維面，財報相關的文字留給後續的 `remove-company-financials`。
  - `README.md`：開頭定位、公開部署段、文件表（補 `compose.research.yaml`）、已 archive 的 OpenSpec 範例指令。
  - `AGENTS.md:9`：專案描述。
  - `docs/research-reader-entry.md`：已完成的 task 仍標成「待接續」。
  - `docs/research-backup.md`：worktree 路徑與 3014。
  - `docs/api.md`、`docs/reading-performance.md`：已移除的「進階資訊」面板。
  - `docs/research-acceptance.md`：已知問題標註處理結果。
- **重開機恢復程序**：`docs/research-lab.md` 寫明重開機後會自動恢復哪些服務、怎麼確認排程已恢復，以及原服務必須維持 stopped 的前提。

**不在範圍內**：
- 雲端或私人網路部署。
- 備份脫離 Docker Desktop 的使用者工作階段。
- MOPS 依日期查詢的回補 adapter。
- `micron-hbm4-remarks` 的重新查核：它的 notes 已如實記錄 403 限制，hbm4 判讀另有兩筆 verified 證據，屬於內容判斷。
- `sources.yaml` 中 15 筆 `year=115` 的年報入口：它們是特定年度文件的正確引用，不是錯誤。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `platform-runtime`：新增兩條 requirement，既有 requirement 文字不變。
  - **排程在重啟後自動恢復**：Docker 或主機重啟後，排程 MUST 自動恢復，不得依賴維護者重新手動啟動；同時不得讓已停止的原服務一併回來。
  - **自動檢查與 runtime 一致**：自動檢查 MUST 使用與 runtime 相同的鎖定依賴；測試 fixtures 在任何平台的 checkout MUST 與版本控制內容逐位元組一致；版本控制中的 runtime 與維運測試 MUST 全部納入自動檢查。

## Impact

- **設定**：`compose.research.yaml`、`.gitattributes`、`.github/workflows/verify.yml`。
- **腳本與測試**：`scripts/research_lab.py`（`validate_config`）、`tests/` 新增 compose 檢查。
- **文件**：`README.md`、`AGENTS.md`、`docs/research-lab.md`、`docs/research-acceptance.md`、`docs/research-reader-entry.md`、`docs/research-backup.md`、`docs/api.md`、`docs/reading-performance.md`。
- **runtime 行為**：
  - 排程服務重啟後會自動回來。
  - 前提不變：原服務 `industryflow` 必須維持 stopped。`unless-stopped` 不會重啟被手動停止的容器，但原服務若被重新 `up`，就會與研究服務爭搶同一組 port。
- **工作目錄**：在既有的 Windows checkout 上，fixtures 要 renormalize 一次，工作區會出現 fixtures 的換行差異。
- **不動的部分**：DB schema、API、前端與資料流程本身。
