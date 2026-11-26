---
schema-version: research-v1
entity-id: product-ethernet-switch-asic
kind: product
name-zh: "交換器晶片"
aliases:
- "switch ASIC"
summary: "依封包標頭、轉送規則與排程選擇輸出埠，並以 SerDes 接入系統的乙太網路 ASIC。"
definition: "整合 Ethernet MAC、封包解析、緩衝與切換 fabric 的交換器晶片。"
purpose: "把各個入埠封包依交換策略轉送至適用出埠，支援資料中心網路拓樸。"
boundary: "晶片的 SerDes 與交換容量給整機設計上限。外部埠、介質、電熱機構與 NOS 由系統配置決定。"
adoption-conditions:
- "核對要服務的 scale-up、scale-out 或跨機房場景，再確認實體埠、封包大小、緩衝、流控及 SDK。"
bottlenecks:
- "前面板埠密度、SerDes 通道、散熱與 SDK 功能支援會限制晶片可在系統中實現的配置。"
substitution-limits:
- "同 Tb/s 晶片仍需核對排程、緩衝和延遲，甚至是否同時支援目標埠與分接。"
reviewed: "2026-11-24"
claims:
- id: switch-asic-forwarding
  statement: "Teralynx 10 的資料路徑含入出埠政策、L2／L3 轉送、緩衝及 QoS，透過 Ethernet MAC、PCS／FEC 與 SerDes 接出。"
  confidence: well-supported
  conditions:
  - "為 Teralynx 10 晶片例。整機介質與埠型取決於平台。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-teralynx-10-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/switching/marvell-teralynx-10-data-center-ethernet-switch-product-brief.pdf
    locator: "Overview、Block Diagram、Key Features"
    read-scope: "已讀 L2／L3、buffer、QoS、112G SerDes 及埠例。"
    stance: supporting
    applicable-period: "Teralynx 10 product brief，2026-11-24 查閱"
- id: switch-asic-lane-and-port
  statement: "Tomahawk 6 公布單晶片 102.4 Tb/s 及 100G／200G SerDes。Teralynx 10 為最高 51.2 Tb/s，簡介列 112G 級 SerDes 與 64×800GbE／128×400GbE 的晶片組態例，原廠於 2024-07-25 宣布量產。"
  confidence: well-supported
  conditions:
  - "容量、電 lane 線路速率及面板埠速率分別驗證；整機廠須完成 SerDes、PCB、媒介與散熱設計。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-tomahawk-6-shipping
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch
    locator: "公告開頭、Flexible Connectivity Options"
    read-scope: "已讀 102.4 Tb/s、100G／200G SerDes 與光電選項。"
    stance: supporting
    applicable-period: "Tomahawk 6，2025-06-03"
  - source-id: marvell-teralynx-10-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/switching/marvell-teralynx-10-data-center-ethernet-switch-product-brief.pdf
    locator: "Overview、Block Diagram、Key Features"
    read-scope: "已讀 L2／L3、buffer、QoS、112G SerDes 及埠例。"
    stance: supporting
    applicable-period: "Teralynx 10 product brief，2026-11-24 查閱"
  - source-id: marvell-teralynx-10-production
    url: https://www.marvell.com/company/newsroom/marvell-teralynx-512t-ethernet-switch-enters-volume-production-for-global-ai-cloud-deployments.html
    locator: "公告開頭、SONiC 段"
    read-scope: "已讀量產與未具名部署聲明。"
    stance: supporting
    applicable-period: "2024-07-25 量產公告"
- id: switch-asic-fabric-boundaries
  statement: "Broadcom Tomahawk Ultra 公告強調緊耦合 scale-up 的低延遲、重傳與 credit 流控。Jericho4 公告針對跨資料中心，描述深緩衝、加密及聚合多條實體連線的邏輯埠。"
  confidence: well-supported
  conditions:
  - "適用於來源的架構。Jericho4 公告的 Availability 為送樣，不能推為每個系統已量產。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-tomahawk-ultra-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-ultra-reimagining-ethernet-switch-hpc
    locator: "Shattering Myths、Built for HPC and AI Scale-Up"
    read-scope: "已讀 scale-up、封包重傳、credit 流控與緊耦合用途。"
    stance: supporting
    applicable-period: "Tomahawk Ultra，2025-07-15"
  - source-id: broadcom-jericho4-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-jericho4-enabling-distributed-ai-computing-across
    locator: "公告主文、Availability"
    read-scope: "已讀跨站距離、深緩衝、MACsec 與送樣狀態。"
    stance: supporting
    applicable-period: "Jericho4，2025-08 公告"
