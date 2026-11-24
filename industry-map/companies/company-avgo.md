---
schema-version: research-v1
entity-id: company-avgo
kind: company
name-zh: 博通
aliases:
- Broadcom
- Broadcom Inc.
summary: 半導體與基礎架構軟體公司；半導體解決方案占 FY2025 營收 58%，成長主要來自客製 AI 加速器與 AI 網路產品，另有約 42% 來自 VMware 等基礎架構軟體。
legacy-keys:
- AVGO
listings:
- ticker: AVGO
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1730168'
research-depth: deep
reviewed: '2026-11-24'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: 10-K Item 7. MD&A（Net Revenue by Segment，FY2025 與 FY2024）；會計年度採 52/53 週制，結束於最接近 10 月 31 日的星期日，故不填固定年度結束日
    read-scope: 已讀分部營收表
    stance: supporting
    applicable-period: FY2024–FY2025（截至 2025-11-02）
roles:
- segment-id: segment-compute
  description: 客製 ASIC 設計與交付
  tier: 1
  baseline-path: ai-server/compute.md
- segment-id: segment-networking
  description: 交換器晶片
  tier: 1
  baseline-path: ai-server/networking.md
claims:
- id: segment-mix
  statement: 10-K 揭露 FY2025 總營收 63,887 百萬美元（成長 24%），其中半導體解決方案 36,858 百萬美元、占 58%，其餘約 42% 為基礎架構軟體；半導體成長主要來自客製 AI 加速器與 AI 網路產品，軟體成長主要來自 VMware Cloud Foundation。
  confidence: well-supported
  conditions:
  - 分部營收不拆分客製 ASIC、交換晶片或光元件個別收入；不得以總營收當作特定產品證據
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: Item 7. MD&A（Net Revenue by Segment 表與說明）
    read-scope: 已讀分部營收表與增減說明
    stance: supporting
    applicable-period: FY2024–FY2025
- id: custom-silicon
  statement: 10-K 說明 Custom Silicon Solutions 提供技術與 IP 平台，為客戶設計 AI、HPC、網路與儲存用 ASIC，整合 HBM、SerDes、IP 核與先進封裝；客製加速器（XPU）依個別客戶規格製作，客戶包括 hyperscaler、AI 前沿模型公司與系統整合商，部分用於機櫃或系統。
  confidence: well-supported
  conditions:
  - 客戶名稱與個別專案未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: Item 1. Business（Networking Connectivity／Custom Silicon Solutions）
    read-scope: 已讀產品說明
    stance: supporting
    applicable-period: FY2025 10-K
- id: ethernet-switching
  statement: 10-K 說明 Ethernet Switching & Routing 產品用於企業與 AI 資料中心、服務供應商網路，為 hyperscaler 與 AI 前沿模型客戶提供高容量、低延遲交換晶片；同一終端市場另有 Ethernet NIC、PHY 與光纖元件。
  confidence: well-supported
  conditions:
  - 10-K 稱這些產品同時用於 AI 與非 AI 工作負載，未拆分收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: Item 1. Business（Networking Connectivity：Ethernet Switching & Routing、NIC、PHY、Fiber Optic Components）
    read-scope: 已讀網路產品說明
    stance: supporting
    applicable-period: FY2025 10-K
- id: manufacturing-partners
  statement: 10-K 說明多數前段晶圓製造外包給 TSMC 等代工廠，大部分封裝測試由 TSMC、Advanced Semiconductor Engineering、Foxconn、Amkor 與矽品等代工；自有晶圓廠則生產 FBAR 濾波器，以及光纖通訊用的 GaAs 與 InP 雷射。
  confidence: well-supported
  conditions:
  - 未揭露各供應商占比
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: Item 1. Business（Manufacturing）
    read-scope: 已讀製造段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: customer-concentration
  statement: 10-K 揭露 FY2025 經銷商占營收 48%，單一經銷商直接銷售占 32%（FY2024 為 28%）；公司估計透過所有通路銷售給前五大終端客戶約占 40%；出貨到中國（含香港）占 17%。風險因素並提到 AI 客戶可能要求以租賃方式取得以其 XPU 為基礎的機櫃或系統。
  confidence: well-supported
  conditions:
  - 終端客戶名稱未揭露；出貨地不等於終端客戶所在地
  reviewed: '2026-10-18'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: Item 1. Business（Sales and Distribution）；Item 1A 客戶集中風險；Item 7 地區營收；Note（concentrations）
    read-scope: 已讀客戶與地區段落
    stance: supporting
    applicable-period: FY2024–FY2025
