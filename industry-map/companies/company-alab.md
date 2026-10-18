---
schema-version: research-v1
entity-id: company-alab
kind: company
name-zh: Astera Labs
aliases:
- Astera Labs
- Astera Labs Inc.
summary: 雲端與 AI 基礎設施連接晶片公司；2025 年營收成長 115%，產品含 Aries retimer、Taurus Ethernet 智慧線纜模組、Leo CXL 控制器與 Scorpio fabric switch，單一終端客戶占營收逾七成。
legacy-keys:
- ALAB
listings:
- ticker: ALAB
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1736297'
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
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: 10-K Item 7. MD&A（Revenue，2023–2025 年度）；SEC 申報期間 2025-12-31
    read-scope: 已讀營收段落
    stance: supporting
    applicable-period: FY2023–FY2025
roles:
- segment-id: segment-networking
  description: 連接橋接晶片
  tier: 2
  baseline-path: ai-server/networking.md
claims:
- id: product-families
  statement: 10-K 列出四個產品家族：Aries PCIe／CXL Smart DSP Retimer 與 Smart Cable Module、Taurus Ethernet Smart Cable Module（以銅纜連接伺服器與交換器）、Leo CXL 記憶體連接控制器，以及 Scorpio Smart Fabric Switch（P 系列 PCIe 6.0、X 系列 GPU 叢集），皆整合 COSMOS 軟體。
  confidence: well-supported
  conditions:
  - 產品清單不揭露各家族營收
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 1. Business（Our Products）
    read-scope: 已讀產品家族段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: revenue-growth
  statement: 10-K 揭露 2025 年營收 852,525 千美元，較 2024 年 396,290 千美元成長 115%，主要來自 Aries、Scorpio 與 Taurus 出貨增加，以及硬體模組與 Scorpio 比重上升帶動平均售價提高；營收絕大部分為產品銷售。
  confidence: well-supported
  conditions:
  - 未揭露各產品家族營收
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 7. MD&A（Revenue）
    read-scope: 已讀營收段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: customer-concentration
  statement: 10-K 說明產品主要售予經銷商與終端客戶的代工夥伴，再用於 hyperscaler、AI 加速器廠與 OEM 系統；2025 年單一終端客戶占營收逾 70%，前三大終端客戶約 86%。依簽約方口徑，五家客戶各占 11%–20%。
  confidence: well-supported
  conditions:
  - 終端客戶比例是公司依訂單資訊估計；客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 1. Business（Customers）；Item 1A 客戶集中風險；Item 8 客戶集中附註
    read-scope: 已讀客戶段落與附註表
    stance: supporting
    applicable-period: FY2023–FY2025
- id: manufacturing-partners
  statement: 10-K 說明所有 IC 由 TSMC 製造，由 Advanced Semiconductor Engineering 與 Amkor 封裝測試；模組、電路板與 IC 載板依賴少數其他製造夥伴。
  confidence: well-supported
  conditions:
  - 未揭露各供應商採購金額；模組與載板夥伴未具名
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 1. Business（Manufacturing and Suppliers）
    read-scope: 已讀製造段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: billing-regions
  statement: 10-K 依客戶帳單地址揭露 2025 年營收：新加坡 276,989 千美元、中國 256,276 千美元、台灣 247,448 千美元、美國 27,428 千美元、其他 44,384 千美元。
  confidence: well-supported
  conditions:
  - 帳單地址多為經銷商與代工夥伴，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 8. 合併財報附註（revenue by geographic area）
    read-scope: 已讀地區營收表
    stance: supporting
    applicable-period: FY2023–FY2025
- id: named-competitors
  statement: 10-K 列出主要競爭者為 Broadcom、Credo、Marvell、Microchip、瀾起（Montage）、譜瑞（Parade）與 Rambus，並稱競爭者通常只在部分產品上競爭。
  confidence: well-supported
  conditions:
  - 競爭依產品線而異
  reviewed: '2026-10-18'
  evidence:
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: Item 1. Business（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2025 10-K
gaps:
- status: not-public
  reason: 10-K 未揭露各產品家族營收與客戶名稱。
- status: not-researched
  reason: Scorpio PCIe／GPU fabric switch 在地圖沒有對應的產品分類（現有交換晶片是 Ethernet），尚未裁決是否新增。
---

## 供應角色

Astera Labs 在[網路環節](/next?focus=segment-networking)屬[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)，主力是 PCIe／CXL [retimer](/next?focus=product-retimer) 與智慧線纜模組。Scorpio fabric switch 目前沒有對應的地圖產品。

## 研究界線

本頁以 FY2025 10-K 為依據。智慧線纜模組是裝在線纜裡的模組，不是整條主動電纜；地區營收依帳單地址，多半是經銷商與代工夥伴所在地。

## 產品與用途

- **Aries**：PCIe／CXL retimer 與智慧線纜模組，延伸處理器、儲存與網路控制器之間的訊號距離（Item 1）。
- **Taurus**：Ethernet 智慧線纜模組，以銅纜連接伺服器與交換器（Item 1）。
- **Leo**：CXL 記憶體連接控制器，擴充與共享 DRAM（Item 1）。
- **Scorpio**：P 系列 PCIe 6.0 與 X 系列 GPU 叢集 fabric switch（Item 1）。

## 商業模式

Fabless，產品以 IC、電路板與模組形式出貨並整合 COSMOS 軟體（Item 1）。2025 年營收 852,525 千美元，成長 115%（Item 7）。2025 年 11 月以 31.1 百萬美元收購光纖耦合技術公司 aiXscale（Item 8）。

## 客戶與供應商

單一終端客戶占逾 70%，前三大終端客戶約 86%；依簽約方口徑五家客戶各占 11%–20%（Item 1A、Item 8）。IC 由 [TSMC](/next?focus=company-tsmc) 製造，[日月光投控](/next?focus=company-3711-tw)旗下 ASE 與 [Amkor](/next?focus=company-amkr) 封測（Item 1）。

## 競爭與替代

10-K 列出 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo)、[Marvell](/next?focus=company-mrvl)、Microchip、瀾起、譜瑞與 Rambus。客戶也可能自行開發或改採競爭方案（Item 1A）。

## 業務曝險

營收幾乎都來自 AI 與雲端資料中心，單一終端客戶占七成以上，是本次深研中終端客戶集中度最高的公司之一。

## 風險

- **終端客戶集中**：單一終端客戶逾 70%。
- **設計導入**：終端客戶可在短時間內重新設計系統、減少使用其產品（Item 1A）。
- **代工集中**：IC 全由 TSMC 製造，製造夥伴集中在亞洲。
- **內部控制**：先前發現的重大內控缺失已於 2025 年完成改善，10-K 仍列為風險（Item 1A、9A）。

## 財務可取性

- SEC companyfacts 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- 產品家族營收：10-K 未公開。
