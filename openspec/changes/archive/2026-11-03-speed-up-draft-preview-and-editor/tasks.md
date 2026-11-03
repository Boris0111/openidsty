# Tasks

**實作環境**：

- 實作在本 change 自己的 worktree 與 branch 進行，不切換主 checkout。

**測試怎麼跑**：

- root 單元測試以 `python -m unittest discover -s tests -p "test_*.py"` 執行，不需要 Docker。
- 需要 PostgreSQL 的後端測試，在臨時、獨立的 PostgreSQL 容器上以本 branch 的程式碼執行；整合時再由演練的 `pg-check` 跑一次。

**演練環境的規則**（依 AGENTS.md 與 `docs/research-deployment.md`「合併前演練」）：

- 實機量測一律從本 PR 的 worktree 以 `scripts/research_drill.py` 進行。
- 開始前記錄正式服務的指紋（容器、image、資料庫清單、volume）；每一步完成後核對一次，必須全部不變。
- Docker Desktop 是手動啟動。沒有在執行時請 Boris 打開；要重啟它之前，先徵得 Boris 同意。

## 1. 量測工具

- [x] 1.1 （2026-11-02：`--help` 可執行；root `tests/test_research_draft_bench.py` 10 項通過，新增 4 項：timing log 解析與中位數、沒有 log 時為 `null`、20 次輪流的頁面清單、`measure()` 報告的 `draft_id`／預覽統計／圖解分開計。原本只供單次預覽選頁的 `preview_entity()` 與 `validations_since()` 已無呼叫端，一併移除）`scripts/research_draft_bench.py` 的預覽量測改為多次（design D8）：
  - 驗證一次後，依固定清單輪流預覽 20 次（`--previews`，預設 20），記錄 p50、p95 與最大值。
  - 從演練 API 容器的 log 擷取 `draft-preview timing`，算出各段的中位數。修正前的程式沒有這行 log，報告記為 `null`，不算失敗。
  - 報告寫出 `draft_id`，給 1.2 的腳本使用。
  - 圖解請求照舊另外記錄。

  驗證：
  - `python scripts/research_draft_bench.py --help` 可以執行。
  - root `tests/test_research_draft_bench.py` 新增案例並通過：預覽的統計欄位、log 行的解析（含沒有 log 的情況）、`draft_id` 欄位。
- [x] 1.2 （2026-11-02：`--help` 可執行；`npm run test:unit` 23 項通過，含新增的 `editor-latency.node.cjs` 7 項。另加 `--interval`（預設 150 ms）、`--timeout`（預設 180 秒）、`--env-file`。trace 摘要以 self time 分類，`other` 另列前幾名事件名稱，讓拼字檢查這類不屬於前四類的成本看得到）新增 `scripts/research_editor_latency.cjs`（design D7）：
  - 參數：`--draft`、`--path`、`--mode raw|form`、`--keys`（預設 30）、`--label`、`--trace`、`--origin`（預設 `http://127.0.0.1:3016`）。
  - owner 密碼從 `INDUSTRYFLOW_DRILL_HOME` 的演練 env 檔讀取，不印出，也不寫入報告。
  - 延遲取 Event Timing 中同一個 `interactionId` 的最大 `duration`；每個按鍵最多等 180 秒，逾時記為失敗並繼續。
  - 加 `--trace` 時輸出 trace 摘要：超過 50 ms 的主執行緒工作，依 script、style／layout、paint、GC、其他分類。
  - 報告寫到 `.work/research-editor-latency/<label>.json`。
  - 百分位、互動分組、trace 分類寫成純函式並匯出。

  驗證：
  - `node scripts/research_editor_latency.cjs --help` 可以執行。
  - 新增 `frontend/tests/editor-latency.node.cjs`，涵蓋百分位、`<16` 的處理、逾時記錄與 trace 分類，並加進 `npm run test:unit`；`npm run test:unit` 全數通過。

## 2. 修正前的基準（演練環境）

