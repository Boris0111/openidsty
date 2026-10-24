# Design

## Context

動機見 proposal.md「Why」；要求見 `specs/research-publishing/spec.md`。

目前草稿流程（`backend/app/research_drafts.py`）的成本分布，以下數字為 2026-10-24 在維護者的 Windows 主機上離線量測（不是容器內；修正前的容器基準由 task 1 量測）：

| 操作 | 目前做了什麼 | 離線量測 |
|---|---|---|
| 儲存（PATCH） | `normalize_payload` 對 260 份文件逐一 `check_document`；`protect_baseline` 對基準版做完整 `git archive`，只為比對 README；寫入後再查一次修訂 | normalize 3.6 s；git archive 162 ms（前一輪記錄） |
| 驗證 | `validate_payload` = 再一次 normalize ＋ 寫暫存目錄 ＋ `validate_map.py` 子程序 ＋ 同 process 內再載入一次 | 12–13 s；其中 `validate_map.py` 子程序約 3 s |
| 比較（diff） | 每次 `git archive` 基準版 ＋ `export_files`（再 normalize 一次並重寫資產） | 約 3.6 s 以上 |
| 預覽 | 完整驗證 ＋ savepoint 內臨時投影後 rollback | ≥ 12 s ＋ 投影 |
| 預覽中的每張圖解 | 每個請求各自完整驗證 | 每張 12 s |

profile 顯示時間幾乎都花在純 Python 的 YAML 解析：一次驗證要呼叫 522 次 `yaml.load`。原因是 `safe_yaml` 先用純 Python 的 `yaml.scan` 數 token，再用純 Python 的 `SafeLoader` 解析；同一份文件在 normalize、驗證器子程序、同 process 載入時各被解析一次。

| 解析對象 | 純 Python | libyaml |
|---|---|---|
| 現有 260 份 YAML／frontmatter，load | 2.13 s | 0.38 s（結果完全相同） |
| 同上，結構上限掃描 | 1.23 s（`yaml.scan`，57,931 token） | 0.14 s（C parser 事件，34,546 個） |
| 擴大資料的關係檔（1.07 MB），load | 4.94 s | 0.91 s |
| 同上，結構上限掃描 | 2.78 s | 0.32 s |

擴大資料由 `scripts/research_scale.py` 的 `build_tree()` 產生（465 個 YAML／Markdown，2.05 MB）。其中關係檔有 170,774 個 token（超過現行每份文件 100,000 的上限，所以匯入被拒）、97,813 個 C parser 事件、展開後 47,380 個節點（現行節點上限 100,000）。

限制條件：

- 研究 API 是單一 uvicorn process；草稿相關 endpoint 多為同步函式，在 threadpool 執行。
- 演練環境（`industryflow-research-drill`）有自動產生的 drill owner 密碼，量測可以腳本化；正式服務的 owner 登入需要 Boris 本人。
- 發布由一次性 worker 執行，worker 自己跑完整 `validate_payload`（`research_publication.py`），與 API process 內的狀態無關。

## Goals / Non-Goals

**Goals:**

- 儲存成本只跟這次改動的檔案有關。
- 每個修訂最多做一次完整驗證，驗證、預覽、圖解共用。
- 所有 YAML 解析都用 libyaml，判定結果與原本完全相同。
- 修正前後在同一環境、同一方法下量測，數字可重現。

**Non-Goals:**

- 不把驗證結果寫入資料庫，也不跨 process 或跨重啟保留。
- 不改預覽的臨時投影方式（只量測，見 D7）。
- 不改發布 worker 的流程。
- 不改前端打字時的渲染方式。目前沒有證據顯示打字會卡；演練時順便觀察，若會卡就記成後續問題。

## Decisions

### D1：YAML loader 以 libyaml 為底，缺少時退回純 Python

`research_documents.UniqueLoader` 與 `validate_map.UniqueKeyLoader` 的父類別改為 `getattr(yaml, 'CSafeLoader', yaml.SafeLoader)`。重複鍵與非文字鍵的檢查寫在 `construct_mapping`，這部分在 C 版仍由 Python 的 constructor 執行，所以規則不變。`compile_archive` 透過子程序執行 `validate_map.py`，會自動用到同一個 loader。

- 研究服務啟動時若沒有 libyaml，記一筆 warning。後端測試另有一項檢查：在 CI 與 API image 內，`yaml.__with_libyaml__` 必須為真。
- 維護者本機沒有 libyaml 時，`validate_map.py` 照常可用，只是比較慢。
- **替代方案**：換成 `ruamel.yaml` 或其他 parser。不採用，因為要新增依賴，且語意差異更大。PyYAML 的 C 版共用同一個 constructor 與 resolver，差異最小。
- **錯誤訊息**：C 版的錯誤位置格式和純 Python 版略有不同。測試只比對錯誤代碼與是否拒絕，不比對錯誤訊息全文。

