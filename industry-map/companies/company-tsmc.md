---
schema-version: research-v1
entity-id: company-tsmc
kind: company
name-zh: 台積電
aliases:
- TSMC
- 台灣積體電路製造
- 台積公司
summary: 晶圓代工龍頭；114 年營收 3.81 兆元、成長 31.6%，7 奈米以下占晶圓銷售 74%，高效能運算占營收 58%；CoWoS 與 SoIC 等 3DFabric 先進封裝持續量產擴充，但年報未揭露封裝營收。
legacy-keys:
- 2330.TW
listings:
- ticker: 2330.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報致股東報告書（PDF 第 7 頁）全年合併營收與稅後淨利，113 與 114 年度並列
    read-scope: 已讀致股東報告書財務段落
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-advanced-packaging
  description: CoWoS 與 SoIC 先進封裝
  tier: 1
  baseline-path: ai-server/advanced-packaging.md
- segment-id: segment-foundry
  description: 先進製程代工主要供應者
  tier: 1
  baseline-path: semiconductor/foundry.md
claims:
- id: revenue-and-nodes
  statement: 年報揭露 114 年合併營收新台幣 3 兆 8,090.5 億元，較前一年成長 31.6%，稅後淨利 1 兆 7,178.8 億元，毛利率 59.9%；晶圓出貨約 1,500 萬片十二吋約當量，7 奈米及以下先進製程占晶圓銷售金額 74%（113 年 69%）。
  confidence: well-supported
  conditions:
  - 先進製程比重以晶圓銷售金額計，不含封裝
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報致股東報告書（PDF 第 7 頁）
    read-scope: 已讀致股東報告書營運成果
    stance: supporting
    applicable-period: 113 至 114 年度
- id: platform-and-region
  statement: 年報揭露 114 年營收依平台為高效能運算 58%、智慧型手機 29%、物聯網 5%、車用電子 5%、消費性電子 1%、其他 2%；依客戶營運總部所在地為北美 75%、亞太（不含中國大陸與日本）9%、中國大陸 9%、日本 4%、歐洲中東非洲 3%。
  confidence: well-supported
  conditions:
  - 地區依客戶總部，不等於晶片出貨或終端使用地；高效能運算含 PC、伺服器、AI 加速器等
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報 2.2.4 市場占有率與競爭（PDF 第 11 頁）
    read-scope: 已讀市場與競爭段落
    stance: supporting
    applicable-period: 114 年度
- id: customer-concentration
  statement: 年報揭露前十大客戶占營業收入淨額約 70%、76%、78%（112–114 年），最大客戶占 25%、22%、19%，第二大客戶占 11%、12%、17%。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報風險因素（PDF 第 71 頁）客戶集中
    read-scope: 已讀客戶集中風險段落
    stance: supporting
    applicable-period: 112 至 114 年度
- id: three-d-fabric
  statement: 年報說明 3DFabric 包含 SoIC 晶片堆疊與 CoWoS、SoW 等後段整合；CoWoS-S 已量產多年，CoWoS-R 於 114 年進入第三年量產，CoWoS-L 進入第二年量產，3 奈米晶片堆疊於 114 年量產，5.5 倍光罩尺寸 CoWoS 已完成認證並計劃 115 年導入量產，COUPE 矽光子引擎預計 115 年量產；嘉義與台南的先進封裝產能持續擴大。
  confidence: well-supported
  conditions:
  - 年報未揭露先進封裝營收、產能數字或客戶
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報 5.1 技術（PDF 第 52–53 頁）；品質暨可靠性（PDF 第 57 頁）；營運（PDF 第 55 頁）
    read-scope: 已讀先進封裝技術與產能段落
    stance: supporting
    applicable-period: 114 年度年報
