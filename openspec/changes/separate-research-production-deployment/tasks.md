# Tasks

本 change 改變的正是「正式服務怎麼部署」，所以 merge 前**不碰正式服務**。

- group 1–6 是離線工作：程式、測試與文件。
- group 7 從本 PR 的 worktree，在演練環境驗證。演練環境會被清空重建；正式服務的容器、image、資料與祕密全程不變，每一步都核對。
- group 8 是 merge 後的首次部署，也就是正式環境切換，需要 Boris 同意並在場（design D12、Migration Plan）。

各 group 的單元測試都放在 root `tests/`，不需要 Docker，以 `python -m unittest discover -s tests -p "test_*.py"` 執行，並在 CI 跑。

## 1. 遷移分類規則

- [x] 1.1 新增 `scripts/migration_rules.py`（design D8），只用標準函式庫：
  - 解析 revision 鏈與 `upgrade()` 內容，以及它引用的 `sql/*.sql`。
  - 標示破壞性語句；命中的遷移須有 `CONTRACT` 或 `EXPAND_REVIEWED`。
  - 檢查鏈線性、單一 head、revision 等於檔名前綴。
  - 提供兩個函式：查詢某提交的遷移鏈與收縮清單、判斷兩個版本之間有沒有收縮遷移。

  驗證：新增 `tests/test_migration_rules.py`，涵蓋以下案例並通過：
  - 實際的遷移目錄。
  - 合成的未標記 `op.drop_table`、`.sql` 內的 `DROP COLUMN`、`alter_column(type_=…)`、`ADD COLUMN … NOT NULL` 沒有 `DEFAULT`：各自失敗，並指出檔案與語句。
  - `revoked_at` 欄位名不被誤判。
  - 鏈分岔、檔名不一致：失敗。
  - `EXPAND_REVIEWED` 標記後通過。
- [x] 1.2 在 `backend/migrations/versions/0009_*.py` 與 `0017_drop_company_financials.py` 加上 `CONTRACT = '<原因>'`，不改其他內容。驗證：
  - `git diff` 只有標記行。
  - `migration_rules` 對實際目錄回報收縮遷移為 `0009`、`0017`。
  - 測試另以「移除 `0017` 標記」的副本確認會失敗。
  - CI 的離線後端測試照常通過。

  結果：`git diff` 只有兩行 `CONTRACT`；`migration_rules` 回報 `0009`、`0017`。本機以鎖定依賴執行離線後端測試：278 passed、97 skipped；另 1 項 `test_managed_git_does_not_touch_development_index_or_allow_schema_edits` 在 Windows 的 git worktree 中失敗（managed Git 的 `worktree` 指令，與遷移無關），以 7.1 的 Linux CI 為準。
- [x] 1.3 新增 `docs/research-deployment.md` 的「遷移：擴充與收縮」一節（design D9）：分兩步移除結構、回退邊界、撤回以新遷移進行、lint 的限制。同時處理過時的「additive」描述：
  - 修正 `docs/research-lab.md:27`。
  - 在 `docs/research-acceptance.md:229`、`:259` 加註「自 `0017` 起不成立」，不改寫歷史。

  驗證：`grep -rn "additive" docs/` 剩下的結果只出現在歷史紀錄或已加註的段落。

## 2. 以提交建置 image

- [x] 2.1 在 `scripts/research_lab.py` 新增建置函式（design D3）：
  - 以 `git -c core.autocrlf=false archive <sha>` 經 Python pipe 給 `docker build -f backend/Dockerfile -`；web 同樣處理。
  - tag `<sha12>`，加上 OCI 與 `io.industryflow.*` labels：alembic head 與收縮清單取自 1.1，Prefect 版本取自 `backend/runtime-constraints.txt`。
  - 同名 tag 已存在且 labels 相符時重用；不符時拒絕。

  驗證：新增 `tests/test_research_build.py`（mock `run`），涵蓋以下案例並通過：
  - archive 與 build 的參數。
  - label 值。
  - 重用與拒絕。
  - 兩個 Dockerfile 的 `COPY` 來源都在版本控制中：從 archive 建置不能缺檔。
