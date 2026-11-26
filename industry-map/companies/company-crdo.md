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
reviewed: '2026-11-24'
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
- id: toucan-cpr61664-compliance
  statement: "Credo Toucan CPR61664 Gen6x16 為 PCIe／CXL retimer，PCI-SIG 以 PCIe 6.x、64 GT/s、x16 登錄。"
  confidence: well-supported
  conditions:
  - "限指定料號和速率；Gen6x8 的 32 GT/s 登錄不能套用相同結論。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: pci-sig-retimer-integrators-2026
    url: https://pcisig.com/developers/integrators-list?field_il_comp_product_type_value=All&keys=&order=created&sort=desc
    locator: "PCI Express 6.x Components: Retimers"
    read-scope: "已讀 CPR61664 與 PT6162 兩筆，x16 64 GT/s。"
    stance: supporting
    applicable-period: "2026-07-31 登錄，2026-11-24 查閱"
- id: span-shift-aec-delivery
  statement: "Credo SPAN CAC8XXXX1A1B-C1-HW 是 3–7 m 的 800G OSFP 直連線組，SHIFT DD 分接為 1–3 m 並可拆成兩個 400G 端。"
  confidence: well-supported
  conditions:
  - "型錄限介面、線長、外殼溫度及 QPRBS31 BER 條件。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 8×106.25 Gb/s、OSFP-RHS 與長度。"
    stance: supporting
    applicable-period: "REV 100924"
  - source-id: credo-800g-shift-dd-breakout-brief
    url: https://credosemi.com/wp-content/uploads/Credo_AEC_800G_SHIFT_DD-2xDD_Product_Brief_2025Sept26.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 800G 分接 2×400G 的線速與長度。"
    stance: supporting
    applicable-period: "2025-09"
- id: dove-80x-optical-dsp-delivery
  statement: "Credo Dove 80X 是 800G 光 DSP 家族；Dove 800 為 8:8，Dove 801 及 802 整合不同光元件 driver。"
  confidence: well-supported
  conditions:
  - "依 driver、介面與線側光元件驗證。產品頁未承諾特定模組認證。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-dove-800-product
    url: https://credosemi.com/products/optical-dsp/dove-800/
    locator: "產品說明、規格表"
    read-scope: "已讀 8:8 與各料號 driver。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
- id: zeroflap-800g-module-delivery
  statement: "Credo 800G ZeroFlap 2×DR4 OSFP-RHS 是平行單模、MPO-12 的完整光模組，產品頁列至 500 m，於 2026-03-17 宣布一般供應。"
  confidence: well-supported
  conditions:
  - "PILOT 遙測還須配交換器軟體與 ZeroFlap Host SDK。公告未列客戶、平台驗證及出貨。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-2xdr4-osfp-rhs
    url: https://credosemi.com/products/zeroflap-optical-transceivers/800g-2xdr4-zeroflap-transceiver-osfp-rhs/
    locator: "產品說明與規格"
    read-scope: "已讀 OSFP-RHS、2×DR4、光路與監控。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
  - source-id: credo-800g-zeroflap-ga
    url: https://s205.q4cdn.com/511065572/files/doc_news/Credo-Launches-800G-ZeroFlap-Optical-Transceivers-Engineered-for-AI-Networks-2026.pdf
    locator: "公告開頭與 News Highlights"
    read-scope: "已讀 GA 範圍及 PILOT 使用。"
    stance: supporting
    applicable-period: "2026-03-17"
gaps:
- status: not-public
  reason: 10-K 未揭露 AEC、retimer、光 DSP 與光模組的個別營收，也未揭露客戶名稱。
---

## 供應角色

依產品分為[SPAN／SHIFT AEC 成品](/next?focus=product-active-electrical-cable)、[Toucan PCIe／CXL retimer](/next?focus=product-retimer)、[Dove 80X 光 DSP](/next?focus=product-optical-dsp)及[ZeroFlap 可插拔光模組](/next?focus=product-optical-transceiver)。

Credo 在[網路環節](/next?focus=segment-networking)屬[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)，供應[主動電纜](/next?focus=product-active-electrical-cable)與 [retimer](/next?focus=product-retimer)，也有[光通訊 DSP](/next?focus=role-optical-dsp)。

## 研究界線

工作範圍以 FY2026 10-K、SPAN／SHIFT、Dove 與 ZeroFlap 產品文件為準。標準相容、一般供應、放量與客戶採用依不同證據認定。

