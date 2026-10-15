# 題材判讀與持續追蹤設計

## Context

動機與四階段範圍見 proposal.md。現有 `Theme.data` 保存 frontmatter，`Theme.prose` 與 `checked` 保存全文及原查核日期；`Financial` 有官方數值及期間，`EventTheme` 有內容分類，但分類不是論點查核。圖譜三種遍歷及公開 API 已可用，現有來源失敗仍保留歷史。

2026-10-14 確認本機資料覆蓋頁因 `.gitignore` 的 `coverage/` 未受版本控制；執行中的容器仍包含此頁。來源擷取與判讀的時間、資料取得與商業化確認必須分開。

本 change 涉及來源流程、研究 Schema、動態觀測、版本保存與前端，因此需要此 design。實作依 P0 → P1 → P2 → P3；先完成各階段必要測試，再進入下一階段，最後共同驗收。

## Goals / Non-Goals

**Goals:**
- 使用者可由題材結論回到支持／反向證據，辨識條件、口徑、缺口及更新是否已納入判讀。
- 研究以 Markdown 維護，資料收集與規則分類自動化；動態觀測及研究版本保存在 PostgreSQL。
- 保留既有 URL、回應欄位、公司輕量頁、歷史事件／財報與三種結構遍歷。

**Non-Goals:**
- 本次不生成 AI 投資結論、評分、價格目標或教學／測驗流程。
- 不加入帳號、跨裝置同步、Email／推播及公司比較介面。關注與已讀基準只保存在此裝置。
- 不把七題材的指標設定宣稱為所有題材專屬數據均已完整取得。

## Decisions

### 1. P0：以受版本控制的來源驗證交付

將 `coverage/` 忽略限縮為真正測試產物路徑（根目錄與各測試專案的產物），納入現有 `frontend/app/coverage/page.tsx`。檢查時使用 `git ls-files` 確認主要 route 均在 tracked tree，而非只用本機 `Test-Path`。不改寫原始來源 fixtures 的格式。

新增 GitHub Actions 工作流，checkout 後用 Python 3.12／Node.js 24 與現有鎖定依賴執行地圖、驗證器、後端離線測試、TypeScript、production build 及離線 Playwright。離線瀏覽器測試使用獨立 config／suite，在 3011 啟動該次 production build，browser interception 回應必要公開 API；既有實際資料 E2E 仍作本機整合驗收，不依賴公開來源在 CI 當下成功。CI 不啟動 ingestion，不將 fixtures 載入正式 API／DB。

來源排查先核對已有的 `configuration_required`、HTTP 403、解析錯誤與最後成功。SEC 使用維護者實際提供的聯絡設定，不從 Git 身分自動代填。單來源重試需記錄結果；官方替代入口必須獨立核對與宣告，不以改寫狀態掩蓋原來源失敗。仍受阻時在驗收列出環境缺口，不要求外部站點必須回傳成功才可交付可靠的失敗處理。

ODM 核對採近 30 日已取得的伺服器／組裝新聞與可讀官方資料，保存最多 20 筆具原文的正例、反例與漏失判定；只有找到內容分類問題才調整規則並更新版本。無近期直接資料時新增近 30 日缺口提示，不以公司提及增加數量。

### 2. P1：判讀寫在題材 Markdown，投影利用既有 JSON

在題材 frontmatter 新增 optional `assessment`，在預期 `milestones` 新增 optional 穩定 `id`。既有 fixtures 與舊檔無新欄位仍合法；本次七題材都補上判讀及里程碑 ID。唯一 Schema 文件與驗證器同步更新。

`assessment` 的資料契約：

| 欄位 | 規則 |
|---|---|
| `summary`、`confidence`、`reviewed` | 摘要、`well-supported / inference / needs-verification`、ISO 日日期；`reviewed` 與散文查核日期一致 |
| `evidence[]` | 題材內唯一 kebab-case `id`、來源註冊表的 canonical `source_id`、HTTPS `url`、必要 `excerpt`、`period`；`published` 可空，未知不補日期 |
| `claims[]` | 題材內唯一 `id`、`stance: supporting / counter`、`statement`、`confidence`、至少一筆 `evidence_ids` |
| `conditions[]`、`gaps[]` | 條件至少一筆；缺口可空；未取得反向證據明示，不造反證 |
| `next_checks[]` | `question`、`evidence_required`；時間沿用預期里程碑，不新增自動完成規則 |
| `paths[]` | 穩定 `id`、有序 `steps`、`mechanism` 敘述、`direction: positive / negative / mixed / unknown`、`conditions`、`claim_ids`；每步包含 from／to、既有遍歷類型及必要 via |
| `milestone_reviews[]` | `milestone_id`、`state: unconfirmed / confirmed / contradicted`、`reviewed`、`note`、`evidence_ids`；confirmed／contradicted 必須有證據，實際發生日期未知時留空 |
| `change_reason` | 首次可記首次結構化；已有版本後的實質修改必須有非空原因 |

