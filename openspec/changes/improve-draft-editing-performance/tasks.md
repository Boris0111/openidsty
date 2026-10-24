# Tasks

需要 PostgreSQL 的測試，一律在臨時、獨立的 PostgreSQL 容器上以本 branch 的程式碼執行；不使用 `research_lab.py pg-check`，因為它會以 branch 的程式碼覆蓋正式服務的 API image。演練環境的量測要在主 checkout 暫時切到本 branch 進行；切換 branch 或重啟 Docker Desktop 前，先徵得 Boris 同意（AGENTS.md）。

## 1. 修正前的基準量測

- [x] 1.1 （2026-10-24：`tests/` 44 項 OK，含新增 `test_research_draft_bench.py` 6 項；擴大資料不改 head，而是建立草稿後經 import 匯入 `build_tree()` 的樹，修正前後走同一路徑；預覽對象自動選含圖解的文件，真實資料為 `concept-hbm-stack`）新增 `scripts/research_draft_bench.py`（design D7）：
  - 以 `research_integration.Session` 和 drill owner 登入，經 web 同網域 proxy 量測：
    - 儲存一份公司文件 ×30。
    - 儲存關係檔 ×30（只限擴大資料）。
    - 首次驗證、重複驗證、diff 各一次。
    - 預覽一份含圖解的文件，含它的所有圖解請求。
  - 輸出 p50／p95／最大值、HTTP 狀態與 API 容器的記憶體高點，寫到 `.work/research-draft-bench/<label>.json`。
  - 草稿無法建立或匯入時，記錄狀態碼與錯誤代碼後繼續量測其他項目，不中止。
  - 驗證：`python scripts/research_draft_bench.py --help` 可執行。`tests/` 新增此腳本的單元測試，涵蓋百分位計算與報告欄位，`python -m unittest discover -s tests -p "test_*.py"` 通過。
- [x] 1.2 （2026-10-24：Boris 同意後，正式服務暫停，演練由備份 `20261023T193005Z` 還原；修正前 API image `e19d022f` 建置後後端沒有其他 commit。真實資料：儲存 p95 3,834 ms、重複驗證 8,377 ms、整頁預覽 27,974 ms。擴大資料：建立草稿成功，匯入回 422 `draft-rejected`。作法調整：擴大資料改為建立草稿後經 import 匯入，不改演練 head，與 6.1 走同一條路；基準與修正後數字合併寫在「草稿編輯修正前後」一節）在演練環境以修正前的程式碼（`main` 的 `d8619f3`）量出兩組基準：
  - 真實資料，label `before-real`。
  - 擴大資料，label `before-scaled`：先用 `research_scale.py` 的測試專用投影把擴大資料設為 head。預期建立草稿與匯入都會因 YAML 上限被拒，照實記錄。
  - 驗證：兩份報告都存在；`docs/research-performance.md` 新增「草稿編輯基準（修正前）」一節，記錄環境、版本、數字，以及每次預覽實際執行了幾次完整驗證。

## 2. YAML 解析改用 libyaml

- [x] 2.1 （2026-10-24：`run_validator_tests.py` 66 類失敗案例全過、`validate_map.py` 通過；`test_service_yaml_uses_libyaml` 通過。另加只供等價測試的 `RESEARCH_YAML_PURE=1` 強制純 Python 版，服務不設定。`test_managed_git...` 在 Windows 失敗為既有問題，原因是 `git worktree`，與本 task 無關）`backend/app/research_documents.py` 的 `UniqueLoader` 與 `scripts/validate_map.py` 的 `UniqueKeyLoader` 改以 `getattr(yaml, 'CSafeLoader', yaml.SafeLoader)` 為父類別，重複鍵與非文字鍵的檢查照舊（design D1）；API 啟動時若沒有 libyaml 就記一筆 warning。驗證：
  - `python tests/run_validator_tests.py` 全數通過。
  - `python scripts/validate_map.py` 通過。
  - 後端新增測試：`yaml.__with_libyaml__` 為真，在 CI 執行。
