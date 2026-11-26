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
reviewed: '2026-11-24'
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
- id: aries-pt6162-compliance
  statement: "Astera Aries PT6162 列入 PCI-SIG PCIe 6.x 64 GT/s x16 名單。Astera Labs 指其 Aries 與 Scorpio 已進入批量產品階段。"
  confidence: well-supported
  conditions:
  - "相容性限該料號與指定測試。原廠量產說明未列 PT6162 客戶／量。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: pci-sig-retimer-integrators-2026
    url: https://pcisig.com/developers/integrators-list?field_il_comp_product_type_value=All&keys=&order=created&sort=desc
    locator: "PCI Express 6.x Components: Retimers"
    read-scope: "已讀 CPR61664 與 PT6162 兩筆，x16 64 GT/s。"
    stance: supporting
    applicable-period: "2026-07-31 登錄，2026-11-24 查閱"
  - source-id: astera-aries6-compliance-announcement
    url: https://www.asteralabs.com/resources/blog/industry-leading-high-volume-scorpio-smart-fabric-switches-and-aries-smart-retimers-achieve-compliance-at-first-pci-sig-6-x-workshop/
    locator: "開頭與測試段落"
    read-scope: "已讀 PCIe 6.x 工作坊及原廠批量說法。"
    stance: supporting
    applicable-period: "2026-11-24 核對公司技術文章"
- id: taurus-aries-cable-module-delivery
  statement: "Astera Taurus EM800-QDX-A／EM800-EPS-A 供 800G Ethernet 銅線組整合，簡介例為 30 AWG、3 m。Aries SCM 則按 PCIe／CXL 應用裝入線組。"
  confidence: well-supported
  conditions:
  - "模組與成品線組分開。Taurus 的長度與 BER 取決於整合用線材與測試結果，不能外推 Aries 的 PCIe 距離。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: astera-taurus-scm-brief
    url: https://www.asteralabs.com/wp-content/uploads/2025/05/PB_Taurus_Ethernet_Smart_Cable_Modules.pdf
    locator: "Product Family Information、Description"
    read-scope: "已讀各 800G SCM 與 3 m 30 AWG；出貨給線纜組件整合。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
  - source-id: alab-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1736297/000173629726000010/alab-20251231.htm
    locator: "Item 1. Business：Aries／Taurus"
    read-scope: "重讀 Aries PCIe/CXL 及 Taurus Ethernet 模組。"
    stance: supporting
    applicable-period: "FY2025 Form 10-K"
gaps:
- status: not-public
  reason: 10-K 未揭露各產品家族營收與客戶名稱。
- status: not-researched
  reason: Scorpio PCIe／GPU fabric switch 在地圖沒有對應的產品分類（現有交換晶片是 Ethernet），尚未裁決是否新增。
---

## 供應角色

Aries 交付[PCIe／CXL retimer](/next?focus=product-retimer)，也有供 PCIe／CXL 線纜整合的 SCM；Taurus 則為[Ethernet AEC](/next?focus=product-active-electrical-cable)線端模組。

Astera Labs 在[網路環節](/next?focus=segment-networking)屬[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)，主力是 PCIe／CXL [retimer](/next?focus=product-retimer) 與智慧線纜模組。Scorpio fabric switch 目前沒有對應的地圖產品。

## 研究界線

本批核對 FY2025 Form 10-K 的各產品家族、Taurus 線材簡介、Aries 型錄與 PCI-SIG 相容清單；認證與量產證據依各來源。

本頁以 FY2025 10-K 為依據。智慧線纜模組是裝在線纜裡的模組，不是整條主動電纜；地區營收依帳單地址，多半是經銷商與代工夥伴所在地。

## 產品與用途

PT6162 是 PCIe 6.x x16 之 64 GT/s retimer。Taurus EM800-QDX-A／EM800-EPS-A 是 800GbE QSFP-DD／OSFP 線組內模組，3 m 例配 30 AWG。Aries Cable Module 屬 PCIe／CXL，板卡、線端及系統交付不同。

- **Aries**：PCIe／CXL retimer 與智慧線纜模組，延伸處理器、儲存與網路控制器之間的訊號距離（Item 1）。
- **Taurus**：Ethernet 智慧線纜模組，以銅纜連接伺服器與交換器（Item 1）。
- **Leo**：CXL 記憶體連接控制器，擴充與共享 DRAM（Item 1）。
- **Scorpio**：P 系列 PCIe 6.0 與 X 系列 GPU 叢集 fabric switch（Item 1）。

## 商業模式

Astera Labs 將 COSMOS 診斷搭配 IC、板卡或模組。Taurus 簡介為線纜廠的組件整合，型錄的距離必須在成品線纜與系統重新驗證。

Fabless，產品以 IC、電路板與模組形式出貨並整合 COSMOS 軟體（Item 1）。2025 年營收 852,525 千美元，成長 115%（Item 7）。2025 年 11 月以 31.1 百萬美元收購光纖耦合技術公司 aiXscale（Item 8）。

## 客戶與供應商

PCI-SIG 名單已確認 PT6162 的標準測試，原廠稱 Aries 屬批量產品。所讀兩份證據未列各機房或客戶的採用、料號出貨量。Taurus 產品簡介只支持模組能力。

單一終端客戶占逾 70%，前三大終端客戶約 86%；依簽約方口徑五家客戶各占 11%–20%（Item 1A、Item 8）。IC 由 [TSMC](/next?focus=company-tsmc) 製造，[日月光投控](/next?focus=company-3711-tw)旗下 ASE 與 [Amkor](/next?focus=company-amkr) 封測（Item 1）。

## 競爭與替代

與[Credo](/next?focus=company-crdo) Toucan CPR61664 比較同 PCIe 6.x 64 GT/s x16 的認證範圍，再驗證板端損耗、功耗、診斷與延遲。Taurus 可與具同介面、同交付的線端 SCM 比較；以相同規格組成線組後才可量測端到端數據。

10-K 列出 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo)、[Marvell](/next?focus=company-mrvl)、Microchip、瀾起、譜瑞與 Rambus。客戶也可能自行開發或改採競爭方案（Item 1A）。

## 業務曝險

PCIe／CXL 路徑長度與速率影響 Aries，短距高速 Ethernet 線纜需求影響 Taurus，各自依平台合格設計及分工。相同季公司成長也可能來自 Scorpio 或其他產品。

營收幾乎都來自 AI 與雲端資料中心，單一終端客戶占七成以上，是本次深研中終端客戶集中度最高的公司之一。

## 風險

不同協定、CXL 需求及主機走線改版可能改變 retimer 單機用量；SCM 需隨線纜組件驗證，樣品與型錄尚不足以預測量產進度。

- **終端客戶集中**：單一終端客戶逾 70%。
- **設計導入**：終端客戶可在短時間內重新設計系統、減少使用其產品（Item 1A）。
- **代工集中**：IC 全由 TSMC 製造，製造夥伴集中在亞洲。
- **內部控制**：先前發現的重大內控缺失已於 2025 年完成改善，10-K 仍列為風險（Item 1A、9A）。

## 財務可取性

FY2025 10-K 及後續 SEC 申報可查公司資料。PT6162、Taurus EM800 及特定平台的收入與出貨未單列。

- SEC 公開財務資料 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- 產品家族營收：10-K 未公開。
