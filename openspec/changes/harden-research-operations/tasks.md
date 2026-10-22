# Tasks

## 1. 排程自動恢復與防回歸

- [x] 1.1 在 `compose.research.yaml` 的 `prefect` 與 `worker` 加上 `restart: unless-stopped`，`deploy` 維持不設 restart；以 `docker compose -f compose.research.yaml --profile scheduler config` 確認兩者帶有該設定、`deploy` 沒有
- [x] 1.2 在 `scripts/research_lab.py` 的 `validate_config` 加入規則：`prefect`、`worker` 必須是 `unless-stopped`，`deploy` 不得設 restart，違反時以服務名稱報錯；以 `python scripts/research_lab.py check` 驗證現行設定通過
- [x] 1.3 在 `tests/` 新增不需 Docker 的測試：以 PyYAML 解析 `compose.research.yaml`，斷言 1.2 的規則；另以缺少 restart 與替 deploy 設 restart 的設定，斷言 `validate_config` 拒絕。以 `python -m unittest discover -s tests -p "test_*.py"` 驗證全部通過
- [ ] 1.4 更新 `docs/research-lab.md`：說明重開機後自動恢復的服務、如何確認排程恢復（`docker ps` 加上 Prefect 下一個整點的 flow run）、暫停排程要明確 `stop`、原服務只能 stop 不能 up；刪除第 27 行「不要提前啟用 scheduler profile」這句過時說明。以文件中的確認指令實際跑一次核對

## 2. 自動檢查與 runtime 一致

- [x] 2.1 在 `.gitattributes` 對 `backend/tests/fixtures/**` 與 `tests/fixtures/**` 設定 `-text`；執行 `git status` 確認 fixtures 沒有本機修改後，刪除工作區的 fixtures 再以 `git checkout -- backend/tests/fixtures tests/fixtures` 取出（單純 checkout 會因 stat 快取而略過，實測無效），再以 `git ls-files --eol backend/tests/fixtures tests/fixtures` 確認工作區不再是 crlf
- [x] 2.2 在 Windows checkout 執行 `python -m pytest backend/tests/test_financial_sec.py -q`，確認原本因 CRLF 失敗的兩項 hash 測試通過
- [ ] 2.3 修改 `.github/workflows/verify.yml`：
  - 依賴安裝改為 `python -m pip install -r backend/requirements.txt -c backend/runtime-constraints.txt`，與 `backend/Dockerfile` 相同
  - pip cache 路徑納入 constraints 檔
  - 驗證步驟改為執行 `python -m unittest discover -s tests -p "test_*.py"`，涵蓋 validator、research schema 與 lab 的測試
  - 驗證方式：push 後 CI 全數通過，log 中可看到 constraints 已套用，以及 root 測試的數量

## 3. 文件對齊現況

- [x] 3.1 更新 `README.md`：
  - 開頭兩段改寫成現況：研究服務、只綁 loopback、scheduler profile 與重啟行為；財報相關文字不動
  - 「自架公開部署」標明目前未對外部署、只供參考
  - 文件表補上 `compose.research.yaml`
  - OpenSpec 範例指令改用 `<name>` 佔位
  - 驗證方式：以 grep 確認 `refocus-industry-explorer` 不再出現
- [x] 3.2 更新 `AGENTS.md` 第 9 行的專案描述，改成目前的研究服務架構，並保留「啟動及資料維護見 README.md」；確認所有 `AGENTS.md` 的連結路徑都存在
- [x] 3.3 修正下列文件的過時描述：
  - `docs/research-reader-entry.md` 第 20 行：已完成的 task 6.1／7 仍被寫成待接續
  - `docs/research-backup.md` 第 9、15、81 行：worktree 路徑與 3014，改成主 repo 與 3010
  - `docs/api.md` 第 57 行、`docs/reading-performance.md` 第 82 行：已移除的「進階資訊」面板
  - 驗證方式：以 `grep -rn "3014\|進階資訊\|task 6.1" docs` 確認只剩歷史紀錄性質的段落

## 4. 整合驗證

- [ ] 4.1 重開機演練：
  - 以 `--profile scheduler up -d` 重建 `prefect` 與 `worker`
  - 重啟 Docker Desktop
  - 確認 `db`、`api`、`web`、`prefect`、`worker` 都回到 running，`deploy` 沒有重跑，原服務容器維持停止，下一個整點出現 `official-information/hourly` 的 flow run
  - 若 worker 卡住而不是結束，記錄現象，再依 design 的 Risks 評估是否追加 healthcheck
- [ ] 4.2 在 `docs/research-acceptance.md` 的「已知問題」記錄處理結果：restart 與 CRLF 已處理、私人網路仍延後，並附上 4.1 的演練結果與日期
- [ ] 4.3 執行完整離線檢查：
  - `python scripts/validate_map.py`
  - `python -m unittest discover -s tests -p "test_*.py"`
  - `cd backend && python -m pytest tests -q`
  - `openspec validate harden-research-operations --strict`
  - 全部通過

## Workflow follow-up

- 合併後，在主 checkout 依 design 的 Migration Plan 執行步驟 1–4。
- 通過 review 後，以 `/opsx:archive` 歸檔，並確認 `platform-runtime` 主 spec 已新增兩條 requirement。
