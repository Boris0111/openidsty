# 最終回歸、走查與交付條件（task 9.4 首輪；task 10.5 最終驗收）

> 2026-10-23 註記：公司財報已由 OpenSpec change `remove-company-financials` 移除；本文提及的 `research-financial-*.md` 文件已刪除，可從 git 歷史查閱。以下內容保留為當時紀錄。

本文件記錄兩輪驗收：

- **2026-10-20 首輪（task 9.4）**：Boris 的閱讀驗收沒有通過（見第三節），因此新增第 10 段調整導覽。tasks.md 中 9.4 的勾選只代表驗收已移交。
- **2026-10-21 最終驗收（task 10.5）**：第 10 段完成後重做回歸、發布與走查，Boris 閱讀驗收通過。各節中標明「task 10.5」的小節是最終結果。

執行日：2026-10-20。對象是隔離預覽 `industryflow-research`（`http://127.0.0.1:3014`）。程式版本 `dde7db9`，含 migration `0016`、coverage 快取與讀者財務查詢修正。

預覽在 9.4 開始時重建：

1. 先手動備份 `20261019T172615Z`，D 槽另有一份。
2. 以 `research_lab.py up` 重建 image，initialize 套用 `0016`。
3. 重建後確認：
   - release 仍是 `4969dd12…`；
   - 讀者角色 `jit=off`；
   - NVIDIA 財務 232 ms、比較 80 ms；
   - 原服務指紋相同。

## 一、自動回歸

| 項目 | 指令 | 結果 |
|---|---|---|
| 地圖 | `python scripts/validate_map.py` | 通過（full）：17 個環節、7 個題材、89 筆來源 |
| validator | `python tests/run_validator_tests.py` | 22 項 schema 測試＋1 個合法基準（2 種模式）＋66 類失敗案例，全部通過 |
| 後端離線 | 臨時容器 `--network none`，唯讀掛載 worktree，`pytest tests` | 283 passed、116 skipped（需 PostgreSQL 的案例由下一列涵蓋） |
| PostgreSQL | `research_lab.py pg-check --suite all`（獨立 `industry_research_test`） | 241 passed；原服務未受影響 |
| typecheck | `npm run typecheck` | 通過 |
| build | `npm run build` | 通過 |
| 前端離線 e2e | `npm run test:e2e:offline`（3011，只攔截必要 API） | 67 passed |
| live e2e（預覽 3014） | 12 個真實服務 spec（讀者 7、管理 5） | 36 passed |
| live e2e（唯讀入口 3015） | `reader-start` 後執行 `research-reader-entry.spec.ts`，跑完 `reader-stop` | 2 passed |
| 發布內容重建 | `research_lab.py rebuild-check`（HEAD） | 254 個研究物件，content hash `18a3b7a5…` 與預覽 release 相同；同一 commit 重建一致 |

紀錄位於 `.work/regression-9.4/`（各步驟 log 與 `summary.txt`）。

- pg-check 是在 9.2 修正後對同一份後端程式執行的；之後的程式變更只有下面的前端錨點修正。
- 修正後重跑了 typecheck、build、前端離線 e2e（68 passed，含新增測試）與預覽 live e2e（36 passed）。

### 最終回歸（task 10.5，2026-10-21）

對象是 HEAD `b212316`，含第 10 段全部變更。10.3（`d313b37`）之後只改了文件，因此 typecheck、build 與前端離線 e2e 沿用 10.3 的結果。

| 項目 | 結果 |
|---|---|
| 地圖 | 通過（full）：17 個環節、7 個題材、89 筆來源 |
| validator | 25 項 schema 測試（含 10.1 新增的應用 `question`／`flow-steps` 3 項）＋1 個合法基準（2 種模式）＋66 類失敗案例，全部通過 |
| 後端離線 | 283 passed、118 skipped（需 PostgreSQL 的案例由下一列涵蓋） |
| PostgreSQL | `pg-check --suite all`：243 passed。執行前暫停預覽與演練環境的 web/api 以釋出記憶體，跑完再啟動 |
| typecheck、build | 通過（10.3） |
| 前端離線 e2e | 67 passed（10.3） |
| live e2e（預覽 3014，新 release） | 43 passed；2 skipped 是唯讀入口的 spec，由下一列執行 |
| live e2e（唯讀入口 3015） | 2 passed，跑完 `reader-stop` |
| 發布內容重建 | `rebuild-check`（HEAD）：254 個研究物件，content hash `b54fdbd6…` 與預覽 release 相同；同一 commit 重建一致；原服務未受影響 |

紀錄位於 `.work/regression-9.4/`，檔名帶 `10.5`。

## 二、發布與走查

### 發布

Boris 以 owner 身分建立草稿並提交發布（`publish_head.py`），發布作業以一次性 worker 執行一次：

- 新 release 是 `a7c1bb50…`（generation 3），Git commit `bae090d`，內容對應 worktree `dde7db9`。
- 理由欄記錄「含 0cd7844 讀者用語修正，供 9.4 閱讀驗收」。
- 隨後的 sync-ref 作業把 `research/published` 同步到 `bae090d`。
- 新 release 的 254 個研究物件中，「全文抽取」「欄位錯位」「-table 模式」「SEC companyfacts」都是 0 筆；舊 release 共 17 處。

### 走查

工具是 `.work/tools/walkthrough_94.cjs`，截圖與 `walkthrough.json` 在 `.work/research-acceptance-review/`。這是工程走查，不能代替 Boris 的閱讀驗收。

桌機 1440×1000 與手機 390×844 各走以下 12 頁：