- [x] 2.2 （2026-10-24：`test_research_documents.py` 38 passed；依 spec 另讓 normalize 的單檔錯誤以 `<path>：` 開頭；擴大資料關係檔的 `safe_yaml` 本機約 1.6 秒；`slow` marker 與 `scaled_tree` fixture 放在 `conftest.py`）`safe_yaml` 的結構上限改用 parser 事件計算，深度上限 32 不變，事件數上限 400,000，展開節點上限 400,000（design D2）。驗證：`backend/tests/test_research_documents.py` 新增以下案例並通過：
  - 剛好不超過與剛好超過事件數上限。
  - 深度 33 被拒。
  - alias 展開超過節點上限被拒。
  - 自我參照 alias 被拒。
  - 擴大資料關係檔（由 `research_scale.build_tree()` 產生）可被接受。
- [x] 2.3 （2026-10-24：`test_yaml_equivalence.py` 2 passed，以 `tests/yaml_probe.py` 在子程序設 `RESEARCH_YAML_PURE=1` 對照；本機耗時：已發布研究＋fixture＋11 個邊界案例 26 秒，擴大資料 99 秒（另建樹 10 秒，標 `slow`）。實測發現：草稿 loader 在兩種 parser 下都拒絕 merge key，地圖驗證器則接受，皆為既有行為，測試照實斷言）新增 loader 等價測試：純 Python 與 C 版各解析一次，比對解析結果與 `validate_payload` 的 `content_hash`。範圍包括：
  - 目前已發布的研究（`industry-map/` 與 `data/` 研究檔）。
  - `tests/fixtures/valid`。
  - 擴大資料。
  - 一組邊界案例：重複鍵、merge key、非 BMP 字元、BOM、tab 縮排。只比對接受或拒絕，不比對訊息全文。

  驗證：測試通過。擴大資料的案例較慢，標成可在 CI 執行的 slow 測試，並記錄執行時間。

## 3. 增量儲存與讀取單一 Git 檔

- [x] 3.1 （2026-10-24：3 項新測試通過。實作為 `normalize_payload(payload, previous=None)`，`normalize_changes` 是具名入口；文字路徑只允許小寫，合法路徑之間不會有大小寫衝突，故測試改為「增量儲存仍拒絕不合法的新路徑」，casefold 檢查保留為第二道防線）`research_documents.py` 新增 `normalize_changes(previous, payload)`（design D3）：
  - 整份層級的檢查每次全做。
  - `check_document` 只對新增或內容改變的檔案執行。
  - 輸出與 `normalize_payload` 相同。

  驗證：單元測試涵蓋以下情境並通過：
  - 只改一份時只檢查該份（以 monkeypatch 計數 `check_document` 的呼叫次數）。
  - 未變動的檔案即使內容不合格，也不會在儲存時被檢查。
  - 新增、刪除、改名大小寫衝突、超過 5 MiB 仍被拒。
  - 輸出與 `normalize_payload` 的結果相同。
- [x] 3.2 （2026-10-24：2 項新測試通過，以只含必要檔案的小型 repo seed，不需 PG；檔案不存在時拋 `MissingResearchFile`（`ValueError` 子類別），讓 `protect_baseline` 保留「基準無 README 視為空字串」的原語意；測試另確認儲存時不呼叫 `files()`）`research_git.py` 新增 `ManagedGit.file(commit, path)`：先 `verify` 再以 `git cat-file blob` 讀取，path 必須通過 `safe_path`。`protect_baseline` 改用它。驗證：測試涵蓋以下情境並通過：
  - 讀到的內容與 `files()` 中的同一檔相同。
  - 檔案不存在時回 `ValueError`。
  - 不合法的 commit 或路徑被拒。
  - README 被修改時仍回 `draft-rejected`。
