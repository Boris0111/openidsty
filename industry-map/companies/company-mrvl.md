---
schema-version: research-v1
entity-id: company-mrvl
kind: company
name-zh: 邁威爾
aliases:
- Marvell
- Marvell Technology
summary: Fabless 資料基礎架構晶片公司；FY2026 資料中心占營收 74%，產品含客製 ASIC、光通訊 DSP、AEC DSP、PCIe retimer 與 Ethernet 交換晶片，已出售車用 Ethernet 業務。
legacy-keys:
- MRVL
listings:
- ticker: MRVL
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1835632'
research-depth: deep
reviewed: '2026-11-24'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: 10-K Item 7. MD&A（Net revenue by end market，FY2024–FY2026）；會計年度結束於最接近 1 月 31 日的星期六，故不填固定年度結束日
    read-scope: 已讀終端市場營收表
    stance: supporting
    applicable-period: FY2024–FY2026（截至 2026-01-31）
roles:
- segment-id: segment-compute
  description: 客製 ASIC 設計
  tier: 1
  baseline-path: ai-server/compute.md
- segment-id: segment-networking
  description: 光通訊數位訊號處理晶片
  tier: 1
  baseline-path: ai-server/networking.md
claims:
- id: data-center-share
  statement: 10-K 揭露 FY2026 營收 8,194.6 百萬美元（成長 42.1%），資料中心終端市場 6,100.3 百萬美元、占 74%（FY2025 72%、FY2024 40%）；資料中心涵蓋 AI 系統與伺服器、Ethernet 交換、儲存與資料中心互連。
  confidence: well-supported
  conditions:
  - 資料中心是終端市場，不是單一產品收入；不得用來證明 ASIC 或 DSP 個別規模
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Our Markets and Products 表）；Item 7. MD&A（Net revenue by end market）
    read-scope: 已讀終端市場表與營收段落
    stance: supporting
    applicable-period: FY2024–FY2026
- id: custom-asic
  statement: 10-K 說明公司依個別客戶規格開發客製晶片，用於 AI、資料中心、運算、網路與儲存，平台整合高速 SerDes、ARM 運算、矽光子與先進封裝（die-to-die、chiplet、CPO）。
  confidence: well-supported
  conditions:
  - 客戶名稱與個別專案未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Custom ASICs）
    read-scope: 已讀客製 ASIC 段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: interconnect-portfolio
  statement: 10-K 列出互連產品包括 PAM 與 coherent DSP、雷射驅動器、TIA、矽光子、CPO、LPO 晶片組、資料中心互連、AEC DSP 與 PCIe retimer；PAM DSP 用於資料中心內的光連接，AEC DSP 與線纜廠合作用於 AI 伺服器銅纜連接。
  confidence: well-supported
  conditions:
  - CPO 與收購而來的 Photonic Fabric 屬新產品線，量產程度未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Interconnects）
    read-scope: 已讀互連產品段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: ethernet-switches
  statement: 10-K 說明 Prestera 與 Teralynx Ethernet 交換晶片涵蓋企業、資料中心、電信、雲端與 AI 系統，並正開發以 Teralynx 架構與 224G SerDes 為基礎的 UALink 與 ESUN scale-up 交換晶片。
  confidence: well-supported
  conditions:
  - scale-up 交換晶片仍在開發
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Ethernet Solutions；Scale-Up Switches）
    read-scope: 已讀交換晶片段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: customer-concentration
  statement: 10-K 揭露 FY2026 有兩家客戶各占營收一成以上（經銷商 A 37%、直接客戶 A 14%），前十大客戶合計 82%；出貨到亞洲客戶占 77%。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露；經銷商背後的終端客戶未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1A（客戶集中風險）；Item 7（地區營收）；合併財報附註（concentrations）
    read-scope: 已讀客戶與地區段落
    stance: supporting
    applicable-period: FY2024–FY2026
- id: portfolio-changes
  statement: 10-K 揭露 2025 年 8 月 14 日以 25 億美元現金將車用 Ethernet 業務售予 Infineon，認列稅前利益 18 億美元；並於 2026 年 2 月完成收購 Celestial AI 與 XConn Technologies。
  confidence: well-supported
  conditions:
  - 收購在 FY2026 期後完成
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Recent Developments）；Item 1A（收購風險）
    read-scope: 已讀近期發展段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: named-competitors
  statement: 10-K 列出直接競爭者包括 AMD、世芯（Alchip）、Astera Labs、Ayar Labs、Broadcom、Cisco、Credo、Intel、創意（GUC）、Lightmatter、MACOM、聯發科、Microchip、瀾起、Nvidia、NXP、Qualcomm、Rambus、Semtech、Socionext 等。
  confidence: well-supported
  conditions:
  - 競爭依產品線而異，列名不代表所有產品直接重疊
  reviewed: '2026-10-18'
  evidence:
  - source-id: mrvl-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1835632/000183563226000011/mrvl-20260131.htm
    locator: Item 1. Business（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2026 10-K
