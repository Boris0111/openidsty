# Tasks

本 change 改變的正是「正式服務怎麼部署」，所以 merge 前**不碰正式服務**。

- group 1–6 是離線工作：程式、測試與文件。
- group 7 從本 PR 的 worktree，在演練環境驗證。演練環境會被清空重建；正式服務的容器、image、資料與祕密全程不變，每一步都核對。
- group 8 是 code review 的修正與重新驗證，merge 前完成，切換才會執行修正後的程式。
- group 9 是 merge 後的首次部署，也就是正式環境切換，需要 Boris 同意並在場（design D12、Migration Plan）。

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

- [x] 7.1 推送 branch、開 draft PR，確認 GitHub Actions 全部通過：新增的 unittest、遷移規則、離線後端、前端與 E2E。驗證：CI 全綠，run 編號記在本 task。

  結果：draft PR #10。提交 `fce6cbf` 的 Offline verification 全綠：push run `40571693319`（6 分 28 秒）、pull_request run `40571703884`（5 分 5 秒）。之後只追加文件與 task 紀錄的提交，最終 run 編號記在 7.9。
- [x] 7.2 準備演練目錄與 image：
  - 建立 `INDUSTRYFLOW_DRILL_HOME` 與演練祕密。
  - 以 `--baseline-commit 7ebbc68`（目前正式的程式內容）建置基準 image，再建置本 PR HEAD 的 image。
  - 驗證：兩個 image 的 labels 正確、沒有 CR；正式服務不變。

  結果（2026-10-28）：演練祕密建在 `%USERPROFILE%\industryflow-drill`。基準 `7ebbc68e9a5b`、PR `fce6cbf10f14` 的 api／web 各約 10 秒（layer 快取）；labels 都是 head `0017`、收縮 `0009,0017`（`7ebbc68` 早於標記，未標記的破壞性遷移計為收縮）、Prefect `3.8.8`、`git-archive`。兩個 image 內 `industry-map` 全部 Markdown 共 0 個 CR。正式服務指紋（容器、DB 清單、`industry_research_test` 計數、volume、資產與 managed Git、`:dev` image）不變。
- [x] 7.3 執行 `research_drill.py restore --backup <最新正式備份>`。驗證：
  - 表、md5、release、refs、資產都與 manifest 一致，`/next` 回 200。
  - 沒有讀取任何正式祕密。
  - 正式服務不變。

  結果：備份 `20261027T193003Z`（manifest 早於 `api_revision`）：不給 `--baseline-commit` 時在動任何容器前拒絕；給 `7ebbc68` 後重用基準 image 還原，RTO 52.7 秒。表、release（`a5df290c…`）、API 實際提供的 release、Git refs、資產 hash 與數量、遷移版本 `0017` 全部相符，`/next` 200。本 worktree 沒有 `.env.research`，演練只讀 `INDUSTRYFLOW_DRILL_HOME` 的祕密。正式服務指紋不變。
- [x] 7.4 `deploy-rehearsal --commit <PR HEAD>`，驗證：
  - smoke 通過。
  - 資料變動只出現在預期的 legacy 地圖表：散文 CRLF 改為 LF、roles／relations 重新寫入。
  - `theme_assessment_versions` 沒有增加。若增加，先在本 change 修正比較方式，再重做本 task。

  結果：`fce6cbf` smoke 六項全過；遷移 `0017 → 0017`；`theme_assessment_versions` 7 → 7。52 張表中只有 `public.sources` 變動（123 列，列數不變）：以備份還原的對照逐欄比對，只有 7 列 `url` 與 83 列 `data.registry_url`，是 initialize 的 `import_documents` 依 `sources.yaml` 寫回作者端形式、每小時的 `register_sources` 再寫回抓取用網址，切換前每次 `up` 都會發生，與本 change 無關。design 預期的「散文 CRLF 改為 LF」沒有發生：`import_map` 以 `read_text()` 讀檔時已把 CRLF 正規化，正式 DB 的 `segments`／`themes` 散文本來就沒有 CR（0 列），roles／relations 重新寫入但內容相同。正式服務指紋不變。