- [x] 3.3 （2026-10-24：臨時 PostgreSQL 容器上 `test_research_drafts.py` 4 passed，含新增 `test_saves_and_imports_recheck_only_edited_files`；PATCH 另把整份 payload 的 JSON 深拷貝改為只複製 `files` dict）`save_revision`（PATCH 與 import）改用 `normalize_changes` 與 `protect_baseline` 的新版本，寫入後直接組出回應，不再重查修訂。驗證：在臨時 PostgreSQL 上跑 `test_research_drafts.py` 全數通過（不含 Windows 既有的 `test_managed_git` 問題），並新增以下案例：
  - 只改一份文件的儲存只檢查該份。
  - 變動的文件含 raw HTML 時被拒，原修訂不變。
  - 相同內容不產生新修訂。
  - 舊修訂的 `If-Match` 仍回 409。

## 4. 基準匯出快取與驗證結果共用

- [x] 4.1 （2026-10-24：`test_draft_caches.py::test_base_export_archives_each_commit_once` 通過；快取值與直接 `export_files(files(commit))` 相同，所以 diff 輸出不變，既有的 diff 整合測試照常通過）新增以 commit 為鍵的基準匯出快取（LRU，最多 2 筆，design D4），`draft_diff` 改用它。驗證：測試確認同一個 commit 連續 diff 兩次，`ManagedGit.files` 只被呼叫一次，diff 結果與修改前相同。
- [x] 4.2 （2026-10-24：`test_draft_caches.py` 7 passed。實作為通用的 `SharedResults`（LRU＋single-flight），`VALIDATIONS` 與 `BASE_EXPORTS` 各一個實例；資產 store 錯誤以 `ASSET_STORE_ERRORS` 常數辨識；每次實際驗證在 `uvicorn.error` 記一行 INFO `draft-validation computed`（只有草稿 ID 與修訂號），供量測計數，所有環境都會記，不只演練環境）新增 `ValidationCache`（design D5），以 `payload_hash` 為鍵：
  - LRU 最多 2 筆，並有 single-flight。
  - 資產尚未取得或資產 hash 不符的錯誤不快取。
  - 等待者有 60 秒逾時，逾時回 503。

  驗證：單元測試涵蓋以下情境並通過：
  - 同一個鍵連續取兩次只計算一次。
  - 8 個 thread 同時取同一個鍵只計算一次，且都拿到相同結果。
  - 計算拋出例外時，等待者都收到錯誤，下一次請求會重新計算。
  - 資產錯誤不被快取。
  - 超過 2 筆時淘汰最久未用的。
- [x] 4.3 （2026-10-24：臨時 PostgreSQL 上新增 3 項通過；完整 PG 套件 164 passed、1 skipped，唯一失敗為既有 Windows `test_managed_git...`。真實資料單頁最多 2 張圖解，「三張圖解請求」以一頁的 2 張加另一頁的 1 張達成，合計仍只驗證 1 次；同修訂預覽兩次回應相同，確認共用 bundle 未被改寫；發布測試把 API 預檢強制設為通過，worker 仍以 `invalid-publication` 拒絕，head 不變）`draft_validate`、`draft_preview`、`draft_asset` 與發布預檢（`research_publication.py` 的 API 端）改用 `ValidationCache`；發布 worker 不改。驗證：在臨時 PostgreSQL 上新增以下案例並通過（以計數 `validate_payload` 的呼叫次數確認）：
  - 驗證後預覽一份引用三張圖解的文件，完整驗證合計只執行 1 次。
  - 儲存新修訂後再驗證，會重新計算。
  - 無效修訂的圖解請求被拒，且不重新計算。
  - 發布 worker 仍執行完整驗證，並拒絕「未變動檔案不合格」的草稿。

## 5. 草稿摘要、PATCH 回應與管理頁

