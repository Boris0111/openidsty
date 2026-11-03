# Design

## Context

動機見 proposal.md「Why」。以下只列影響作法的現況與限制。

**預覽的投影**（`backend/app/research_drafts.py` 的 `draft_preview`）：

- 取得已驗證的 bundle 後，在 `connection.begin_nested()` 內呼叫 `research_compile.project()`，讀出 `detail_payload` 與 `graph_payload`，最後 rollback。
- 上一輪在 worker 容器內量過：時間幾乎都花在 `project()`（真實資料 2.69 秒、擴大資料 9.45 秒），detail 與 graph 合計不到 0.35 秒。

**`project()` 寫入資料庫的方式**（2026-11-02 不連資料庫實測：以假連線記錄 `project()` 發出的語句）：

- 每一列都經由 `insert()` 建一個新的 `text()`，再單獨 `execute` 一次。
- 真實資料（HEAD）共 3,026 次 `INSERT`：entity_aliases 713、taxonomy_links 362、entities／entity_snapshots 各 254，其餘每張表在 200 次以下。
- 擴大資料共 10,822 次：relations 3,034、relation_claims 3,000、entity_aliases 918。
- `legacy_history()` 讀舊歷史表時，每一列再額外查一到兩次（`theme_indicators`、`technical_observations`、`technical_documents`）。這部分的次數取決於正式 DB 的舊資料量，離線量不到。
- 推論（needs verification）：擴大資料約 10,800 次往返，平均每次約 0.85 ms，大致可以解釋 9.45 秒。純 Python 端的成本（每列建 `text()`、序列化 JSON、算 hash）在 Windows 上約 2 秒，容器內的比例還要實測才知道。

**`project()` 的呼叫端**：

- 閱讀預覽（savepoint）。
- 發布 worker 的 projection 步驟與 activation 交易（`research_publication.py`，都在 `engine.begin()` 內）。
- `research_rebuild_check.py`，以及 `scripts/research_scale.py` 的測試用投影。
- 測試直接使用模組層級的 `insert()` 與 `document()` 準備資料（`test_research_v2.py` 等）。這兩個函式的立即寫入語意必須保留。

**驅動程式**：SQLAlchemy 2.0.48 搭配 psycopg 3.3.3。以 `connection.execute(text(...), [dict, ...])` 傳入多筆參數時，會走 cursor 的 `executemany`；psycopg 3 的 `executemany` 會自動使用 pipeline mode，一次送出多筆，不必每筆等回應。

**管理頁編輯器**（`frontend/components/ResearchEditor.tsx`；以下為提案時的了解，D6 的「為什麼改變」是量測後的結果）：

- 兩個文字框都是 controlled：每次按鍵都 `setDocument({...current, content})`，整個 `ResearchEditor` 重新 render，React 再把近 1 MB 的字串寫回 `<textarea>`。
- 每次按鍵也會呼叫 `setDirty(true)`、`setPreview(undefined)`、`setDiff('')`。
- 原始文字框沒有關閉拼字檢查，也會自動換行。
- 上一輪量到：擴大資料的關係檔 p50 277 ms，但有一次按鍵卡了 108 秒；公司文件以表單編輯時 p95 247 ms。卡住的成因沒有查證。

**實機量測的位置**：依 AGENTS.md 與 `docs/research-deployment.md`「合併前演練」，從本 PR 的 worktree 以 `scripts/research_drill.py` 在演練環境（web 3016、API 8016）進行。

## Goals / Non-Goals

**Goals:**

- `project()` 的輸出完全不變，只改寫入方式；發布與預覽一起受惠。
- 編輯器的文字框關閉沒有用處的瀏覽器處理（拼字檢查、原始文字的自動換行），資料流動方式不變（2026-11-03 由 uncontrolled 改為此目標，見 D6）。
- 先用 trace 查清 108 秒的成因，修完再用同一方法確認。
- 量測工具與方法留在 repo，之後擴充時可以重量。