- id: bcm57708-host-adapter-delivery
  statement: "Broadcom BCM57708 產品簡介列單埠 800GbE、OSFP-RHS 與 PCIe 6 x16 的 NIC 成卡，含 CEM 與獨立 OCP 3.0 料號。"
  confidence: well-supported
  conditions:
  - "限 57708-PB103。型錄、PCI-SIG／OCP 形式以及任一機房的端到端驗證與出貨分開查核。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm57708-nic-brief
    url: https://docs.broadcom.com/doc/57708-PB
    locator: "Overview、Features、Ordering Information"
    read-scope: "已讀單埠 800GbE、PCIe 6 x16、RoCE、OSFP-RHS 與 PCIe／OCP 料號。"
    stance: supporting
    applicable-period: "57708-PB103，2026-03-13"
- id: tomahawk-asic-delivery
  statement: "Broadcom Tomahawk 6 公布單晶片 102.4 Tb/s 與 100G／200G SerDes，於 2026-03-12 宣布量產出貨。前代 BCM78900 出現在智邦 AS9817-64O 的料號資料。"
  confidence: well-supported
  conditions:
  - "限各自 ASIC 世代。前代設計配置不證明同客戶採用 Tomahawk 6 或下單量。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-tomahawk-6-volume-2026
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-now-shipping-worlds-first-1024-tbps-switch-production
    locator: "開頭及 Highly optimized 段"
    read-scope: "已讀 Tomahawk 6 家族量產出貨。"
    stance: supporting
    applicable-period: "2026-03-12"
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Components"
    read-scope: "已讀指定整機與 BCM78900 控制器。"
    stance: supporting
    applicable-period: "E092023-AP-R01"
- id: bcm85822-optical-dsp-delivery
  statement: "BCM85822 光模組 DSP PHY 在 800GbE 模式以 8×106 Gb/s 主機側對 4×226 Gb/s 線側，整合雷射 driver。"
  confidence: well-supported
  conditions:
  - "此處限 DSP PHY 晶片與型錄規格；適用模組與客戶驗收另核。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm85822-optical-dsp-brief
    url: https://docs.broadcom.com/doc/85822-DIE-PB
    locator: "Overview、Key Features"
    read-scope: "已讀 gearbox、driver 及 FEC。"
    stance: supporting
    applicable-period: "85822-DIE-PB100，2023-09-18"
- id: inp-laser-fabrication-scope
  statement: "FY2025 Form 10-K 說明博通自有晶圓廠含光纖通訊用 InP 及 GaAs 雷射製程。"
  confidence: well-supported
  conditions:
  - "原文未拆料號、客戶、出貨及外售或自用比例。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: "Item 1. Business：Manufacturing"
    read-scope: "重讀自有 InP／GaAs 雷射與外包 CMOS 的範圍。"
    stance: supporting
    applicable-period: "FY2025 截至 2025-11-02"
gaps:
- status: not-public
  reason: 10-K 未拆分客製 ASIC、交換晶片、光元件或 AI 相關營收，也未揭露終端客戶名稱。
- status: not-public
  reason: 半導體部分只描述競爭者類型（IDM、fabless 與大型 OEM 自研），未具名。
---

## 供應角色

依交付分為[Tomahawk 交換 ASIC](/next?focus=product-ethernet-switch-asic)、[BCM85822 光 DSP](/next?focus=product-optical-dsp)、[InP 通訊雷射](/next?focus=product-inp-laser-chip)與[BCM57708 NIC 成卡](/next?focus=product-datacenter-network-adapter)。

博通也提供[主機用 Ethernet 網路介面卡](/next?focus=product-datacenter-network-adapter)，BCM57708 料號另屬卡級交付。

Broadcom 在[運算環節](/next?focus=segment-compute)屬[客製 ASIC 設計與交付](/next?focus=role-custom-asic-partner)，在[網路環節](/next?focus=segment-networking)屬[交換器晶片](/next?focus=role-switch-silicon)，並以自有晶圓廠生產光通訊雷射，屬[光通訊雷射與光電晶片](/next?focus=role-optical-chip)。

## 研究界線

本批重讀 FY2025 10-K Manufacturing／Networking Connectivity，再依料號簡介與出貨公告確認晶片、卡與系統的分工。