- [x] 5.1 （2026-10-24：臨時 PostgreSQL 上 drafts／publication／publication-interfaces 共 24 passed，含新增 `test_summary_and_save_response_carry_no_unrelated_content`；PATCH 回應的 `documents` 不再重跑 `check_document`（內容剛在儲存時檢查過），避免擴大資料的關係檔每次儲存多花約 1.6 秒；離線 CI 方式 278 passed）新增 `GET /api/admin/drafts/{id}/summary`；`PATCH /api/admin/drafts/{id}` 改回傳摘要加上 `documents`（design D6）。驗證：在臨時 PostgreSQL 上新增 API 測試並通過，確認以下行為：
  - summary 不含檔案內容，ETag 等於修訂號。
  - PATCH 回應含新修訂與剛儲存文件的 `frontmatter`／`markdown`／`content`。
  - 未登入或缺 CSRF 時被拒。
  - `GET /drafts/{id}`、`/export`、`/import` 的格式不變（既有測試通過）。
- [x] 5.2 （2026-10-24：`npm run typecheck` 通過；`npm run test:e2e:offline` 64 passed；`research-editor.spec.ts` 屬 live config 且需 `RESEARCH_E2E`，改以本 branch 的 `next start`（127.0.0.1:3017，不碰正式服務）執行，桌機／手機 2 passed。mock 對完整 `GET /drafts/{id}` 回 500，所以舊程式碼會失敗；新增斷言：儲存後 drafts 類請求只有一個 PATCH，清單中的修訂號同步為 2）`frontend/lib/admin-proxy.ts` 的 GET allowlist 加入 `drafts/{uuid}/summary`。`ResearchEditor.tsx` 選擇草稿時改讀 summary，儲存後直接用 PATCH 回應更新草稿、文件與清單中的修訂號，不再重新讀取文件或清單。驗證：
  - `npm run typecheck` 通過。
  - 更新 `frontend/tests/research-editor.spec.ts` 的 mock，新增斷言：儲存時只發出一個 PATCH，沒有後續的 document 或 drafts 請求；選擇草稿時不請求完整的 `/drafts/{id}`。
  - `npm run test:e2e:offline` 全數通過。
- [x] 5.3 （2026-10-24：`research_drafts.py` 的 14 個路由與 API 表逐一對照一致；`GET /drafts/{id}` 拆成獨立一列以區分完整讀取與摘要）更新 `docs/research-drafts.md`：
  - API 表加入 summary，註明 PATCH 回應的格式。
  - 「儲存與匯入」段補上「只重驗有變動的檔案；驗證與發布仍檢查全部檔案」。
  - 結構上限改為事件數與節點數。

  驗證：文件中的 API 表與 `research_drafts.py` 的路由逐一對照一致，`grep -n "summary" docs/research-drafts.md` 有結果。

## 6. 修正後的整合量測與記錄

- [x] 6.1 （2026-10-24：只建置 image、未啟動正式服務，演練 api／web 以 `b036a28e`／`ade412b2` 重建，image 內有 libyaml。全部達標：真實資料公司文件儲存 p95 357 ms；擴大資料匯入 200，公司文件 307 ms、關係檔 2,345 ms；重複驗證 56／81 ms；`draft-validation computed` 兩組各 1 次，預覽與圖解 0 次；API 記憶體高點 178 MiB）在演練環境以本 branch 重建 API／web 後，用 `research_draft_bench.py` 量出 `after-real` 與 `after-scaled`；擴大資料改走正式的 CLI 匯入路徑建立草稿。驗證：兩份報告中下列項目都符合 spec「草稿儲存只檢查有變動的內容」與「同一修訂的完整驗證結果重複使用」：
  - 真實資料：公司文件儲存 p95 ≤ 500 ms。
  - 擴大資料：公司文件儲存 p95 ≤ 1 s；關係檔儲存 p95 ≤ 3 s。
  - 重複驗證 ≤ 300 ms。
  - 每次預覽的完整驗證次數 ≤ 1。
  - 擴大資料的匯入、驗證與預覽都成功。

  未達標時，記錄實際數字與拆解，交給 Boris 決定，不得調整目標來湊數。