**Non-Goals:**

- 不改預覽「savepoint 內投影再 rollback」的模式（D3）。
- 不改 `detail_payload`、`graph_payload` 的查詢，也不改讀取投影的資料表結構。
- 不改發布 worker 的流程、檢查點與失敗處理，只是 `project()` 變快。
- 不碰單行的 frontmatter 欄位（`<input>`），維持 controlled。
- 不在 CI 跑效能目標，延遲目標只在演練環境驗證。

## Decisions

### D1：`project()` 改用批次寫入器，依 foreign key 順序整批送出

`research_compile.py` 新增一個只給 `project()` 使用的批次寫入器 `ProjectionWriter`：

- **累積**：`add(table, values, conflict)` 只產生參數（jsonb 欄位照舊用 `canonical()` 序列化），先存在記憶體。同一張表依「欄位組合＋是否 `ON CONFLICT DO NOTHING`」分組，組內保持加入的順序。
- **送出**：`flush()` 依常數 `PROJECTION_ORDER` 逐表處理，每組只建一個 `text()`，以 `connection.execute(statement, rows)` 送出，每次最多 1,000 列。
- **`PROJECTION_ORDER`**：等於目前程式碼裡各表第一次被寫入的順序，所以 foreign key 的父表一定先於子表。`research_releases` 最先，接著是 entities、entity_snapshots、legacy_mappings、listings、source_identifiers、entity_aliases、release_sources、documents、document_revisions、release_documents、research_claims、claim_evidence、taxonomy_links、company_offerings、offering_claims、relations、relation_claims、assets、release_assets，最後是 legacy_history。
- **防呆**：寫入一張不在清單裡的表時，直接拋錯，避免日後新增的表被默默排錯順序。
- **寫入時機**：`project()` 只在兩個時間點 `flush()`。一是最後把 `research_releases` 從 `preparing` 改成 `ready` 之前；二是在 `activate_bootstrap` 之前，因為它會查 `release_head`。這兩處以外，`project()` 寫入期間沒有讀回自己寫的投影表，所以延後寫入不影響任何判斷。
- **`ON CONFLICT DO NOTHING` 的判定不變**：
  - 同一張表的不同組，送出順序與舊程式的寫入順序相同。例如 taxonomy_links：舊程式先寫完 `bundle['taxonomy']`，才寫 roles 產生的 baseline 連結。
  - 組內也保持原順序，所以發生衝突時，仍由先寫入的那一列保留。
- **核對用的立即模式**：`ProjectionWriter(connection, immediate=True)` 會在 `add` 時立刻執行，等同舊行為，只供等價核對使用（D5 的測試與 `rebuild-check`）。`project()` 新增 keyword 參數 `immediate=False` 傳給寫入器；正式的呼叫端都不傳。
- **模組層級的 `insert()` 與 `document()` 保持立即寫入**，給其他呼叫端與測試使用。`project()` 內部改呼叫寫入器版本。

**替代方案**：

- **每組用一條多列 `VALUES` 的語句**：往返更少，但每條語句有參數數量上限（65,535），要自己切批、自己組 SQL。`executemany`＋pipeline 已能把往返壓到很低，先不用。
- **`COPY`**：最快，但不支援 `ON CONFLICT DO NOTHING`，jsonb 也要自己編碼，不採用。
- **只合併連續的同表寫入**（完全保留原本的語句順序）：snapshot 迴圈裡每個實體會交錯寫 entities、snapshots、aliases，relations 與 relation_claims 也是交錯寫，連續的段落很短，幾乎省不到往返，不採用。

### D2：`legacy_history` 每張表只讀一次

先各讀一次 `theme_indicators`（indicator → themes）、`technical_observations`（id → document_id）、`technical_documents`（id → data），建成 dict 再遍歷，取代每一列的查詢。遍歷順序（`ORDER BY id`）、找不到實體時的錯誤訊息、寫入的列都不變；寫入改走 D1 的寫入器。