本頁以 FY2025 10-K 為依據。約四成二營收是 VMware 等基礎架構軟體，與地圖無關；半導體營收也沒有拆出客製 ASIC、交換晶片或雷射，所以不能用總營收或半導體分部營收證明任何單一產品的規模。

## 產品與用途

Tomahawk 6 為 102.4 Tb/s ASIC，200G 或 100G 級 SerDes 依介面。BCM85822 把 8×106 Gb/s host lane 對到 4×226 Gb/s line lane，含 driver。10-K 所述自有 InP 雷射製程未揭露波長或料號。

BCM957708-P1800GOL02 是 PCIe 6 x16、單 800GbE OSFP-RHS 的 NIC；OCP 3.0 型式有獨立料號。

- **客製晶片（XPU）**：依 hyperscaler 與 AI 前沿模型客戶規格設計的加速器，整合 HBM、SerDes 與先進封裝（Item 1）。
- **Ethernet 交換與路由**：企業與 AI 資料中心、服務供應商網路的交換晶片（Item 1）。
- **網路介面與實體層**：Ethernet NIC、PHY 收發器與光纖元件（Item 1）。
- **其他半導體**：無線 RF（FBAR）、Wi-Fi／藍牙、伺服器與儲存、寬頻與工業（Item 1）。
- **基礎架構軟體**：VMware Cloud Foundation 等（Item 7）。

## 商業模式

Tomahawk 供整機廠做系統設計；10-K 區分內部專用雷射製程和委外標準 CMOS。不同產品的製造與整合條件須分別跟進。

以外包製造為主，少數專有製程自建晶圓廠（Item 1）。FY2025 營收 63,887 百萬美元，半導體 58%、軟體 42%（Item 7）。

## 客戶與供應商

智邦 AS9817-64O 具名 BCM78900，是型號設計配置。2026-03-12 公告 Tomahawk 6 量產出貨；該公告未提供終端客戶出貨量。光 DSP、雷射與 NIC 也需分別取得採用證據。

經銷商占營收 48%，單一經銷商占 32%；前五大終端客戶約 40%（Item 1、1A）。供應商方面，10-K 具名 [TSMC](/next?focus=company-tsmc)、[日月光投控](/next?focus=company-3711-tw)旗下的日月光與矽品，以及 [Amkor](/next?focus=company-amkr)。

## 競爭與替代

可在 51.2 Tb/s 級比較 Tomahawk 5 與[邁威爾](/next?focus=company-mrvl) Teralynx 10 的轉送、緩衝與系統適配。BCM85822 的 8:4 光 DSP 和 Spica 8:8 需對齊兩側 lane、FEC 與光元件後才可比較。

NIC 同角色可與[輝達](/next?focus=company-nvda)比較，先確定網路需要單埠 800GbE，或可使用 2×400GbE；再對齊主機插槽、RoCE 與驅動。

半導體部分只描述 IDM、fabless 與大型 OEM 自研三類競爭者。在[客製 ASIC](/next?focus=role-custom-asic-partner) 角色可與 [Marvell](/next?focus=company-mrvl)、[世芯](/next?focus=company-3661-tw)、[創意](/next?focus=company-3443-tw)比較；Marvell 10-K 把 Broadcom 列為直接競爭者。客戶自研也是替代來源。

## 業務曝險

交換 ASIC 需求受有效埠、網路層數及速度升級影響。光 DSP、雷射和 NIC 應依模組配置及主機端口分開觀察。

10-K 把半導體成長歸因於客製 AI 加速器與 AI 網路產品，但沒有金額。AI 曝險集中在少數大客戶，前五大終端客戶約四成。

## 風險

高密度設計需通過 SerDes、散熱與 NOS 驗證。CPO、LPO 及高 radix 都可能改變前面板模組或晶片的用量。

- **客戶集中**：少數 AI 客戶可能要求更有利的價格與合約條件，甚至以租賃取得 XPU 機櫃或系統（Item 1A）。
- **代工集中**：先進製程依賴 TSMC，封測集中在亞洲。
- **地緣政治**：出貨到中國約 17%。
- **業務組合**：軟體占四成以上，讀取 AI 晶片曝險時需排除。

## 財務可取性

FY2025 Form 10-K 有集團與分部資訊。未分拆本批交換 ASIC、雷射、光 DSP 或 NIC 的型號收入。

- SEC 公開財務資料 可自動取得標準科目；主要申報來源設為 SEC。
- 會計年度採 52/53 週制，與曆年不同，跨公司比較需對齊期間。
- 客製 ASIC、交換晶片與 AI 營收：10-K 未公開。