- `/next`
- 應用（AI 機櫃液冷）
- 角色（晶片端取熱）
- 產品（液冷冷板）
- 公司（雙鴻）與它的財務區
- 術語圖解（兩個液冷回路）
- 公司比較（Vertiv、輝達）
- 公司索引
- 此裝置收藏
- 傳聞觀察
- 舊網址 `/companies/3324.TW`

| 檢查 | 桌機 | 手機 |
|---|---|---|
| 12 頁都是 200，沒有水平溢出、console 錯誤，也沒有維護用語（進階資訊、parser、候選數、csrf、工具名稱） | 通過 | 通過 |
| 返回、前進、重新整理後仍是網址指定的研究；網址固定 `release_id` | 通過 | 通過 |
| 鍵盤 Tab 的第一站是「跳到主要內容」，接著是品牌與主導覽；停到的元素都在畫面上（焦點框樣式另由閱讀驗收判斷） | 通過 | 通過 |
| 公司頁加入收藏後，收藏頁列出雙鴻，並說明只存在此裝置 | 通過 | 通過 |
| 舊 ticker 網址解析到雙鴻 | 通過 | 通過 |

### 走查發現並修正的問題

**分享的財務連結沒有停在財務區**：

- **現象**：直接打開 `/next?focus=company-auras#company-data` 時，網址補上 `release_id` 的同時把 `#company-data` 拿掉了，畫面停在頁首。
- **影響**：財務驗收（已刪除的 `research-financial-acceptance.md`，見 git 歷史）列的入口連結都帶這個錨點。
- **修正**：補 `release_id` 時保留 hash；上方研究、關係與圖解載入後，捲到財務區一次。
- **驗證**：新增離線測試，在 390×400 的小視窗確認錨點保留、財務區在畫面內。先拿掉修正確認這項測試會失敗，加回修正後才通過。重建預覽後，桌機與手機打開分享連結都停在「雙鴻：財務與近期資訊」。

## 三、Boris 閱讀驗收

在 `http://127.0.0.1:3014/next` 閱讀（release `a7c1bb50…`）。建議路線，以及需要你判斷的問題：

1. **從液冷讀到公司**：
   - 路線：`/next` → 「AI 機櫃液冷」應用 → 「晶片端取熱」角色 → 「液冷冷板」產品 → 雙鴻 → 關係與來源 → 「查看財務與近期資訊」。
   - 要判斷的是：「中文標題 → 產品交付與商業意義 → 關係與證據 → 數據與追蹤」這個閱讀順序是否合適。
2. **手機開公司連結**：手機直接打開公司網址時，第一屏是液冷流程的標題與示意，公司內容在下方；在頁內點選則會捲到內容。要決定這樣可以接受，還是分享連結應直接停在公司內容。
3. **深研內容**：抽讀 3 家，例如雙鴻、台達電、Broadcom。看三件事：
   - 商業模式、客戶／供應商、風險是否有閱讀價值；
   - 「未公開／未取得」的說明是否清楚；
   - 8 條「待核實」主張的呈現方式是否可以接受。
4. **產品頁的「代表公司」段落**：仍以既有環節角色列出。要決定是否全面改寫。
5. **財務與比較**：
   - 要讀的頁面：雙鴻月營收、輝達的 EPS 與非曆年期間、Vertiv 和輝達的比較。
   - 要判斷的是：原幣、實際期間與「不可比較」原因是否看得懂。
6. **收藏與備份**：在收藏頁匯出 JSON，再於另一個瀏覽器匯入，看說明是否足夠。

**首輪驗收結論（2026-10-20）：未通過。**

Boris 認為整體結構與功能拆分可行，但必須調整以下三點：

| 回饋 | 處理 |
|---|---|
| 新版「IndustryFlow 產業研究」與原「半導體與 AI 產業研究」主頁的互動與連結不清楚，讀者跳到另一資訊頁容易迷失 | task 10.2：新舊頁共用頁首、搜尋與麵包屑；重複頁面以內容較完整者為準 |
| 為何只有液冷供應鏈有專屬頁籤與圖解 | task 10.1、10.3：移除專屬頁籤；12 條供應鏈採同一版型，沒有圖解的用文字步驟；公司頁獨立 |
| 公司財務只有最近期資訊，對中長期趨勢分析效益不大 | 另開 change（SEC 擴及全部美國公司、放寬顯示期數、台灣歷史來源）；本 change 交付時列為已知缺口 |

第 10 段完成後，在 task 10.5 重做回歸、走查與閱讀驗收。

### 第 10 段調整後的走查（task 10.4，2026-10-20）

依首輪回饋完成：

- **10.1**：應用的 `question`／`flow-steps` 與液冷文字修正（`9d406c9`）。
- **10.2**：共用閱讀外框（`95b57a6`）。
- **10.3**：以供應鏈取代液冷頁籤（`d313b37`）。

現行導覽見 [讀者導覽](research-navigation.md)。

**走查環境**：在演練環境 `http://127.0.0.1:3016` 進行，release `e40e32fb…`，以演練用 owner 發布目前分支的內容。預覽 3014 仍是首輪的 `a7c1bb50…`；新內容要在 10.5 由 Boris 發布，在那之前，預覽的鏈頁沒有問題式標題與步驟。工具是 `.work/tools/walkthrough_10.cjs`，截圖與 `walkthrough.json` 在 `.work/research-acceptance-review/chains/`。