### D2：結構上限改以 C parser 事件計算，並依擴大資料重新校準

`safe_yaml` 不再用純 Python 的 `yaml.scan`，改以 `yaml.parse(..., Loader=同一個 loader)` 逐一讀事件：遇到 `MappingStartEvent`／`SequenceStartEvent` 時深度加一，遇到對應的 End 事件減一。深度上限仍是 32。

- 事件數上限：400,000 個。擴大資料關係檔是 97,813 個，約有 4 倍餘裕。
- alias 展開後的節點上限：從 100,000 提高到 400,000。擴大資料是 47,380 個，約有 8 倍餘裕。
- 拒絕自我參照 alias 的規則不變。
- 5 MiB 草稿上限不變，所以單一文件的實際規模仍有上界。
- **為什麼可以放寬**：PyYAML 建構 alias 時是共用同一個物件，不會真的複製，記憶體不會被放大；真正會放大的是之後的遞迴處理，而節點上限擋的就是這個。把節點上限設為 400,000，走訪成本也還在亞秒等級。
- **替代方案**：只提高 token 上限、繼續用純 Python 的 scan。不採用，因為光掃描擴大資料的關係檔就要 2.8 秒。

### D3：增量 normalize

新增 `normalize_changes(previous, payload)`。`previous` 是目前修訂已存的 payload，它在當初儲存時已通過 normalize。

1. 整份檢查每次都做：envelope 欄位、檔案數、5 MiB 序列化大小、全部路徑的 `safe_path`、casefold 後是否重複、資產 hash 格式。這些都是毫秒等級。
2. `check_document` 只對 `previous` 沒有的路徑或內容不同的檔案執行。
3. 輸出格式與 `normalize_payload` 相同（排序後的 files／assets）。

`save_revision` 與 import 都改用這個函式。建立草稿（`export_files`）、驗證與發布仍用完整的 `normalize_payload`。

- `save_revision` 寫入後直接組出回傳結果，不再重查一次修訂（目前會再讀一次約 1–2 MB 的 jsonb）。
- **替代方案**：把每個檔案的檢查結果存進資料庫。不採用，因為上一個修訂本身就是「已通過檢查」的證明，不需要另存狀態。

### D4：讀取單一 Git 檔與基準匯出快取

- `ManagedGit.file(commit, path)`：先 `verify(commit)`，再以 `git cat-file blob <commit>:<path>` 讀取，path 必須通過 `safe_path`。`protect_baseline` 改用這個方法。
- 基準匯出快取：`export_files(ManagedGit().files(commit))` 的結果以 commit 為鍵，存在 process 內的 LRU，最多 2 筆。commit 不可變，資產又是內容定址，所以快取不會過期。diff 改用快取。
- **替代方案**：快取 `git archive` 的 tar bytes。不採用，因為瓶頸在後面的 normalize，不在 archive。

### D5：依修訂內容 hash 快取驗證結果，同一修訂只算一次

新增 `research_drafts` 內部的 `ValidationCache`，鍵是 `draft_revisions.payload_hash`（normalize 後內容的 digest，已含資產 sha），值是 `(result, bundle)`。

- LRU 最多 2 筆，通常就是目前修訂與上一個修訂。bundle 含資產 bytes，擴大資料下單筆可能達數 MB，所以上限不設大。
- **single-flight**：全域 lock 保護一張「鍵 → 進行中的計算」表。第一個請求負責計算，其他請求等它完成後讀結果。endpoint 在 threadpool 執行，所以用 `threading` 的 primitive。
- 驗證、預覽、圖解三個 endpoint 都改為從快取取得；圖解只需要 `result['valid']` 與 bundle 裡的 media-type。
- **無效結果也快取**，但「資產尚未取得」與「資產 hash 不符」這兩種錯誤例外。這兩種錯誤來自資產 store 的狀態，而不是修訂內容，補上檔案後應能重試。
- **與發布的關係**：發布 worker 自己跑 `validate_payload`，不讀這個快取，所以發布前的完整驗證不受影響。API 端發布前的預檢（`research_publication.py:112`）可以用快取，因為 worker 還會再驗證一次。
- **快取何時失效**：部署新版驗證器時 API process 會重啟，快取自然清空，不需要另外為驗證器版本設計失效機制。
- **替代方案**：
  - 把驗證結果存進 `draft_revisions`：驗證器改版後需要額外的失效設計，而且 bundle 太大，不適合放資料庫。
  - 用 `functools.lru_cache`：沒有 single-flight，也無法排除資產錯誤。