- [x] 2.2 調整 compose 與設定檢查（design D4）：
  - `compose.research.yaml`、`compose.research-drill.yaml` 移除 `build:`，image 改用 `${RESEARCH_IMAGE_TAG:?…}`。
  - `compose(..., tag=)` 在濾除 host `RESEARCH_*` 後注入 tag。
  - `validate_config(config, tag)` 要求 12 位十六進位，所有服務一致，且沒有 `build:`。

  驗證：
  - 更新 `tests/test_research_lab_restart.py` 與既有設定檢查測試。
  - 新增測試：tag 格式錯誤、服務 tag 不一致、出現 `build:`、host 環境的 `RESEARCH_IMAGE_TAG` 被忽略，四種情況都會被拒絕。
- [x] 2.3 本機建置檢查，只建 image，不啟動任何服務：以本 branch HEAD 建置 api 與 web。驗證：
  - `docker image inspect` 可見全部 labels。
  - 在 image 內讀取 `/workspace/industry-map/themes/800vdc.md`，沒有 CR。
  - 建置前後，正式容器的 ID 與 image ID 不變。
  - 結果記在本 task。
  - `docs/research-deployment.md` 新增「建置與 image 版本」一節。

  結果（2026-10-28，提交 `2cbcaf4`）：api `f5a1965df35e`、web `879a42d05a9f`，共 202 秒；兩者 labels 齊全（revision `2cbcaf42a6ad…`、alembic-head `0017`、contract-revisions `0009,0017`、prefect-version `3.8.8`、build `git-archive`）。image 內 `800vdc.md` 0 個 CR、SHA-256 與 git blob 相同（舊 `:dev` 為 136 個 CR）。正式服務 8 個容器的 ID、image ID、狀態與啟動時間建置前後相同。

## 3. 部署目錄、防護與部署紀錄

- [x] 3.1 新增部署目錄與防護（design D1、D2、D5）：
  - `deployments/home.json`、`ledger.jsonl`（只追加，含 `schema_version`）、`.lock`。
  - 會改變正式服務的動作，取得 lock 後檢查四項：標記、乾淨 working tree（含未追蹤檔案）、HEAD 等於紀錄、容器 revision 等於紀錄。
  - `status`、`check` 只回報，不拒絕。
  - `.gitignore` 加入 `/deployments/`。

  驗證：新增 `tests/test_research_guard.py`，以下各種情況都被拒絕，且訊息指出原因：
  - 缺少標記。
  - 路徑不符。
  - 有未提交修改或未追蹤檔案。
  - HEAD 漂移。
  - 容器 revision 漂移。
  - 第二個寫入者拿不到 lock。
- [x] 3.2 `check()` 不再呼叫 `setup()`；`setup()` 在 volume `industryflow-research_pg-data` 已存在時拒絕產生祕密。驗證：
  - 測試：volume 存在、沒有 `.env.research` 時，`setup` 拒絕且不寫檔。
  - 測試：`check` 不會建立或追加 `.env.research`。
- [x] 3.3 調整 `backup()`（design D5、D11）：
  - 與部署共用 lock。
  - manifest 加入運行中 api 容器的 image ID、revision 與 `alembic_version`，欄位只增不改。
  - 30 天清理跳過標記為回退邊界的備份。

  驗證：在 `tests/` 新增或擴充測試，涵蓋 manifest 欄位、清理時保留回退邊界、lock 被占用時等待或拒絕。
- [x] 3.4 更新文件：
  - `docs/research-deployment.md` 新增「部署目錄與防護」「部署紀錄欄位」兩節。
  - `docs/research-backup.md` 改寫：排程改用部署目錄的 venv 與絕對路徑、共用 lock、回退邊界不清理。

  驗證：文件列出的欄位與 3.1、3.3 的測試資料一致。

## 4. 部署與回退指令

