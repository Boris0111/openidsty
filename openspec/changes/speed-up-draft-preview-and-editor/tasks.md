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

- [ ] 1.1 `scripts/research_draft_bench.py` 的預覽量測改為多次（design D8）：
  - 驗證一次後，依固定清單輪流預覽 20 次（`--previews`，預設 20），記錄 p50、p95 與最大值。
  - 從演練 API 容器的 log 擷取 `draft-preview timing`，算出各段的中位數。修正前的程式沒有這行 log，報告記為 `null`，不算失敗。
  - 報告寫出 `draft_id`，給 1.2 的腳本使用。
  - 圖解請求照舊另外記錄。

  驗證：
  - `python scripts/research_draft_bench.py --help` 可以執行。
  - root `tests/test_research_draft_bench.py` 新增案例並通過：預覽的統計欄位、log 行的解析（含沒有 log 的情況）、`draft_id` 欄位。
- [ ] 1.2 新增 `scripts/research_editor_latency.cjs`（design D7）：
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

- [ ] 2.1 量出修正前的預覽基準：
  - `research_drill.py down`，再 `restore --backup latest`。演練此時執行的是備份的基準 image，也就是 `main` 的程式。
  - 以 1.1 的工具量 `before-real` 與 `before-scaled`；擴大資料以 import 匯入，與上一輪相同。

  驗證：
  - 兩份報告都存在，各含 20 次預覽的 p50、p95 與最大值。
  - 正式服務的指紋不變。
- [ ] 2.2 量出修正前的輸入延遲，並查清 108 秒的成因：
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

- [ ] 3.1 `research_compile.py` 新增 `ProjectionWriter` 與 `PROJECTION_ORDER`（design D1），`project()` 改用它：
  - 只在兩個時間點 `flush()`：把 release 改成 `ready` 之前，以及 `activate_bootstrap` 之前。
  - `project()` 新增 keyword 參數 `immediate=False`。
  - 未列在 `PROJECTION_ORDER` 的表直接拋錯。
  - 模組層級的 `insert()`、`document()` 保持立即寫入。
  - 回傳值新增 `timings`（design D4），只含各階段的毫秒數。

  驗證：
  - `backend/tests/test_research_compile.py` 等離線測試通過。
  - 臨時 PostgreSQL 上，`test_research_drafts.py`、`test_research_publication.py`、`test_research_v2.py`、`test_publication_interfaces.py`、`test_research_restart.py` 全數通過。
- [ ] 3.2 `legacy_history()` 改為每張表只讀一次（design D2），寫入改走寫入器。

  驗證：臨時 PostgreSQL 上新增測試並通過：
  - 建立六種舊歷史（assessment、indicator-definition、indicator-observation、technical-document、technical-observation、technical-review）各至少一筆。
  - 斷言寫出的 legacy_history 列（entity、kind、legacy ID、content hash、data）與依原規則推得的預期列完全相同。
  - 引用不存在的實體時，錯誤訊息與修改前相同。
- [ ] 3.3 新增 `backend/tests/test_projection_writer.py`（design D5 第一層），並加入 `research_pg_checks.py` 的 `all` suite：
  - 同一份 bundle 分別在兩個 savepoint 內以立即模式與批次模式投影。每張 `research.*` 投影表依主鍵排序後算 hash，比對兩邊相同，release ID 與 content hash 也相同。
  - 資料包括 `tests/fixtures/valid`、目前已發布的研究，以及擴大資料。擴大資料標為 `slow`；`scripts/` 不存在時（API image）skip，與既有的 scaled-tree 測試相同。
  - 失敗案例：寫入未列出的表時拋錯；一批寫入違反限制（重複的 relation ID）時整次 rollback，savepoint 外查不到這次的任何列。

  驗證：
  - 臨時 PostgreSQL 上全數通過，含 slow 案例；本 task 記錄 slow 案例的耗時。
  - `grep -n "test_projection_writer" backend/app/research_pg_checks.py` 有結果。
- [ ] 3.4 `draft_preview` 在 rollback 後記一行 INFO `draft-preview timing`（design D4），欄位：草稿 ID、修訂號、`project_ms`、`flush_ms`、`detail_ms`、`graph_ms`。預覽的回應格式不變。

  驗證：臨時 PostgreSQL 上新增測試並通過：
  - 每次預覽剛好記一行，欄位都是數字。
  - log 不含實體名稱或內文。
  - 預覽後資料庫沒有新增 release，也沒有投影列（spec「預覽不留下候選版本」）。
  - 預覽途中拋錯時，同樣沒有留下任何列。
- [ ] 3.5 `research_rebuild_check.py` 加上立即模式與批次模式的比對（design D5 第二層）：
  - 在既有的斷言之前，先在 savepoint 內以立即模式投影並記下各表的列數與 md5，rollback 後再以批次模式投影，比對必須相同。
  - 報告 JSON 新增 `projection_tables` 與 `writer_equivalent`。
  - 比對用的「各表列數與 md5」寫成共用函式，3.3 的測試也用同一個函式。

  驗證：
  - 3.3 的測試透過共用函式涵蓋比對邏輯。
  - 實機執行在 5.2。
