---
schema-version: research-v1
entity-id: company-3665-tw
kind: company
name-zh: 貿聯
aliases:
- BizLink
- 貿聯-KY
- 貿聯
summary: 線束與連接組件廠；資訊科技與數據傳播產品占營收比重由 24.4% 升至 42.4%，前十大客戶合計約四成八。
legacy-keys:
- 3665.TW
listings:
- ticker: 3665.TW
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
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 81 頁（PDF 第 83 頁）主要產品之營業比重，113 與 114 年度並列
    read-scope: 已讀營業比重表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-interconnect
  description: 高速線材與線束
  tier: 1
  baseline-path: ai-server/interconnect.md
claims:
- id: product-mix
  statement: 年報主要產品營業比重依產品順序為：資訊科技與數據傳播 42.4%（113 年度 24.4%）、工業用 33.1%、車用 13.3%、電器用 11.1%、其他 0.1%。
  confidence: well-supported
  conditions:
  - 比重表依產品順序與合計 100% 核對；不拆分 AI 資料中心產品
  reviewed: '2026-10-18'
  evidence:
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 81 頁（PDF 第 83 頁）主要產品之營業比重
    read-scope: 已讀營業比重表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: hpc-ai-focus
  statement: 年報稱 HPC 與 AI 基礎設施應用已逐步成為公司重要成長支柱，並強化高功率、高速互連與系統整合能力；光電互連方面正在開發與評估矽光子與 CPO 相關技術。
  confidence: inference
  conditions:
  - 矽光子與 CPO 仍在開發與評估階段，不代表量產
  reviewed: '2026-10-18'
  evidence:
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 11 頁（PDF 第 13 頁）公司簡介與市場布局
    read-scope: 已讀公司簡介段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報稱 114 年度前十大客戶合計占營業收入淨額 47.91%（前期 36.67%），反映 AI 與高效能運算資料中心產業市場集中度較高；113 至 114 年度沒有任何供應商進貨超過 10%。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露；公司自評無過度集中風險
  reviewed: '2026-10-18'
  evidence:
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 116 頁（PDF 第 118 頁）進貨或銷貨集中所面臨之風險
    read-scope: 已讀進銷貨集中段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: global-footprint
  statement: 年報稱營運據點遍布 20 個國家，擁有橫跨三大洲、超過 40 座生產基地的製造與供應鏈體系。
  confidence: well-supported
  conditions:
  - 未揭露各基地產品分工
  reviewed: '2026-10-18'
  evidence:
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 11 頁（PDF 第 13 頁）
    read-scope: 已讀公司簡介段落
    stance: supporting
    applicable-period: 114 年度年報
- id: fx-exposure
  statement: 年報稱主要銷售地區為歐、美，交易多以美元計價；114 年度匯兌損失 399,631 仟元，約占營收 0.56%。
  confidence: well-supported
  conditions:
  - 匯兌損益受當期部位影響
  reviewed: '2026-10-18'
  evidence:
  - source-id: bizlink-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3665&year=115&mtype=F&
    locator: 114 年度年報第 113 頁（PDF 第 115 頁）匯率變動
    read-scope: 已讀匯率段落
    stance: supporting
    applicable-period: 113 至 114 年度
gaps:
- status: not-public
  reason: 年報未拆分 AI 資料中心線材或電源線束收入，也未揭露客戶名稱。
- status: not-public
  reason: 年報未列出具名競爭者。
---

## 供應角色

貿聯在[互連環節](/next?focus=segment-interconnect)屬[高速線材與線束](/next?focus=role-cable-harness)，提供資料中心與工業、車用等領域的線束與連接組件。

## 研究界線

本頁以 114 年度股東會年報為依據。產品比重表已依產品順序與合計核對。矽光子與 CPO 仍在開發與評估，不視為量產能力。

## 產品與用途

- **資訊科技與數據傳播**：資料中心與 HPC 相關的高速與高功率互連（第 11、81 頁）。
- **工業**：半導體與自動化設備線束、拖鏈電纜、機器人線纜管理方案（第 81 頁）。
- **車用與電器**：車用線束與家電相關產品（第 81 頁）。
- **開發中**：矽光子與 CPO 相關光電互連（第 11 頁）。

## 商業模式

以模組化設計、快速打樣與量產導入支援客戶，在 20 個國家、超過 40 座生產基地生產（第 11 頁）。資訊科技與數據傳播比重由 24.4% 升至 42.4%，取代工業成為最大產品類別（第 81 頁）。

## 客戶與供應商

114 年度前十大客戶合計約 47.91%，前期為 36.67%；年報把集中度上升歸因於 AI 與 HPC 資料中心產業特性（第 116 頁）。沒有任何供應商超過一成。年報未揭露客戶名稱；客戶端來源方面，[Credo](/next?focus=company-crdo) FY2026 10-K 揭露其主動電纜由貿聯製造。

## 競爭與替代

年報沒有具名競爭者。在[高速線材與線束](/next?focus=role-cable-harness)角色，可與[信邦](/next?focus=company-3023-tw)比較；銅與光的取捨要看整條通道，不能由 CPO 概念推定銅纜被全面替代。

## 業務曝險

資訊科技與數據傳播占 42.4%，是 AI 資料中心需求最直接的曝險；但年報沒有拆出其中多少來自 AI 伺服器。

## 風險

- **客戶集中上升**：前十大客戶比重一年上升約 11 個百分點。
- **技術路線**：光互連與 CPO 的導入時程會影響銅線產品需求。
- **匯率**：以美元計價為主，114 年度產生匯兌損失（第 113 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 產品比重可由年報核對；營業現金流、資本支出需由合併財報人工補錄。
- AI 資料中心產品收入：年報未公開。
