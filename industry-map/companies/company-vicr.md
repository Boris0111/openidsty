---
schema-version: research-v1
entity-id: company-vicr
kind: company
name-zh: Vicor
aliases:
- Vicor
- Vicor Corporation
summary: 高密度電源模組廠；Advanced Products（含權利金）占 2025 年營收 61%，客戶集中在資料中心與 hyperscaler，主要在麻州單一工廠製造。
legacy-keys:
- VICR
listings:
- ticker: VICR
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '751978'
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
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: 10-K Item 1（Advanced Products 營收占比，2023–2025 年度）；SEC 申報期間 2025-12-31
    read-scope: 已讀營收占比與 MD&A 營收段落
    stance: supporting
    applicable-period: FY2023–FY2025
roles:
- segment-id: segment-power
  description: 高密度電源模組
  tier: 2
  baseline-path: ai-server/power.md
claims:
- id: product-categories
  statement: 10-K 將產品分為 Advanced Products 與 Brick Products；Advanced Products 用於自有的 Factorized Power Architecture（FPA），包括供 GPU 與 AI ASIC 使用的 Power-on-Package 與裝在主機板背面的垂直供電方案。
  confidence: well-supported
  conditions:
  - 產品能力說明不揭露具體平台或客戶
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 1. Business（Overview；FPA 與 vertical power delivery 段落）
    read-scope: 已讀產品與架構段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: advanced-share
  statement: 10-K 揭露含權利金在內的 Advanced Products 營收占 2025 年總營收約 61.0%（2024 年 55.0%、2023 年 55.3%）；2025 年總營收 407,701,000 美元，較 2024 年成長 13.5%。
  confidence: well-supported
  conditions:
  - Advanced Products 含權利金收入，不等於產品出貨
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 1. Business（Advanced Products 營收占比）；Item 7. MD&A（Net Revenues）
    read-scope: 已讀營收占比與 MD&A 段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: customer-markets
  statement: 10-K 說明 Advanced Products 客戶集中在企業運算中的資料中心與 hyperscaler 領域，Brick Products 客戶則以航太國防、工業設備、測試儀器與軌道運輸為主；2025 年有一家客戶占總營收約 11.1%（2024 年 12.1%）。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 8. Financial Statements（customers 與 concentration 附註）
    read-scope: 已讀客戶市場與集中度附註
    stance: supporting
    applicable-period: FY2023–FY2025
- id: patent-settlement
  statement: 10-K 的 MD&A 說明 2025 年毛利增加主要來自 4,500 萬美元的專利訴訟和解款；2025 年淨利 118,556,000 美元。
  confidence: well-supported
  conditions:
  - 一次性和解款不代表經常性營運獲利
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 7. MD&A（Gross Margin；Overview）
    read-scope: 已讀毛利與淨利段落
    stance: supporting
    applicable-period: FY2025
- id: andover-manufacturing
  statement: 10-K 說明多數電源元件與系統在麻州 Andover 工廠製造，並把該廠長期停產列為風險；部分元件由單一供應商提供。
  confidence: well-supported
  conditions:
  - 未揭露具名供應商
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 1A. Risk Factors（Andover facility；third-party vendors）
    read-scope: 已讀製造與供應風險段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: china-exports
  statement: 10-K 揭露 2025 年銷往中國（含香港）約占總營收 11.9%，以工業與軌道用 Brick Products 為主。
  confidence: well-supported
  conditions:
  - 出口受美國出口管制規範
  reviewed: '2026-10-18'
  evidence:
  - source-id: vicr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/751978/000119312526085102/vicr-20251231.htm
    locator: Item 1. Business（competition 與 China exports 段落）
    read-scope: 已讀出口段落
    stance: supporting
    applicable-period: FY2023–FY2025
gaps:
- status: not-public
  reason: 10-K 未拆分 AI／hyperscaler 產品收入與權利金金額，也未揭露客戶名稱。
- status: not-public
  reason: 10-K 只描述競爭者類型（IDM、fabless 電源半導體廠、電源供應器廠），未具名。
---

## 供應角色

Vicor 在[電源環節](/next?focus=segment-power)屬[板端電源轉換](/next?focus=role-board-power-conversion)，以[高密度電源模組](/next?focus=product-power-module)把母線電壓送到 GPU 或 AI ASIC 附近。

## 研究界線

本頁以 FY2025 10-K 為依據。Advanced Products 的占比包含權利金，2025 年獲利又受一筆專利和解款影響，閱讀營收與毛利時要分開看。客戶名稱沒有揭露。

## 產品與用途

- **Advanced Products**：FPA 架構元件、供 GPU／AI ASIC 的 Power-on-Package，以及裝在主機板背面的垂直供電方案（Item 1）。
- **Brick Products**：傳統架構的整合式電源，用於航太國防、工業、測試與軌道運輸（Item 8 附註）。
- **前端設備**：把 AC 轉成 DC 的產品，也用於資料中心伺服器機櫃（Item 1）。

## 商業模式

自行設計並在 Andover 工廠製造，另有權利金收入。2025 年總營收 407,701,000 美元，Advanced Products（含權利金）約占 61%。

## 客戶與供應商

Advanced Products 的客戶集中在資料中心與 hyperscaler；2025 年一家客戶約占 11.1%（Item 8 附註）。部分元件由單一供應商提供，曾經歷半導體元件短缺（Item 1A）。

## 競爭與替代

10-K 說 Advanced Products 主要與 IDM 及 fabless 電源半導體廠的電源模組與 IC 競爭，Brick Products 與大型電源供應器廠競爭，但未具名。在[板端電源轉換](/next?focus=role-board-power-conversion)角色，可與 [MPS](/next?focus=company-mpwr) 比較；模組與 IC 方案依設計取捨。

## 業務曝險

Advanced Products 占比由 2024 年 55.0% 升到 2025 年 61.0%，說明資料中心需求與權利金的貢獻上升；但 10-K 沒有拆出權利金金額，不能把全部增量歸給產品出貨。

## 風險

- **單一廠製造**：多數產品在 Andover 單廠製造，長期停產會重大影響營收。
- **客戶集中**：一家客戶約占一成一，資料中心客戶又集中在少數 hyperscaler。
- **一次性收益**：2025 年毛利受 4,500 萬美元專利和解款拉高，不能當成經常性水準。
- **出口管制**：中國營收約一成二，受美國出口管制規範。

## 財務可取性

- SEC companyfacts 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- Advanced 與 Brick 的營收占比可由 10-K 核對。
- 權利金金額與 AI 相關產品收入：10-K 未公開。