- [ ] 3.6 更新文件：
  - `docs/research-data-model.md` 的 rebuild-check 段落補上寫入方式的比對與新的報告欄位。
  - `docs/research-drafts.md` 的預覽段落補上 `draft-preview timing` 這行 log。
  - `docs/research-deployment.md`「合併前演練」中 `rebuild-check` 的註解改為「PR 改了研究內容的編譯或投影時」。
  - `research_compile.py` 的 `PROJECTION_ORDER` 旁註明：新增投影表時必須加入，並依 foreign key 排序。

  驗證：`grep -n "writer_equivalent" docs/research-data-model.md`、`grep -n "draft-preview timing" docs/research-drafts.md` 都有結果。

## 4. 管理頁編輯器（前端）

- [ ] 4.1 `frontend/components/ResearchEditor.tsx` 的兩個文字框改為 uncontrolled（design D6）：
  - 使用 `defaultValue`、`ref`，`key` 由路徑加上 `loadVersion` 組成。
  - `onInput` 只處理第一次修改。
  - 儲存與切換模式前，以 `currentDocument()` 從 ref 讀出內容。
  - 原始文字框：`spellCheck={false}`、`wrap="off"`，並關閉 autocomplete、autocorrect、autocapitalize。
  - 表單內文的文字框：`spellCheck={false}`。
  - frontmatter 的單行欄位維持 controlled。

  驗證：`npm run typecheck` 通過。
- [ ] 4.2 `frontend/tests/research-editor.spec.ts` 新增 spec「管理頁儲存的就是畫面上的內容」四個情境的測試，桌機與手機各一次：
  - 輸入後立刻儲存：PATCH 的內容含最後輸入的字元。原始文字模式下用約 1 MB 的 mock 檔，只核對內容正確，不量時間。
  - 從表單切換到原始文字：原始文字包含剛輸入的內容。
  - 第一次修改：顯示「有未儲存修改」，選擇草稿、選擇檔案、驗證、比較、預覽都停用。
  - 儲存後換另一份文件：文字框顯示新文件的內容，沒有殘留前一份的文字。

  驗證：
  - 以本 branch 的 `next start`（127.0.0.1:3017，不碰正式服務）設 `RESEARCH_E2E` 執行 `research-editor.spec.ts`，全數通過（含既有測試）。
  - `npm run test:e2e:offline` 全數通過。

## 5. 修正後的整合量測與記錄（演練環境，從本 change 的 worktree）

- [ ] 5.1 推送 branch、開 draft PR，確認 GitHub Actions 全部通過（validator、root unittest、離線後端、前端 typecheck／unit／build、離線 E2E、公開靜態頁）。驗證：PR 與 run 編號記在本 task。
- [ ] 5.2 演練環境依序執行：
  - `restore --backup latest`
  - `deploy-rehearsal --commit <PR HEAD>`
  - `pg-check --commit <PR HEAD> --suite all`
  - `rebuild-check --commit <PR HEAD>`

  驗證：
  - `deploy-rehearsal` 的 smoke 通過。
  - `pg-check` 全數通過，含 `test_projection_writer.py`。
  - `rebuild-check` 報告的 `writer_equivalent` 為 `true`，舊歷史的各類筆數與正式資料相同。
  - 報告路徑記在本 task；正式服務的指紋不變。
- [ ] 5.3 在 5.2 部署的演練上，量修正後的數字：
  - 預覽：`after-real` 與 `after-scaled`。
  - 輸入延遲：`after-real-company`、`after-real-relations`、`after-scaled-relations`（加 `--trace`）。

  驗證：報告中下列項目符合 spec：
  - 「已驗證修訂的閱讀預覽有時間上限」：真實資料 p95 ≤ 1 秒，擴大資料 p95 ≤ 2 秒，20 次預覽都成功。
  - 「管理頁編輯大型文件不會凍結」：三組按鍵延遲的 p95 ≤ 300 毫秒，最大值 ≤ 1 秒，沒有逾時。
  - API 記憶體高點與上一輪的 178 MiB 比較，並記錄下來。

  未達標時，記錄實際數字與分段耗時（`draft-preview timing`、trace 摘要），交給 Boris 決定。不得調整目標來湊數。
- [ ] 5.4 `rollback-rehearsal`：回到 restore 的基準 image，判定應為 `expand-only`，回退後 smoke 通過。驗證：報告路徑記在本 task；正式服務的指紋不變。
- [ ] 5.5 記錄結果：
  - `docs/research-performance.md` 的新一節補上修正後的數字、分段耗時與 108 秒的處理結果。
  - 上一節「未在本 change 處理的後續問題」逐項標註處理結果。
  - `docs/research-acceptance.md`「草稿編輯的剩餘成本」這一列改為修正後的狀態。

  驗證：文件數字與 `.work/research-draft-bench/*.json`、`.work/research-editor-latency/*.json` 以程式逐一比對一致。

## Workflow follow-up

- 1–5 全部勾完、在 branch 上 archive（`research-publishing` 主 spec 合入本 change 新增的四項 requirement），CI 再確認一次全綠之後，PR 才交給 Boris merge（AGENTS.md「先驗證、再 merge」）。
- merge 後由 Boris 依 `docs/research-deployment.md` 從部署目錄部署，部署紀錄的 smoke 結果就是紀錄。
- 部署後 Boris 在正式 `/admin` 預覽幾頁，確認回應明顯變快；結果簡短記在 `docs/research-acceptance.md`。這是正式環境的確認，不阻擋 merge。
- 之後依產品順序進入地圖廣度擴充（光通訊、電網／電力設備、網路系統）。