- [x] 6.2 （2026-10-24：兩組都超過 2 秒門檻，已列為後續問題。worker 容器內逐段計時：臨時投影真實資料 2.69 秒、擴大資料 9.45／9.49 秒，detail 與 graph 合計不到 0.35 秒。輸入延遲以 headless Chromium 量：公司文件 p50 96 ms、p95 247 ms；擴大資料關係檔（972,942 字）p50 277 ms，但一次按鍵卡住 108 秒）確認預覽的臨時投影耗時：如果已驗證修訂的預覽 p95 超過 2 秒，記錄投影的耗時拆解，列為後續問題（design D7）。同時以擴大資料在管理頁打開關係檔、輸入幾行文字，觀察是否有明顯延遲並記錄。驗證：結果寫入 `docs/research-performance.md`。
- [x] 6.3 （2026-10-24：數字以程式逐一比對 4 份報告 JSON 一致，修正兩處四捨五入；`research-acceptance.md` 改為「草稿編輯的剩餘成本」一列）更新 `docs/research-performance.md`：
  - 新增「草稿編輯修正前後」一節：環境、版本、兩組資料、表格、API 記憶體高點、以 libyaml 取代後的驗證耗時。
  - 「草稿路徑的限制」一節逐項標註處理結果。
  - `docs/research-acceptance.md` 中「草稿關係數上限約 1,700 條；每次儲存約 3 秒」這一列改為修正後的狀態。

  驗證：文件中的數字與 `.work/research-draft-bench/*.json` 一致。

## 7. CI 與正式服務走查

- [x] 7.1 （2026-10-24：draft PR #9；commit `49f9f9a` 的 CI run 40054916057、40054954858 全綠：validator 66 類與 `tests/` 44 項、離線後端 280 passed／96 skipped（Linux 上 `test_managed_git` 也通過）、typecheck／unit／build、離線 E2E 64 passed、公開靜態頁 52 passed。後續只改文件的 commit 於 archive 前再確認一次 CI）推送 branch、開 PR，確認 GitHub Actions 全部通過，包括離線後端測試（含 libyaml 檢查與 loader 等價測試）、validator 測試、前端 typecheck 與離線 E2E。驗證：CI 全綠；PR 與 run 編號記錄在本 task。
- [x] 7.2 （2026-10-24：Boris 同意後，主 checkout 切到本 branch，`research_lab.py up` 重建並啟動正式服務，排程恢復。Boris 在 `/admin` 走完儲存、驗證、比較與 18 次預覽，完整驗證只執行 1 次；CLI 用舊修訂資料夾匯入回 409，草稿仍為修訂 4；讀者 release `a5df290c…` 與摘要 hash 前後相同，沒有發布作業。預覽的頁面都沒有圖解，圖解共用由演練環境驗證。記錄在 `docs/research-performance.md`「正式服務演練」；push 後主 checkout 切回 `main`）正式服務演練：徵得 Boris 同意後，在主 checkout 切到本 branch，執行 `python scripts/research_lab.py up` 重建 API／web。由 Boris 登入 `/admin`，做以下操作：
  - 建立草稿。
  - 以表單修改一份公司文件並儲存。
  - 驗證、與基準比較、閱讀預覽（含圖解）。
  - 用一份舊修訂的檔案匯入，確認回 409。

  不發布，演練後刪除或留著這份草稿都可以，但不影響讀者。驗證：
  - 讀者 `/next` 的內容不變。
  - API log 顯示這次預覽只做 1 次完整驗證。
  - 演練結果與時間記錄在 `docs/research-performance.md`，並在本 task 註記；完成後主 checkout 切回 `main`。

## Workflow follow-up

- tasks 全部勾完（含 7.2 正式服務演練）後，在 branch 上 archive，`research-publishing` 主 spec 合入本 change 的新增 requirements。
- archive 後才把 PR 交給 Boris merge；merge 後依 memory 的順序進入地圖廣度擴充。