來源引用使用 registry canonical ID；事件／觀測另保留實際 runtime source ID。以 registry 名稱呈現研究來源，其 runtime 狀態只是擷取狀態，manual 或暫時失敗不能被當作證據從未存在，也不能表示該文件剛被重新查核。

驗證器檢查所有 local ID、引用、列舉、日期及路徑。線性步驟需符合 upstream／downstream；題材擴散需同屬該題材，手足步驟需共享指定下游。正確結構不證明經濟因果或內容正確性；每個傳導假設仍標 inference。新增欄位的最低完整度於七題材交付檢查確認。

判讀由既有研究整理並重新核對引用；若沒有重新查核，不把 2026-10-07 改成實作日。題材查核基準之後的非例行、已發布、直接分類事件列為候選資訊；日期以台北日界比較，未知發布日另列缺口。候選與數值更新不修改 authored assessment。既有 `status` 列舉不新增產品成熟度的另一套混淆列舉。

相較另建一套研究 YAML 或由模型即時產生結論，這種投影可重用既有全文匯入、來源基準與失效時閱讀能力。

### 3. P2：先接九項具體指標，保留衡量界線

新增 `data/theme-indicators.yaml`，只宣告定義與擷取設定，不放觀測數字。指標允許關聯多個題材，驗證來源及題材引用。首輪固定如下，不由實作者臨時選資料來補數：

| 指標 ID | 題材／用途 | 資料與口徑 |
|---|---|---|
| `aaon-liquid-cooling-revenue` | 液冷，direct | AAON 官方季度公告明確區分的 BASX-branded liquid cooling sales；USD、單季，限定該公司的產品口徑 |
| `avc-monthly-revenue` | 液冷，proxy | 3017.TW 官方單月總營收，TWD |
| `micron-quarterly-revenue` | HBM4，proxy | MU 官方單季總營收，USD，保留財報起迄，不當成 HBM4 收入 |
| `landmark-monthly-revenue` | CPO，proxy | 3081.TWO 官方單月總營收，TWD |
| `tsmc-2nm-wafer-revenue-share` | 2nm，direct | 台積電當季已實現 2nm 晶圓營收占比，percent，分母為晶圓營收 |
| `tsmc-monthly-revenue` | 2nm，proxy | 2330.TW 官方單月總營收，TWD |
| `broadcom-quarterly-revenue` | ASIC／GPU，proxy | AVGO 官方單季總營收，USD，不將軟體／網路與 ASIC 收入混為一談 |
| `delta-monthly-revenue` | 800VDC，proxy | 2308.TW 官方單月總營收，TWD，不當成 800VDC 收入 |
| `vertiv-quarterly-revenue` | 電力瓶頸，proxy | VRT 官方單季總營收，USD，明示含熱管理／服務而非純供電收入 |

既有 TWSE／TPEx／SEC 財務投影重用 `Financial`，只取已宣告欄位及 monthly／quarterly 口徑；VRT 在現有公司補充檔加入公開 CIK 1674101，以原 per-company SEC 設定展開，保留其他來源 ID。SEC 缺少聯絡設定時相應指標保留 configuration_required。