- [x] 7.5 `rollback-rehearsal` 回到基準 image。驗證：
  - 沒有執行 initialize，smoke 通過。
  - `theme_assessment_versions` 不變。
  - 報告判定「只差擴充遷移」。

  結果：從 `fce6cbf` 回到 `7ebbc68`，沒有執行 initialize，以 `up --no-deps` 替換 api／web，smoke 六項全過；52 張表全部不變，`theme_assessment_versions` 7 → 7；判定 `expand-only`，中間沒有遷移（兩者都在 `0017`）。報告 `rollback-rehearsal-20261027T195309Z.json`。正式服務指紋不變。
- [x] 7.6 收縮遷移的拒絕：以 `6c0afd1^`（`0017` 之前）建置 image，嘗試讓演練回退到它。驗證：回退被拒絕，訊息指出 `0017` 與回退邊界，演練服務不變。

  結果：`6c0afd1^` 為 `5ceb9a6`，image `5ceb9a62c4f7` 的 labels 為 head `0016`、收縮 `0009`。`rollback-rehearsal --commit 6c0afd1^` 在動任何容器前拒絕：「Rolling back from 0017 to 0016 crosses contract migration(s) 0017; restore the rollback-boundary backup 20261027T193003Z (the backup this drill was restored from)」。演練容器的 ID、image 與啟動時間前後相同。報告 `rollback-rehearsal-20261027T195457Z.json`。
- [x] 7.7 執行演練環境的 `pg-check --suite all`。驗證：
  - 全部通過。
  - 正式 cluster 沒有新增資料庫（以 `psql -l` 唯讀比對）。
  - 正式 volume 的修改時間不變。

  結果：第一次以 `fce6cbf` 執行 474 秒，157 passed、1 error。錯誤是 `test_scaled_relation_manifest_is_accepted` 的 `scaled_tree` fixture 匯入 `scripts/research_scale.py`，而 API image 只帶兩支驗證腳本；這是 2026-10-24 PR #9 起就存在的問題（`7ebbc68` 的 `all` 已包含這個檔案），與本 change 無關。`8b6e2d9` 讓該 fixture 在沒有這支腳本時 skip（CI 從 checkout 照常執行），`cbabf01` 讓 `pg-check` 失敗時也留下報告與 log。第二次執行途中因主機記憶體不足被中止（不是測試失敗）。2026-10-28 以 `24d0a8c` 重跑：**157 passed、1 skipped**（即上述 scaled 測試），478.5 秒，報告 `pg-check-20261028T095148Z.json`，`worktree_dirty: false`。`industry_research_test` 只建在演練 cluster；正式 cluster 的資料庫清單、`industry_research_test` 的交易與寫入計數、各 volume 及資產／managed Git 的修改時間與檔案數，三次執行前後都不變。
- [x] 7.8 防護與遮蔽的實機確認：在本 worktree（沒有部署目錄標記，也沒有正式祕密）執行以下操作：
  - `research_lab.py deploy --commit <任一 main 提交>`
  - `research_lab.py setup`
  - 一個故意失敗的演練步驟

  驗證：
  - 前兩個指令在改變任何狀態前就拒絕，`setup` 沒有寫入祕密。
  - 失敗輸出中沒有演練祕密或正式祕密。
  - 正式服務不變。

  結果（本 worktree，沒有 `deployments/home.json`，也沒有 `.env.research`）：`deploy --commit 7ebbc68` 以「No deployments/home.json here」拒絕，HEAD、git status、`FETCH_HEAD` 都沒變，也沒有建立 `deployments/`。`setup` 以「Volume industryflow-research_pg-data already exists」拒絕，沒有寫入 `.env.research`。故意失敗的演練步驟（在演練 worker 印出 `$DATABASE_URL` 後 exit 3）：錯誤訊息含 exit 3 與連線字串，但密碼處為 `[REDACTED]`，4 個演練祕密值出現 0 次；這個 checkout 沒有正式祕密檔，演練也從不載入它。正式服務指紋不變。
- [x] 7.9 把 7.2–7.8 的結果整理進 `docs/research-deployment.md` 的「演練紀錄」，並在本檔各 task 註記。驗證：文件中的數字與 `.work/research-drill/` 的報告一致。

  結果：「演練紀錄」一節與各 task 註記已更新；文件中的數字（RTO 52.7 秒、預演部署 61.0 秒、`theme_assessment_versions` 7 → 7、52 張表、pg-check 157 passed／1 skipped／478.5 秒）都與 `.work/research-drill/` 的 restore、deploy-rehearsal、兩份 rollback-rehearsal 與 pg-check 報告逐項核對相符。CI：最後一個含程式變更的提交 `24d0a8c` 全綠（push run `40575896080`、pull_request run `40575906955`）；之後的提交只改文件與本檔。