- [x] 4.1 新增 `deploy --commit <sha>`，順序依 design D6：
  1. 第一父鏈檢查。
  2. checkout 目標後由目標版本的腳本接手。
  3. 拒絕矩陣。
  4. 部署前備份。
  5. 建置。
  6. 執行 `run --rm --no-deps initialize`。
  7. 成功後才 `up --no-deps` 運行中的 app 服務，排程啟用時依序處理 prefect、deploy、worker。
  8. smoke 檢查。
  9. 寫入紀錄。

  失敗時的行為：
  - initialize 失敗：checkout 回原提交，不替換服務。
  - smoke 失敗：只記錄並印出回退指令，或說明只能還原備份；不自動回退。

  驗證：新增 `tests/test_research_deploy.py`，涵蓋以下案例並通過：
  - 非第一父鏈的提交被拒絕。
  - 會由目標版本的腳本接手。
  - 資料庫版本不在目標鏈上、Prefect 忙碌但沒有 `--force`、有收縮遷移但沒有 `--allow-contract`：各自被拒絕。
  - 呼叫順序為備份 → 建置 → initialize → up。
  - initialize 失敗時沒有任何 `up`，且留下失敗紀錄。
  - smoke 失敗時有失敗紀錄與回退指令，沒有自動回退。
  - db 永遠不在 `up` 的服務清單中。
- [x] 4.2 新增 `rollback --to <seq>`（design D7）：
  - 目標必須是成功的紀錄。
  - 依部署紀錄中遷移鏈的聯集，判斷有沒有收縮遷移。
  - Prefect 版本不同時拒絕。
  - 不執行 initialize。
  - image 不存在時重建，並標記 `rebuilt`。

  驗證：新增 `tests/test_research_rollback.py`，涵蓋以下案例並通過：
  - 目標失敗或不存在。
  - 目標 head 新於資料庫。
  - 區間內有收縮遷移。
  - Prefect 版本不同。
  - 成功路徑：沒有 initialize，`up --no-deps`，排程啟用時重新註冊。
  - 重建後標記 `rebuilt`。
- [x] 4.3 其餘指令調整：
  - 新增 `status`、`scheduler-start`。
  - `up` 改為提示使用 `deploy`。
  - 移除 `pg-check`、`rebuild-check`。
  - `seed-git`、`bootstrap`、`restore` 不再建置，並受防護。
  - `public-snapshot`、`start`、`stop` 使用紀錄中的 tag。

  驗證：
  - 測試：每個動作都不會呼叫 `docker build` 或 `compose build`。
  - 測試：在防護不通過時拒絕。
  - `python scripts/research_lab.py --help` 列出新的動作清單。
- [x] 4.4 更新文件：
  - `docs/research-deployment.md` 新增「部署」「回退」「smoke 失敗時」三節。
  - `docs/research-lab.md`：L3、L12、L23，以及 L38、L46 的手動 compose 指令，改為 `deploy`／`status`／`scheduler-start`。
  - `docs/research-owner.md`、`research-reader-entry.md` 的 compose 指令加上 tag 來源（由 `status` 取得）。
  - `docs/public-snapshot.md:27` 改為在部署目錄進行。
  - `README.md` 的啟動與維運段落。

  驗證：在描述**現行程序**的文件中，`grep -rn "research_lab.py up\|:dev" README.md docs/` 都找不到；歷史紀錄段落不改。

  結果：剩下的命中都在歷史紀錄（`research-acceptance.md`、`research-integration.md`、`research-performance.md`、`research-runtime-incident-20261017.md`、`research-service-implementation.md`），以及 `research-deployment.md` 描述切換前 `:dev` 系統的段落（tombstone 為何能擋住舊 branch、2.3 的建置對照、「回到 pre-ledger image」的回復指令），這些段落本來就要指名舊的 `:dev` image。另修正 `research-source-updates.md` 一處現行說明（`start` 不啟動排程，改用 `scheduler-start`）。

## 5. 演練環境

- [x] 5.1 調整 `scripts/research_drill.py` 的基礎設定（design D10）：
  - compose 注入 tag。
  - 演練祕密改到 `INDUSTRYFLOW_DRILL_HOME`（預設 `%USERPROFILE%\industryflow-drill`）。
  - `setup` 不再讀 `ROOT/.env.research`，改用 `--sec-user-agent`。
  - `run()` 同時遮蔽正式與演練祕密。
  - `scripts/research_scale.py`、`research_draft_bench.py` 改用 `research_drill.ENV_FILE`。

  驗證：新增 `tests/test_research_drill_env.py`，涵蓋以下案例並通過：
  - 在沒有 `.env.research` 的目錄，路徑解析與 `setup` 都正常。
  - 錯誤訊息中的演練祕密被遮蔽。
  - 兩個腳本讀到的是同一個路徑。