- [x] 2.1 （2026-11-02：備份 `20261101T193004Z`、基準 `01de3e0`，還原核對全部相符，RTO 66.7 秒。`before-real` 預覽 20／20 成功，p50 2,636、p95 2,819、最大 2,869 ms；`before-scaled` 20／20，p50 9,159、p95 9,854、最大 10,320 ms。正式服務指紋在 down、restore、owner、量測後都與開始時相同）量出修正前的預覽基準：
  - `research_drill.py down`，再 `restore --backup latest`。演練此時執行的是備份的基準 image，也就是 `main` 的程式。
  - 以 1.1 的工具量 `before-real` 與 `before-scaled`；擴大資料以 import 匯入，與上一輪相同。

  驗證：
  - 兩份報告都存在，各含 20 次預覽的 p50、p95 與最大值。
  - 正式服務的指紋不變。
- [x] 2.2 （2026-11-02：三組都沒有逾時、30 字都打進文字框。`before-real-company` p95 24、最大 32 ms；`before-real-relations`（49,473 字）p95 24、最大 32 ms；`before-scaled-relations`（972,942 字）p95 168、最大 168 ms。**108 秒沒有重現**，修正前就已符合 spec 的延遲目標。trace：60 個長工作合計 3,902 ms，paint 41%、其他（原生文字編輯與選取同步）26%、style／layout 25%、script 8%、GC 0，沒有拼字檢查事件。主因是 Chromium 處理百萬字文字框，不在 D6 主要範圍內，已告知 Boris，group 4 等他決定。量測中修正了 latency 腳本的 trace 分類，並加上「輸入後增加的字數」核對）量出修正前的輸入延遲，並查清 108 秒的成因：
  - 量三組：
    - `before-real-company`：真實資料的 `company-auras.md`，表單模式。
    - `before-real-relations`：真實資料的 `research-relations.yaml`，原始文字模式。
    - `before-scaled-relations`：擴大資料的關係檔，原始文字模式，加 `--trace`。
  - 以 trace 摘要判定最長那次按鍵的主因屬於哪一類。

  驗證：
  - 三份報告與 trace 摘要都存在。
  - `docs/research-performance.md` 新增「預覽與編輯器修正前後（2026-11，`speed-up-draft-preview-and-editor`）」一節，寫入修正前的環境、版本、數字，以及 108 秒的判定。若沒有重現 108 秒，照實記錄量到的最大值。
  - **如果主因不在 design D6 處理的範圍內**（例如是 Chromium 本身排版文字框的成本，而不是 React 重繪或拼字檢查），先告知 Boris，由他決定是否照 D6 繼續，再進行 group 4。

## 3. 投影批次寫入（後端）

- [x] 3.1 （2026-11-02：臨時 PostgreSQL 上 `test_research_compile.py`、drafts、publication、v2、publication_interfaces、restart 共 40 passed、1 skipped。與 design 的差異：同一張表內「連續且形狀相同」的列合成一批，形狀改變就另起一批，各批依加入順序送出。這完整保留原本的寫入順序，比「依欄位組合分組」更嚴格；欄位會變動的表（如 listings）只是多幾批。PG 套件以 3 GB 上限的容器執行；之後一次完整 `all` 清單在約 42%（96 項全過）時因主機記憶體不足被系統中止，完整套件改由 5.2 的 `pg-check --suite all` 執行）`research_compile.py` 新增 `ProjectionWriter` 與 `PROJECTION_ORDER`（design D1），`project()` 改用它：
  - 只在兩個時間點 `flush()`：把 release 改成 `ready` 之前，以及 `activate_bootstrap` 之前。
  - `project()` 新增 keyword 參數 `immediate=False`。
  - 未列在 `PROJECTION_ORDER` 的表直接拋錯。
  - 模組層級的 `insert()`、`document()` 保持立即寫入。
  - 回傳值新增 `timings`（design D4），只含各階段的毫秒數。

  驗證：
  - `backend/tests/test_research_compile.py` 等離線測試通過。
  - 臨時 PostgreSQL 上，`test_research_drafts.py`、`test_research_publication.py`、`test_research_v2.py`、`test_publication_interfaces.py`、`test_research_restart.py` 全數通過。
