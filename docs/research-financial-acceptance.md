# 台灣／SEC 財務整合的驗收

## 頁面入口（task 6.3，2026-10-18）

以下為本機隔離預覽；公司內點「查看財務與近期資訊」即可到財務區，切指標及口徑，選任一筆「查來源與修訂」讀原始文件與歷史。不是所有公司都有完整深研或財務。

| 入口 | 可以查什麼 |
|---|---|
| [雙鴻](http://127.0.0.1:3014/next?focus=company-auras#company-data) | 台灣上櫃月營收、原值／倍率、提供者彙整日期 |
| [台積電](http://127.0.0.1:3014/next?focus=company-tsmc#company-data) | 台灣上市月營收，保留 TWD 與實際年月 |
| [Vertiv](http://127.0.0.1:3014/next?focus=company-vertiv#company-data) | SEC 全年／單季／累計及期末、申報日與官方來源 |
| [輝達](http://127.0.0.1:3014/next?focus=company-nvda#company-data) | SEC 非曆年期間、基本及稀釋 EPS 分開 |
| [公司比較](http://127.0.0.1:3014/next?view=compare&company_ids=company-vertiv,company-nvda) | 選 2–4 家；角色／產品／風險及財務，期間／範圍／主要來源未核對不排名 |
| [傳聞觀察](http://127.0.0.1:3014/next?view=observations) | 獨立未證實資訊；沒有資料就顯示空清單，不為展示填入傳聞 |

首次讀取後網址固定 `release_id`，篩選、分頁、比較公司與觀測修訂亦保留在 URL，可分享及上一頁。Release 固定研究內容，動態財務仍依讀取時間呈現，不代表財務永久快照。快取與 manifest 採用另屬 6.4。

## 本次單次更新的真實官方資料

透過既有到期更新機制，四個已註冊來源各請求一次並成功。沒有把測試 fixtures 或舊 Float 寫成新版數值；常駐排程／Prefect worker 仍關閉，SEC 沿用已設定 User-Agent 及共用限流，沒有提交聯絡 header。

| 來源 | 解析 records | 新觀測修訂 | 官方回應 SHA-256 |
|---|---:|---:|---|
| [TWSE 月營收](https://openapi.twse.com.tw/v1/opendata/t187ap05_L) | 72 | 108 | `ed3a8aa324336a026c4c70b902694e2a6142aae70b418af8760c947bb88bb990` |
| [TPEx 月營收](https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O) | 26 | 39 | `a27fea120daa8ef4543bcbf6e31426cad2e0201111ee8d97916fbb5fce2727a6` |
| [NVIDIA companyfacts](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json) | 2286 | 1201 | `19ef503a5770f5660964b3c3aea6937579d9b359da344afe6a9adf59c63d26ff` |
| [Vertiv companyfacts](https://data.sec.gov/api/xbrl/companyfacts/CIK0001674101.json) | 850 | 445 | `bd014465e4ffacad9de91c1c4afa057a4ec69ca9d2bded7fd660044be38a3ed3` |

records 是 adapter 解析數，不等於公司或觀測數；新修訂包含可追溯衍生值。Application 實查共 **1793** canonical observations、4 個成功 source jobs；台灣 feed 只對應現有已發布公司，不猜新身分。

原值例：雙鴻 `2026-09-01 ～ 2026-09-30` 為 `2884061 TWD thousand`、倍率 `1000`，呈現 `2884061000 TWD`；提供者彙整日期 `2026-10-17`，正式申報日未提供。Vertiv `2025-01-01 ～ 2025-12-31` 營收 `10229900000 USD`；輝達 `2025-01-27 ～ 2026-01-25` 營收 `215938000000 USD`，不能當作相同期間。

台灣快照含去年同月及今年累計，不代表有 36 個連續月份。台灣季度財年、合併範圍及主要申報來源未核對時仍保留限制；SEC 股別及範圍亦不猜。缺值不填零，整體財務不當成液冷或 AI 收入。來源失效保留研究與原引用。

瀏覽器合成測試只 mock API，PostgreSQL 契約使用獨立 test DB；真實頁面直接查這批官方值。截圖在忽略的 `.work/research-financial-review/`，屬工程走查，不等同 Boris 驗收。真實測試中的日期／原值斷言對應本次快照，未來更新須重新查核，不能為通過測試改寫正式值。

```powershell
python scripts/research_lab.py pg-check --suite research-dynamic
cd frontend
npm run build
npx playwright test --config playwright.offline.config.ts research-financial.spec.ts research-content.spec.ts research-navigation.spec.ts
# 隔離 preview up 完成且 API healthy 後：
$env:RESEARCH_E2E='1'
$env:E2E_BASE_URL='http://127.0.0.1:3014'
npx playwright test research-financial.spec.ts research-dynamic.spec.ts research-service.spec.ts research-navigation.spec.ts research-content.spec.ts
```

Application migration `0015`、head `03799774-3553-5ff6-9910-13a68468af15`、34 正式關係、2915 事件／1970 linked events 未改；owner／publish jobs／financial import batches 均 0。閱讀設計見 [財務閱讀](research-financial-reading.md)。

## 歷史：6.2 階段為什麼沒有頁面財務

### 當時狀態

2026-10-17 查核並於 2026-10-18 階段完成時複核隔離預覽 `industryflow-research`：新版 `research.financial_observations` 為 0、source refresh jobs 為 0；來源排程及 worker 沒有開啟。研究頁在 task 6.2 階段提供公司／產品／術語及來源，尚未完成 task 6.3 的財務圖表、修訂查閱及公司比較操作畫面。

已完成的 5.1–5.6 是 Decimal 財務模型、台灣／SEC adapters、官方補錄、共用更新機制及讀者 API。實際官方樣本已在獨立 test DB 驗證，不曾把測試 fixtures 灌進預覽 application DB。因此「後端驗證通過」不能當作「頁面有完整真實財務可驗收」。既有 legacy Float 財務另保留原契約，不冒充新版精確觀測。

### 當時可驗證的後端證據

| 範圍 | 證據／入口 |
|---|---|
| 台灣上市／上櫃官方原始列、單位與來源 hash | `backend/tests/fixtures/official-tw-20261017/`，含台積電／雙鴻的月營收、損益與負債樣本，以及 provenance |
| SEC 真實資料、非曆年期間及 comparative EPS 重列 | `backend/tests/fixtures/official-sec-20261017/`，含 Vertiv／NVIDIA selected facts 與 provenance；不含聯絡 header |
| 程式行為與限制 | [台灣 adapter](research-financial-tw.md)、[SEC adapter](research-financial-sec.md)、[財務指標](research-financial-metrics.md)、[動態 API](research-dynamic-api.md) |
| 預覽 API 的真實目前狀態 | `http://127.0.0.1:3014/api/v2/companies/company-auras/financials`、`http://127.0.0.1:3014/api/v2/companies/company-vertiv/financials`；沒有值時回空 items 與缺口，不填零 |

重跑官方 fixtures 與真實 PostgreSQL 契約（只使用獨立 `industry_research_test`，不抓外網、不寫入預覽數值）：

```powershell
python scripts/research_lab.py pg-check --suite financial-core
python scripts/research_lab.py pg-check --suite financial-sec
python scripts/research_lab.py pg-check --suite research-dynamic
```

### 當時尚待完成的流程（本輪已接續 6.3）

先完成 6.3 財務閱讀、原幣／期間／累計、來源及修訂、2–4 公司比較與不可比較原因；再對少量真實公司單次更新官方來源並核對 API 與頁面。不能用合成數值或舊 Float 補畫完整曲線。SEC 沿用已設定的 User-Agent 及共用限流，無須重新提供聯絡資訊。

台灣月營收可直接依原年月整理；季度摘要須有證據支持的財年日期設定，否則保留待核對缺口。官方摘要沒提供的 CFO／capex／現金、未核對合併範圍、EPS 股別及公司主要申報來源，仍不能假設已完整。單次更新與開啟常駐排程分開處理；本輪不因查核而自動啟動排程。
