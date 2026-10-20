---
schema-version: research-v1
entity-id: company-aph
kind: company
name-zh: 安費諾
aliases:
- Amphenol
- Amphenol Corporation
summary: 全球連接器與互連系統廠；2025 年 IT datacom 占營收約 36%，AI 帶動 Communications Solutions 有機成長 71%；官網另列液冷快接頭產品線。
legacy-keys:
- APH
listings:
- ticker: APH
  market: US
  exchange: XNYS
  share-class: Class A common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '820313'
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
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: 10-K Item 7. MD&A（Net Sales 與分部營收，2023–2025 年度）；SEC 申報期間 2025-12-31
    read-scope: 已讀 MD&A 營收段落
    stance: supporting
    applicable-period: FY2023–FY2025
roles:
- segment-id: segment-interconnect
  description: 高速連接器與液冷快接頭
  tier: 1
  baseline-path: ai-server/interconnect.md
claims:
- id: it-datacom-share
  statement: 10-K 揭露 2025 年各終端市場占營收約為：IT datacom 36%、工業 19%、汽車 15%、通訊網路 10%、國防 9%、行動裝置 6%、商用航太 5%；IT datacom 產品包括高速、電源與主動／被動光纖互連，用於 AI 與機器學習系統。
  confidence: well-supported
  conditions:
  - 終端市場比重不等於 AI 專用收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 1. Business／Markets（各終端市場段落）
    read-scope: 已讀七個終端市場段落
    stance: supporting
    applicable-period: FY2025
- id: segment-growth
  statement: 10-K 揭露 2025 年營收 23,094.7 百萬美元，較 2024 年成長 52%（有機 38%）；Communications Solutions 約占 52%、有機成長 71%，主要來自 IT datacom 中的 AI 應用，Interconnect and Sensor Systems 約占 22%，也提到 AI 應用帶動。
  confidence: well-supported
  conditions:
  - 營收含收購貢獻；分部營收不拆分 AI 金額
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 7. MD&A（Net Sales；segment 段落）
    read-scope: 已讀營收與分部段落
    stance: supporting
    applicable-period: FY2024–FY2025
- id: backlog-ai
  statement: 10-K 估計 2025 年底未交貨確定訂單約 89 億美元（2024 年底約 61 億美元），增加主要來自支援 AI 應用產品的需求與收購；未交貨訂單出貨前一般可取消。
  confidence: well-supported
  conditions:
  - backlog 可在出貨前取消，不等於確定營收
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 1. Business（Backlog）
    read-scope: 已讀 backlog 段落
    stance: supporting
    applicable-period: 2024-12-31、2025-12-31
- id: customers-and-competitors
  statement: 10-K 說明產品售予數千家 OEM、EMS、ODM 與服務供應商，2023–2025 年沒有單一客戶占營收一成以上，經銷商約占 19%；主要競爭者包括 Aptiv、Belden、Corning、Foxconn Interconnect Technology、Glenair、HUBER+SUHNER、Luxshare、Jonhon、Molex、Rosenberger、Sensata、TE Connectivity 與 Yazaki。
  confidence: well-supported
  conditions:
  - 競爭依產品線而異
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 1. Business（Customers；Competition）
    read-scope: 已讀客戶與競爭段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: commscope-acquisition
  statement: 10-K 揭露 2026 年 1 月 9 日完成收購 CommScope 的 Connectivity and Cable Solutions 業務，總價約 105 億美元現金，增加 IT datacom 與通訊網路的光纖互連能力；融資使債務增加，預估 2026 年淨利息費用約 8 億美元。
  confidence: well-supported
  conditions:
  - 收購在 FY2025 期後完成，FY2025 數字未含此業務
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 7. MD&A（Liquidity）；Note 15 Subsequent Events；Item 1A 收購與債務風險
    read-scope: 已讀收購與融資段落
    stance: supporting
    applicable-period: FY2025 10-K（期後事項）
- id: geographic-exposure
  statement: 10-K 揭露 2025 年非美國市場約占營收 65%，其中中國約 16%；約九成員工在美國以外，在約 40 個國家設計、製造與組裝。
  confidence: well-supported
  conditions:
  - 地區依客戶所在地
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/820313/000110465926013549/aph-20251231x10k.htm
    locator: Item 1A. Risk Factors（global operations）；Item 1. Business（Manufacturing）
    read-scope: 已讀地區與製造段落
    stance: supporting
    applicable-period: FY2025