本頁以 FY2026 10-K 為依據。10-K 只說 AEC 貢獻了逾 99% 的營收增量，沒有揭露 AEC 占總營收的比例。客戶集中度有簽約方與終端客戶兩種口徑，兩者不能混用。

## 產品與用途

SPAN 800G OSFP 直連 3–7 m，SHIFT 800G DD 至 2×400G DD 可配 1–3 m。CPR61664 列 PCIe 6.x x16 64 GT/s。Dove 800 支援 8:8；Dove 801／802 對應不同 driver。800G ZeroFlap 2×DR4 OSFP-RHS 可用 MPO-12 平行單模 500 m。

- **主動電纜（AEC）**：ZeroFlap AEC，用於 AI 與一般伺服器的 scale-up／scale-out 銅纜連接（Item 1）。
- **Retimer 與 DSP**：光與銅 Ethernet、PCIe 用 retimer 與 DSP（Item 1）。
- **其他**：ZeroFlap 光收發模組、OmniConnect 記憶體方案、SerDes chiplet 與 IP 授權（Item 1）。

## 商業模式

由線纜夥伴製造完整 AEC，再依客戶平台驗證。Dove 以 IC 交付，ZeroFlap 以成品模組提供，再配合 PILOT／Host SDK 擷取遙測。

Fabless；晶圓由 TSMC 生產，封測外包，AEC 由貿聯製造（Item 1）。FY2026 營收 1,335,116 千美元，成長 205.7%，淨利 472.3 百萬美元（Item 7）。

## 客戶與供應商

FY2026 10-K 對貿聯的揭露屬 AEC 製造關係，未指向特定 SPAN／SHIFT 料號或後段客戶。ZeroFlap 於 2026-03-17 公布一般供應，原公告未揭露特定驗證機房與出貨。

簽約方口徑下客戶 A 占 49%、客戶 B 占 32%；終端客戶口徑下三家分別占 33%、32%、19%（Item 7、Note 3）。前十大客戶約 90%。供應商具名 [TSMC](/next?focus=company-tsmc)、[日月光投控](/next?focus=company-3711-tw)旗下 ASE、[Amkor](/next?focus=company-amkr)、[京元電](/next?focus=company-2449-tw)、矽格與[貿聯](/next?focus=company-3665-tw)。

## 競爭與替代

CPR61664 可對照[Astera Labs](/next?focus=company-alab) PT6162 的 PCIe 6.x 名單與 x16 測試；須再對齊板端、韌體與負載。SPAN／SHIFT 為線組，Taurus SCM 是供線纜廠整合的模組。Dove 800 可和 Spica Gen2 依 8:8 光 DSP 的電介面與 driver 比較。

10-K 列出 [Broadcom](/next?focus=company-avgo)、[Marvell](/next?focus=company-mrvl) 與 [Astera Labs](/next?focus=company-alab)，以及線纜與光模組廠。AEC 與光模組、被動銅纜互為替代選項，取捨要看傳輸距離、功耗與可靠度。

## 業務曝險

FY2026 10-K 可辨認 AEC 對出貨變化的影響。實際曝險仍取決於短距佈線、已認證線組與客戶分布；出貨增量也無法代表每種高速料號的比重。

北美客戶占比由 15% 跳到 58%，營收增量幾乎全來自 hyperscaler 的 AEC 放量，曝險集中在少數雲端業者的 AI 機櫃部署。

## 風險

例如機櫃間連線變長而改用光路，可抵銷 AEC 的成長；光模組遙測功能需要 NOS 與管理代理相容；retimer 須另查板端資格。

- **客戶集中**：前十大客戶約 90%，三家終端客戶合計逾八成。
- **單一代工**：晶圓全部由 TSMC 生產，AEC 由貿聯製造。
- **無長期採購承諾**：客戶可在通知期內取消或延後訂單（Item 1A）。
- **技術替代**：光互連或 CPO 普及會壓縮 AEC 的適用距離。

## 財務可取性

SEC FY2026 10-K 為公司與應用口徑來源。指定線組、光 DSP、retimer 或 ZeroFlap 光模組的獨立收入未公開。

- SEC 公開財務資料 可自動取得標準科目；主要申報來源設為 SEC。
- 會計年度結束於 4 月底前後，與曆年不同，跨公司比較需對齊期間。
- AEC 與 retimer 個別營收：10-K 未公開。