- id: novaspica-dsp-delivery
  statement: "MV-CD822 Spica Gen2 為 800G 8×100G PAM4 retimer；MV-CD432 Nova 為 1.6T 16×100G 主機側對 8×200G 線側 gearbox，並整合調變器 driver。"
  confidence: well-supported
  conditions:
  - "各自適用的 lane 配置與光元件須重新驗證；未揭露具名模組與料號出貨。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-spica-gen2-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-spica-gen2-product-brief.pdf
    locator: "Features、Applications"
    read-scope: "已讀 8×100G、分接及光元件。"
    stance: supporting
    applicable-period: "MV-CD822，2022-12"
  - source-id: marvell-nova-mv-cd432-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-nova-1.6t-pam4-dsp-for-optical-transceiver-applications-product-brief.pdf
    locator: "Features、Description"
    read-scope: "已讀 16:8、調變器 driver、FEC。"
    stance: supporting
    applicable-period: "MV-CD432，2023-03"
- id: teralynx-10-switch-delivery
  statement: "Teralynx 10 交換 ASIC 公布最高 51.2 Tb/s、112G 級 SerDes 與 64×800GbE／128×400GbE 例，Marvell 於 2024-07-25 公告量產與未具名部署。"
  confidence: well-supported
  conditions:
  - "實際面板與 NOS 依整機。FY2026 10-K 的 UALink／ESUN 開發方向另列。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-teralynx-10-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/switching/marvell-teralynx-10-data-center-ethernet-switch-product-brief.pdf
    locator: "Overview、Block Diagram"
    read-scope: "已讀轉送、lane 與埠配置。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
  - source-id: marvell-teralynx-10-production
    url: https://www.marvell.com/company/newsroom/marvell-teralynx-512t-ethernet-switch-enters-volume-production-for-global-ai-cloud-deployments.html
    locator: "公告開頭及 SONiC 段"
    read-scope: "已讀量產、客戶部署與軟體。"
    stance: supporting
    applicable-period: "2024-07-25"
- id: alaska-p-and-a-delivery
  statement: "Alaska P MV-CHP10160 是 PCIe Gen6 x16、64 GT/s、CXL 3.x retimer；Alaska A MV-CHA180C0C 為 800G Ethernet AEC 用 8:8 PAM4 線端 DSP。"
  confidence: well-supported
  conditions:
  - "線纜商交付成品。Alaska P 採用公告限系列，未列 MV-CHP10160 的具名採用與出貨。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-alaska-p-mv-chp10160
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/pcie-retimers/marvell-alaska-p-gen6-16l-pcie-retimer-product-brief.pdf
    locator: "Overview、Key Features"
    read-scope: "已讀 x16、64 GT/s、CXL 及損耗。"
    stance: supporting
    applicable-period: "2024-05"
  - source-id: marvell-alaska-a-mv-cha180c0c
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/phys-transceivers/marvell-alaska-a-800g-pam4-dsp-product-brief.pdf
    locator: "Overview、Block Diagram"
    read-scope: "已讀 8:8 與 AEC 應用。"
    stance: supporting
    applicable-period: "2022-02"
  - source-id: marvell-alaska-p-adoption-2025
    url: https://www.marvell.com/company/newsroom/marvell-announces-pcie-retimers-adoption-by-ai-dc-providers.html
    locator: "開頭、夥伴引言"
    read-scope: "已讀系列採用與機型驗證界線。"
    stance: supporting
    applicable-period: "2025-12-09"
- id: fastlinq-nic-form-factor
  statement: "FastLinQ 41000 表 3 列 QL41262HLCU-11 系列為雙 25／10GbE SFP28 成卡，可支援 RoCE。"
  confidence: well-supported
  conditions:
  - "是歷史例，未核目前供貨及同級 800G 成卡交付。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-fastlinq-41000-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/ethernet-adaptersandcontrollers/marvell-ethernet-adapters-fastlinq-41000-series-product-brief.pdf
    locator: "Table 3 Ordering Information"
    read-scope: "已讀指定料號、埠型、雙埠和卸載。"
    stance: supporting
    applicable-period: "AH2058022-00 Rev J，2021-11"
gaps:
- status: not-public
  reason: 10-K 未拆分客製 ASIC、光 DSP、AEC DSP、retimer 或交換晶片營收，也未揭露客戶名稱。
---

## 供應角色

以型號連到[光 DSP](/next?focus=product-optical-dsp)、[交換 ASIC](/next?focus=product-ethernet-switch-asic)及[PCIe retimer](/next?focus=product-retimer)。Alaska A 是[AEC](/next?focus=product-active-electrical-cable)線端 DSP，供線纜商整合。

