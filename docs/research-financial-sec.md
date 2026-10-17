# SEC 財務 adapter 與設定

Task 5.3 **尚未完成**：程式與合成邊界測試已實作，官方實際 companyfacts 樣本尚待本機設定有效 `SEC_USER_AGENT` 後擷取核對；不可把離線合成測試當成真實來源驗收。自動到期擷取仍由 task 5.5 接入，尚未啟動 scheduler。

## 本機設定

在新版 worktree 的 `.env.research` 加入一行 `SEC_USER_AGENT=IndustryFlow Research <你的公開研究聯絡 email>`，將整個尖括號部分換成實際 email，不保留括號。這是 SEC 要求的專案名稱／聯絡資訊，不是 API key；程式不自行猜測聯絡人，不把此設定提交 Git、放進公開研究或一般讀者回應。Compose 會在下次建立 app 容器時載入它；既有容器的環境不會因存檔立即更新。不要複製別人的 email 或官方範例作為實際聯絡人。

完整設定後，使用 `python scripts/research_lab.py up` 重建隔離版；不要直接顯示 `docker compose config` 的完整展開內容，也不提前開 scheduler。單次擷取及其 admin 操作由 task 5.5 完成。未設定時 SEC 回 `configuration_required`，台灣來源不應受影響；不把拒絕當成空財報。

官方依據：[SEC API 範圍](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)、[EDGAR 存取及 User-Agent](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)、[SEC Fair Access](https://www.sec.gov/about/developer-resources)。2026-10-17 實讀官方文件，SEC 目前指引為每個使用者總計不超過 10 req/s；本專案採更低的 2 req/s 上限。

## Mapping 與資料邊界

`financial_sec.TAGS` 明列 US GAAP 標準 tag，不從 tag 名稱模糊推測；companyfacts 未提供或只使用自訂 tag 時保留缺口。非 US GAAP taxonomy 目前回 `unsupported-taxonomy`，由台灣正式來源／官方補錄提供資料，不假裝完成 IFRS mapping。

| Canonical metric | US GAAP tag |
|---|---|
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax／Revenues／SalesRevenueNet |
| gross-profit | GrossProfit |
| operating-income | OperatingIncomeLoss |
| net-income-parent／net-income-total | NetIncomeLoss／ProfitLoss，分開保存 |
| eps-basic／eps-diluted | EarningsPerShareBasic／EarningsPerShareDiluted |
| operating-cash-flow | NetCashProvidedByUsedInOperatingActivities |
| capex | PaymentsToAcquirePropertyPlantAndEquipment，正值購置支出；負值須核對 |
| cash-and-equivalents | CashAndCashEquivalentsAtCarryingValue，不混受限制現金 |
| total-liabilities | Liabilities，不使用 LiabilitiesAndStockholdersEquity 或當作有息負債 |

同一申報期間的 alternative revenue tags 若數值不同，保留待核對，不以 tag 順序掩蓋定義差異。毛利率僅由同一 accession、原始期間、幣別的毛利及營收衍生。YoY 與累計相減沿用 financial core 的相容性條件，不在 parser 內猜跨申報相容性。

保留 CIK、accession、tag、原始值／單位、實際起迄、filed、form、原始 `fy/fp/frame` 及來源申報索引 URL。Companyfacts 只提供整個申報主體的標準 facts，未提供原始 XML context ID／完整維度；保存取得的 context，不創造不存在的 XML 識別。意外帶產品／維度的列不當成公司總額。申報範圍明列 `whole-filing-entity`，不由此推導特定產品收入。

`fy/fp` 是申報 metadata，不能直接用在 comparative facts；期間依原始起迄，只有明確核對的日期對應才能加 fiscal year／quarter。年、單季、累計、期末分開；不把每份 10-Q 所有 facts 都當本季。EPS 基本／稀釋各別，普通股／ADR 未明列則 `unspecified`，不可直接比較。來源的實際歷史可用範圍決定覆蓋，不承諾完整歷史或自訂產品／客戶收入。

## 共用限流

`OfficialHttp` 自動辨識 SEC 主機，所有 SEC 呼叫（包含 retry 與每次 redirect）通過同一 PostgreSQL session advisory lock。每次取得鎖先等待 0.5 秒並持有至實際 HTTP 呼叫結束，故不同 client、程序與流程都不能各自用滿 2 req/s。程序中斷時 PostgreSQL 釋放鎖，下一個程序仍須先等待 0.5 秒；DB 不可用時不降級成各程序限流。

這是單一**啟用中擷取環境**的總限流；不得同時啟用舊版、其他 DB 或其他主機的來源 worker，否則彼此不能共用這把鎖。原版來源 worker 目前停止。此設計不新增 Redis／微服務；網路延遲會令實際速率更低，2 req/s 是上限而非保證吞吐量。

SEC 只允許核對的官方 HTTPS 主機，不向外部重新導向傳送聯絡 email。原有 HTTP 重試仍由 task 5.5 統一為共用預算；本次僅確保所有嘗試均受同一限流。

## 已驗證與待驗證

`python scripts/research_lab.py pg-check --suite financial-sec`：16 項合成／真實 DB 測試通過，包含 11 類標準 tag、不同期間、基本／稀釋 EPS、未知股別、自訂 tag 缺口、歧義欄位、重編、同值新申報、重跑不假更新；三個獨立程序使用同一 PostgreSQL gate 的實際間距符合 0.5 秒，HTTP 失敗釋放鎖。HTTP 對外請求使用 MockTransport，不傳送合成 email；一般 IR 頁跳轉 SEC 也必須經同一 gate。

**待取得：** 官方實際 companyfacts 回應的 hash、日期、原始 selected fixtures 與逐項比對。未取得前 task 5.3 checkbox 保持未完成；目前不能宣稱 SEC 擷取或完整 task 5.3 已交付。