| 檢查 | 桌機 1440×1000 | 手機 390×844 |
|---|---|---|
| 12 條供應鏈頁 | 全部 200、沒有溢出或 console 錯誤、沒有維護用語；頁首 7 個入口 | 同左 |
| 圖解 | 7 條有圖解的都實際載入；5 條沒有圖解的都顯示文字步驟說明 | 手機改用直式圖解 |
| 步驟與產品 | 步驟數與內容一致，每條都有產品卡（2 到 11 張） | 同左 |
| 地圖 → 鏈 | 散熱面板列出「AI 機櫃液冷」卡片，連結帶回原地圖選取 | 同左 |
| 產品頁 | 位置列標出「伺服器二次側」，並在第一屏內；麵包屑為「產業地圖 › 散熱 › AI 機櫃液冷」 | 同左 |
| 公司頁 | 雙鴻獨立呈現，不放圖解；列出「AI 機櫃液冷：有產品證據：液冷冷板、液對液 CDU、機櫃歧管」；財務連結停在財務區 | 同左 |
| 返回與搜尋 | 麵包屑「散熱」回到原地圖選取；單一搜尋「台積電」開啟公司研究 | 同左 |
| 舊網址 | `/companies/3324.TW`、`/watchlist`、`/compare`、環節與題材的 `/next` 網址都轉到現在負責的頁面 | 同左 |
| 事件 | 「官方與報導」「傳聞觀察」兩個分頁 | 同左 |

### 最終發布與預覽走查（task 10.5，2026-10-21）

**發布**：Boris 以 owner 身分用 `publish_head.py` 提交發布，發布作業與隨後的 sync-ref 各以一次性 worker 執行一次：

- 新 release 是 `a5df290c…`（generation 4），Git commit `7a0bda2`，內容對應 worktree `b212316`。
- 內容 hash `b54fdbd6…`，與演練環境 `e40e32fb…` 相同，所以兩邊讀到的是同一份內容。
- 12 條供應鏈都有問題式標題與步驟。

**走查**：工具與 10.4 相同，對象改為預覽 `http://127.0.0.1:3014`，紀錄在 `.work/research-acceptance-review/chains-preview/`。結果與 10.4 一致，桌機與手機都通過：

- 12 條鏈：7 條圖解實際載入，5 條顯示文字步驟；步驟數與內容相符。
- 沒有溢出、console 錯誤或維護用語，頁首 7 個入口。
- 跨頁流程都通過：
  - 地圖卡片 → 鏈 → 產品位置列（第一屏）→ 雙鴻獨立公司頁 → 財務區；
  - 麵包屑返回地圖、搜尋台積電；
  - 5 個舊網址轉址；
  - 事件兩個分頁。

### Boris 最終閱讀驗收（task 10.5，2026-10-21）

**結論：通過。**

- **首輪的前兩點已關閉**：新舊站共用外框；12 條供應鏈採同一版型。
- **第三點**：財務中長期歷史依既定決定另開 change，列於第五節已知缺口，不阻擋本 change 交付。

## 四、資料來源限制

讀者看到的資料受下列限制；細節見各連結。

- **台灣財務**：
  - TWSE／TPEx OpenAPI 的月營收是最新一期快照，附去年同月與今年累計，不是連續 36 個月的歷史。
  - 季度財年、合併範圍與主要申報來源未核對時保留限制。
  - 提供者只給彙整日期，不提供正式申報日（台灣 adapter（已刪除的 `research-financial-tw.md`，見 git 歷史））。
- **美國財務**：
  - SEC companyfacts 只映射標準 taxonomy；自訂 tag 保留缺口。
  - 股別與合併範圍不猜（SEC adapter（已刪除的 `research-financial-sec.md`，見 git 歷史））。
  - 全站共用每秒 2 個請求的限流。
- **未提供的指標**：例如部分台灣公司的營業現金流、資本支出，只能依官方財報人工核對補錄（財務匯入（已刪除的 `research-financial-imports.md`，見 git 歷史））。不提供通用 PDF 自動解析。
- **產品別收入與具名客戶**：多數公司只揭露合併總營收；產品能力不等於具名客戶採用。26 家深研逐項記錄「未公開／未取得／不適用」，見 [深研交付矩陣](research-deep-delivery-matrix.md)。
- **待核實主張**：163 條主張中有 8 條待核實（公司自述或轉述第三方統計，未取得原始資料），清單見 [總核對](research-final-review.md)。
- **事件來源**：
  - 2026-10-14 的重試中，台積電與 NVIDIA 的 IR 頁回 403，本輪沒有重新嘗試。
  - 歷史只回補到 RSS／分頁能取得的範圍，見 [來源](sources.md)。
- **傳聞**：只放觀察區，不進正式供應圖；目前沒有為了展示而填入傳聞。

## 五、已知缺口