Marvell 在[運算環節](/next?focus=segment-compute)屬[客製 ASIC 設計與交付](/next?focus=role-custom-asic-partner)，在[網路環節](/next?focus=segment-networking)屬[光通訊 DSP](/next?focus=role-optical-dsp)、[交換器晶片](/next?focus=role-switch-silicon)與[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)（PCIe retimer、AEC DSP）。

## 研究界線

本批重讀 FY2026 Form 10-K 的 Interconnects、Ethernet Solutions、Item 1A，並按產品簡介及出貨公告核對型號、期間與採用範圍。

本頁以 FY2026 10-K 為依據。資料中心占 74% 是終端市場口徑，包含 ASIC、DSP、交換晶片與儲存，不能拿來證明任何單一產品的規模。車用 Ethernet 已出售，Celestial AI 與 XConn 是期後收購。

## 產品與用途

Spica Gen2 MV-CD822 為 800G 8×100G，Nova MV-CD432 為 1.6T 16×100G 至 8×200G 並整合 driver。Teralynx 10 為 51.2 Tb/s ASIC。MV-CHP10160 為 64 GT/s Gen6 x16 retimer。MV-CHA180C0C 為 800G 線端 8:8 DSP。FastLinQ QL41262HLCU-11 是雙 25／10GbE 歷史成卡例。

- **客製 ASIC**：依客戶規格的 AI 與資料中心晶片，平台含 SerDes、ARM、矽光子與先進封裝（Item 1）。
- **互連**：PAM／coherent 光 DSP、驅動器、TIA、矽光子、CPO、LPO、AEC DSP、PCIe retimer（Item 1）。
- **Ethernet**：Prestera 與 Teralynx 交換晶片、Alaska PHY、控制器與網卡；開發中的 UALink／ESUN scale-up 交換晶片（Item 1）。
- **儲存控制器**與通訊等其他產品（Item 1）。

## 商業模式

以晶片及配套軟體進入整合流程。AEC DSP 要由線材廠設計，交換 ASIC 需配整機電熱、NOS 或 SAI；產品交付與整機出貨在不同層級確認。

Fabless，晶圓代工主要在台灣，封測在亞太（Item 1A）。FY2026 營收 8,194.6 百萬美元，成長 42.1%，資料中心占 74%（Item 7）。

## 客戶與供應商

Teralynx 10 於 2024-07-25 公布量產與未具名部署。2025-12-09 公告確認 Alaska P 家族採用，Supermicro 表示其系統將支援，具體機型與合格料號仍待核。

經銷商 A 占 37%、直接客戶 A 占 14%，前十大客戶 82%；亞洲出貨 77%（Item 1A、7）。10-K 說合格晶圓代工廠多數在台灣同一地區，但本頁未具名代工廠。

## 競爭與替代

與[博通](/next?focus=company-avgo)比較 51.2 Tb/s 級 ASIC 要對齊埠、功能與負載。光 DSP 與[Credo](/next?focus=company-crdo)比較時核對 lane 映射。PCIe Gen6 x16 再與[Astera Labs](/next?focus=company-alab) Aries 比較。Alaska A 的晶片型錄不能直接與成品 AEC 的功耗對照。

10-K 直接具名 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo)、[Astera Labs](/next?focus=company-alab)、[世芯](/next?focus=company-3661-tw)、[創意](/next?focus=company-3443-tw)、Nvidia、AMD 等。客戶自行開發晶片也是替代來源（Item 1）。

## 業務曝險

高速光埠與主機 PCIe 的通道條件各自驅動不同產品。資料中心終端市場口徑仍含其他業務，需追實際產品採用。

資料中心由 FY2024 的 40% 升到 FY2026 的 74%，前十大客戶占 82%，曝險集中在少數雲端客戶的 AI 支出。

## 風險

光或電架構更動可降低 DSP／retimer 用量。10-K 指出已認證的零件仍須等待客戶整機量產，且製程或供應商變更可能觸發重新認證。

- **客戶集中**：一家經銷商占 37%，前十大客戶 82%。
- **代工集中**：多數合格代工廠位於台灣同一地區。
- **設計導入**：design win 得失直接影響營收（Item 1A）。
- **收購整合**：Celestial AI 與 XConn 的整合與技術落地。

## 財務可取性

FY2026 Form 10-K 有終端市場銷售與期間口徑。所讀資料未拆各型號出貨、收入或下游客戶。

- SEC 公開財務資料 可自動取得標準科目；主要申報來源設為 SEC。
- 會計年度結束於 1 月底，與曆年差一個月，跨公司比較需對齊期間。
- ASIC、光 DSP、交換晶片營收：10-K 未公開。
