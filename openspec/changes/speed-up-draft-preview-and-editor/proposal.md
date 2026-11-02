# Proposal

## Why

上一個效能 change（`improve-draft-editing-performance`，2026-10-24）留下兩個問題，交給 Boris 決定是否處理（`docs/research-performance.md`「未在本 change 處理的後續問題」）。2026-11-02 Boris 決定：在地圖廣度擴充之前先修好。

1. **閱讀預覽很慢**：每次預覽都把整份研究投影進 savepoint 再 rollback。真實資料約 2.7 秒，擴大資料約 9.5 秒，且隨研究規模成長。
2. **大型檔案在管理頁會卡住**：擴大資料的關係檔約 97 萬字，在管理頁直接編輯時，有一次按鍵卡了 108 秒。

目前真實資料的關係檔只有 5.4 萬字，但廣度擴充會讓兩個問題一起變大，所以要在擴充前處理。

## What Changes

- **投影改為批次寫入**：
  - 原因：`research_compile.project()` 每寫一列就單獨送一次 `INSERT`（2026-11-02 不連資料庫實測）。真實資料約 3,000 次，擴大資料約 10,800 次，其中 relations 與 relation_claims 各約 3,000 次。另外 `legacy_history` 每筆舊歷史都要再查一到兩次資料庫。
  - 改法：同一張表的列累積後批次送出，順序照 foreign key 由上而下；`legacy_history` 改為每張表預先讀一次。
  - **寫入的列、release ID 與內容 hash 完全不變**。閱讀預覽與發布 worker 共用 `project()`，所以發布也一起變快，流程不變。
- **預覽維持 savepoint ＋ rollback**：
  - 不把預覽用的候選 release 留在資料庫，讀者角色永遠看不到未發布的內容，這點不變。
  - 不做「依修訂快取投影結果」或「只投影需要的實體」。批次寫入後仍未達標時，記錄耗時拆解，交給 Boris 決定下一步。
- **管理頁的原始文字編輯框不再逐鍵重繪**：
  - 原始 Markdown／YAML 文字框與表單的內文文字框，改為不受 React 控制（uncontrolled）。打字時不更新 React state，只在第一次修改時標記「有未儲存修改」；儲存與切換模式時才從文字框讀出內容。
  - 原始文字框關閉拼字檢查與自動換行（`spellCheck={false}`、`wrap="off"`）。
  - 選擇另一份文件或重新載入草稿時，文字框必須換成新內容，不得留著舊文字。
  - 不新增前端套件（Boris 2026-11-02 決定），也不限制網頁上可編輯的檔案大小。
- **先查清 108 秒的成因，再修**：
  - 修正前，以 headless Chromium 錄下卡住那次按鍵的 performance trace，判定時間主要花在 React script、layout、拼字檢查或 GC。
  - 修正後用同一方法再量一次。如果卡頓的成因不在上述修法的範圍內，記錄下來交給 Boris 決定，不擴大範圍。
- **把量測工具留在 repo**：
  - `scripts/research_draft_bench.py` 的預覽量測從 1 次改為多次，才算得出 p95，並加上 `project()` 的分段計時。
  - 新增管理頁輸入延遲的量測腳本。上一輪的 108 秒是臨時量的，沒有留下工具。
  - 修正前後的數字寫入 `docs/research-performance.md`，`docs/research-acceptance.md` 的「草稿編輯的剩餘成本」一列跟著更新。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `research-publishing`：新增四項 requirement：
  - 已驗證修訂的閱讀預覽有回應時間上限，不隨研究規模線性變慢。
  - 預覽與發布的投影內容與批次化之前逐列相同。
  - 管理頁編輯近百萬字的檔案時，按鍵不會凍結頁面。
  - 管理頁儲存與切換模式時，用的是文字框當下的內容（改成 uncontrolled 之後的正確性保證）。

## Impact

- **後端**：
  - `backend/app/research_compile.py`：`project()`、`insert()`、`document()`、`legacy_history()` 改為批次寫入。
  - `backend/app/research_drafts.py`：預覽流程不變，只沿用新的 `project()`。
  - 發布 worker（`research_publication.py`）也呼叫 `project()`，介面不變。
  - `research_rebuild_check.py` 多做一件事：用真實的舊歷史資料比對逐列與批次兩種寫法，報告新增每張表的列數與 md5。
  - 不新增資料表或 migration。
- **前端**：
  - `frontend/components/ResearchEditor.tsx`：文字框改為 uncontrolled，並調整 dirty 判斷、儲存與切換模式。
  - `frontend/tests/research-editor.spec.ts` 新增行為測試：打字後儲存送出的是畫面上的內容，切換文件時文字框會換成新內容。
- **量測**：
  - `scripts/research_draft_bench.py`：預覽改為多次，加上分段計時。
  - 新增管理頁輸入延遲腳本（Node＋前端既有的 `@playwright/test`，同 `scripts/reading_walkthrough.cjs` 的作法），報告寫到 `.work/`。
- **文件**：`docs/research-performance.md`、`docs/research-acceptance.md`。
- **營運**：
  - 實機量測依 AGENTS.md 從本 PR 的 worktree 在演練環境進行（`scripts/research_drill.py`），不切換主 checkout，正式服務不執行未合併的程式碼。
  - 投影程式改變，所以要在演練環境跑 `rebuild-check` 與 `pg-check`。
  - 管理頁量測需要演練的 owner 密碼，從 `INDUSTRYFLOW_DRILL_HOME` 的演練 env 檔讀取，不印出、也不寫進報告。
  - merge 後由 Boris 從部署目錄部署，正式環境的確認記在 `docs/research-acceptance.md`。
- **相依套件**：不新增。
- **不在範圍內**：
  - 依修訂快取投影結果、只投影部分實體、把預覽候選 release 保留在資料庫。
  - 改用 CodeMirror 等編輯器套件；限制網頁可編輯的檔案大小。
  - 關係檔格式精簡或拆檔（屬於 Schema 變更，要另外決定）。
  - 首次驗證的耗時（擴大資料約 7.4 秒，每個修訂只算一次，已由上一個 change 的驗證快取處理）。
  - 讀者頁面與公開靜態快照。