## 8. code review 修正（merge 前完成）

`/code-review` 的類別 1、2 共 13 項，加上修正過程中發現、屬於本 change 範圍的疏漏（8.2 的收縮清單重算、8.8）。類別 3（`prefect` 資料庫不在備份內、`scheduler-start`／`rollback` 沒有原服務互斥檢查）另開 change 處理。

- [x] 8.1 遷移規則補強（design D8；code review #1、#5、#6）：
  - `ALTER TABLE` 中不寫 COLUMN 的 `DROP <欄位>`，與沒有 `DEFAULT` 的 `ADD <欄位> … NOT NULL`。
  - `DROP INDEX`、`ALTER … DROP DEFAULT`、`DROP ROLE`、`DROP EXTENSION`、`ALTER POLICY`。
  - Alembic `add_column` 欄位帶 `nullable=False` 或 primary key，卻沒有 `server_default`。
  - 分析 `upgrade()` 引用的模組層常數與它呼叫的模組層 helper（遞迴），仍不看 `downgrade()`。
  - `0016` 加 `EXPAND_REVIEWED`，只加標記行。

  驗證：`tests/test_migration_rules.py` 為每條新規則加入失敗與通過案例（含常數與 helper）；實際目錄的 lint 通過，收縮遷移仍為 `0009`、`0017`；`git diff` 中 `0016` 只有標記行。

  結果：新規則對既有遷移只多標出 `0016` 的 `ALTER POLICY`，加上 `EXPAND_REVIEWED` 後實際目錄通過，收縮仍為 `0009`、`0017`；`7ebbc68` 這類早於標記的提交則把 `0016` 也算作收縮（只會更嚴格）。`tests/test_migration_rules.py` 30 項通過。
- [x] 8.2 image 同一性與回退收縮清單（design D3、D7；code review #2）：
  - 既有 image 只比對 revision、alembic head、Prefect 版本與 `build`，不比對 `contract-revisions`。
  - 回退判斷除了部署紀錄的聯集，再併入以現行規則重算的目前提交收縮清單。

  驗證：測試涵蓋「只有 `contract-revisions` 不同時重用」「其他 label 不同時仍拒絕」「紀錄中未列、但現行規則判為收縮的遷移會讓回退被拒絕」。

  結果：`IDENTITY_LABELS` 只含 revision、alembic head、Prefect 版本與 `build`；回退以 `commit_info(目前提交)` 併入收縮清單。三種情境各有測試並通過。
- [x] 8.3 Prefect 檢查（design D6、D7；code review #3、#4）：
  - 無法查詢時拒絕，`--force` 略過。
  - 替換排程服務前再檢查；有執行中的 run 時最多等 10 分鐘，仍未結束就寫入失敗紀錄、保留舊服務；收縮部署則等待後照樣替換並記下被中斷的 run。

  驗證：測試涵蓋查詢失敗被拒絕、`--force` 略過、替換前出現的 run 會等待、逾時中止（沒有替換、有失敗紀錄）、收縮部署逾時後仍替換。

  結果：`prefect_busy()`、`wait_for_idle()`（10 分鐘）與 `scheduler_idle()` 在部署與回退兩邊都套用；測試在 `test_research_deploy.py`、`test_research_rollback.py` 通過。
- [x] 8.4 紀錄必定寫入（design D6；code review #9、#15）：
  - 部署與回退在任何例外（含 KeyboardInterrupt）下都寫入紀錄；寫紀錄時查詢 Docker 失敗，仍以已知欄位寫入。
  - 上一版腳本在目標腳本執行期間忽略 Ctrl-C；目標腳本沒有留下紀錄時，依容器實際的 revision 補記失敗紀錄，並據此決定 checkout。

  驗證：測試涵蓋替換中的 KeyboardInterrupt、`finish()` 中 Docker 失敗、目標腳本未留紀錄時的補記（容器已換與未換兩種）。

  結果：`replace_and_smoke()` 接住 BaseException 後先寫紀錄再重新拋出；`finish()` 在 Docker 失敗時寫入 `state_error`；`hand_over()` 交接期間忽略 SIGINT，目標腳本以非 0、非拒絕（`REFUSED_EXIT`）結束且沒有紀錄時，以 `record_from_containers()` 補記。測試通過。