| 缺口 | 影響 | 處理 |
|---|---|---|
| 財務只有近期資料 | 台灣 49 家只有最新月營收與去年同月；美國只有 2 家載入 SEC，且只顯示年度 3 期、季度 8 期，不足以分析中長期趨勢 | 依 Boris 決定另開 change：SEC 擴及全部美國公司、放寬顯示期數、驗證台灣歷史來源 |
| 5 條供應鏈沒有圖解；HBM 鏈全部產品，以及 CCL、PCB 兩項產品，尚無公司的產品證據 | 這些鏈以文字步驟呈現，產品卡標示「尚未核對公司的產品證據」 | 本輪只統一版型；新增圖解與內容補強另排 |
| 常駐排程在預覽中關閉 | 到期更新只靠維護者單次觸發，數值不會每小時或每天自動更新 | 正式切換時啟用，且同一時間只能有一個環境在抓取 |
| 8 條待核實主張 | 讀者看到「待核實」標記 | 取得原始資料或第三方報告後再升級或刪除 |
| 產品頁「代表公司」段落 | 仍以既有環節角色列出；能力連結與缺口理由已更新 | 依閱讀驗收決定是否全面改寫 |
| 草稿編輯的剩餘成本（2026-10-24 更新） | 原本的「關係數上限約 1,700 條、每次儲存約 3 秒」已由 `improve-draft-editing-performance` 處理：3,000 條關係可匯入，公司文件儲存 p95 0.36 秒（擴大資料 0.31 秒）。仍偏慢的是預覽的臨時投影（真實資料約 2.7 秒、擴大資料約 9.5 秒），以及管理頁直接編輯近百萬字的關係檔時的輸入延遲 | 是否另開 change 由 Boris 決定（[效能基準](research-performance.md)「草稿編輯修正前後」） |
| coverage p99 為 1.1 到 1.4 秒 | 只影響 owner 覆蓋頁，偶爾較慢 | 目標只要求 p95，已達標 |
| 容量只驗證到 10 位讀者、這台主機與量測過的資料規模 | 不能宣稱公開網站容量 | 擴大使用前重新量測 |
| 跨裝置讀取尚未設定 TLS | reader gateway 只綁 loopback | 見下方切換檢查表 |
| 收藏存在各自的 origin | 3014 預覽的收藏不會自動出現在正式 origin | 用 JSON 匯出／匯入；正式 origin 首次使用時自動遷移 v1 題材收藏 |

## 六、正式切換檢查表

切換要等 Boris 驗收並另行授權後才進行。合併 `main`、正式部署與歸檔都不在本 change 自動執行。

1. **驗收紀錄**：本文件第三節記錄 Boris 的閱讀驗收結論。2026-10-21 最終驗收通過，必要驗收都已關閉。
2. **切換前備份**：
   - 執行 `research_lab.py backup --secondary D:\backups\industryflow-research`，並備份原服務 DB 與 volume。
   - 確認備份 hash，並在演練環境還原一次（`research_drill.py restore`、`migrate`）。
