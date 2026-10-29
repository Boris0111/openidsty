# Tasks

本 change 建立在 `separate-research-production-deployment` 之上：該 change merge 並完成正式環境切換（它的 group 9）之後，才從 `main` 開始實作。單元測試都放在 root `tests/`，不需要 Docker，以 `python -m unittest discover -s tests -p "test_*.py"` 執行，並在 CI 跑。

## 1. `prefect` 資料庫納入備份

- [x] 1.1 `backup()` 傾印 `prefect` 資料庫（design D1）：
  - `pg_dump -Fc --exclude-table-data=log --exclude-table-data=events --exclude-table-data=event_resources`，寫成 `prefect.dump`。
  - manifest 新增 `prefect`：`alembic_version`，以及 `deployment`、`work_pool`、`flow_run` 的筆數（傾印前查詢）。
  - `prefect.dump` 與其他檔案一樣列入 `files`、`sizes`，並複製到第二份副本。

  驗證：`tests/test_research_backup.py` 確認傾印參數（三張表只排除資料）、manifest 的 `prefect` 欄位、`prefect.dump` 出現在主副本與第二份副本，且既有欄位不變。
- [x] 1.2 Prefect 升版的回退邊界（design D2）：
  - 目標與目前的 `prefect_version` 不同時，部署前備份標記 `rollback_boundary`，紀錄寫入 `prefect_boundary: true`。
  - `latest_boundary()` 同時考慮收縮與 Prefect 邊界。
  - `rollback_refusals()` 的 Prefect 拒絕訊息指出 Prefect 邊界備份與 `docs/research-backup.md` 的事故程序。

  驗證：`tests/test_research_deploy.py` 涵蓋 Prefect 版本相同時不標記、不同時標記；`tests/test_research_rollback.py` 確認拒絕訊息含邊界備份名稱與事故程序；`tests/test_research_backup.py` 確認 30 天清理保留這份備份。

## 2. 演練還原 `prefect`

- [x] 2.1 `research_drill.py restore` 還原 `prefect`（design D3）：
  - manifest 列有 `prefect.dump` 時，在演練 cluster 建立 `prefect` 資料庫，以 `pg_restore --exit-on-error` 還原，核對 `alembic_version` 與三項筆數。
  - 報告加入 `prefect_restored` 與核對結果；舊備份記為 `prefect_restored: false` 並註明原因，不算失敗。

  驗證：`tests/test_research_drill.py` 涵蓋新舊兩種 manifest、核對不符時的失敗訊息，以及沒有 `prefect.dump` 時不建立資料庫。

## 3. 互斥檢查與 `bootstrap`

- [x] 3.1 `scheduler-start` 與 `rollback` 執行原服務互斥檢查（design D5）：
  - `scheduler-start` 在啟動 `prefect` 前檢查。
  - `rollback` 在現行腳本判斷相容性時一併檢查，位於備份與 checkout 之前。

  驗證：`tests/test_research_lab_actions.py`、`tests/test_research_rollback.py` 確認原服務運行或 port 被占用時拒絕，訊息指出占用者，且沒有任何 compose、備份或 checkout。
- [x] 3.2 `bootstrap` 改用 `git -c core.autocrlf=false archive`（design D6）。驗證：測試確認 archive 參數；`tests/test_research_lab_actions.py` 的靜態檢查擴充為「所有 `git archive` 呼叫都帶 `core.autocrlf=false`」。

## 4. 文件

- [x] 4.1 更新文件：
  - `docs/research-backup.md`：檔案表加入 `prefect.dump`、manifest 的 `prefect` 欄位、事故時還原 `prefect` 的程序（design D4）。
  - `docs/research-deployment.md`：Prefect 邊界、回退的拒絕訊息、`scheduler-start` 與 `rollback` 的互斥檢查，以及 Prefect 升版時要重新確認被排除的表名。
  - `docs/research-lab.md`：`scheduler-start` 的互斥檢查。

  驗證：文件描述與 1.1–3.2 的測試一致；`DocumentedCommandTests` 通過。

## 5. 驗證（演練環境，從本 change 的 worktree）

開始前記錄正式服務的指紋（容器、image、資料庫清單、volume），每一步完成後都核對一次，必須全部不變。

- [ ] 5.1 root unittest 全數通過，CI 全綠。驗證：run 編號記在本 task。
- [ ] 5.2 以真實資料驗證 `prefect` 的傾印與還原：
  - 複製最新一份正式備份到暫存資料夾。
  - 以 1.1 的相同參數，從正式 `prefect` 資料庫唯讀傾印一份 `prefect.dump`；這與每日備份讀取的內容相同。
  - 把 SHA-256、大小與 `prefect` 欄位補進暫存資料夾的 manifest。
  - 從空的演練環境以這份資料夾執行 `restore`。

  驗證：
  - 研究資料核對全部相符，`prefect_restored: true`，遷移版本與三項筆數相符。
  - 記下 `prefect.dump` 的大小與傾印耗時。
  - 正式服務指紋不變。
- [ ] 5.3 把 5.1–5.2 的結果記入 `docs/research-backup.md`（傾印大小、耗時、還原核對）。驗證：文件數字與 `.work/research-drill/` 的報告一致。

## Workflow follow-up

- 1–5 全部勾完並在 branch 上 archive 之後，PR 才交給 Boris merge（依 `AGENTS.md`「先驗證、再 merge」）。archive 要在 `separate-research-production-deployment` archive 之後。
- merge 後依 `docs/research-deployment.md` 部署，再手動觸發一次每日備份：
  - 核對 `prefect.dump` 的 SHA-256、manifest 的 `prefect` 欄位與 D: 的副本。
  - 把這份備份還原到演練環境。
  - 結果記在 `docs/research-acceptance.md`。這是只有正式環境才有的行為，不阻擋 merge。
- 正式 Prefect 中卡住的 run 與 Prefect 的保留期限，由 Boris 另行決定（design Open Questions）。