- [x] 3.2 （2026-11-02：`test_projection_writer.py` 的 `test_legacy_history_reads_lookups_once_and_keeps_every_row` 與 `test_missing_entity_message_is_unchanged` 通過。預期列由測試內保留的舊規則（逐列查詢）推得，六種都有；兩種寫法下 `public.*` 的查詢都是 9 次（3 張對照表各 1 次、6 張歷史表各 1 次），與舊歷史的筆數無關）`legacy_history()` 改為每張表只讀一次（design D2），寫入改走寫入器。

  驗證：臨時 PostgreSQL 上新增測試並通過：
  - 建立六種舊歷史（assessment、indicator-definition、indicator-observation、technical-document、technical-observation、technical-review）各至少一筆。
  - 斷言寫出的 legacy_history 列（entity、kind、legacy ID、content hash、data）與依原規則推得的預期列完全相同。
  - 引用不存在的實體時，錯誤訊息與修改前相同。
- [x] 3.3 （2026-11-02：臨時 PostgreSQL 上 10 passed，含 slow。擴大資料案例的 call 15.9 秒（兩種寫法各投影一次並逐表算 md5），另有 setup 建資料樹 5.9 秒。另含 3 個不需 DB 的寫入器單元測試，CI 離線也會執行：送出順序、每批 1,000 列、表內順序與衝突規則的先後。臨時環境為了讓 `authored`／`scaled_tree` 和 CI 一樣走 `git archive`，在容器內把程式複製成臨時 Git 快照後執行）新增 `backend/tests/test_projection_writer.py`（design D5 第一層），並加入 `research_pg_checks.py` 的 `all` suite：
  - 同一份 bundle 分別在兩個 savepoint 內以立即模式與批次模式投影。每張 `research.*` 投影表依主鍵排序後算 hash，比對兩邊相同，release ID 與 content hash 也相同。
  - 資料包括 `tests/fixtures/valid`、目前已發布的研究，以及擴大資料。擴大資料標為 `slow`；`scripts/` 不存在時（API image）skip，與既有的 scaled-tree 測試相同。
  - 失敗案例：寫入未列出的表時拋錯；一批寫入違反限制（重複的 relation ID）時整次 rollback，savepoint 外查不到這次的任何列。

  驗證：
  - 臨時 PostgreSQL 上全數通過，含 slow 案例；本 task 記錄 slow 案例的耗時。
  - `grep -n "test_projection_writer" backend/app/research_pg_checks.py` 有結果。
- [x] 3.4 （2026-11-02：臨時 PostgreSQL 上 `test_preview_logs_stage_times_only_and_leaves_no_candidate` 通過。3 次預覽剛好 3 行，欄位都是數字，不含實體 ID、名稱或內文；預覽後、以及 graph 階段故意拋錯後，所有投影表的列數都與預覽前相同）`draft_preview` 在 rollback 後記一行 INFO `draft-preview timing`（design D4），欄位：草稿 ID、修訂號、`project_ms`、`flush_ms`、`detail_ms`、`graph_ms`。預覽的回應格式不變。

  驗證：臨時 PostgreSQL 上新增測試並通過：
  - 每次預覽剛好記一行，欄位都是數字。
  - log 不含實體名稱或內文。
  - 預覽後資料庫沒有新增 release，也沒有投影列（spec「預覽不留下候選版本」）。
  - 預覽途中拋錯時，同樣沒有留下任何列。
- [x] 3.5 （2026-11-02：共用函式為 `research_compile.projection_tables()`，3.3 的等價測試都用它；實機執行在 5.2）`research_rebuild_check.py` 加上立即模式與批次模式的比對（design D5 第二層）：
  - 在既有的斷言之前，先在 savepoint 內以立即模式投影並記下各表的列數與 md5，rollback 後再以批次模式投影，比對必須相同。
  - 報告 JSON 新增 `projection_tables` 與 `writer_equivalent`。
  - 比對用的「各表列數與 md5」寫成共用函式，3.3 的測試也用同一個函式。

  驗證：
  - 3.3 的測試透過共用函式涵蓋比對邏輯。
  - 實機執行在 5.2。
- [x] 3.6 （2026-11-02：兩個 grep 都有結果）更新文件：
  - `docs/research-data-model.md` 的 rebuild-check 段落補上寫入方式的比對與新的報告欄位。
  - `docs/research-drafts.md` 的預覽段落補上 `draft-preview timing` 這行 log。
  - `docs/research-deployment.md`「合併前演練」中 `rebuild-check` 的註解改為「PR 改了研究內容的編譯或投影時」。
  - `research_compile.py` 的 `PROJECTION_ORDER` 旁註明：新增投影表時必須加入，並依 foreign key 排序。

  驗證：`grep -n "writer_equivalent" docs/research-data-model.md`、`grep -n "draft-preview timing" docs/research-drafts.md` 都有結果。

