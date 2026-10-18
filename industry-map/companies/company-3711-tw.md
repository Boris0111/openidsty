---
schema-version: research-v1
entity-id: company-3711-tw
kind: company
name-zh: 日月光投控
aliases:
- ASE Technology Holding
- 日月光投控
- ASE
summary: 全球最大委外封測集團，2025 年營收 6,453.9 億元：封裝 3,083.4 億元（成長 17.8%）、測試 719.0 億元（成長 31.8%）、EMS 2,571.9 億元（衰退 5.2%）；成長來自領先先進封裝與測試。
legacy-keys:
- 3711.TW
listings:
- ticker: 3711.TW
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
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 5. Operating Results（Operating Revenues，2024–2025 曆年）
    read-scope: 已讀營收段落
    stance: supporting
    applicable-period: 2024–2025 曆年
roles:
- segment-id: segment-advanced-packaging
  description: 委外封測與先進封裝
  tier: 1
  baseline-path: ai-server/advanced-packaging.md
claims:
- id: revenue-mix
  statement: 20-F 揭露 2025 年營收 NT$645,387.7 百萬元，較 2024 年成長 8.4%；封裝 NT$308,342.6 百萬元（成長 17.8%）、測試 NT$71,900.2 百萬元（成長 31.8%），成長主要來自領先先進封裝與測試需求；EMS NT$257,192.7 百萬元（衰退 5.2%），占營收 39.9%。
  confidence: well-supported
  conditions:
  - 領先先進封裝營收未單獨揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 5. Operating Results（Operating Revenues）；Item 3 原料段落（EMS 比重）
    read-scope: 已讀營收段落
    stance: supporting
    applicable-period: 2024–2025
- id: advanced-packaging
  statement: 20-F 說明封裝技術涵蓋 2.5D、FO-MCM、FO-EB、CoWoS、CoPoS、CoWoP、CPO 與 3D IC、覆晶、堆疊與細間距打線，並稱其領先先進封裝方案協助先進 ASIC 與 HBM 產品上市。
  confidence: well-supported
  conditions:
  - 技術清單不揭露各技術營收、產能或客戶
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 4. Information on the Company（Research and Development；packaging technology）
    read-scope: 已讀技術段落
    stance: supporting
    applicable-period: FY2025 20-F
- id: customer-concentration
  statement: 20-F 揭露前五大客戶占營收約 48.0%、48.4%、46.5%（2023–2025），且有一家客戶（含代其提供 OEM 服務的客戶）占營收一成以上。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 4. Information on the Company（Customers）
    read-scope: 已讀客戶段落
    stance: supporting
    applicable-period: 2023–2025
- id: end-use-and-region
  statement: 20-F 揭露 2025 年封測營收依終端應用為通訊 45.8%、運算 24.0%、消費性／工業／車用及其他 30.2%；依客戶總部所在地為美國 56.7%、台灣 18.0%、亞洲 15.2%、歐洲 10.0%。
  confidence: well-supported
  conditions:
  - 地區依客戶總部，不等於出貨或終端使用地
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 3（end-use applications）；Item 4 Sales and Marketing 地區表
    read-scope: 已讀終端應用與地區表
    stance: supporting
    applicable-period: 2023–2025
- id: competition
  statement: 20-F 說明封測業競爭來自其他封測廠、具自有封測能力的 IDM，以及供應鏈其他層級的公司，並以台積電提供 InFO 等先進封裝技術為例；EMS 業務則與其他大型 EMS 廠競爭。
  confidence: well-supported
  conditions:
  - 20-F 未列出具名封測同業
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 4. Information on the Company（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2025 20-F
- id: substrate-supply
  statement: 20-F 說明 IC 載板由少數供應商生產（例如景碩、南亞電路板、欣興），AI 帶動的 HPC 需求使晶片與載板設計更複雜；2025 年集團自有載板業務供應約 8.7% 的載板需求。
  confidence: well-supported
  conditions:
  - 20-F 以這三家說明市場供應集中，未揭露向各家的採購金額
  reviewed: '2026-10-18'
  evidence:
  - source-id: ase-20f-2025
    url: https://www.sec.gov/Archives/edgar/data/1122411/000119312526135585/d50802d20f.htm
    locator: 20-F Item 3. Key Information（raw materials 風險）
    read-scope: 已讀原料段落
    stance: supporting
    applicable-period: FY2025 20-F
gaps:
- status: not-public
  reason: 20-F 未單獨揭露領先先進封裝（2.5D、CoWoS 類）營收與客戶名稱。
- status: not-obtained
  reason: 114 年度中文股東會年報多數頁面字型編碼無法擷取，未能以年報交叉核對。
---

## 供應角色

日月光投控在[先進封裝環節](/next?focus=segment-advanced-packaging)同時屬[委外封裝](/next?focus=role-osat-assembly)、[晶圓與成品測試服務](/next?focus=role-test-service)與[中介層與 2.5D／3D 整合](/next?focus=role-interposer-integration)。EMS 約占營收四成，不在地圖範圍。

## 研究界線

本頁以 FY2025 20-F 為依據。中文年報多數頁面無法擷取文字，未能交叉核對。20-F 只列出 2.5D、CoWoS 類技術能力，沒有揭露先進封裝營收，所以中介層角色的規模無法量化；EMS 營收需排除。

## 產品與用途

- **封裝**：覆晶、打線、堆疊、扇出與 2.5D／3D 先進封裝，含 CoWoS、CoPoS、CoWoP 與 CPO（Item 4）。
- **測試**：晶圓與成品測試，2025 年成長 31.8%（Item 5）。
- **EMS**：系統級組裝，2025 年衰退 5.2%（Item 5）。
- **載板**：集團自有載板業務供應約 8.7% 的需求（Item 3）。

## 商業模式

為 IDM、fabless 與代工廠提供委外封測，另有 EMS。2025 年營收 NT$645,387.7 百萬元，成長 8.4%；營業利益 NT$51,420.8 百萬元，營業利益率 8.0%（Item 5）。

## 客戶與供應商

前五大客戶約 46.5%，一家客戶逾一成（Item 4）。美國客戶占 56.7%。客戶端 10-K 具名日月光為封測廠的包括 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo) 與 [Astera Labs](/next?focus=company-alab)（見關係）。載板供應集中在少數廠，例如[景碩](/next?focus=company-3189-tw)、[南電](/next?focus=company-8046-tw)與[欣興](/next?focus=company-3037-tw)（Item 3）。

## 競爭與替代

20-F 未具名封測同業，但把[台積電](/next?focus=company-tsmc)的 InFO 列為供應鏈其他層級的競爭例子（Item 4）。在[委外封裝](/next?focus=role-osat-assembly)可與 [Amkor](/next?focus=company-amkr)、[力成](/next?focus=company-6239-tw)比較；IDM 也可能自行封測。

## 業務曝險

封測成長由領先先進封裝與測試帶動，通訊與運算合計約七成；但 AI 相關封裝營收沒有揭露。

## 風險

- **AI 需求放緩**：20-F 把 AI 需求反轉列為風險（Item 3）。
- **高固定成本**：測試與領先先進封裝的設備折舊高，產能利用率影響獲利（Item 3）。
- **載板供應**：載板由少數供應商生產，可能短缺（Item 3）。
- **地緣政治**：營運集中在台灣與中國大陸。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 封裝、測試、EMS 營收可由 20-F 核對。
- 領先先進封裝營收：20-F 未公開。
