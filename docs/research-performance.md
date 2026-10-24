# 小群讀取效能基準（task 9.2）

> 2026-10-23 註記：公司財報已由 OpenSpec change `remove-company-financials` 移除；題材代理指標仍使用月營收與 SEC 營收。本文提及的財務資料、頁面與測試為當時紀錄，不再代表現況。

執行日：2026-10-18 至 10-20（台灣時間）。對象是還原演練環境 `industryflow-research-drill`（web `127.0.0.1:3016`），細節見 [備份與還原](research-backup.md)。測試資料只寫入演練 DB，不寫入預覽或正式 DB。

```powershell
cd scripts
python research_drill.py restore --backup ..\backups\research\<時間>; python research_drill.py migrate; python research_drill.py owner
..\..\openspec_pjt\.venv\Scripts\python.exe research_load.py --label real-fixed --background twse-revenue     # 報告：.work/research-load/<label>.json
```

**結論**：修正讀者財務查詢後，真實資料與擴大資料兩組都達標。修正前，擴大資料的 financial p95 是 5.9 秒，另有 8.5% 回 503。

## 工作負載與環境

| 項目 | 設定 |
|---|---|
| 讀者 | 10 個 closed-loop 讀者，暖機 60 秒後量測 300 秒 |
| 查詢比例 | profile 35%、graph 25%、search 15%、financial 15%、coverage 10% |
| 路徑 | 負載腳本 → web 同網域 proxy（3016）→ 演練 API → 演練 PostgreSQL；不只量測前端記憶體命中 |
| 查詢內容 | profile 含公司、產品、角色、應用頁；financial 含單一公司財務與兩家公司的年度比較；coverage 用演練 owner 登入讀取 |
| 背景更新 | 量測開始時對 `twse-revenue` 做一次真實官方來源更新 |
| 目標 | 每類 p95 < 500 毫秒、coverage p95 < 1 秒、樣本至少 100 筆、沒有非預期錯誤 |
| 硬體 | Windows 11、16 個邏輯 CPU、15.4 GB RAM；Docker Desktop 29.2.1（WSL2），可用 16 CPU、7.46 GiB |
| 服務設定 | PostgreSQL 16.15（`shared_buffers` 128 MB、`work_mem` 4 MB、`/dev/shm` 64 MB）；研究 API 為單一 uvicorn process，讀者連線池 5＋5 |
| 修正前版本 | 真實資料 `a5980e2`、擴大資料 `22b8d6c`；API image `sha256:7ac6de7b…` |
| 修正後版本 | `22b8d6c` 加上本次修正（migration `0016`）；API image `sha256:529d32de…` |

修正後兩輪開始前，主機可用記憶體約 2.8 GB（預覽 web／API 已暫停，Chrome 等程式已關閉）。兩輪都完整跑完，資源取樣沒有錯誤。量測期間 DB log 沒有 ERROR；只有還原時預期的「role 已存在」，以及冷讀重啟造成的連線終止。

## 兩組資料

| 資料 | 內容 |
|---|---|
| 真實資料 | 排程備份 `20261018T215359Z` 還原的預覽內容（release `4969dd12…`）：95 家公司、127 個產品／角色／應用頁，其中 51 家有財務 |
| 擴大資料 | 在真實資料上加入 205 家合成公司（`company-synth-NNN`）和合成來源 `synthetic-load-test`：共 300 家公司、3,034 條關係、100,275 筆財務觀測，其中 133 家有財務 |

擴大資料的建立方式（`scripts/research_scale.py`，記錄在 `.work/research-load/scaled-dataset.json`）：

1. 先照正式流程走草稿匯入，被拒絕（422）：3,000 條關係的 `research-relations.yaml` 超過草稿 YAML 的 token 上限。這是本次發現的限制，見下方「草稿路徑的限制」。
2. 改走測試專用投影：
   - 地圖先通過 `validate_map.py`。
   - 在演練環境的暫存 Git repo 做 `git archive`，再由一次性容器投影成 release `feee00f5…`。
   - 財務資料是把 NVIDIA 的群組、原始事實與觀測複製給 82 家合成公司。

合成資料只用來測容量，沒有冒充研究結論。

## 結果

每格依序為 p50／p95／p99／最大值（毫秒），樣本數與錯誤另列。

### 擴大資料