- [x] 5.2 `restore --backup latest|<path>` 改用備份 manifest 記錄的基準 image：依 revision 建置或重用。舊 manifest 沒有 revision 時，要求 `--baseline-commit`。驗證：測試涵蓋新舊兩種 manifest、基準 image 不存在時會建置、`latest` 選到最新一份完整備份。
- [x] 5.3 新增 `deploy-rehearsal --commit <sha>` 與 `rollback-rehearsal`，與 `research_lab.py` 共用建置、initialize、替換、smoke 與回退判斷。
  - 不檢查主線與部署目錄，只操作 drill project。
  - 報告寫到 `.work/research-drill/`，內容包括：各表列數與 md5 差異、遷移版本前後、`theme_assessment_versions` 增減、revision、`worktree_dirty`。

  驗證：測試以 mock 確認以下各點：
  - project 是 `industryflow-research-drill`。
  - 拒絕條件與正式環境相同。
  - 報告欄位齊全。
- [x] 5.4 把 `pg-check`、`rebuild-check` 搬到 `research_drill.py`，只連演練的資料庫 cluster 與 volume。驗證：測試確認 compose project、DB host 與 volume 都屬於演練環境；`research_lab.py` 已沒有這兩個動作。
- [x] 5.5 更新文件：
  - `docs/research-backup.md` 的演練段落（`INDUSTRYFLOW_DRILL_HOME`、`--backup latest`、基準 image）。
  - `docs/research-performance.md`、`research-integration.md` 中的演練祕密路徑。
  - `docs/research-deployment.md` 新增「合併前演練」一節。

  驗證：照文件指令的參數，與 `research_drill.py --help` 一致。

## 6. 流程規則

- [x] 6.1 改寫 `AGENTS.md`「先驗證、再 merge」（design D12）：
  - merge 前的實機驗證從 PR worktree 在演練環境進行，不切換主 checkout。
  - merge 後依 `docs/research-deployment.md` 部署，部署紀錄的 smoke 結果就是紀錄。
  - 只有正式環境才有的行為，在部署後核對，記在 `docs/research-acceptance.md`。
  - 產物表加入 `docs/research-deployment.md`。

  驗證：在 `AGENTS.md`、`README.md` 與描述現行程序的 `docs/`，`grep -rn "切到該 PR 的 branch\|主 checkout 暫時切\|worktree 沒有 .env.research"` 都找不到。

## 7. 整合驗證（演練環境，從本 PR 的 worktree）

開始前記錄正式服務的容器 ID、image ID、資料庫清單與 volume 清單，每一步完成後都核對一次，必須全部不變。演練環境會被 `down` 清空。

- [ ] 7.1 推送 branch、開 draft PR，確認 GitHub Actions 全部通過：新增的 unittest、遷移規則、離線後端、前端與 E2E。驗證：CI 全綠，run 編號記在本 task。
- [ ] 7.2 準備演練目錄與 image：
  - 建立 `INDUSTRYFLOW_DRILL_HOME` 與演練祕密。
  - 以 `--baseline-commit 7ebbc68`（目前正式的程式內容）建置基準 image，再建置本 PR HEAD 的 image。
  - 驗證：兩個 image 的 labels 正確、沒有 CR；正式服務不變。
- [ ] 7.3 執行 `research_drill.py restore --backup <最新正式備份>`。驗證：
  - 表、md5、release、refs、資產都與 manifest 一致，`/next` 回 200。
  - 沒有讀取任何正式祕密。
  - 正式服務不變。
- [ ] 7.4 `deploy-rehearsal --commit <PR HEAD>`，驗證：
  - smoke 通過。
  - 資料變動只出現在預期的 legacy 地圖表：散文 CRLF 改為 LF、roles／relations 重新寫入。
  - `theme_assessment_versions` 沒有增加。若增加，先在本 change 修正比較方式，再重做本 task。
- [ ] 7.5 `rollback-rehearsal` 回到基準 image。驗證：
  - 沒有執行 initialize，smoke 通過。
  - `theme_assessment_versions` 不變。
  - 報告判定「只差擴充遷移」。