### D3：預覽維持 savepoint＋rollback，不快取、不做部分投影

**選擇**：只讓 `project()` 本身變快，預覽的流程不變。

**替代方案**：

- **把預覽用的候選 release 保留在資料庫，以內容 hash 重複使用**：release ID 由 commit 與內容 hash 決定，保留下來的 `ready` 版本會與之後發布同一內容的投影共用同一個 ID，預覽與發布的資料就混在一起了。此外，讀者角色的隔離要多靠一層 status 過濾，還要設計清除規則。風險與工作量都比批次寫入大，不採用。
- **只投影預覽需要的實體與鄰居**：等於在讀者的 SQL 之外，再維護一套「哪些列算需要」的規則，預覽與讀者頁面的結果可能不一致，違反「沿用讀者契約」的原則，不採用。
- **在記憶體裡從 bundle 直接算出 detail 與 graph**：理由同上，會出現第二套讀取邏輯。

**未達標時**：如果批次寫入後仍不符合 spec「已驗證修訂的閱讀預覽有時間上限」，記錄 D4 的分段耗時，交給 Boris 決定下一步。不調整目標，也不在本 change 擴大範圍。

### D4：`project()` 的分段計時

- `project()` 回傳值新增 `timings`：各階段的毫秒數，包括 snapshots、documents、claims、taxonomy 與 offerings、relations、assets、legacy history、flush。值只有數字，不含內容。
- 預覽在 rollback 後，於 `uvicorn.error` 記一行 INFO：`draft-preview timing draft=<id> revision=<n> project_ms=… flush_ms=… detail_ms=… graph_ms=…`。這與上一輪的 `draft-validation computed` 同一個 logger，量測腳本從演練 API 容器的 log 擷取。
- 發布 worker 不另外記錄，只會因為回傳值多一個欄位而不受影響（它只讀 `release_id`）。

### D5：投影等價的驗證分兩層

1. **常駐測試**（需要 PostgreSQL，與既有 PG 測試相同，在臨時容器與演練的 `pg-check` 執行）：
   - 同一份 bundle 在兩個 savepoint 內分別以 `immediate=True` 與批次模式投影。
   - 每次投影後，把該 release 在所有 `research.*` 投影表的列依主鍵排序，序列化成 hash 後 rollback，再比對兩邊的 hash。
   - 資料包括 `tests/fixtures/valid` 與目前已發布的研究；擴大資料（`research_scale.build_tree()`）標為 `slow`。
   - 舊歷史的資料用測試 DB 的既有 legacy fixture；沒有的話，在測試內建立最少的 legacy 列，讓 D2 的路徑被執行到。
2. **實機核對（`rebuild-check`）**：
   - `research_rebuild_check.py` 原本就會用正式 DB 複製過來的真實舊歷史，在測試 DB 投影後 rollback。
   - 在既有的斷言之前，先在 savepoint 內以立即模式投影一次，記下每張表的列數與 md5，rollback 後再以批次模式投影，比對兩邊必須相同。
   - 報告的 JSON 新增 `projection_tables`（每張表的列數與 md5）與 `writer_equivalent: true`。
   - 這樣不必改 `research_drill.py` 的參數，演練時照常執行 `rebuild-check --commit <PR HEAD>` 即可。
   - 再加上 `pg-check --suite all` 全數通過。
   - D2 改的是讀取方式，兩種模式都會用到，所以另外用單元測試核對：建立六種舊歷史各至少一筆，斷言寫出的 legacy_history 列與依原規則推得的預期列完全相同。

這裡不拿修正前（`main`）的投影直接比較：那需要在同一個 DB 上跑兩個 image 的程式。兩種寫法的差別只在送出方式，產生列的程式是共用的，所以比對立即模式與批次模式，就等於比對了批次化前後的行為。

另外加兩個失敗案例：