| 類別 | 修正前（`scaled.json`） | 錯誤 | 修正後（`scaled-fixed.json`） | 錯誤 | 修正後判定 |
|---|---|---|---|---|---|
| profile | 1,612 筆：63／133／169／310 | 0 | 4,770 筆：194／291／357／522 | 0 | 達標 |
| graph | 1,156 筆：104／182／239／366 | 0 | 3,277 筆：221／344／418／561 | 0 | 達標 |
| search | 692 筆：37／77／111／244 | 0 | 2,001 筆：128／202／265／458 | 0 | 達標 |
| financial | 706 筆：5,123／**5,935**／6,534／7,105 | **60（503）** | 2,024 筆：290／**431**／526／688 | 0 | 達標 |
| coverage | 442 筆：97／248／758／905 | 0 | 1,304 筆：281／712／1,226／1,810 | 0 | 達標 |

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 吞吐量 | 每秒 15.4 個請求 | 每秒 44.6 個請求 |
| DB CPU（平均／最高） | 1,200%／1,467% | 116%／141% |
| API CPU（平均／最高） | 64%／150% | 138%／187% |
| 結束時記憶體 | DB 903 MiB、API 123 MiB、web 283 MiB | DB 226 MiB、API 104 MiB、web 400 MiB |
| DB 連線最多 | 22 | 16 |
| DB 回傳列數 | 12.7 億 | 1.7 億 |
| 從磁碟讀的 block | 166 萬 | 3.1 萬 |
| 背景更新 | 15.8 秒 | 10.8 秒 |

量測於 2026-10-19 10:09 UTC（修正前）與 17:01 UTC（修正後）開始。

修正前其他類別的延遲較低，只是因為讀者都卡在 financial：讀者是 closed loop，實際併發的其他請求變少。修正後吞吐量是原來的 2.9 倍，各類別在真正的 10 人併發下仍達標。

### 真實資料

| 類別 | 修正前（`real.json`） | 修正後（`real-fixed.json`） | 錯誤 | 判定 |
|---|---|---|---|---|
| profile | 5,933 筆：163／242／292／427 | 5,553 筆：173／261／320／444 | 0／0 | 達標 |
| graph | 4,038 筆：168／249／297／412 | 3,827 筆：179／272／323／500 | 0／0 | 達標 |
| search | 2,514 筆：110／172／224／305 | 2,380 筆：118／183／230／342 | 0／0 | 達標 |
| financial | 2,464 筆：201／340／526／815 | 2,324 筆：205／314／381／526 | 0／0 | 達標 |
| coverage | 1,685 筆：232／576／1,106／1,756 | 1,582 筆：265／637／1,363／1,638 | 0／0 | 達標 |

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 吞吐量 | 每秒 55.4 個請求 | 每秒 52.2 個請求 |
| DB CPU（平均） | 81% | 68% |
| API CPU（平均） | 141% | 145% |
| DB 連線最多 | 17 | 17 |
| DB 回傳列數 | 9,400 萬 | 5,600 萬 |
| 背景更新 | 9.8 秒 | 11.8 秒 |

量測於 2026-10-18 22:47 UTC（修正前）與 2026-10-19 17:09 UTC（修正後）開始。兩輪都幾乎全部命中 buffer，沒有使用暫存檔，沒有 deadlock。所有成功回應的快取標頭都是 `no-store`；修正前擴大資料那輪的 503 回應沒有 `Cache-Control`。

### 冷讀

每格是重啟後的第一個請求／緊接的第二個請求（毫秒）。檔案在 `.work/research-load/cold-*.json`，量測工具為 `.work/tools/cold_reads.py`。

| 情境 | 公司頁 | 圖 | 搜尋 | 台達電財務 | NVIDIA 財務 | 比較 | coverage |
|---|---|---|---|---|---|---|---|
| 擴大資料，修正前（重啟 DB、API、web） | 71／34 | 57／40 | 51／20 | 1,157／999 | 3,320／3,222 | 3,169／3,144 | 465／90 |
| 擴大資料，修正後（API 重建；DB 未重啟） | — | — | — | 42／42 | 213／150 | 64／65 | — |
| 真實資料，修正前（剛重啟的預覽 API；DB 未重啟） | 78／29 | 59／50 | 32／35 | 134／74 | 317／269 | 260／250 | 未測（需 Boris 的 owner 密碼） |
| 真實資料，修正後（重啟 DB、API、web） | 68／30 | 64／82 | 34／20 | 79／64 | 78／95 | 55／55 | 540／161 |