- [ ] 7.6 收縮遷移的拒絕：以 `6c0afd1^`（`0017` 之前）建置 image，嘗試讓演練回退到它。驗證：回退被拒絕，訊息指出 `0017` 與回退邊界，演練服務不變。
- [ ] 7.7 執行演練環境的 `pg-check --suite all`。驗證：
  - 全部通過。
  - 正式 cluster 沒有新增資料庫（以 `psql -l` 唯讀比對）。
  - 正式 volume 的修改時間不變。
- [ ] 7.8 防護與遮蔽的實機確認：在本 worktree（沒有部署目錄標記，也沒有正式祕密）執行以下操作：
  - `research_lab.py deploy --commit <任一 main 提交>`
  - `research_lab.py setup`
  - 一個故意失敗的演練步驟

  驗證：
  - 前兩個指令在改變任何狀態前就拒絕，`setup` 沒有寫入祕密。
  - 失敗輸出中沒有演練祕密或正式祕密。
  - 正式服務不變。
- [ ] 7.9 把 7.2–7.8 的結果整理進 `docs/research-deployment.md` 的「演練紀錄」，並在本檔各 task 註記。驗證：文件中的數字與 `.work/research-drill/` 的報告一致。

## 8. merge 後：正式環境切換（需 Boris 同意並在場；不阻擋 merge）

- [ ] 8.1 建立部署目錄：
  - `git clone` origin 到 `C:\Users\User\industryflow-prod`，`checkout --detach <merge 提交>`。
  - 建立 `.venv` 與 `deployments/home.json`。

  驗證：`research_lab.py status` 回報「尚無部署紀錄」，`git status` 乾淨。
- [ ] 8.2 複製 `.env.research` 與 `backups/research` 到部署目錄。驗證：
  - 逐檔 SHA-256 相同。
  - Boris 確認祕密已另存受保護副本，例如密碼管理器。
- [ ] 8.3 保留回復點：
  - 目前的 `:dev` image 另標為 `pre-ledger-api`／`pre-ledger-web`。
  - 寫入一筆 `adopt` 紀錄（容器、image ID、alembic 版本）。

  驗證：`status` 顯示 `adopt` 紀錄，舊 image 有新 tag。
- [ ] 8.4 首次部署：避開整點 :07，從部署目錄執行 `deploy --commit <merge 提交>`。驗證：
  - db 在內的容器都已重建。
  - bind mount 與 `working_dir` label 都指向部署目錄。
  - smoke 通過，紀錄為 `succeeded`。
  - 停機時間記下。
  - 下一個整點的 `official-information/hourly` flow run 成功。
- [ ] 8.5 改寫備份排程（design D11）後手動觸發一次。驗證：
  - `backup-log.jsonl` 有新紀錄，D: 有對應副本。
  - manifest 含運行容器的 image ID、revision、`alembic_version`。
- [ ] 8.6 把 8.5 的備份還原到演練環境。驗證：`restore` 以 manifest 的 revision 為基準 image，核對全部通過。
- [ ] 8.7 封住開發 checkout：
  - 放入 tombstone `.env.research`。
  - Boris 移除開發 checkout 中原本的祕密與 `backups/research`，並刪除本機舊 branch。

  驗證：在開發 checkout 執行 `research_lab.py check` 會拒絕，且沒有產生祕密；部署目錄的 `status` 沒有不一致。
- [ ] 8.8 在 `docs/research-acceptance.md` 新增「十三、正式環境切換（separate-research-production-deployment task 8）」一節，內容包括步驟（UTC）、結果、停機時間與限制。驗證：表格中的數字與部署紀錄、備份 log 一致。

## Workflow follow-up

- group 1–7 全部勾完後，PR 才交給 Boris merge。本 change 是 D12 所述的例外：merge 前**不** archive，因為 group 8 只能在 merge 後進行。
- merge 後依 group 8 切換正式環境；完成後以後續的 docs PR 提交 8.8 的紀錄，並 archive 本 change，把 `platform-runtime` 的 delta 合入主 spec。
- archive 之後，agent 的 memory「verify-before-merge」要改成新規則：演練環境驗證、merge 後部署。