- id: foundry-2-share
  statement: 年報估計 114 年台積公司產出占「積體電路製造 2.0」市場產值的 40%（113 年 34%）；積體電路製造 2.0 是台積公司自行擴充的定義，包含封裝、測試、光罩製造與不含記憶體的整合元件製造。
  confidence: inference
  conditions:
  - 市場定義與估計來自公司本身，不能與傳統晶圓代工市占直接比較
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報 2.2.2 市場概況與 2.2.4（PDF 第 10–11 頁）
    read-scope: 已讀市場概況段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: global-capacity
  statement: 年報說明亞利桑那第一座晶圓廠已於 113 年第四季量產，熊本第一座廠於 113 年底量產、第二座規劃 3 奈米，德勒斯登特殊製程廠興建中，新竹與高雄籌備多期 2 奈米廠，並在台中建置 1.4 奈米廠。
  confidence: well-supported
  conditions:
  - 海外廠產能與時程可能調整
  reviewed: '2026-10-18'
  evidence:
  - source-id: tsmc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2330&year=115&mtype=F&
    locator: 114 年度年報致股東報告書（PDF 第 6 頁）；營運（PDF 第 55 頁）
    read-scope: 已讀產能布局段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未揭露先進封裝（CoWoS、SoIC）營收、產能數字與客戶名稱。
- status: not-researched
  reason: 年報財務報表另冊與 SEC 20-F 尚未讀取；本頁只用股東會年報本冊。
---

## 供應角色

台積電在[晶圓代工環節](/next?focus=segment-foundry)屬[先進邏輯代工](/next?focus=role-advanced-logic-foundry)，在[先進封裝環節](/next?focus=segment-advanced-packaging)屬[中介層與 2.5D／3D 整合](/next?focus=role-interposer-integration)。兩個角色分開比較，封裝能力不算進代工角色。

## 研究界線

本頁以 114 年度股東會年報本冊為依據；此版每頁含兩個印刷頁，引用 PDF 頁碼。年報沒有揭露先進封裝營收，所以 CoWoS 的規模不能從總營收或高效能運算比重推估。「積體電路製造 2.0」市占是公司自訂的市場定義。

## 產品與用途

- **先進邏輯代工**：N2、N3、N4／N5、N6／N7 等製程，用於 AI 加速器、CPU、手機 SoC 與網路晶片（PDF 第 12、52 頁）。
- **3DFabric 先進封裝**：CoWoS-S／R／L、SoIC、InFO、SoW 與 COUPE 矽光子引擎（PDF 第 52–53 頁）。
- **特殊製程**：射頻、嵌入式記憶體、電源管理與感測器等（PDF 第 12 頁）。

## 商業模式

只製造客戶設計的晶片，不生產自有品牌產品（PDF 第 10 頁）。114 年營收 3.81 兆元、稅後淨利 1.72 兆元、毛利率 59.9%（PDF 第 7 頁）。

## 客戶與供應商

114 年為 534 個客戶生產 1 萬 2,682 種產品；前十大客戶占 78%，最大客戶 19%、第二大 17%（PDF 第 7、71 頁）。北美客戶占 75%。客戶端 10-K 具名台積電為代工廠的包括 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo) 與 [Astera Labs](/next?focus=company-alab)（見關係）。

## 競爭與替代

年報未具名競爭者，只說競爭對手可能以低價或分散供應鏈爭取訂單（PDF 第 70 頁）。在[先進邏輯代工](/next?focus=role-advanced-logic-foundry)可與[三星電子](/next?focus=company-005930-ks)比較；在[中介層整合](/next?focus=role-interposer-integration)可與[日月光投控](/next?focus=company-3711-tw)比較，日月光 20-F 把台積電的 InFO 列為封裝業的競爭來源。

## 業務曝險

高效能運算占 58%，前兩大客戶合計 36%；AI 需求同時透過先進製程與 CoWoS 封裝傳到營收，但年報只揭露前者的比重。

## 風險

- **客戶集中**：前十大客戶 78%，第二大客戶比重一年由 12% 升到 17%。
- **地緣政治與海外擴廠**：亞利桑那、熊本與德勒斯登的成本與時程。
- **先進封裝產能**：AI 晶片出貨受 CoWoS 產能限制，年報只說明持續擴充。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由合併財報人工補錄。
- 先進封裝營收：年報未公開。