限制：

- 重啟 DB 會清空 `shared_buffers`，但 WSL2 的 OS page cache 不一定會清空，所以「冷」指 process 與 PostgreSQL buffer 冷。
- 擴大資料修正後沒有再重啟 DB 量冷讀：量完修正後的負載，演練環境就換回了真實資料。

## financial 未達標的原因與修正

用讀者角色在閒置的演練 DB（擴大資料）逐段量測 NVIDIA 財務請求。原型都在會 rollback 的交易內執行，結束後確認 policy 與 index 沒有改變。

| 條件 | 主查詢 | 引用來源 | 推導輸入 | 合計 |
|---|---|---|---|---|
| 修正前 | 2,099 ms | 583 ms | 400 ms | 3,098 ms |
| 修正前，改用 superuser（不套 RLS） | 45 ms | 295 ms | — | — |
| 只關閉 JIT | 110 ms | 419 ms | 423 ms | 968 ms |
| 關閉 JIT 並關閉平行查詢 | 112 ms | 976 ms | 335 ms | 1,437 ms |
| 採用的修正，但保留 JIT | 525 ms | 14 ms | 41 ms | — |
| **採用的修正** | **93 ms** | **14 ms** | **43 ms** | 約 150 ms |

三個原因：

1. **JIT 編譯**：
   - 讀者的 RLS policy 寫成多層 `IN (SELECT …)`：financial_observations → financial_groups → entities → entity_snapshots → research_releases。
   - planner 把每層展開成掃描整張表的 hashed SubPlan，所以成本估計隨全庫資料量變大。
   - 擴大資料下，成本越過 `jit_inline_above_cost`／`jit_optimize_above_cost`（500,000），每次查詢都花約 2 秒做 JIT。
   - 真實資料量較小，沒有越過門檻。
2. **503 來自 `/dev/shm` 用光**：
   - 引用來源查詢用平行 hash join 掃過全部 190,758 筆原始事實與整條發布鏈。
   - 10 個讀者同時這樣做，Docker 預設 64 MB 的 `/dev/shm` 不夠用。DB log 記錄了 `could not resize shared memory segment … No space left on device`。
   - 這個 DB 錯誤由 API 轉成 `database-unavailable` 503。
3. **檢查成本跟著全庫變大，而不是跟著這一頁變大**：
   - RLS 與引用 view 都是先算出「全部已發布資料」再比對。
   - `financial_fact_citations` 是 `security_barrier` view，`p.fact_id = f.fact_id` 這種 join 條件推不進去，所以每次都把全部已發布事實算一遍。

採用的修正（migration `0016_reader_row_lookups` 與 `research_financials.enrich`）：

- **三張大表的讀者 policy**（financial_observations、financial_derivations、observation_provenance）：
  - 從 `IN (SELECT …)` 改為以鍵值逐列 `EXISTS` 檢查上層列。
  - 可見範圍不變，仍是「上層列在它自己的 policy 下可見才可讀」。
  - financial_groups、entities、entity_snapshots 的 policy 只涉及數百列，維持原樣。
- **`research_reader_login` 設定 `jit=off`**：讀者查詢都是短的鍵值查詢，JIT 只會增加延遲。保留 JIT 時，主查詢仍要 525 ms。
- **引用來源改為逐筆查詢**：改用 `CROSS JOIN LATERAL (… WHERE c.fact_id = p.fact_id OFFSET 0)`。`OFFSET 0` 防止 planner 把它攤平回一般 join，view 就成為逐筆的鍵值查詢；view 本身與 `security_barrier` 不變。
- **新增 PostgreSQL 契約測試** `test_reader_financial_lineage_stays_limited_to_published_companies`：
  - 讀者 session 的 `jit` 是 off。
  - 已發布公司的觀測、來源、推導與引用都可讀。
  - 未發布公司的同類資料都讀不到，經 LATERAL 路徑也一樣。
  - `pg-check --suite all` 共 241 項通過。
- **`research_drill.py migrate`**：備份保留備份當時的 schema 版本（`0015`）。還原後先升級到目前版本，再重建 API，讀者 session 才會套用新的角色設定。

沒有採用的作法：