- id: liquid-cooling-portfolio
  statement: Amphenol Industrial 產品頁列出 UQD、UQDB、UQD/UQDB Rev 2.0、BMQC、LQC、MQD 與 SHQD 液冷快接頭系列，應用包括 AI 資料中心液冷、HPC 與機櫃盲插介面，並稱部分產品與 OCP 的 UQD、BMQC 規格一致。
  confidence: well-supported
  conditions:
  - 產品頁不揭露客戶、出貨或收入；OCP 用語為 aligned，不是認證聲明
  reviewed: '2026-10-18'
  evidence:
  - source-id: aph-liquid-cooling-product-page
    url: https://amphenol-industrial.com/products/liquid-cooling-systems/
    locator: Amphenol Industrial〈Liquid Cooling Systems〉產品頁（系列清單、Applications、OCP 段落）
    read-scope: 已讀產品頁全文；未讀連結的白皮書與型錄
    stance: supporting
    applicable-period: 2026-10-18 讀取（頁面無日期）
gaps:
- status: not-public
  reason: 10-K 不拆分 AI 相關營收，也未揭露客戶名稱；液冷快接頭不在 10-K 中，收入未公開。
- status: not-researched
  reason: 液冷快接頭的白皮書、型錄與 OCP 產品清單尚未讀取，量產與客戶採用未核實。
---

## 供應角色

Amphenol 在[互連環節](/next?focus=segment-interconnect)同時屬於[高速與處理器連接器](/next?focus=role-high-speed-connector)、[高速線材與線束](/next?focus=role-cable-harness)與[液路快接頭](/next?focus=role-liquid-quick-disconnect)三個角色。前兩項來自 10-K，液冷快接頭來自官方產品頁。

## 研究界線

本頁以 FY2025 10-K 與 Amphenol Industrial 產品頁為依據。10-K 完全沒有提到液冷，快接頭只能證明產品能力，不能證明客戶採用或收入。2026 年 1 月完成的 CommScope 收購不在 FY2025 數字內。

## 產品與用途

- **IT datacom**：高速、電源與主動／被動光纖互連，用於 AI 與機器學習系統（Item 1）。
- **三個分部**：Communications Solutions（連接器、高速／電源／光纖線纜、天線）、Harsh Environment Solutions（強固互連、特殊線纜、印刷電路）、Interconnect and Sensor Systems（Item 1）。
- **液冷快接頭**：UQD、UQDB、Rev 2.0、BMQC、LQC、MQD、SHQD 系列，用於 AI 資料中心液冷與機櫃盲插（產品頁）。

## 商業模式

在約 40 個國家垂直整合生產，以分散的事業單位經營並持續收購（Item 1）。2025 年營收 23,094.7 百萬美元，成長 52%，其中有機成長 38%；2025 年完成五件收購，2026 年 1 月再完成約 105 億美元的 CommScope 收購（Item 7、Note 15）。

## 客戶與供應商

客戶為數千家 OEM、EMS、ODM 與服務供應商，沒有單一客戶超過一成，經銷商約占 19%（Item 1）。客戶名稱未揭露。

## 競爭與替代

10-K 列出 TE Connectivity、Molex、Foxconn Interconnect Technology、Luxshare、Corning 等主要競爭者。在[高速與處理器連接器](/next?focus=role-high-speed-connector)可與[嘉澤](/next?focus=company-3533-tw)比較，在[高速線材與線束](/next?focus=role-cable-harness)可與[貿聯](/next?focus=company-3665-tw)比較；液冷快接頭的替換要依流量、壓降與冷卻液相容性逐案驗證。

## 業務曝險

IT datacom 約占 36%，Communications Solutions 有機成長 71%，backlog 由 61 億升到 89 億美元，10-K 都把增量歸因於 AI 應用。CommScope 收購會再提高光纖互連比重。

## 風險

- **收購整合與債務**：CommScope 是史上最大收購，預估 2026 年淨利息費用約 8 億美元。
- **backlog 可取消**：訂單出貨前一般可取消。
- **地緣政治**：非美國市場約 65%，中國約 16%。
- **終端循環**：AI 資本支出放緩會直接影響 IT datacom。

## 財務可取性

- SEC 公開財務資料 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- 終端市場與分部比重可由 10-K 核對。
- AI 相關營收與液冷快接頭收入：未公開。