兩個直接數值來源在單一來源註冊表新增 `aaon-earnings-metrics` 與 `tsmc-node-metrics`，與原 IR 來源分開保存健康狀態：
- AAON：從 [官方 Investor News](https://investors.aaon.com/investor-news) 發現季度結果，首次最多 5 頁／8 份季度公告、近兩年；以 current-quarter 區塊的 liquid cooling sales 標籤取值，不能取 BASX 混合收入或九個月累計。[Q4 2025](https://investors.aaon.com/investor-news/aaon-reports-fourth-quarter-and-full-year-2025-results-carries-record-backlog-into-2026)、[Q1 2026](https://investors.aaon.com/investor-news/aaon-reports-first-quarter-2026-results-with-record-sales-and-backlog-robust-earnings-growth-and-raises-full-year-guidance) 是已核對的 HTML 解析入口。
- 台積電：從 [季度索引](https://investor.tsmc.com/english/quarterly-results) 發現最近兩年、最多 8 季的官方新聞稿；取當季 `2-nanometer ... total wafer revenue` 百分比，缺少該欄位則不產生數值。保留發布日與當季起迄，指引不作觀測。[2026 Q2 官方稿](https://pr.tsmc.com/japanese/news/3326) 已確認包含明確期間及占比欄位。

沿用現有 HTTP 限速、逾時、重試及免費範圍。新來源在既有 hourly 流程後段串行執行，共用防重疊鎖；原事件／財報 parser 契約保持相容。首次受限範圍回補後，每小時只核對最新公告及必要修訂。財務代理指標重用已取得資料，不為同一輪重複抓相同 financial source。

### 4. P2／P3：動態觀測與研究版本採 additive migration

P2 migration `0003` 新增：
- `indicators`：定義識別、名稱、kind、unit、frequency、basis、來源設定與限制；由定義檔冪等投影。
- `theme_indicators`：題材與指標關聯，讓同一觀測可供多個題材使用。
- `indicator_observations`：指標、實際 source ID、文件 identity、原始期別、period_start／end、basis、unit／currency、Decimal 數值、日期語意、published／reported／fetched、raw excerpt、修訂序號及內容 hash。

同一指標＋來源文件／資料集＋對象＋期間＋宣告的報告頻率口徑為邏輯觀測；單月、單季、累計與年度各自獨立。來源實際揭露的衡量範圍、單位及數值是可修訂內容，與該邏輯觀測最新有效內容相同時不追加，相異時追加修訂，保留舊值。若官方更正範圍而使數值不再符合指標定義，保留該修訂及不適用原因，不當成可比較有效值。比較最新有效修訂，不因重跑更新 fetched 時間產生修訂。Numeric 存數值，API 以十進位字串傳輸；不做匯率換算或補零。可比較的 amount 計增幅，percent 型值以百分點呈現變化；沒有前期或分母為零時回傳不可計算原因。

每個指標最新期別的資料年齡與 HTTP 健康分開：monthly 距 period_end 超過 60 日、quarterly 超過 180 日標示資料過舊，原期間仍完整可見；沒有值則 unavailable，不將未設定與 failed 混成 stale。至少兩個可比較觀測才畫連線趨勢，單筆呈現數值與期間。

里程碑核對仍屬 authored assessment：動態數值與候選新聞只能提供待查依據。confirmed／contradicted 的 note 說明具體對象與適用範圍；預期日期保留原 year／quarter／month 精度，不用日期逾期自動完成或否定。這避免把季度產品收入推定為所有候選公司均已商用。

P3 migration `0004` 新增 `theme_assessment_versions`：theme、遞增 version ID、結構化 payload、content_hash、原 reviewed、recorded_at、reason，並加入題材 active 狀態以保存退場題材的歷史而不再列為公開有效題材。首次只保存當時基準，不偽造更早版本。

判讀匯入在同一 transaction 內比較當前結構化內容：摘要、支持程度、原 status／checked、論點／證據、條件、缺口、下一確認點、路徑及里程碑核對。排除全文排版、runtime 狀態、取得時間、候選資訊與動態指標；按穩定 ID 正規化。相同 hash 不追加，hash 改變追加並要求變更原因；回到歷史內容也追加一筆還原紀錄。inactive 題材在一般 API 與關注摘要視為不可用，DB 歷史保留。

### 5. 唯讀介面與相容性

新增介面（既有欄位與 URL 保留）：

| GET | 回應內容 |
|---|---|
| `/api/themes/{id}/assessment` | `available`、題材 status／checked、完整 assessment、來源擷取警示、候選資訊與未知日期數、`current_version_id` |
| `/api/themes/{id}/indicators?limit=12` | 每個指標定義、取得狀態、最近各期有效觀測、來源／修訂、可比較增減與缺口；limit 1–36 |
| `/api/themes/{id}/assessment/versions?limit=20` | 版本摘要、目前版本、原查核日、記錄時間及原因；limit 1–100，offset 非負 |
| `/api/themes/{id}/assessment/versions/{version_id}` | 該題材的 immutable 版本 payload |
| `/api/themes/{id}/assessment/compare?from_version=...&to_version=...` | 結論／狀態／支持程度及各穩定 ID 的新增、移除、修改；原證據連結與作者原因 |
| `/api/theme-updates?ids=...` | 去重後最多 20 個題材的可用狀態、目前 version ID、indicator_token、candidate_token、待確認摘要；不存在項目逐項回報 |

`/api/themes` 及詳情新增 `assessment_summary`，舊 `status`、`checked`、全文、milestones 與 events 保留。無 assessment 時 available=false，缺口明示；不存在或 inactive 題材回 404，版本不屬該題材回 404，非法範圍參數回 422。候選日期不由 reported／activity／fetched 替代。

覆蓋 API 在題材 row additive 新增 `assessment_available`、`assessment_checked`、`indicator_count`、`available_indicator_count` 與 `indicator_gaps`；環節 row 中不適用的判讀欄位用 null／空清單，既有 30／90 日計數不變。現有 Markdown 報告保留原表並新增題材判讀／指標區塊。

更新 token 由各題材最新有效觀測的 identity／revision／內容，以及候選資訊的 identity／內容計算；排除取得時間與 HTTP 嘗試資訊。API 不接受或儲存個人已讀狀態，不新增公開寫入 endpoint。

### 6. 前端閱讀與此裝置關注

沿用現有配色、16px 正文、手機與鍵盤導航。題材頁順序為判讀卡 → 支持／反向論點、條件與缺口 → 指標及商業化核對 → 全文與預期查核點 → 候選資訊／事件。論點展開可見來源、期間及摘錄；沒有反證如實說明，原始機器欄位放在進階明細。

題材列表與環節的題材連結增加判讀摘要與查核基準；事件詳情可跳到直接相關題材的判讀。原完整結構候選先用明確標籤收合，可展開所有路徑；不刪除 API 路徑、不用取前五筆假裝最重要。

版本比較使用兩個版本選取器及欄位差異，顯示目前版本、當時查核日與記錄時間。比對不呼叫生成式模型。

新增 `/watchlist` 與主導覽入口。localStorage key `industryflow.theme-watchlist.v1` 保存 `theme_ids` 及每題材已顯示的 version ID／indicator_token／candidate_token。首次關注以當時資料建立基準；僅在使用者點「標為已讀」時記錄已顯示 token，移除關注同步移除基準。以 mount 後讀取避免 hydration 誤判；損壞資料或儲存失敗改成本次記憶體暫存並顯示限制，其他閱讀不受影響。

判讀更新、指標新期／修訂、候選資訊為三種獨立提示；沒有實質變更時不亮更新。未知日期只標新收錄／待確認，不宣稱新發生；來源失敗另顯示健康警示。無有效關注時提供回題材列表的入口。

### 7. 驗收與階段順序

- P0：tracked route、乾淨 checkout build、離線導覽、來源失敗保留與近 30 日缺口通過，才進入 P1。
- P1：七題材結構／引用與原查核基準、證據界線、候選不自動改判讀、三種遍歷／回路及桌機／手機入口通過，才進入 P2。
- P2：migration 保留既有資料、兩個 direct parser 真實樣本、七題材 proxy／direct 定義、期別／單位／零值／修訂／失敗隔離與里程碑不自動完成通過，才進入 P3。live 不可取得者另列環境限制。
- P3：同內容重跑不追加版本／未讀、還原版本、跨題材 404、版本 diff、localStorage 損壞／失效、讀取競態及公開唯讀約束通過。
- 完整交付另核對正式資料與 fixtures 隔離、每小時更新、重啟持久化、七題材判讀／指標矩陣及只讀使用者走查。使用者應能從判讀找出來源、成立條件與主要不確定性。

## Risks / Trade-offs

- [來源暫時封鎖或缺 SEC 設定] → 具名記錄限制、保留歷史、官方替代來源獨立宣告；不造假成功。
- [代理數據被看成題材收入] → 定義中固定 kind、scope、limit，數值旁同步呈現；兩個直接來源仍只代表具名公司的特定口徑。
- [格式或業務命名改變] → parser 必須確認標籤、期間與單位；不明確就失敗並保留已取得觀測，真實反例防止取到混合收入。
- [研究與新數據不同步] → 原查核日、未納入證據、指標修訂各別提示；新數據不自動升級結論。
- [維護量提高] → 首輪固定九項指標及七份判讀；沒有新鮮證據就保存原基準，後續擴充以可核對來源為前提。
- [本機關注無同步] → 明確此裝置語意，儲存失效提供提示；帳號及通知另行規劃。

## Migration Plan

P0 先把漏檔與 CI 修正納入 tracked tree。P1 增加 optional Schema、判讀投影及 UI，不需 DB migration。P2 上線前備份，執行 0003、匯入指標定義、從既有 Financial 投影，再執行受限的直接來源回補；記錄真實取得範圍。P3 執行 0004、為目前判讀建立一筆初始版本，加入版本及關注介面。

所有匯入在完整結構驗證後寫入；歷史事件、財報及觀測保留。維護時沿用既有 flow 完成／防重疊操作，不清除 Prefect 歷史。回滾應用 image、保留新增表及資料，不以 destructive downgrade 回退。每階段在隔離 DB／測試環境確認，再核對正式筆數與重啟；新的判讀、指標與來源健康以實測記錄為準。

## Open Questions

維護者的實際 SEC 聯絡設定與執行環境能否存取受限官方來源，於 apply 的來源操作時核對；其缺少／失敗處理已在規格定義，不改變本次範圍、資料契約或任務順序。