## 4. 管理頁編輯器（前端）

**2026-11-03 Boris 決定**：修正前的量測（2.2）已在目標內，主因是 Chromium 本身，所以文字框**維持 controlled，只加低風險屬性**（design D6）。原本的 uncontrolled 改動與 spec「管理頁儲存的就是畫面上的內容」一併移除，4.1、4.2 依此改寫。

- [x] 4.1 （2026-11-03：`npm run typecheck` 通過）`frontend/components/ResearchEditor.tsx` 的兩個文字框加上屬性（design D6），維持 controlled：
  - 原始文字框：`spellCheck={false}`、`wrap="off"`，並關閉 autocomplete、autocorrect、autocapitalize。
  - 表單內文的文字框：`spellCheck={false}`。
  - 輸入、儲存、切換模式與 dirty 判定都不改。

  驗證：`npm run typecheck` 通過。
- [x] 4.2 （2026-11-03：本 branch 的 `next start`（3017，`API_ORIGIN` 指向演練 API 8016）上，mock API 的 4 項通過：新增的桌機、手機各 1 項，既有的草稿編輯桌機、手機各 1 項。檔案中另 2 項打真實 API 的既有測試在 3017 失敗，原因是演練 API 只允許 3016 的管理來源（回 403 `admin-origin-denied`），與本 change 無關，改在 5.2 部署本 branch 到演練後對 3016 執行完整檔案。`npm run test:e2e:offline` 64 passed）`frontend/tests/research-editor.spec.ts` 新增測試，桌機與手機各一次：
  - 原始文字框（YAML 檔）帶有 `spellcheck="false"`、`wrap="off"`、`autocomplete="off"`、`autocorrect="off"`、`autocapitalize="off"`。
  - 表單內文的文字框帶有 `spellcheck="false"`，仍會自動換行。
  - 在原始文字框輸入後顯示「有未儲存修改」，儲存送出的內容含剛輸入的字元（controlled 行為不變）。

  驗證：
  - 以本 branch 的 `next start`（127.0.0.1:3017，不碰正式服務）設 `RESEARCH_E2E` 執行 `research-editor.spec.ts`，全數通過（含既有測試）。
  - `npm run test:e2e:offline` 全數通過。

## 5. 修正後的整合量測與記錄（演練環境，從本 change 的 worktree）

- [x] 5.1 （2026-11-03：draft PR #14。PR HEAD `21560f6` 的 push run `41579204107`、PR run `41579210281` 全綠；之前的 `20d3533`、`8baefca` 也全綠）推送 branch、開 draft PR，確認 GitHub Actions 全部通過（validator、root unittest、離線後端、前端 typecheck／unit／build、離線 E2E、公開靜態頁）。驗證：PR 與 run 編號記在本 task。
- [x] 5.2 （2026-11-03，第二輪，PR HEAD `21560f6`。第一輪對 `8baefca` 的 `pg-check` 有 2 項失敗：新測試讀 root `tests/fixtures/valid`，API image 裡沒有這個目錄。修正後從 `down` 重做。報告都在本 worktree 的 `.work/research-drill/`：
  - `restore-20261103T043754Z.json`：備份 `20261102T193005Z`、基準 `01de3e0`，核對全部相符，RTO 99.1 秒（`restore-20261103T042311Z.json` 為第一輪）。
  - `deploy-rehearsal-20261103T044130Z.json`：smoke 全過，遷移 `0017 → 0017`，只有 `public.sources` 變動（initialize 的既有行為），其餘 51 張表不變，67.9 秒。
  - `pg-check-20261103T044848Z.json`：165 passed、3 skipped，6 分 53 秒；含 `test_projection_writer.py`，fixture 等價案例與擴大資料案例在 image 內 skip（CI 與臨時 PostgreSQL 上已通過）。
  - `rebuild-check-20261103T044926Z.json`：`writer_equivalent: true`，21 張投影表兩種寫法相同；254 個研究物件，舊歷史 assessment 7、指標定義 9、指標觀測 29、技術文件 8、技術觀測 8、技術審查 8，與演練 DB 中還原自正式備份的資料相同。
  - 正式服務指紋在每一步前後都與開始時相同）演練環境依序執行：
  - `restore --backup latest`
  - `deploy-rehearsal --commit <PR HEAD>`
  - `pg-check --commit <PR HEAD> --suite all`
  - `rebuild-check --commit <PR HEAD>`

  驗證：
  - `deploy-rehearsal` 的 smoke 通過。
  - `pg-check` 全數通過，含 `test_projection_writer.py`。
  - `rebuild-check` 報告的 `writer_equivalent` 為 `true`，舊歷史的各類筆數與正式資料相同。
  - 報告路徑記在本 task；正式服務的指紋不變。
