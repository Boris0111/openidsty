---
schema-version: research-v1
entity-id: company-delta-electronics
kind: company
name-zh: 台達電
aliases:
- Delta Electronics
- 台達
- 台達電子
summary: 電力電子大廠，四大範疇中電源及零組件占五成；年報描述 800VDC 供電與液冷系統，沒有單一客戶超過一成。
legacy-keys:
- 2308.TW
listings:
- ticker: 2308.TW
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
  calendar-valid-from: '2025-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 86 頁（PDF 第 89 頁）民國 114 年總營收與四大事業範疇營收比重
    read-scope: 已讀營運概況段落
    stance: supporting
    applicable-period: 114 年度（2025 曆年）
roles:
- segment-id: segment-power
  description: 伺服器電源與供電架構
  tier: 1
  baseline-path: ai-server/power.md
claims:
- id: business-mix
  statement: 年報稱民國 114 年總營收為新台幣 5,548.85 億元，「電源及零組件」、「交通」、「自動化」與「基礎設施」營收比重分別為 50%、7%、10% 和 33%；電源及零組件包括零組件、電源及系統、風扇與散熱管理。
  confidence: well-supported
  conditions:
  - 範疇比重不拆出 AI 資料中心或液冷收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 86 頁（PDF 第 89 頁）
    read-scope: 已讀營運概況段落
    stance: supporting
    applicable-period: 114 年度
- id: ai-power-products
  statement: 年報描述因應 800VDC 或 ±400VDC 架構的產品，包括將 800VDC 降至 50VDC／48VDC 的 19 吋 90kW DC/DC 機架電源、結合超級電容約可提供 10 秒備援的機架式電容系統，以及 1.1MW 列間電源系統。
  confidence: well-supported
  conditions:
  - 屬產品發展說明，未揭露出貨、客戶或收入；98.5% 等效率數字是公司揭露的最高值
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 90 頁（PDF 第 93 頁）市場分析「電源及零組件」
    read-scope: 已讀電源及零組件段落
    stance: supporting
    applicable-period: 114 年度年報
- id: liquid-cooling-growth
  statement: 年報稱隨資料中心液冷需求快速成長，相關系統業務是 114 年台達最重要的成長動能之一，液冷方案以完整系統形式交付，涵蓋冷卻架構設計、系統整合與現場部署支援。
  confidence: well-supported
  conditions:
  - 年報未揭露液冷收入金額，也未列出具體 CDU 型號
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 91 頁（PDF 第 94 頁）市場分析「基礎設施」
    read-scope: 已讀基礎設施段落
    stance: supporting
    applicable-period: 114 年度年報
- id: no-concentration
  statement: 年報揭露 113 與 114 年度沒有任一銷貨客戶超過合併銷貨 10%，也沒有單一外部供應商進貨達合併進貨 10%。
  confidence: well-supported
  conditions:
  - 年報未揭露客戶名稱
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 95 頁（PDF 第 98 頁）主要進銷貨對象；第 116 頁（PDF 第 119 頁）集中風險
    read-scope: 已讀主要供應商與客戶段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: ai-customer-relationships
  statement: 年報稱台達與主要 AI 晶片供應商及雲端服務客戶維持合作關係，投入 AI 電源與散熱解決方案研發，但未列出公司名稱。
  confidence: needs-verification
  conditions:
  - 未具名，不能據此建立具名客戶或合作關係
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 90 頁（PDF 第 93 頁）「電源及零組件」第一段
    read-scope: 已讀該段
    stance: supporting
    applicable-period: 114 年度年報
- id: materials-and-fx
  statement: 年報稱主要材料為半導體元件、被動元件與部分機構元件，並與主要供應商簽訂年度用量合約；營業收入與應收應付主要以美元計價。
  confidence: well-supported
  conditions:
  - 未揭露供應商名稱
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 95 頁（PDF 第 98 頁）主要原料之供應狀況；第 112 頁（PDF 第 115 頁）匯率變動
    read-scope: 已讀原料與匯率段落
    stance: supporting
    applicable-period: 114 年度年報