- 寫入器遇到未列在 `PROJECTION_ORDER` 的表時拋錯。
- 一批寫入違反限制時（例如重複的 relation ID），整次投影 rollback，資料庫不留下任何列。發布路徑以既有的發布失敗測試確認正式版本不切換。

### D6：文字框維持 controlled，只加低風險屬性（Boris 2026-11-03 決定）

**選擇**：

- 原始文字框：`spellCheck={false}`、`wrap="off"`、`autoComplete="off"`、`autoCorrect="off"`、`autoCapitalize="off"`。內容是 YAML 與 Markdown 原始碼，拼字檢查與自動修正沒有用處；YAML 以行為單位，不自動換行、改為水平捲動可以接受。
- 表單內文的文字框：`spellCheck={false}`（內文是中文，拼字檢查沒有用處）；保留自動換行，方便閱讀散文。
- 兩個文字框維持 controlled：輸入照舊更新 React state，儲存、切換模式與 dirty 判定都不變。

**為什麼改變原本的 uncontrolled 設計**：

- 修正前的量測（2026-11-02，D7）沒有重現 108 秒。約 97 萬字的關係檔 p95 168 ms，三組都已在 spec 目標內。
- trace 中 React script 約占 8%（約每鍵 10 ms），其餘是 Chromium 本身的 paint、排版與選取同步。uncontrolled 只能省下 React 那一塊。
- uncontrolled 讓「文字框裡的內容」與「React 以為的內容」成為兩份。只要有一處沒同步，就會出現切換檔案後把前一份文字存進新檔案、或漏存最後輸入的錯誤。效益小、風險新增，不採用。
- 推論（needs verification）：headless Chromium 可能沒有拼字字典，所以 trace 看不到拼字檢查；日常使用的 Chrome 有字典時，關閉拼字檢查可能有幫助。

**原本的設計（未採用）**：兩個文字框改用 `defaultValue`＋`ref`，`key` 隨載入、儲存、切換模式更換；`onInput` 只在第一次修改時標記 dirty；儲存與切換模式前以 `currentDocument()` 從 ref 讀出內容。若日後廣度擴充使延遲接近目標，可另開 change 重新評估。

**其他替代方案**：

- 維持 controlled，改用 `useDeferredValue` 或 debounce 延後更新 state：React 仍要把整段字串寫回文字框，瀏覽器仍要重排版面，治標不治本。
- CodeMirror 等只渲染可見範圍的編輯器：Boris 2026-11-02 決定不新增套件。
- 限制網頁可編輯的大小：同樣不採用，spec 要求不新增大小限制。

### D7：先錄 trace 查 108 秒的成因

新增 `scripts/research_editor_latency.cjs`（Node＋前端既有的 `@playwright/test`，寫法同 `scripts/reading_walkthrough.cjs`）：

- **登入**：以 headless Chromium 開啟演練 web（預設 `http://127.0.0.1:3016`）。owner 密碼從 `INDUSTRYFLOW_DRILL_HOME` 的演練 env 檔讀 `DRILL_OWNER_PASSWORD`，不印出，也不寫入報告。
- **操作**：依參數選擇草稿（`--draft`）、檔案（`--path`）與模式（`--mode raw|form`），把游標放在文字中段，依序輸入 N 個字元（預設 30，間隔 150 ms）。
- **延遲的算法**：每個按鍵的延遲取 Event Timing API（`PerformanceObserver` type `event`，與 INP 同一套定義）中，同一個 `interactionId` 的最大 `duration`，也就是從按鍵到下一個畫面。低於 16 ms 的事件不會被回報，記為 `<16`。每個按鍵最多等 180 秒，逾時記為失敗並繼續。
- **trace**：加上 `--trace` 時，以 `browser.startTracing` 錄下整段輸入，輸出 trace 的摘要：超過 50 ms 的主執行緒工作，依 script、style／layout、paint、GC、其他分類，列出前幾名的耗時。原始 trace 留在 `.work/research-editor-latency/`。
- **報告**：`.work/research-editor-latency/<label>.json`，內容包括 p50、p95、最大值、逾時數、檔案字數與環境。

