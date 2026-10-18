---
schema-version: research-v1
entity-id: company-mpwr
kind: company
name-zh: 芯源系統
aliases:
- Monolithic Power Systems
- MPS
- 芯源系統
summary: Fabless 電源晶片公司；2025 年 Enterprise Data（伺服器與 AI 系統）占營收 25.2%，前三大客戶皆為經銷商、合計 54%。
legacy-keys:
- MPWR
listings:
- ticker: MPWR
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1280452'
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2023-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: 10-K Item 1 End Markets and Applications 表（2025、2024、2023 年度）；SEC 申報期間 2025-12-31
    read-scope: 已讀終端市場比重表
    stance: supporting
    applicable-period: FY2023–FY2025
roles:
- segment-id: segment-power
  description: 電源管理晶片
  tier: 1
  baseline-path: ai-server/power.md
claims:
- id: fabless-model
  statement: 10-K 說明 MPS 採 fabless 模式，但與一般 fabless 不同，自行開發製程與封裝技術並安裝在代工夥伴設備上；晶圓代工位於中國、台灣、南韓與新加坡，封裝由中國、台灣、馬來西亞與南韓的外包廠完成。
  confidence: well-supported
  conditions:
  - 未揭露具名代工或封裝供應商
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1. Business（Manufacturing；fabless business model 段落）
    read-scope: 已讀製造與供應鏈段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: end-market-mix
  statement: 10-K 的終端市場表顯示 Enterprise Data（雲端與本地 CPU 伺服器、工作站與 AI 系統）占 2025 年營收 25.2%，2024 年 32.5%、2023 年 17.7%；Storage and Computing 占 2025 年 26.3%。
  confidence: well-supported
  conditions:
  - Enterprise Data 含一般伺服器，不等於 AI 加速器專用收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1. Business／End Markets and Applications 表
    read-scope: 已讀終端市場比重表
    stance: supporting
    applicable-period: FY2023–FY2025
- id: distributor-concentration
  statement: 10-K 揭露 2025 年三家經銷商分別占營收 26%、18% 與 10%，前三大客戶（皆為經銷商）合計 54%；10-K 也說明多數產品最終售予 OEM 與 ODM，但這些客戶沒有採購承諾。
  confidence: well-supported
  conditions:
  - 經銷商名稱與最終客戶未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1. Business（Customers, Sales and Marketing）；Item 1A 客戶集中風險
    read-scope: 已讀客戶與經銷段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: asia-revenue
  statement: 10-K 揭露對亞洲客戶的銷售占 2025 年營收 92%（2024 年 94%）；銷售以美元計價，但美元走強可能帶來價格壓力。
  confidence: well-supported
  conditions:
  - 地區依出貨對象，不等於終端使用地
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1. Business（Customers, Sales and Marketing）
    read-scope: 已讀地區與幣別段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: named-competitors
  statement: 10-K 列出主要競爭者為 Analog Devices、Infineon、NXP、ON Semiconductor、Power Integrations、Renesas、ROHM、Semtech、STMicroelectronics 與 Texas Instruments。
  confidence: well-supported
  conditions:
  - 競爭依產品線而異
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1. Business（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: trade-and-export-risk
  statement: 10-K 風險因素說明美國出口管制可能限制部分產品與交易，美中關稅與報復性關稅可能影響業務與財務結果。
  confidence: well-supported
  conditions:
  - 風險敘述不量化影響
  reviewed: '2026-10-18'
  evidence:
  - source-id: mpwr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1280452/000143774926006113/mpwr20251231_10k.htm
    locator: Item 1A. Risk Factors（export controls；tariffs）
    read-scope: 已讀出口管制與關稅段落
    stance: supporting
    applicable-period: FY2025 10-K
gaps:
- status: not-public
  reason: 10-K 未拆分 AI 加速器專用電源收入，也未揭露經銷商、OEM 或 ODM 名稱。
---

## 供應角色

MPS 在[電源環節](/next?focus=segment-power)屬[板端電源轉換](/next?focus=role-board-power-conversion)，提供把母線電壓降到晶片電壓的[電源管理與電壓調節晶片](/next?focus=product-pmic-voltage-regulator)與電源模組。

## 研究界線

本頁以 FY2025 10-K 為依據。終端市場表的 Enterprise Data 包含一般 CPU 伺服器與 AI 系統，不能直接當成 AI 加速器電源收入；經銷商與最終客戶都沒有具名。

## 產品與用途

10-K 說明 DC to DC 方案用於雲端與本地 CPU 伺服器、AI 系統、記憶體、儲存、筆電、車用與網通等。終端市場分為 Storage and Computing、Enterprise Data、Automotive、Communications、Consumer 與 Industrial。

## 商業模式

Fabless，但自有製程與封裝技術，安裝在代工夥伴設備上（Item 1）。主要透過經銷商與加值轉售商銷售，前三大客戶都是經銷商，2025 年合計 54%。

## 客戶與供應商

2025 年三家經銷商分別占營收 26%、18% 與 10%；多數產品最終售予 OEM／ODM，但沒有採購承諾。亞洲客戶占營收 92%。晶圓在中國、台灣、南韓與新加坡代工，封裝在中國、台灣、馬來西亞與南韓。

## 競爭與替代

10-K 列出 ADI、Infineon、NXP、onsemi、Power Integrations、Renesas、ROHM、Semtech、ST 與 TI。在[板端電源轉換](/next?focus=role-board-power-conversion)角色，可與 [Vicor](/next?focus=company-vicr) 的電源模組方案比較；模組與分立方案依設計取捨，不能只比效率數字。

## 業務曝險

Enterprise Data 由 2023 年 17.7% 升到 2024 年 32.5%，2025 年回到 25.2%，顯示伺服器與 AI 系統需求的波動。2025 年最大終端市場是 Storage and Computing（26.3%）。

## 風險

- **經銷商集中**：前三大經銷商合計 54%，經銷商的信用、庫存與策略變化會影響營收。
- **設計導入不保證採購**：OEM／ODM 沒有採購承諾，design win 不保證量產。
- **地緣政治**：亞洲營收占九成以上，製造集中在亞洲；美國出口管制與美中關稅可能影響業務。

## 財務可取性

- SEC companyfacts 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- 終端市場比重可由 10-K 表格核對。
- AI 加速器專用電源收入：10-K 未公開。