- 調大 `/dev/shm`：只會把錯誤藏起來。
- 關閉平行查詢：實測反而更慢。
- 加 `entity_snapshots(entity_id)` index：原型顯示效益很小。
- 降低併發，或用其他類別的平均值掩蓋：規格明文禁止。

**預覽套用時點**：9.2 期間只升級演練環境，`research_lab.py start` 只重新啟動既有容器。預覽在 9.4 首輪（2026-10-20）以 `research_lab.py up` 重建並套用 `0016`，coverage 快取（`a5980e2`）也同時上線。

## coverage 修正前後

10 人短測（暖機 5 秒、量測 20 秒）時，coverage 的 p95 是 3,574 ms（`smoke.json`）：

- 原因是 API 只有一個 process，每次請求都重算全庫覆蓋彙總，彼此排隊。
- `a5980e2` 改為依內容指紋（head generation 加上 15 張輸入表的 hash）重用結果 30 秒；任何輸入改變就重算。
- 修正後，同樣的短測降到 377 ms（`smoke-memo.json`），完整 5 分鐘的各輪在 576 到 712 ms 之間。
- 修正前的短測 financial 有 56 筆錯誤，原因是負載腳本把比較參數寫錯（`ids` 應為 `company_ids`），屬於測試工具錯誤。

## 已知限制

- **coverage 的 p99 超過 1 秒**：各輪 1,106 到 1,363 ms，最大 1.8 秒。目標只要求 p95，已達標；尾端延遲來自快取過期後的那一次重算。
- **容量只驗證到量測範圍**：10 個讀者、這台主機與上述資料規模。超過這個規模不能宣稱已保證容量。
- **合成財務是複製的**：82 家合成公司的財務是 NVIDIA 的複本，分布比真實資料整齊。
- **背景更新只測了一個來源**：每輪只對 `twse-revenue` 做一次更新，沒有測多個來源同時到期。

## 草稿路徑的限制（2026-10-24 由 `improve-draft-editing-performance` 處理）

建立擴大資料時發現下列問題。依 Boris 決定（2026-10-19）另開 change 處理；各項結果見下一節「草稿編輯修正前後」。

- **關係數上限** → **已處理**。改以 parser 事件數與展開節點數計算，上限各 400,000；擴大資料（3,000 條關係）可以匯入。
  - 原記錄：草稿 YAML 的 token 上限是 100,000。當時 `research-relations.yaml` 有 7,049 個 token：taxonomy 262 筆占約 56%，offerings 46 筆占 25%，relations 25 筆占 19%。每條關係約 55 個 token，大約 1,700 條就會碰到上限；3,000 條的匯入會被拒絕（422）。
- **每次儲存都重驗全部檔案** → **已處理**。只重驗新增或內容改變的檔案，解析改用 libyaml。
  - 原記錄：網站表單即使只改一個欄位，也會對全部 261 個檔案（809 KiB）重跑檔案安全檢查，約 3.0 秒；其中 Python 的 YAML 解析約 2.7 秒。API 只有一個 process，儲存期間讀者也會被拖慢。
- **基準比對** → **已處理**。改用 `ManagedGit.file()` 只讀 README。原記錄：每次儲存都對基準版做完整 `git archive`（162 ms）。
- **關係數接近上限時精簡 taxonomy 或拆檔** → **未處理**（Schema 變更）。新上限下，擴大資料的關係檔約用掉 1/4 的事件上限。

## 草稿編輯修正前後（2026-10-24，`improve-draft-editing-performance`）

量測工具：`scripts/research_draft_bench.py`，報告在 `.work/research-draft-bench/{before,after}-{real,scaled}.json`。

| 項目 | 設定 |
|---|---|
| 環境 | 還原演練 `industryflow-research-drill`（web 3016），由排程備份 `20261023T193005Z` 還原，schema `0017`；主機同上方「工作負載與環境」 |
| 正式服務 | 量測期間暫停（`research_lab.py stop`，只留 DB） |
| 修正前 | API image `sha256:e19d022f…`（`main` `d8619f3` 的後端；image 建置後後端沒有其他 commit） |
| 修正後 | API image `sha256:b036a28e…`（branch `6eb5a45`），web `sha256:ade412b2…`；image 內 PyYAML 6.0.3 含 libyaml |
| 路徑 | 量測腳本 → web 同網域 proxy → 演練 API → 演練 PostgreSQL；drill owner 登入 |
| 樣本 | 公司文件（`company-auras`）儲存 30 次、關係檔儲存 30 次（只限擴大資料）；首次驗證、重複驗證、diff、預覽各 1 次 |
| 擴大資料 | 建立草稿後，以 CLI 相同的 import endpoint 匯入 `research_scale.build_tree()` 的樹：466 個檔案、2.19 MB、300 家公司、3,000 條關係 |
| 預覽 | `concept-hbm-stack` 與它的 2 張圖解（瀏覽器式平行請求） |