3. **回復路徑**：
   - schema 都是 additive；回復時切回原 image 與原服務，保留新版 volume，不執行 destructive downgrade。（註：自 `0017` 起不成立，`0009` 與 `0017` 是收縮遷移，規則見 [部署與回退](research-deployment.md#遷移擴充與收縮)。）
   - 研究內容的還原與資料庫的還原分開操作。
4. **祕密**：為正式環境產生新的 DB、session、owner 憑證，不沿用預覽的 `.env.research`。owner 密碼由 Boris 在互動終端設定。
5. **私人網路**：
   - 只公開 reader gateway，在它前面設 HTTPS reverse proxy 並限制網段。
   - 管理入口維持 loopback；若要跨裝置管理，改用 `RESEARCH_ADMIN_MODE=https` 與 Secure cookie（[owner](research-owner.md)、[唯讀入口](research-reader-entry.md)）。
6. **排程與限流**：
   - 啟用 Prefect 排程（每小時檢查到期，財務／月營收每天）。
   - 停用其他環境的抓取，避免超過提供者總限流。
   - SEC User-Agent 使用正式聯絡設定。
7. **原 origin 與舊連結**：
   - 新版接手原 origin。
   - 舊 ticker 深連結與舊題材網址可解析；舊 `#candidates` 轉到數據與追蹤。
   - v1 收藏在同一 origin 遷移一次。
8. **切換後檢查**：
   - manifest 與 release 正確；
   - live e2e 通過；
   - 抽查 5 家公司的財務與來源；
   - 備份排程指向正式環境；
   - 原服務停止前保留可回復的 image。
9. **歸檔**：依 `add-evidence-based-theme-assessments` → `improve-industry-reading-and-technical-evidence` → 本 change 的順序同步主 specs。本 change 退役 `theme-watchlist`（`retire_capabilities: true`）。

## 七、2026-10-21 正式切換紀錄

依第六節檢查表執行，Boris 於 2026-10-21 授權。程式版本為 `main` 的 `1f2a716`（PR #1 合併），加上 change `cutover-research-service-to-original-origin` 的 port 與互斥檢查修改。各步驟的原始輸出存在 `.work/cutover-20261021/`。

| 步驟 | 結果 |
|---|---|
| 2. 切換前備份 | `research_lab.py backup --secondary D:\backups\industryflow-research`：`20261021T093452Z`，release `a5df290c…`（第 4 代），C／D 兩份 5 個檔案的 SHA-256 相符。原服務 volume（`industryflow_pg-data`、`industryflow_caddy-*`、`industryflow-reading-db` 的匿名 volume）打包到 `D:\backups\industryflow-original\20261021\`，附 `SHA256SUMS` |
| 2. 演練還原 | 把同一份備份還原到 `industryflow-research-drill`：全表筆數與內容、release、Git refs、資產全部相符，`/next` 回 200，RTO 55.7 秒；`migrate` 前後都是 `0016`。演練完成後以 `research_drill.py down` 移除 |
| 3. 回復路徑 | 見下方「回復步驟」。schema 都是 additive，沒有 destructive downgrade（註：自 `0017` 起不成立，見 [部署與回退](research-deployment.md#遷移擴充與收縮)） |
| 4. 祕密 | 在主專案產生新的 `.env.research`（DB、session、reader、writer 四組都是新的隨機值；只沿用 `SEC_USER_AGENT`），以 `ALTER ROLE` 與 initialize 換掉三個 DB 帳號的密碼。從 Compose 網路實測：新密碼可連線，預覽的舊密碼全部被拒絕。Boris 在自己的終端執行 `research_owner reset`，`credential_version` 1→2（17:49）；session secret 換新後，舊 session 全部失效 |
| 5. 私人網路 | **延後**：Boris 決定這次不做。目前只綁 loopback，沒有跨裝置讀取 |
| 6. 排程與限流 | 演練環境已移除，原服務停止，只剩研究服務一個環境；scheduler 的啟用與補抓另外記錄 |
| 7. 原 origin | 研究服務改綁 web 3010、API 8010、Prefect 4201，reader 3015 不變；3014／8014 已不再監聽。active release 切換前後都是 `a5df290c…`，volume 名稱不變。`research_lab.py up`／`start` 會在原服務有容器運行或 port 被他人占用時拒絕 |

### 在 3010 的驗收

| 項目 | 結果 |
|---|---|
| 後端離線（容器內 `pytest tests`） | 281 passed、118 skipped、2 failed。失敗的 2 項是 `test_financial_sec.py` 的官方樣本 hash：主專案 checkout 以 CRLF 寫出 `backend/tests/fixtures/official-sec-20261017/*.json`（`git ls-files --eol` 為 `w/crlf`），與 provenance 的 LF hash 不符；worktree 的 LF checkout 在 10.5 回歸時通過。這與 port 修改無關，另案處理 |
| 互斥檢查單元測試 | `python -m unittest tests.test_research_lab_exclusion`：5 passed（原服務運行中、port 被他人占用、被自己占用、演練 project 不誤判、`docker ps` 解析） |
| live e2e（3010） | 讀者、管理、收藏、來源更新、財務補錄共 36 passed；2 skipped 是唯讀入口的 spec，由下一列執行 |
| live e2e（唯讀入口 3015） | `reader-start` 後 2 passed，跑完 `reader-stop` |
| 舊 ticker 深連結 | `/companies/3324.TW` → `/next?focus=company-auras&release_id=a5df290c…`，標題「雙鴻」 |
| 舊題材網址 | `/themes/liquid-cooling` 回 200，標題「液冷散熱」 |
| `#candidates` | `/themes/liquid-cooling#candidates` 開在「數據與追蹤」分頁，錨點可見 |
| v1 收藏遷移 | 只放 v1 清單（`industryflow.theme-watchlist.v1`，2 個題材）的新瀏覽器環境：首次開啟遷移成 2 個 v2 題材目標、`v1_migrated: true`、v1 原值保留；重新整理後沒有重複遷移 |

### 3014 上的收藏

瀏覽器的 localStorage 依網址隔離，在 3014 預覽存的收藏不會出現在 3010，切換時也沒有自動搬移。

- 若 3014 時期已用「收藏 → 匯出備份」存過 JSON：到 `http://127.0.0.1:3010/watchlist` 選「匯入」，預覽合併結果後確認。
- 若沒有匯出過：3014 的資料仍在同一個瀏覽器裡，但要有服務在 3014 才能開頁面匯出。可以暫時把 3014 轉到 3010（例如 `docker run --rm -p 127.0.0.1:3014:3014 alpine/socat TCP-LISTEN:3014,fork TCP:host.docker.internal:3010`），在 `http://127.0.0.1:3014/watchlist` 匯出後停止轉送，再到 3010 匯入。轉送期間管理入口會拒絕 3014 的 Origin，這是預期行為。
- 原服務 3010 上的 v1 題材收藏不受影響，第一次開啟新版時會自動遷移。

### 回復步驟

```powershell
cd C:\Users\User\openspec_pjt
python scripts/research_lab.py stop    # 停止 reader、scheduler、web、API，釋放 3010／8010／4201；volume 保留
docker compose up -d                   # 原服務以原 image 與原資料回到 3010
```

原服務的 image 與 volume 都沒有刪除。研究內容與資料庫的還原要分開操作，見 [備份與還原](research-backup.md)。

### 排程、補抓與切換後檢查

**排程**：`--profile scheduler` 啟動 Prefect（4201）、登錄 deployments（`official-information/hourly` 每小時第 7 分鐘，以及 publication／source 的 refresh 與每分鐘補派），並啟動 worker。研究服務是唯一在抓取的環境。

**補抓**：排程停擺期間，最後一次自動抓取是 10-15 23:07，最後一筆入庫事件是 10-18 00:07。以 `ingestion` 服務執行一次 `python -m app.ingest`（不帶 `--backfill-days`，沿用各來源預設的回補範圍：RSS／產業 90 天、SEC 申報 120 天）。59 個來源中，49 個成功、6 個部分成功、4 個失敗；事件 2,915 → 3,096 筆，10-19 有 34 筆、10-20 有 48 筆。紀錄在 `.work/cutover-20261021/ingest-backfill.log`。

- 部分成功的 6 個（SEC `mpwr`／`vicr` 財務、TWSE／TPEx 財務與資產負債）：官方內容已取得，但有欄位或財年待核對，和既往狀態相同。
- 失敗的 4 個（`ir-nvidia`、`ir-tsmc`、`tsmc-node-metrics`、`ocp-cold-plate`）都是 HTTP 403：這些官方網站封鎖自動擷取，切換前就是如此，不是停擺造成的。

**無法補回的缺口：台股重大訊息**。`twse-announcements`／`tpex-announcements` 的 OpenAPI 只提供最近一個交易日的資料（10-21 抓到的是 10-20 的公告）。因此 **10-15（四）、10-16（五）、10-19（一）** 三個交易日的重大訊息沒有入庫；前後交易日每天約 7～13 筆。現有 adapter 無法依日期查歷史；若要補回，需另開 change，寫 MOPS 依日期查詢的 adapter。這三天以後的 TSMC、雙鴻等台股公司事件，閱讀時要知道有這個空窗。

**備份排程**：Windows 工作排程器的 `IndustryFlow Research Daily Backup`（每日 03:30）原本的工作目錄是 worktree，已改為 `C:\Users\User\openspec_pjt`。手動觸發一次結果為 `ok`（`20261021T102926Z`，61.9 秒），D 槽也有一份。worktree 裡 `backups\research\` 的舊備份保留不動，D 槽有同樣的副本。

**抽查 5 家公司財務**（`/api/v2/companies/<id>/financials`，經 3010）：

| 公司 | 來源 | 最新營收期間 |
|---|---|---|
| 台積電 | `tw-mops-summary`，official＋derived | 2026-09 月營收，來源彙整日 10-17 |
| 雙鴻 | `tw-mops-summary`，official＋derived | 2026-09 月營收 |
| NVIDIA | `sec`，official＋derived | 截至 2026-07-26 的年初至今 |
| Vertiv | `sec`，official | 2026-06-30 季 |
| AMD | `sec`，official＋derived | 2026-06-27 季 |

五家都沒有回報 gap。台股 10 月營收要到 11 月上旬才公布，所以月營收停在 9 月是正常的。

### 已知問題（另案處理）

- ~~`prefect` 與 `worker` 在 `compose.research.yaml` 沒有 `restart` 設定，Docker 或主機重開機後排程不會自己恢復~~：已由 `harden-research-operations`（PR #3）處理，演練結果見第八節。
- ~~主專案 checkout 的 SEC 測試 fixtures 是 CRLF，造成 2 項 hash 測試失敗~~：已由 PR #3 以 `-text` 處理，主 checkout 於 2026-10-23 重新取出，42 個 fixtures 皆為 LF。
- 第 5 步私人網路延後。

## 八、2026-10-23 排程自動恢復演練

change `harden-research-operations`（tasks 1.4、4.1）。PR #3 先於演練合併（merge commit `1b1d197`），演練在主 checkout 的 `main` 上進行；此後的 change 改為先驗證再 merge（見 `AGENTS.md`）。

**修正前的實況**：Docker Desktop 於約 19:37 UTC 啟動後，`db`、`api`、`web` 自動回來，`prefect`、`worker` 停在 `Exited (255)`，也就是上次關機時被終止的狀態。排程從啟動後就沒有運作，這正是這次修正的問題。

| 步驟（UTC） | 結果 |
|---|---|
| 20:10 fixtures 刪除後重新取出 | 42 個皆為 `w/lf attr/-text`，工作區無其他變動 |
| 20:10 `research_lab.py check` | 通過，含新的 restart 規則 |
| 20:11 `--profile scheduler up -d` | 只重建 `prefect`、`worker`，`deploy`、`initialize` 重跑後 Exited (0)；`db`、`api`、`web` 未重建。RestartPolicy：`prefect`、`worker`、`db`、`api`、`web` 為 `unless-stopped`，`deploy` 為 `no` |
| 20:12 重建後 | worker 連上 Prefect，`research-publication-reconciliation` 執行完成 |
| 20:12:37 `docker desktop restart` | 20:13:19 完成 |
| 20:13:25 重啟後 | 5 個常駐服務在同一秒自動啟動；`deploy`、`initialize` 未重跑；原服務 `industryflow-*` 與 `reader` 維持停止 |
| 20:13:47 worker 開始提交 flow run | `prefect`、`worker` 的 RestartCount 皆為 0：worker 與 Prefect 同時啟動，約 20 秒後自行連上，既沒有結束也沒有卡住，不需追加 healthcheck |
| 21:07 整點 `official-information/hourly`（`stalwart-rook`） | **Completed**，但 21:32:51 才開始、21:33:00 結束，晚了 26 分鐘。原因是 worker 先補跑停機前已排好的 10-21 12:07／13:07／14:07 三筆（20:32–20:45 執行，其中一筆 4 分鐘），而 `--limit 1` 的名額又要與每 60 秒一次的 3 個 reconciliation flow 共用 |

**停機空窗**：10-21 15:07 到 10-22 20:07 之間沒有任何 hourly run。Prefect 停機期間不會建立排程，所以約 30 小時沒有抓取，這次的自動恢復修正也補不回來。重大訊息：10-21 有入庫（TWSE 6 筆、TPEx 3 筆）。10-22 在 21:11 UTC 時是 0 筆，但 OpenAPI 要到隔天白天才提供前一個交易日的資料，要等台北時間 10-23 白天的抓取後才能判斷，目前待確認。

**限制**：這次重啟的是 Docker Desktop，沒有重開整台主機。Docker Desktop 依附使用者登入，所以實際行為是「登入並啟動 Docker Desktop 後自動恢復」（見 [research-lab](research-lab.md)）。

**後續（另案）**：
- **整點延遲**：hourly 與每分鐘的 reconciliation 共用 `--limit 1` 的 worker；恢復後，停機前排好的舊 run 也會依序補跑。可評估分開 work queue、提高 worker 上限，或讓過期太久的 run 直接略過。
- **停機空窗回補**：要靠 MOPS 依日期查詢的 adapter。
- **10-22 重大訊息**：台北時間 10-23 白天之後查 `events` 確認有沒有入庫。

## 九、2026-10-23 移除公司財報的正式服務驗證（remove-company-financials task 9.2）

維護者同意後，在主 checkout 以 detached HEAD 切到 PR branch（`0442b8d`）執行。原始數據在主 checkout 的 `.work/remove-company-financials/live-9.2.json`（被 Git 忽略）。

| 步驟 | 結果 |
|---|---|
| 1. 再備份一次 | `backups/research/20261023T110134Z`，第二份在 `D:\backups\industryflow-research\20261023T110134Z`；備份時 release `a5df290c…`，其他服務未受影響 |
| 2–3. 重建 api／web，initialize 升級 | `research_lab.py up`：alembic `0016 → 0017`，`research` 下 `financial*` 物件 `18 → 0`；事件 3197、財務事件 147、legacy 營收 326、指標觀測 28、release 皆不變 |
| 4. 重建 worker | scheduler profile `up -d --no-build`；api、web、prefect、worker 同一 image（`88e0440c…`），deploy exit 0 |

**驗證項目：**

- **營收單次更新**（與後台「更新一次」同一條路徑，在 worker 內執行）：`twse-revenue`、`tpex-revenue` 各 1 次 HTTP 200，`success`、新增 0、指標變動 0。7 家代理指標 25 筆與 task 1.1 基準逐筆一致（4 家台股月營收；3 家 SEC 未重抓，沿用原值）。信心：well-supported。
- **移除的入口**：`/api/v2/companies/company-auras/financials`（經 Next proxy）、`/api/admin/financial-imports`、舊 `/api/compare` 都回 404。
- **公司比較**：`/api/v2/compare` 只回 `companies`，欄位為摘要、角色、產品、商業模式、風險、主張與缺口，沒有 metric；`max-age=86400`。畫面上沒有財務表格；文字中的「營業現金流」來自 Vertiv 研究的缺口說明，屬研究內容。
- **事件**：「財報／營收」篩選仍在，列出 `twse-revenue` 產生的月營收事件。
- **收藏**：公司即使帶舊的 `values` 基準，回應仍為 `applicable:false`；題材照常 `applicable:true`。
- **移除的來源**（design Open Question）：registry 同步後 6 列標為 `retired`，分別是 `twse/tpex-financials`、`twse/tpex-balance`，以及 per-company 展開前的 `sec-facts`、`sec-submissions` 基底列。公開來源頁顯示「已停用」。後台的停用按鈕與 409 由自動測試涵蓋，未以 owner 登入實機操作。
- **讀者端 live E2E**（`RESEARCH_E2E=1`，3010）：explorer、research-cache、content、dynamic、navigation、service、watchlist 共 25 passed。另外桌機 1440／手機 390 截圖公司頁、比較、事件、來源頁，四頁皆無橫向溢出。
- **10-22 重大訊息**（第八節的待確認項目）：已入庫，`twse-announcements` 13 筆、`tpex-announcements` 5 筆。

**注意**：merge 前正式服務跑的是 PR branch 的程式，DB 已是 0017。這段期間不要從 `main` 重建 image：`main` 的 alembic 不認得 `0017`，initialize 會失敗，程式也仍會讀已刪除的財務表。若要退回，只能用步驟 1 的備份還原（0017 沒有 downgrade）。

## 十、2026-10-23 公開研究快照的正式資料演練（publish-static-research-snapshot task 4.2）

維護者同意後，在主 checkout 以 detached HEAD 切到 PR branch（`d0e6c08`）執行。依 `docs/public-snapshot.md` 的指令操作，沒有改動資料庫。

| 步驟 | 結果 |
|---|---|
| 1. 重建 api／web | `research_lab.py up`，用 PR branch 的程式重建 image；其他服務不受影響 |
| 2. 匯出 | `research_lab.py public-snapshot`：版本 `a5df290c…`（generation 4），870 個檔案、5.4 MB。各類筆數與資料庫相同：公司 95、產品 59、角色 56、環節 17、應用 12、題材 7、術語 7、研究 1、alias 713、圖解 14。另有引用文件 182 份、技術文件 4 份、代號 95 個。容器內外兩次外洩掃描都沒有發現 |
| 3. 重跑匯出 | 除了 `export.json`，兩次輸出逐位元組相同 |
| 4. 建置與爬頁 | `npm run build:static`：快照內的引用與圖解都存在；輸出 953 個檔案；外洩掃描沒有發現。爬頁 398 passed，8 項只適用合成快照而略過。所有實體頁、95 個代號頁、地圖、題材、目錄與比較都沒有缺檔，也沒有 `/api` 請求；每類頁面在 390px 寬度下都沒有水平溢出 |
| 5. parity | `snapshot-parity.mjs` 和正式 API 比對 6,020 次，0 差異：搜尋 1,328 次（所有 alias、1～2 字前綴、英文 token，跨頁合併比對）、公司搜尋 100 次、目錄 3,590 次（每個單一條件、兩兩組合與 200 個三條件抽樣，含分頁）、比較 303 次（含不合法輸入）、resolve 191 次、研究詳情 254 次、關係圖 254 次。抽查確認比對的是有內容的結果，例如「台積」命中台積電的 3 個 alias、台股公司 49 家 |
| 6. 停機閱讀 | 16:01:43–16:04:45 UTC 停止 worker、prefect、web、api 與 db，API 與網站都無法連線。期間公開版搜尋「台積」得到台積電，比較台積電與廣達、題材「液冷散熱」都正常，`/api` 請求 0 次；地圖、題材、目錄、比較、供應鏈共 53 頁爬頁通過 |
| 7. 恢復 | 依序啟動 db、api、web、prefect、worker；研究版本仍為 `a5df290c…`（generation 4），網站 200。停機約 3 分鐘，沒有碰到每小時 :07 的排程 |

**注意**：

- **正式服務跑的是 PR branch**：merge 前 api、web 跑的是 PR branch 的程式；worker、prefect 是重啟原容器，仍是舊 image（`88e0440c…`）。
- **可以隨時從 `main` 重建**：這個 change 沒有 migration，從 `main` 重建 image 不會失敗，只是少了匯出模組。
- **Next.js 的安全升級提示**：在 agent 環境中，`build:static` 每隔一次會因 Next.js 16.4.0 的安全升級提示中止，重跑即可。這次步驟 4 是第二次才通過。

## 十一、2026-10-23 第一次公開部署（publish-static-research-snapshot task 4.3）

維護者選定 Cloudflare Pages、專案名稱 `industryflow`，同意上傳並以自己的帳號完成 `wrangler login`。部署用的帳號是 crv57485@gmail.com。

| 步驟 | 結果 |
|---|---|
| 1. 建立專案 | wrangler 4.152 把 `pages project create` 轉交給新版流程，結果失敗，沒有建立任何東西；改加 `--force`，直接建立在 Cloudflare Pages 上，正式網址 `https://industryflow.pages.dev` |
| 2. 第一次部署 | 上傳第十節建置的 `frontend/out`（`d0e6c08`），952 檔加 `_headers`，部署 `5e29d050` |
| 3. 抽查發現問題 | 頁面、全站安全標頭與快取標頭都正確，但圖解沒有套上 sandbox CSP。原因是 `_headers` 規則 `/snapshot/*/assets/*` 用了兩個 `*`，Cloudflare Pages 不認得 |
| 4. 修正並重新部署 | 規則改為 `/snapshot/:release/assets/*`（`6b9d693`）。主 checkout 前進到該 commit，重跑 `build:static`，爬頁 398 passed；保存 `public-snapshot/a5df290c…-site` 後重新部署為 `fdc59bb4`，只上傳 61 個有變動的檔案 |

**公開網址抽查（部署 `fdc59bb4`）：**

- **狀態碼**：`/`、`/themes/liquid-cooling`、`/next`、`/companies`、快照 manifest 都是 200。`/events`、`/admin`、`/api/v2/manifest` 都是 404。
- **標頭**：
  - 全站有 CSP（含 `frame-ancestors 'none'`）、`X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`、Referrer-Policy、Permissions-Policy。
  - HTML 是 `max-age=0, must-revalidate`；`/_next/static/*` 與快照檔是 `max-age=31536000, immutable`。
  - 圖解另外帶有 `default-src 'none'; style-src 'unsafe-inline'; sandbox`，兩條 CSP 同時生效。
- **瀏覽器檢查**：
  - 地圖（散熱）、題材「液冷散熱」、台積電、台股公司目錄、供應鏈都正常顯示。代號 `2330.TW` 會轉到台積電。
  - 搜尋「台積」得到台積電，比較頁並列台積電與廣達。
  - 頁尾顯示「研究快照：2026-10-21 發布的研究版本」與免責聲明。
  - 沒有 `/api` 請求、快照檔錯誤或頁面錯誤。
  - 公開網址上等不到 `networkidle`，所以這次抽查改用「讀取中文字消失後等 1.5 秒」判斷頁面已載入。

**回復**：重新部署 `public-snapshot/a5df290c…-site`，或在 Cloudflare 後台把部署回復到先前版本。

## 十二、2026-10-24 Next.js 安全修補的正式服務驗證（patch-nextjs-security-advisories task 2.1）

前端 `next` 從 `16.4.0` 升到 `16.4.3`，修補 GHSA-2464-fhr4-w9xw、GHSA-673q-mjm6-r5xr、GHSA-p3m5-59mp-jv5r。維護者同意後，主 checkout 從 `6b9d693` 切到 PR #8 的 `36c7564`（detached），執行 `python scripts/research_lab.py up`。

| 檢查 | 結果 |
|---|---|
| 重建 | 成功，`protected_services_unchanged: true`。只重建 api 與 web；worker、prefect、db 沿用原容器 |
| 容器內版本 | `docker exec industryflow-research-web-1` 讀 `next/package.json`，版本是 `16.4.3` |
| 讀者端 live E2E（`RESEARCH_E2E=1`，3010） | 37 passed、2 skipped，連跑兩次都是 0 unexpected、0 flaky。skip 的兩項是 `research-reader-entry.spec.ts` 的讀者入口（3015）測試，要明確開啟才會跑 |
| 頁面抽查（桌機 1440、手機 390） | 產業地圖 `/`、供應鏈 `/next`、題材 `/themes` 與「液冷散熱」、公司頁 `/companies/2330.TW`（台積電）都是 200，沒有 console 錯誤，也沒有橫向溢出 |
| 搜尋 | 在共用搜尋框輸入「台積」，得到台積電，點選後開啟 `/next?focus=company-tsmc&release_id=…` |

**附註**：

- 不帶 `?ticker=` 的 `/companies` 顯示「無法開啟這家公司的研究」，並附上公司索引連結。原因是空 ticker 送到 `/api/v2/resolve` 會回 422。這是既有設計，與這次升級無關：`CompanyRedirect` 從 `1abf1e5` 以後沒有改過，站內也沒有連結指向不帶參數的 `/companies`。
- **公開網站不重新部署**。三個漏洞都在 Next.js 伺服器端，`industryflow.pages.dev` 是純靜態檔。下次發布研究、重建公開版時，就會用到新版。
- **建置不再中止**：升級後在 agent 環境中跑 standalone 與 `build:static`，都沒有出現安全升級提示。`docs/public-snapshot.md` 已刪除對應的注意事項。
- **merge 前**：正式服務的 api 與 web 跑的是 PR branch。merge 後，主 checkout 切回 `main` 並 pull，再執行一次 `research_lab.py up`。