- [x] 8.5 rollback 交接給目標版本的腳本（design D7；code review #7）：現行腳本完成 lock、防護、目標有效性、相容性、Prefect 與回退前備份，checkout 後以目標腳本建置、替換、smoke 並寫入紀錄。

  驗證：`tests/test_research_rollback.py` 確認相容性判斷與備份都在 checkout 之前、目標腳本以 handover 接手、目標腳本失敗時部署目錄回到運行中的提交。

  結果：`rollback()` 只做判斷、備份與交接，`rollback_target()` 由目標版本的腳本執行建置、`validate`、替換、smoke 與紀錄。`tests/test_research_rollback.py` 依新結構重寫，23 項通過。
- [x] 8.6 備份（design D11；code review #10）：等 lock 上限 30 分鐘；先寫入 `<時間>.partial`，完成才改名；下一次備份清除殘留的 `.partial`。

  驗證：測試涵蓋等待上限、成功後只剩正式資料夾、失敗與中止後殘留 `.partial` 被下一次備份清除、`--backup latest` 與清理都不選 `.partial`。

  結果：`BACKUP_LOCK_WAIT = 1800`；主副本與第二份副本都先寫 `.partial` 再改名，失敗時刪除這次的資料夾，下一次備份在持有 lock 時清掉殘留。測試通過。
- [x] 8.7 演練修正（design D10；code review #8、#11、#13）：
  - smoke 在演練中不比對 db 的 working_dir。
  - 最近一次 `restore` 的基準記在 `INDUSTRYFLOW_DRILL_HOME`，並核對演練 db 容器 ID。
  - `setup --sec-user-agent` 可補寫或更新既有 env。
  - `research_load.py` 記錄演練實際運行的 image 與 revision。

  驗證：測試涵蓋從另一個 worktree 預演時 smoke 通過、db 容器不同時 `rollback-rehearsal` 要求 `--commit`、`setup` 補寫 SEC 聯絡字串、`research_load` 的 image 取自運行中的演練 API。

  結果：演練的 smoke 帶 `working_dir_skip=('db',)`；`restore` 另寫 `INDUSTRYFLOW_DRILL_HOME/last-restore.json`（含 db 容器 ID），`rollback-rehearsal` 只在容器相同時採用；`setup --sec-user-agent` 補寫或取代既有值；`research_load.py` 改用 `running_images()`。測試通過。
- [x] 8.8 回退期間拒絕 `public-snapshot`（design D11、Risks）。驗證：測試確認運行中的紀錄是 `rollback` 時拒絕、下一次部署後恢復。

  結果：`main()` 在運行中的紀錄為 `rollback` 時拒絕 `public-snapshot`；`PublicSnapshotTests` 兩項通過。
- [x] 8.9 更新文件：`docs/research-deployment.md`（部署、回退、遷移規則、演練）、`research-backup.md`（等待上限、`.partial`）、`public-snapshot.md`（回退期間拒絕）。驗證：文件描述與 8.1–8.8 的測試一致，文件中的演練指令與 `research_drill.py --help` 一致。

  結果：`research-deployment.md` 更新部署（Prefect 無法查詢、替換前再檢查、紀錄必定寫入、交接期間的 Ctrl-C 與補記）、回退（交接給目標腳本、收縮清單重算）、建置（只比對 identity labels）、遷移規則與 `0016`、演練（db working_dir、`last-restore.json`）與紀錄欄位；`research-backup.md` 更新等待上限、`.partial` 與 `setup --sec-user-agent`；`public-snapshot.md` 改為回退期間由程式拒絕。`DocumentedCommandTests` 與 `test_record_fields_are_documented` 通過。
