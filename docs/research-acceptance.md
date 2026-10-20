# 最終回歸、走查與交付條件（task 9.4 首輪；最終驗收為 task 10.5）

本文件記錄 2026-10-20 的首輪驗收。這一輪 Boris 的閱讀驗收沒有通過（見第三節），最終驗收已移到 task 10.5，等第 10 段的導覽調整完成後重做。tasks.md 中 9.4 的勾選只代表驗收已移交，不代表驗收完成。

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
- **影響**：[財務驗收](research-financial-acceptance.md)列的入口連結都帶這個錨點。
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

## 四、資料來源限制

讀者看到的資料受下列限制；細節見各連結。

- **台灣財務**：
  - TWSE／TPEx OpenAPI 的月營收是最新一期快照，附去年同月與今年累計，不是連續 36 個月的歷史。
  - 季度財年、合併範圍與主要申報來源未核對時保留限制。
  - 提供者只給彙整日期，不提供正式申報日（[台灣 adapter](research-financial-tw.md)）。
- **美國財務**：
  - SEC companyfacts 只映射標準 taxonomy；自訂 tag 保留缺口。
  - 股別與合併範圍不猜（[SEC adapter](research-financial-sec.md)）。
  - 全站共用每秒 2 個請求的限流。
- **未提供的指標**：例如部分台灣公司的營業現金流、資本支出，只能依官方財報人工核對補錄（[財務匯入](research-financial-imports.md)）。不提供通用 PDF 自動解析。
- **產品別收入與具名客戶**：多數公司只揭露合併總營收；產品能力不等於具名客戶採用。26 家深研逐項記錄「未公開／未取得／不適用」，見 [深研交付矩陣](research-deep-delivery-matrix.md)。
- **待核實主張**：163 條主張中有 8 條待核實（公司自述或轉述第三方統計，未取得原始資料），清單見 [總核對](research-final-review.md)。
- **事件來源**：
  - 2026-10-14 的重試中，台積電與 NVIDIA 的 IR 頁回 403，本輪沒有重新嘗試。
  - 歷史只回補到 RSS／分頁能取得的範圍，見 [來源](sources.md)。
- **傳聞**：只放觀察區，不進正式供應圖；目前沒有為了展示而填入傳聞。

## 五、已知缺口

| 缺口 | 影響 | 處理 |
|---|---|---|
| 常駐排程在預覽中關閉 | 到期更新只靠維護者單次觸發，數值不會每小時或每天自動更新 | 正式切換時啟用，且同一時間只能有一個環境在抓取 |
| 8 條待核實主張 | 讀者看到「待核實」標記 | 取得原始資料或第三方報告後再升級或刪除 |
| 產品頁「代表公司」段落 | 仍以既有環節角色列出；能力連結與缺口理由已更新 | 依閱讀驗收決定是否全面改寫 |
| 草稿關係數上限約 1,700 條；每次儲存約 3 秒 | 目前 25 條關係，不受影響；成長後網站編輯會被拒絕或變慢 | 依 Boris 決定另開 change（[效能基準](research-performance.md)） |
| coverage p99 為 1.1 到 1.4 秒 | 只影響 owner 覆蓋頁，偶爾較慢 | 目標只要求 p95，已達標 |
| 容量只驗證到 10 位讀者、這台主機與量測過的資料規模 | 不能宣稱公開網站容量 | 擴大使用前重新量測 |
| 跨裝置讀取尚未設定 TLS | reader gateway 只綁 loopback | 見下方切換檢查表 |
| 收藏存在各自的 origin | 3014 預覽的收藏不會自動出現在正式 origin | 用 JSON 匯出／匯入；正式 origin 首次使用時自動遷移 v1 題材收藏 |

## 六、正式切換檢查表

切換要等 Boris 驗收並另行授權後才進行。合併 `main`、正式部署與歸檔都不在本 change 自動執行。

1. **驗收紀錄**：本文件第三節記錄 Boris 的閱讀驗收結論；必要驗收都已關閉。
2. **切換前備份**：
   - 執行 `research_lab.py backup --secondary D:\backups\industryflow-research`，並備份原服務 DB 與 volume。
   - 確認備份 hash，並在演練環境還原一次（`research_drill.py restore`、`migrate`）。
3. **回復路徑**：
   - schema 都是 additive；回復時切回原 image 與原服務，保留新版 volume，不執行 destructive downgrade。
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