- [x] 5.3 （2026-11-03：量測完成。擴大資料的預覽未達原定 2 秒，**Boris 2026-11-03 決定目標改為 3 秒後收尾**，spec 已同步修改；以新目標判定全部達標。真實資料預覽 20／20 成功，p95 833 ms ≤ 1 秒；擴大資料 20／20 成功，p95 2,899 ms（> 原定 2 秒、≤ 新目標 3 秒），分段中位數 project 2,079（其中 flush 1,579）、detail 438、graph 45 ms。輸入延遲三組 p95 24／24／144 ms、最大 32／24／168 ms、沒有逾時，達標。API 記憶體高點 102／185 MiB，上一輪 178 MiB。另對演練 3016 跑完整 `research-editor.spec.ts`，6 項全過，含 4.2 留下的 2 項真實 API 測試）在 5.2 部署的演練上，量修正後的數字：
  - 預覽：`after-real` 與 `after-scaled`。
  - 輸入延遲：`after-real-company`、`after-real-relations`、`after-scaled-relations`（加 `--trace`）。

  驗證：報告中下列項目符合 spec：
  - 「已驗證修訂的閱讀預覽有時間上限」：真實資料 p95 ≤ 1 秒，擴大資料 p95 ≤ 3 秒（原定 2 秒，2026-11-03 Boris 調整），20 次預覽都成功。
  - 「管理頁編輯大型文件不會凍結」：三組按鍵延遲的 p95 ≤ 300 毫秒，最大值 ≤ 1 秒，沒有逾時。
  - API 記憶體高點與上一輪的 178 MiB 比較，並記錄下來。

  未達標時，記錄實際數字與分段耗時（`draft-preview timing`、trace 摘要），交給 Boris 決定。不得調整目標來湊數。
- [x] 5.4 （2026-11-03：`rollback-rehearsal-20261103T045540Z.json`：`21560f6` → `01de3e0`，判定 `expand-only`，沒有執行 initialize，smoke 全過，52 張表全部不變；正式服務指紋不變）`rollback-rehearsal`：回到 restore 的基準 image，判定應為 `expand-only`，回退後 smoke 通過。驗證：報告路徑記在本 task；正式服務的指紋不變。
- [x] 5.5 （2026-11-03：三處文件都已更新；以一次性腳本從 10 份 JSON 報告重算並比對文件中的 49 個數字，全部一致。Boris 調整擴大資料目標後，兩份文件的判定一併更新）記錄結果：
  - `docs/research-performance.md` 的新一節補上修正後的數字、分段耗時與 108 秒的處理結果。
  - 上一節「未在本 change 處理的後續問題」逐項標註處理結果。
  - `docs/research-acceptance.md`「草稿編輯的剩餘成本」這一列改為修正後的狀態。

  驗證：文件數字與 `.work/research-draft-bench/*.json`、`.work/research-editor-latency/*.json` 以程式逐一比對一致。

## Workflow follow-up

- 1–5 全部勾完、在 branch 上 archive（`research-publishing` 主 spec 合入本 change 新增的三項 requirement），CI 再確認一次全綠之後，PR 才交給 Boris merge（AGENTS.md「先驗證、再 merge」）。
- merge 後由 Boris 依 `docs/research-deployment.md` 從部署目錄部署，部署紀錄的 smoke 結果就是紀錄。
- 部署後 Boris 在正式 `/admin` 預覽幾頁，確認回應明顯變快；結果簡短記在 `docs/research-acceptance.md`。這是正式環境的確認，不阻擋 merge。
- 之後依產品順序進入地圖廣度擴充（光通訊、電網／電力設備、網路系統）。