- [x] 8.10 重新驗證：
  - root unittest 全數通過，CI 全綠（run 編號記在本 task）。
  - 演練：`down` 後重做 `restore`、`deploy-rehearsal`、`rollback-rehearsal` 與收縮遷移的拒絕，再以 PR HEAD 重跑 `pg-check --suite all`（`0016` 的標記進了 backend），並重做 7.8 的防護檢查。
  - 每一步核對正式服務指紋不變；結果記入 `docs/research-deployment.md` 的「演練紀錄」。

  結果（2026-10-29，提交 `4ceb598`）：root unittest 243 項通過；CI 全綠（push run `40723794379`、pull_request run `40723804858`）。演練：`down` 後以 `20261027T193003Z`、基準 `7ebbc68` 還原，RTO 61.5 秒、核對全部相符，基準 image 雖然收縮清單 label 與現行規則不同仍被重用（8.2 的實機確認）；`deploy-rehearsal --commit 4ceb598` smoke 全過、`theme_assessment_versions` 7 → 7、只有 `public.sources` 變動；`rollback-rehearsal` 從 `last-restore.json` 取得基準，沒有 initialize、52 張表不變、判定 `expand-only`；回退到 `6c0afd1^` 被拒絕並指出 `0017`；`pg-check --suite all` 157 passed、1 skipped（492.1 秒）；7.8 的防護與遮蔽檢查重做通過。正式服務指紋（容器、DB 清單、`industry_research_test` 計數、volume、資產與 managed Git、`:dev` image）每一步都不變。結果記在「演練紀錄」的「group 8 修正後的重新驗證」。

## 9. merge 後：正式環境切換（需 Boris 同意並在場；不阻擋 merge）

- [ ] 9.1 建立部署目錄：
  - `git clone` origin 到 `C:\Users\User\industryflow-prod`，`checkout --detach <merge 提交>`。
  - 建立 `.venv` 與 `deployments/home.json`。

  驗證：`research_lab.py status` 回報「尚無部署紀錄」，`git status` 乾淨。
- [ ] 9.2 複製 `.env.research` 與 `backups/research` 到部署目錄。驗證：
  - 逐檔 SHA-256 相同。
  - Boris 確認祕密已另存受保護副本，例如密碼管理器。
- [ ] 9.3 保留回復點：
  - 以 `research_lab.py adopt` 把目前的 `:dev` image 另標為 `industryflow-research-api:pre-ledger`、`industryflow-research-web:pre-ledger`。
  - 寫入一筆 `adopt` 紀錄（容器、image ID、alembic 版本）。

  驗證：`status` 顯示 `adopt` 紀錄，舊 image 有新 tag。
- [ ] 9.4 首次部署：避開整點 :07，從部署目錄執行 `deploy --commit <merge 提交> --recreate-db`。驗證：
  - db 在內的容器都已重建。
  - bind mount 與 `working_dir` label 都指向部署目錄。
  - smoke 通過，紀錄為 `succeeded`。
  - 停機時間記下。
  - 下一個整點的 `official-information/hourly` flow run 成功。
- [ ] 9.5 改寫備份排程（design D11）後手動觸發一次。驗證：
  - `backup-log.jsonl` 有新紀錄，D: 有對應副本。
  - manifest 含運行容器的 image ID、revision、`alembic_version`。
- [ ] 9.6 把 9.5 的備份還原到演練環境。驗證：`restore` 以 manifest 的 revision 為基準 image，核對全部通過。
- [ ] 9.7 封住開發 checkout：
  - 放入 tombstone `.env.research`。
  - Boris 移除開發 checkout 中原本的祕密與 `backups/research`，並刪除本機舊 branch。

  驗證：在開發 checkout 執行 `research_lab.py check` 會拒絕，且沒有產生祕密；部署目錄的 `status` 沒有不一致。
- [ ] 9.8 在 `docs/research-acceptance.md` 新增「十三、正式環境切換（separate-research-production-deployment task 9）」一節，內容包括步驟（UTC）、結果、停機時間與限制。驗證：表格中的數字與部署紀錄、備份 log 一致。

## Workflow follow-up

- group 1–8 全部勾完後，PR 才交給 Boris merge。本 change 是 D12 所述的例外：merge 前**不** archive，因為 group 9 只能在 merge 後進行。
- merge 後依 group 9 切換正式環境；完成後以後續的 docs PR 提交 9.8 的紀錄，並 archive 本 change，把 `platform-runtime` 的 delta 合入主 spec。
- code review 類別 3（`prefect` 資料庫不在備份內、`scheduler-start`／`rollback` 沒有原服務互斥檢查）另以新的 change 處理，不在本 change。
- archive 之後，agent 的 memory「verify-before-merge」要改成新規則：演練環境驗證、merge 後部署。
