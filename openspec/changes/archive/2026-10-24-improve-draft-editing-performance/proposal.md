# Proposal

## Why

2026-10-23 的產品定位決定：地圖要先往廣度擴充（光通訊、電網／電力設備、網路系統），但**擴充前必須先修好草稿編輯效能**。目前網站表單只改一個欄位，也要等全部 261 個檔案重新檢查（約 3 秒）；驗證、預覽、甚至預覽裡的每一張圖解，都會從頭重跑整份研究的完整編譯（本機實測 12–13 秒）。擴大資料（300 家公司、3,000 條關係）連草稿匯入都會被 YAML token 上限拒絕。檔案越多，這些成本會一起變大，所以要在擴充前處理。上一輪效能 change 已記下問題與建議（`docs/research-performance.md`「草稿路徑的限制」）。

## What Changes

- **YAML 解析改用 libyaml（C 版）**：
  - 草稿檢查（`safe_yaml`）與地圖驗證器（`validate_map.py`、編譯器）共用的 YAML 解析都改用 C 版 loader。
  - 照樣拒絕重複鍵與非文字鍵，結構深度、數量與 alias 展開也照樣有上限。
  - 結構上限改用 C parser 的事件數計算，不再先用純 Python 掃描一次。
  - 環境沒有 libyaml 時退回純 Python 版，結果不變，只是比較慢；研究服務的 image 必須有 libyaml，由測試檢查。
- **儲存只重驗有變動的檔案**：
  - 表單儲存與 CLI 匯入時，只有新增或內容改變的檔案要重跑單檔安全檢查；沒改的檔案沿用上一個已接受修訂的結果。
  - 整份草稿的大小、檔案數、路徑重複與資產 hash 這類便宜的檢查仍每次全做。
  - **完整驗證與發布前的檢查不變**，仍檢查全部檔案。
- **不再為了比對一個檔案而讀出整個基準版**：
  - `ManagedGit` 新增讀取單一檔案的方法；儲存時只讀基準版的 `industry-map/README.md`。
  - 與基準比較（diff）時，基準版的匯出結果依不可變的 commit 暫存在記憶體，不再每次重新匯出、重寫資產。
- **同一修訂只完整驗證一次**：
  - 驗證結果以修訂內容的 hash 為鍵，暫存在 API process 內（有數量上限）。
  - 驗證、閱讀預覽、預覽中的圖解請求共用同一份結果；圖解請求不再各自重跑完整編譯。
  - 同一修訂有多個請求同時到達時，只做一次驗證，其餘等結果。
- **草稿 YAML 上限依擴大資料重新校準**：3,000 條關係的擴大資料要能正常匯入草稿，並保留明確餘裕。上限仍然存在，5 MiB 草稿上限與深度上限都不變。
- **管理頁儲存只需一次往返**：
  - 目前儲存會連打三個請求：PATCH（回傳整份約 0.85 MB 草稿）、重新讀取文件、重新讀取草稿清單。
  - 改為 PATCH 一次回傳修訂摘要與剛儲存的文件。
  - 選擇草稿時改讀摘要（只有檔案清單，沒有全文）。
  - **BREAKING（僅限管理 API）**：`PATCH /api/admin/drafts/{id}` 的回應改為摘要，不再含全部檔案內容。唯一的使用端是管理頁，會一起修改；CLI 的匯出、匯入不受影響。
- **量測與記錄**：
  - 先在演練環境量出修正前的基準：真實資料與擴大資料兩組，儲存、驗證、比較、預覽、圖解各量一次。
  - 修正後用同一方法再量一次，結果寫入 `docs/research-performance.md`。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `research-publishing`：新增草稿編輯的回應時間與規模要求：
  - 儲存成本只跟這次改了什麼有關，不隨整份研究變大。
  - 同一修訂的驗證結果重複使用，圖解與預覽不重跑完整編譯。
  - 擴大資料規模的草稿可以匯入與儲存。
  - 加速不得放寬安全與驗證規則：完整驗證、發布前檢查與重複鍵等規則照舊。

## Impact

- **後端**：`backend/app/research_documents.py`（YAML loader、單檔檢查、增量 normalize）、`research_drafts.py`（儲存、diff、驗證、預覽、圖解共用快取、PATCH 回應與新的摘要讀取）、`research_git.py`（讀取單一檔案）、`research_compile.py`（驗證器子程序沿用 C loader）。不新增資料表或 migration。
- **驗證器**：`scripts/validate_map.py` 的 `UniqueKeyLoader` 改為優先使用 C 版；改完要跑 `tests/run_validator_tests.py`。維護者本機沒有 libyaml 時照常可用。
- **前端**：`frontend/components/ResearchEditor.tsx` 改用摘要與 PATCH 回應；`frontend/lib/admin-proxy.ts` 允許新的摘要路徑；`frontend/tests/research-editor.spec.ts` 跟著更新。
- **文件**：`docs/research-drafts.md` 的 API 表、`docs/research-performance.md` 的修正前後量測。
- **營運**：量測需要在演練環境以維護者身分登入，需要 Boris 本人輸入密碼；演練要在主 checkout 切到這個 branch 進行（依 AGENTS.md）。
- **相依套件**：不新增套件。`PyYAML==6.0.3` 的 Linux wheel 已內含 libyaml，要在 image 內確認。
- **不在範圍內**：
  - 關係檔格式精簡或拆檔（屬於 Schema 變更，`industry-map/README.md` 要另外決定）。
  - 發布 worker 的流程與耗時。發布會自動受惠於較快的 YAML 解析，但流程不變。
  - 預覽的臨時投影（savepoint 內建立再 rollback）先只量測；若量測顯示它單獨就超過目標，記錄下來，另外決定是否處理，不在本 change 擴大範圍。
  - 一般讀者頁面與公開靜態快照。