每格為 p95（單次項目為該次），毫秒。

| 項目 | 真實資料 修正前 | 真實資料 修正後 | 擴大資料 修正前 | 擴大資料 修正後 | 目標 |
|---|---|---|---|---|---|
| 建立草稿 | 3,380 | 922 | 3,909 | 778 | — |
| 匯入擴大資料 | — | — | **422 `draft-rejected`**（2,432） | 200（2,467） | 可匯入 |
| 儲存公司文件 p95（p50） | 3,834（3,398） | **357**（158） | 無法量（匯入被拒） | **307**（265） | ≤ 500／≤ 1,000 |
| 儲存關係檔 p95（p50） | — | — | 無法量 | **2,345**（1,794） | ≤ 3,000 |
| 首次驗證 | 8,843 | 2,206 | 無法量 | 7,413 | — |
| 重複驗證 | 8,377 | **56** | 無法量 | **81** | ≤ 300 |
| 與基準比較（diff） | 3,813 | 833 | 無法量 | 166（基準匯出已快取） | — |
| 預覽 | 11,478 | 2,757 | 無法量 | 10,203 | 見下方 |
| 預覽的 2 張圖解 | 8,211／16,494 | 123／152 | 無法量 | 87／160 | — |
| 整頁預覽（含圖解） | 27,974 | 2,911 | 無法量 | 10,364 | — |
| 每次預覽的完整驗證次數 | 3（依程式推算：預覽 1＋圖解各 1） | **0**（已在首次驗證時算過） | — | **0** | ≤ 1 |
| API 記憶體高點 | 120 MiB | 112 MiB | 124 MiB | 178 MiB | — |

完整驗證次數取自 API 的 `draft-validation computed` log：修正後兩組資料各 1 次（首次驗證），之後的重複驗證、預覽與圖解都沒有再算。修正前的程式沒有這行 log，次數依程式碼推算（標為推論）。

**判定**：spec「草稿儲存只檢查有變動的內容」「同一修訂的完整驗證結果重複使用」「擴大規模的研究可以走草稿流程」三項目標都達成。

### 未在本 change 處理的後續問題

1. **預覽的臨時投影**（design D7 門檻：已驗證修訂的預覽 p95 > 2 秒）。在演練 worker 容器內逐段計時，savepoint 內 rollback：

   | 草稿 | 臨時投影 `project()` | detail | graph |
   |---|---|---|---|
   | 真實資料（修訂 31，261 檔） | 2.69 秒 | 0.05 秒 | 0.01 秒 |
   | 擴大資料（修訂 62，466 檔），`concept-hbm-stack` | 9.45 秒 | 0.10 秒 | 0.02 秒 |
   | 擴大資料，`company-auras` | 9.49 秒 | 0.28 秒 | 0.04 秒 |

   預覽時間幾乎都在「把整份研究投影進 savepoint 再 rollback」，與看哪一頁無關，且隨研究規模成長。是否另開 change（例如依修訂快取投影結果，或只投影需要的實體）交給 Boris 決定。

2. **大型檔案在管理頁的輸入延遲**。以 headless Chromium 在演練管理頁量「按鍵到下一個畫面」：

   | 檔案 | 字數 | 按鍵數 | p50 | p95 | 最大 |
   |---|---|---|---|---|---|
   | `company-auras.md`（表單內文） | 1,592 | 23 | 96 ms | 247 ms | 283 ms |
   | 擴大資料 `research-relations.yaml`（原始文字） | 972,942 | 23 | 277 ms | **108,132 ms** | 108,132 ms |

   約 97 萬字的關係檔在網站表單中有一次按鍵卡住 108 秒，實際上無法在網站編輯；CLI 匯出／匯入不受影響。design 已把前端渲染列為本 change 的非目標，這裡只記錄。真實資料的關係檔目前約 5 萬字，影響較小，但會隨廣度擴充成長。