- id: switch-asic-radix-demand
  statement: "加速器連線變快或變多，在 leaf-spine 拓樸相同時會拉動交換容量。高 radix 或 breakout 可能合併部分交換層，降低整機與 ASIC 數量。"
  confidence: inference
  conditions:
  - "核對實際下行／上行埠數、超額配置、跳數與軟硬體合格狀態。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-teralynx-10-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/switching/marvell-teralynx-10-data-center-ethernet-switch-product-brief.pdf
    locator: "Overview、Block Diagram、Key Features"
    read-scope: "已讀 L2／L3、buffer、QoS、112G SerDes 及埠例。"
    stance: supporting
    applicable-period: "Teralynx 10 product brief，2026-11-24 查閱"
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀前面板 OSFP800、breakout、BCM78900、ONIE 與電熱機構。"
    stance: supporting
    applicable-period: "AS9817-64O，E092023-AP-R01"
  - source-id: broadcom-tomahawk-6-shipping
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch
    locator: "公告開頭、Flexible Connectivity Options"
    read-scope: "已讀 102.4 Tb/s、100G／200G SerDes 與光電選項。"
    stance: supporting
    applicable-period: "Tomahawk 6，2025-06-03"
gaps:
- status: not-obtained
  reason: "未取得同埠速率、封包長度、開啟同等功能及負載下的晶片延遲、功耗、可用緩衝與價格。"
- status: not-public
  reason: "上述文件未提供各架構特定終端客戶的晶片用量或分項收入。"
---

## 定義與用途

輸入埠的 SerDes 接收高速位元，PCS／FEC 將它交給 Ethernet MAC。以 Teralynx 10 的 block diagram 為例，封包在入埠查表、執行政策，經交換 fabric 決定輸出位置。流量集中到同一出埠時，緩衝與排程負責暫存和分配傳輸。晶片交付包括這些資料路徑能力；面板端的光模組、線組、散熱、電源及網路作業系統由[交換器系統](/next?focus=product-datacenter-switch)整合。

## 採用條件與限制

### 看清晶片 lane 與面板埠

舉例，Teralynx 10 簡介列 51.2 Tb/s、112G 級 SerDes，與 64×800GbE 或 128×400GbE 的設計模式。Tomahawk 6 的晶片公告列 102.4 Tb/s 並支援 100G 級與 200G 級 SerDes。機箱可能只配其中一組 lane、電埠與光介面，埠數要以整機資料表為準。提高 lane 速率要重驗走線損耗、訊號完整性與光電介面。在功耗與成本比較中也要納入 retimer、散熱、可插拔光模組或 CPO 光引擎。

### 拓樸決定需要的 ASIC 功能

- **Scale-up**。放大同一緊耦合運算域；看負載下的延遲、封包大小、重傳與 credit 流控。Broadcom Tomahawk Ultra，2025-07-15。
- **Scale-out**。用 leaf-spine 等拓樸連接多台伺服器；看上／下行埠、負載平衡、壅塞、遙測及 NOS。Teralynx 10 簡介、Tomahawk 6 公告。
- **跨機房**。較長的鏈路需查傳輸設備、保護、加密、緩衝及鏈路延遲。Jericho4 公告，HyperPort 是多條 800GbE 聚合的邏輯埠，Availability 列送樣。

## 供應角色與公司

屬於[交換器晶片](/next?focus=role-switch-silicon)。在相同 51.2 Tb/s 級別，[博通](/next?focus=company-avgo) Tomahawk 5 BCM78900 與[邁威爾](/next?focus=company-mrvl) Teralynx 10 都可支援 800G 交換設計。智邦 AS9817-64O 資料表列出 BCM78900，邁威爾 2024-07-25 公告 Teralynx 10 量產與未具名部署。同級比較需對齊埠配置、負載、流控、功能與測試條件。

### 容量升級何時拉動晶片需求

**Inference。** 埠速度和端點數上升若推動拓樸保留原交換層數並加裝機箱，交換晶片與高階 SerDes 需求可能增長。若新 ASIC 的埠數足以合併兩層，或實際布線／終端速率限制上線，所需晶片數量可能少於按總頻寬推算。先追可用的 ASIC／NOS 組合、端點與連線數，再查實際系統出貨及驗證。
