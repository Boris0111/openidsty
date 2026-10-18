---
schema-version: research-v1
entity-id: company-crdo
kind: company
name-zh: Credo
aliases:
- Credo
- Credo Technology Group
summary: 高速連接晶片與主動電纜公司；FY2026 營收成長 205.7%，增量逾 99% 來自 hyperscale 客戶的 AEC 放量，AEC 由貿聯代工製造。
legacy-keys:
- CRDO
listings:
- ticker: CRDO
  market: US
  exchange: XNAS
  share-class: ordinary shares
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1807794'
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: 10-K Item 7. MD&A（Revenue，FY2026 與 FY2025）；會計年度結束於 4 月底前後的星期六，故不填固定年度結束日
    read-scope: 已讀營收與成本段落
    stance: supporting
    applicable-period: FY2025–FY2026（截至 2026-05-02）
roles:
- segment-id: segment-networking
  description: 高速連接晶片與線材
  tier: 2
  baseline-path: ai-server/networking.md
claims:
- id: product-portfolio
  statement: 10-K 說明產品組合包括 ZeroFlap 主動電纜（AEC）與光收發模組、OmniConnect 記憶體方案，以及用於光與銅 Ethernet、PCIe 的 retimer 與 DSP；產品基於自有 SerDes 與 DSP 技術，速度 32G 至 200G／lane，另有 SerDes IP 授權與 chiplet。
  confidence: well-supported
  conditions:
  - 產品清單不揭露各產品營收
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: Item 1. Business（Overview）；Item 7（Overview）
    read-scope: 已讀產品組合段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: aec-revenue
  statement: 10-K 揭露 FY2026 營收 1,335,116 千美元，較 FY2025 的 436,775 千美元成長 205.7%；MD&A 說明增量主要來自 AEC 出貨量，hyperscale 資料中心客戶的 AEC 放量貢獻逾 99% 的營收增量。FY2026 淨利 472.3 百萬美元。
  confidence: well-supported
  conditions:
  - 10-K 未揭露 AEC 占總營收比例，只說明增量來源
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: Item 7. MD&A（Revenue；Cost of Revenue；Overview）
    read-scope: 已讀營收與成本說明
    stance: supporting
    applicable-period: FY2025–FY2026
- id: customer-concentration
  statement: 10-K 以簽約方口徑揭露 FY2026 客戶 A 占營收 49%（FY2025 67%）、客戶 B 占 32%；另以終端客戶口徑補充，FY2026 三家終端客戶分別占 33%、32%、19%，FY2025 單一終端客戶占 63%。前十大客戶約 90%，北美客戶占 58%（FY2025 15%）。
  confidence: well-supported
  conditions:
  - 簽約方可能是終端客戶的代工夥伴；客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: Item 7（Overview 終端客戶表）；Note 3 Concentrations；Item 1A 客戶集中風險
    read-scope: 已讀兩種口徑的客戶表與地區說明
    stance: supporting
    applicable-period: FY2024–FY2026
- id: manufacturing-partners
  statement: 10-K 說明 FY2026 晶圓全部由 TSMC 生產；封裝由 Amkor 與 ASE 負責，測試由京元電子（KYEC）與矽格（Sigurd）負責，AEC 產品由貿聯（BizLink）製造。
  confidence: well-supported
  conditions:
  - 未揭露各供應商採購金額
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: Item 1. Business（Manufacturing and Suppliers）；Note 3 Concentrations
    read-scope: 已讀製造與供應商段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: named-competitors
  statement: 10-K 列出主要競爭者為 Broadcom、Marvell 與 Astera Labs，以及多家線纜與光收發模組供應商，並稱競爭者通常只在部分產品上與其競爭。
  confidence: well-supported
  conditions:
  - 競爭依產品線而異
  reviewed: '2026-10-18'
  evidence:
  - source-id: crdo-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm
    locator: Item 1. Business（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2026 10-K
gaps:
- status: not-public
  reason: 10-K 未揭露 AEC、retimer、光 DSP 與光模組的個別營收，也未揭露客戶名稱。
---

## 供應角色

Credo 在[網路環節](/next?focus=segment-networking)屬[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)，供應[主動電纜](/next?focus=product-active-electrical-cable)與 [retimer](/next?focus=product-retimer)，也有[光通訊 DSP](/next?focus=role-optical-dsp)。

## 研究界線

本頁以 FY2026 10-K 為依據。10-K 只說 AEC 貢獻了逾 99% 的營收增量，沒有揭露 AEC 占總營收的比例。客戶集中度有簽約方與終端客戶兩種口徑，兩者不能混用。

## 產品與用途

- **主動電纜（AEC）**：ZeroFlap AEC，用於 AI 與一般伺服器的 scale-up／scale-out 銅纜連接（Item 1）。
- **Retimer 與 DSP**：光與銅 Ethernet、PCIe 用 retimer 與 DSP（Item 1）。
- **其他**：ZeroFlap 光收發模組、OmniConnect 記憶體方案、SerDes chiplet 與 IP 授權（Item 1）。

## 商業模式

Fabless；晶圓由 TSMC 生產，封測外包，AEC 由貿聯製造（Item 1）。FY2026 營收 1,335,116 千美元，成長 205.7%，淨利 472.3 百萬美元（Item 7）。

## 客戶與供應商

簽約方口徑下客戶 A 占 49%、客戶 B 占 32%；終端客戶口徑下三家分別占 33%、32%、19%（Item 7、Note 3）。前十大客戶約 90%。供應商具名 [TSMC](/next?focus=company-tsmc)、[日月光投控](/next?focus=company-3711-tw)旗下 ASE、[Amkor](/next?focus=company-amkr)、[京元電](/next?focus=company-2449-tw)、矽格與[貿聯](/next?focus=company-3665-tw)。

## 競爭與替代

10-K 列出 [Broadcom](/next?focus=company-avgo)、[Marvell](/next?focus=company-mrvl) 與 [Astera Labs](/next?focus=company-alab)，以及線纜與光模組廠。AEC 與光模組、被動銅纜互為替代選項，取捨要看傳輸距離、功耗與可靠度。

## 業務曝險

北美客戶占比由 15% 跳到 58%，營收增量幾乎全來自 hyperscaler 的 AEC 放量，曝險集中在少數雲端業者的 AI 機櫃部署。

## 風險

- **客戶集中**：前十大客戶約 90%，三家終端客戶合計逾八成。
- **單一代工**：晶圓全部由 TSMC 生產，AEC 由貿聯製造。
- **無長期採購承諾**：客戶可在通知期內取消或延後訂單（Item 1A）。
- **技術替代**：光互連或 CPO 普及會壓縮 AEC 的適用距離。

## 財務可取性

- SEC companyfacts 可自動取得標準科目；主要申報來源設為 SEC。
- 會計年度結束於 4 月底前後，與曆年不同，跨公司比較需對齊期間。
- AEC 與 retimer 個別營收：10-K 未公開。