### D6：草稿摘要與 PATCH 回應

- 新增 `GET /api/admin/drafts/{id}/summary`，回傳 `{draft_id, base_release_id, revision, schema_version, paths, assets}`，ETag 為修訂號。`paths` 是排序後的文字檔路徑。
- `PATCH /api/admin/drafts/{id}` 改回傳摘要，加上 `documents: {path: document_parts}`，涵蓋這次變更中仍存在的檔案（**BREAKING**，只影響管理 API）。
- `GET /drafts/{id}`、`/export`、`/import` 的格式不變，CLI 不需要修改。
- `frontend/lib/admin-proxy.ts` 的 GET allowlist 加入 `summary`。
- `ResearchEditor.tsx`：
  - 選擇草稿時改讀 summary，`Draft` 型別的 `files` 改為 `paths`。
  - 儲存後直接用 PATCH 回應更新 draft 與 document，在本地更新清單中這份草稿的修訂號，不再重新讀取文件與草稿清單。
  - `AdminOperations` 只用到 draft_id、base_release_id、revision，不受影響。
- **替代方案**：PATCH 加 `?view=summary` 參數，讓舊行為保留。不採用，因為唯一的使用端就是管理頁，保留兩種回應只會多一條沒人用的路徑。

### D7：量測方法與預覽投影的處理門檻

新增 `scripts/research_draft_bench.py`，沿用 `research_integration.Session`、drill owner 與 `research_scale.py` 的資料：

- 走 web 同網域 proxy，打真實的 API 與 PostgreSQL。
- 兩組資料：真實資料，以及擴大資料（以 CLI 匯入路徑建立；修正前會被上限擋下，這本身就是一筆基準記錄）。
- 每組量測：儲存一份公司文件 ×30、儲存關係檔 ×30（只限擴大資料）、首次驗證、重複驗證、diff、預覽一份含圖解的文件（含所有圖解請求）。
- 計數方式：預覽是否重跑完整驗證，由 API 的 debug log 計數驗證次數；log 只寫在演練環境，不進入回應內容。
- 報告寫到 `.work/research-draft-bench/<label>.json`，摘要寫入 `docs/research-performance.md`。

預覽的臨時投影：如果修正後「已驗證修訂的預覽」p95 仍超過 2 秒，就記錄投影耗時的拆解，交給 Boris 決定是否另開 change。本 change 不處理。

## Risks / Trade-offs

- [C 版與純 Python 版在少數 YAML 邊界的行為不同] → 新增等價測試，對現有研究、`tests/fixtures/valid` 與擴大資料逐份比對兩種 loader 的解析結果與編譯 hash；另外比對一組邊界案例（重複鍵、merge key、非 BMP 字元、BOM、tab 縮排）的接受或拒絕結果。
- [增量檢查放過「規則收緊後才變得不合格」的舊檔案] → 只影響儲存；驗證與發布仍做完整檢查（spec「發布仍全面檢查」）。發布 worker 不使用任何快取。
- [快取讓 API process 記憶體增加] → 驗證快取與基準快取各最多 2 筆。演練時記錄 API 的記憶體高點，與前一輪的 104–123 MiB 比較。
- [single-flight 的等待者在計算失敗時卡住] → 計算者在 `finally` 內移除進行中的項目並通知等待者；等待者有逾時（與 proxy 的 60 秒一致），逾時後回 503，可以重試。
- [放寬 YAML 上限擴大了被攻擊的面] → 只有 owner 能寫入草稿，深度與自我參照的檢查不變，5 MiB 上限也不變。結構炸彈的測試保留，並加上「剛好超過新上限」的案例。
- [PATCH 回應格式改變，可能有其他使用端] → 已確認 CLI 不使用 PATCH，`research_scale.py` 只用 import／export；E2E 測試的 mock 同步更新。
- [Windows 主機的離線數字與容器內不同] → spec 的目標以演練環境容器內的量測為準；本文件的離線數字只用來決定方向。

## Migration Plan

1. 不需要 migration，也不改資料表。
2. 部署方式：重建 API 與 web image（`research_lab.py up`）。驗證快取只存在記憶體，重啟後自然是空的。
3. 回復方式：切回前一個 commit 重建 image。草稿與修訂資料格式不變，可直接沿用。
4. 前後端必須一起部署：舊管理頁會預期 PATCH 回傳 `files`。兩者都由 `research_lab.py up` 一次重建，所以不會只更新一邊。