**流程**：

- 修正前先以 `--trace` 量 `before-*`，判定 108 秒的主因。
- 修正後量 `after-*`。如果主因不在 D6 處理的範圍內，例如是 Chromium 本身排版百萬字文字框的成本，記錄下來交給 Boris 決定，不擴大範圍。
- 結果：修正前的主因正是 Chromium 本身（見 D6），Boris 2026-11-03 據此改選 D6 的低風險屬性。

量測需要的擴大資料草稿，由 `research_draft_bench.py --dataset scaled` 建立，並在報告中寫出 `draft_id`。latency 腳本以這個 ID 打開草稿。

### D8：預覽量測改為多次

`research_draft_bench.py`：

- 驗證一次後，預覽改為依固定清單輪流預覽 20 次（預設清單：`concept-hbm-stack`、`company-auras`，以及幾個 segment 與 theme；擴大資料另加合成公司），記錄 p50、p95 與最大值。
- 從演練 API 容器的 log 擷取 D4 的 `draft-preview timing`，算出各段的中位數。
- 圖解請求照舊另外記錄，不計入預覽時間，與 spec 的定義一致。

## Risks / Trade-offs

- [批次送出的順序錯誤，違反 foreign key 或改變衝突時保留哪一列] → `PROJECTION_ORDER` 以目前的首次寫入順序為準；遇到未列出的表就拋錯；以立即模式與批次模式逐表比對 hash（D5）；演練環境再跑 `rebuild-check` 與 `pg-check`。
- [pipeline mode 下，錯誤要到同步時才回報，錯誤訊息或位置與逐列寫入不同] → 整次投影都在交易或 savepoint 內，失敗時一律整次 rollback。發布 worker 原本就以通用的例外處理把作業記為失敗；D5 的失敗案例確認不留下任何列。
- [所有列先放在記憶體，API 記憶體上升] → 估計擴大資料約十多 MB（推論）。量測時記錄 API 的記憶體高點，與上一輪的 178 MiB 比較；明顯超出時記錄並交給 Boris。
- [擴大資料的純 Python 成本本身就接近 2 秒] → 每組只建一個 `text()`，已省下每列重建 SQL 的成本。剩下的序列化與 hash 由 D4 的分段計時看出；未達標時依 D3 處理。
- [輸入延遲隨關係檔變長而成長，廣度擴充後接近目標] → 推論：主要成本（選取同步、排版）大致隨文字長度成長。`research_editor_latency.cjs` 留在 repo，擴充後可重量；接近目標時另開 change，重新評估 uncontrolled 或其他作法。
- [Event Timing 在 headless Chromium 的數字與實際使用的感受不同] → 量測方法與環境寫進報告；同時以 trace 檢查最長的那次。目標以演練環境的 headless 量測為準，與上一輪的量測方式一致。
- [關閉拼字檢查與自動換行改變了編輯體驗] → 內容是中文與 YAML，拼字檢查沒有用處；只有原始文字框關閉自動換行，YAML 本來就以行為單位，水平捲動可以接受。

## Migration Plan

1. 不需要資料庫 migration，也不改資料表與 API 格式。
2. merge 前：從本 PR 的 worktree 在演練環境依序執行 `restore`、`deploy-rehearsal`、`rollback-rehearsal`、`pg-check --suite all`、`rebuild-check`，再量 `after-*`。
3. merge 後：Boris 依 `docs/research-deployment.md` 從部署目錄部署。前後端由同一次部署一起更新；兩者之間沒有格式相依，只更新一邊也能運作。
4. 回退：依「回退」一節回到前一個 image。沒有 schema 變更，屬於 `expand-only`；草稿與已發布的資料都不受影響。