- id: sae-power-litigation
  statement: 年報揭露 SAE Power 對台達提起的營業秘密與專利訴訟；其中一案已於民國 115 年 1 月以不得再訴方式駁回，另一案法院於 114 年 12 月裁定續行。
  confidence: well-supported
  conditions:
  - 年報未估計可能損失金額
  reviewed: '2026-10-18'
  evidence:
  - source-id: delta-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2308&year=115&mtype=F&
    locator: 114 年度年報第 116 頁（PDF 第 119 頁）訴訟或非訟事件
    read-scope: 已讀訴訟表
    stance: supporting
    applicable-period: 截至年報刊印日
gaps:
- status: not-public
  reason: 年報未拆分 AI 資料中心、800VDC 產品或液冷系統營收，也未揭露客戶名稱。
- status: not-public
  reason: 年報未列出具名競爭者；Vertiv 10-K 則把台達列為利基型競爭者（見 Vertiv 研究）。
---

## 供應角色

台達在[電源環節](/next?focus=segment-power)提供[電源架與機架式電源](/next?focus=product-power-shelf-psu)，也透過基礎設施範疇交付液冷與資料中心整合方案。它同時出現在供電與散熱兩個研究情境，閱讀時要先分清楚是哪一種交付。

## 研究界線

本頁以 114 年度股東會年報為依據。年報描述 800VDC、液冷與 AI 資料中心的產品方向，但沒有拆出這些業務的營收，也沒有客戶名稱；與 AI 晶片及雲端客戶的合作屬公司自述，標為待核實。

## 產品與用途

- **AI 供電**：19 吋 90kW DC/DC 機架電源（800VDC 降至 50／48VDC）、超級電容機架式電容系統（約 10 秒備援）、晶片端 DC/DC 配電板、1.1MW 列間電源系統（第 90 頁）。
- **資料中心基礎設施**：800VDC／±400VDC 供電、大型 UPS、800G 乙太網路交換器、液冷系統與 AI 貨櫃型資料中心（第 91 頁）。
- **其他範疇**：電動車動力系統、工業與樓宇自動化、儲能與充電（第 86、91 頁）。

## 商業模式

114 年總營收新台幣 5,548.85 億元，電源及零組件 50%、基礎設施 33%、自動化 10%、交通 7%（第 86 頁）。年報強調以電力電子核心能力提供整合方案，並收購晶睿通訊擴充樓宇自動化（第 91 頁）。

## 客戶與供應商

沒有任何客戶或外部供應商占比達 10%（第 95 頁）。年報說與主要 AI 晶片供應商及雲端客戶維持合作，但未具名（第 90 頁）。主要材料為半導體元件、被動元件與機構元件，採年度用量合約（第 95 頁）。

## 競爭與替代

年報沒有具名競爭者。[Vertiv](/next?focus=company-vertiv) 的 10-K 把台達列為利基型競爭者。在[機櫃與系統電源](/next?focus=role-rack-power-supply)角色，可與[光寶科](/next?focus=company-2301-tw)、[康舒](/next?focus=company-6282-tw)比較；800VDC 架構會改變電源轉換的位置，不是所有既有電源產品都等比例受惠。

## 業務曝險

AI 資料中心相關業務分散在電源及零組件與基礎設施兩個範疇，合計占營收八成三，但其中多少來自 AI 或液冷，年報沒有揭露。

## 風險

- **架構轉換**：800VDC 等新架構仍在導入，產品是否量產需逐案核對。
- **訴訟**：SAE Power 營業秘密與專利訴訟仍有一案續行（第 116 頁）。
- **匯率**：營收與應收應付以美元為主，公司以資產負債相抵自然避險（第 112 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 範疇營收比重可由年報核對；營業現金流、資本支出需由合併財報人工補錄。
- AI 資料中心、800VDC 與液冷收入：年報未公開。
