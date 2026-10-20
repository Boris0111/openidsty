# SEC 財務 adapter 與設定

Task 5.3 已完成標準 mapping、官方實際樣本及修訂／共用限流驗證。自動到期擷取仍由 task 5.5 接入，尚未啟動 scheduler；本次樣本沒有寫入 application 財務。

## 本機設定

在新版 worktree 的 `.env.research` 加入一行 `SEC_USER_AGENT=IndustryFlow Research <你的研究聯絡 email>`，將整個尖括號部分換成實際 email，不保留括號。SEC 明文請自動化工具宣告 User-Agent，以機構名稱及聯絡 email 為範例；本專案據此要求 email 格式，不代表必須使用個人主要信箱。可使用自己控制、可收信的專用信箱或 alias。這不是 API key；程式不自行猜測聯絡人，不把設定提交 Git、放進公開研究或一般讀者回應。Compose 會在建立 app 容器時載入它；既有容器不會因存檔立即更新。

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

2026-10-17 使用 Boris 已設定的聯絡資訊，經同一 PostgreSQL gate 實際取得 Vertiv（CIK 1674101）及 NVIDIA（CIK 1045810）companyfacts，均 HTTP 200。原始回應保存在忽略的 `.work/sec-official-20261017/`；`backend/tests/fixtures/official-sec-20261017/provenance.json` 保存 UTC 擷取時間、URL、完整回應及 selected fixtures 的 SHA-256。Selected JSON 保留已映射指標 2023 年以後的事實與其他 namespace，以 Decimal 精確重序列化，不經 Float；沒有保存請求 header 或聯絡 email。

最新 `financial-sec` 為 **19 passed**：新增兩家公司官方數值／非曆年日期比對，以及真實 PostgreSQL 的 NVIDIA basic EPS comparative history。2023-01-29 年度 EPS 在 2023／2024／2025 申報依序為 1.76／1.76／0.18，保存 3 筆 provenance、2 次數值 revision；整批重跑新增 revision／active change 均為 0。這是後續申報重列，不能只憑數值變化宣稱公司會計錯誤。其他 namespace（如 ecd、invest、ffd）僅標為尚未映射，不能擅自稱為公司自訂 taxonomy；API 原本就不保證取得 issuer extensions。
