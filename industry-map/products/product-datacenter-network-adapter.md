---
schema-version: research-v1
entity-id: product-datacenter-network-adapter
kind: product
name-zh: "資料中心主機網路介面卡"
aliases:
- "datacenter NIC"
- "SmartNIC"
- "SuperNIC"
summary: "連接主機 PCIe 與資料中心網路，按型號提供封包、DMA 或 RDMA 卸載。"
definition: "將主機 PCIe 資料轉成網路傳輸並接收回存的介面卡產品，可有多埠、主機卸載或網路協定加速。"
purpose: "讓伺服器、GPU 或其他端點透過外部網路與交換器或同層裝置通訊。"
boundary: "本頁以成卡為交付。控制器是卡內晶片，PCIe retimer 維持板端電鏈路，交換器連接多個網路端點。"
adoption-conditions:
- "對齊插槽實際 lane、PCIe 世代、卡型、散熱、驅動、韌體、RoCE 及交換器埠。"
bottlenecks:
- "PCIe 通道或主機存取頻寬、外部埠型、卸載相容性與機箱散熱。"
substitution-limits:
- "單 800GbE、2×400GbE、800G InfiniBand 各對應不同網路與布線，需按實際協定及端點比較。"
reviewed: "2026-11-24"
claims:
- id: nic-host-to-fabric
  statement: "NIC 一側以 PCIe 接主機，另一側以外部網路埠傳輸封包。BCM57708 與 ConnectX-8 C8180 支持硬體網路處理，PCIe 介面和外側 Ethernet／InfiniBand 選項需分別看型號。"
  confidence: well-supported
  conditions:
  - "卡型、散熱與驅動選項按各產品資料，交換器與媒介另外驗證。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm57708-nic-brief
    url: https://docs.broadcom.com/doc/57708-PB
    locator: "Overview、Features、Ordering Information"
    read-scope: "已讀單埠 800GbE、PCIe 6 x16、RoCE、OSFP-RHS 與 PCIe／OCP 料號。"
    stance: supporting
    applicable-period: "57708-PB103，2026-03-13"
  - source-id: nvidia-connectx8-hardware-specs
    url: https://networking-docs.nvidia.com/connectx8hw/specifications
    locator: "C8180 SuperNICs Specifications"
    read-scope: "已讀外型、OSFP-RHS、PCIe 6 x16、散熱與協定。"
    stance: supporting
    applicable-period: "C8180，2026-11-24 查閱"
  - source-id: nvidia-connectx8-system-requirements
    url: https://networking-docs.nvidia.com/connectx8hw/introduction
    locator: "Socket Direct、System Requirements、Features and Benefits"
    read-scope: "已讀 x16 或雙 PCIe 連接、驅動及平台散熱要求。"
    stance: supporting
    applicable-period: "ConnectX-8 使用手冊，2026-11-24 查閱"
- id: nic-port-rate-is-per-protocol
  statement: "BCM957708-P1800GOL02 列單埠 800GbE OSFP-RHS 與 PCIe Gen6 x16。ConnectX-8 C8180 900-9X81E-00EX-ST0 在所讀 OPN 表列 800G XDR InfiniBand 或 2×400GbE、單 OSFP cage。"
  confidence: well-supported
  conditions:
  - "C8180 數值限所查韌體與 OPN；不同 Ethernet 模式不能用聚合帶寬直接替換。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm57708-nic-brief
    url: https://docs.broadcom.com/doc/57708-PB
    locator: "Overview、Features、Ordering Information"
    read-scope: "已讀單埠 800GbE、PCIe 6 x16、RoCE、OSFP-RHS 與 PCIe／OCP 料號。"
    stance: supporting
    applicable-period: "57708-PB103，2026-03-13"
  - source-id: nvidia-connectx8-compatible-opns
    url: https://networking-docs.nvidia.com/connectx8fwrn/40451020/firmware-compatible-products
    locator: "Firmware Compatible Products：C8180 900-9X81E-00EX-ST0、-DT0"
    read-scope: "已讀 800G XDR IB 或 2×400GbE、OSFP 及 PCIe 6 x16。"
    stance: supporting
    applicable-period: "ConnectX-8 Firmware Release Notes v40.45.1020"
- id: nic-card-and-chip-scope
  statement: "Broadcom 在 BCM57708 簡介列 PCIe CEM 或 OCP 3.0 成卡；NVIDIA 以 ConnectX-8 OPN 列成卡；研華 PCIE-2711NP-MEA1E 是使用 NVIDIA ConnectX-6 控制器的單埠 200GbE 成卡。"
  confidence: well-supported
  conditions:
  - "台灣研華例用於辨認卡級整合，規格與 800GbE 案例不同，不能作同速 NIC 排名或認定同一法人的晶片交付。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm57708-nic-brief
    url: https://docs.broadcom.com/doc/57708-PB
    locator: "Overview、Features、Ordering Information"
    read-scope: "已讀單埠 800GbE、PCIe 6 x16、RoCE、OSFP-RHS 與 PCIe／OCP 料號。"
    stance: supporting
    applicable-period: "57708-PB103，2026-03-13"
  - source-id: nvidia-connectx8-compatible-opns
    url: https://networking-docs.nvidia.com/connectx8fwrn/40451020/firmware-compatible-products
    locator: "Firmware Compatible Products：C8180 900-9X81E-00EX-ST0、-DT0"
    read-scope: "已讀 800G XDR IB 或 2×400GbE、OSFP 及 PCIe 6 x16。"
    stance: supporting
    applicable-period: "ConnectX-8 Firmware Release Notes v40.45.1020"
  - source-id: advantech-pcie-2711-datasheet
    url: https://advdownload.advantech.com/productfile/PIS/PCIE-2711/file/PCIE-2711_DS%28101722%2920221019135351.pdf
    locator: "Introduction、Part Number"
    read-scope: "已讀 PCIE-2711NP-MEA1E、ConnectX-6 控制器、200GbE 與主機介面。"
    stance: supporting
    applicable-period: "2022-10-17 版"
- id: nic-adoption-path
  statement: "伺服器提高 scale-out 端點速率或網路冗餘可能增加高速 NIC／埠需求，是否增加成卡數取決於每卡埠數與主機 PCIe 佈局。"
  confidence: inference
  conditions:
  - "追蹤每主機所需網路與冗餘域、實際 lane／插槽、驅動與互通；提高單卡密度可抵銷卡數。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-bcm57708-nic-brief
    url: https://docs.broadcom.com/doc/57708-PB
    locator: "Overview、Features、Ordering Information"
    read-scope: "已讀單埠 800GbE、PCIe 6 x16、RoCE、OSFP-RHS 與 PCIe／OCP 料號。"
    stance: supporting
    applicable-period: "57708-PB103，2026-03-13"
  - source-id: nvidia-connectx8-compatible-opns
    url: https://networking-docs.nvidia.com/connectx8fwrn/40451020/firmware-compatible-products
    locator: "Firmware Compatible Products：C8180 900-9X81E-00EX-ST0、-DT0"
    read-scope: "已讀 800G XDR IB 或 2×400GbE、OSFP 及 PCIe 6 x16。"
    stance: supporting
    applicable-period: "ConnectX-8 Firmware Release Notes v40.45.1020"
  - source-id: nvidia-connectx8-system-requirements
    url: https://networking-docs.nvidia.com/connectx8hw/introduction
    locator: "Socket Direct、System Requirements、Features and Benefits"
    read-scope: "已讀 x16 或雙 PCIe 連接、驅動及平台散熱要求。"
    stance: supporting
    applicable-period: "ConnectX-8 使用手冊，2026-11-24 查閱"
gaps:
- status: not-obtained
  reason: "未取得兩家同單埠、同協定、同 CPU／GPU 路徑與驅動下的尾端延遲、功耗與量產成本。"
- status: not-public
  reason: "所讀料號表未列平台實際出貨量、具名終端客戶及料號收入。"
---

## 定義與用途

資料從 CPU 或 GPU 透過 PCIe 進入網路介面卡，再以 Ethernet 或 InfiniBand 經線纜與[交換系統](/next?focus=product-datacenter-switch)傳到其他節點。NIC 的 DMA 讓裝置能在主機記憶體與卡之間搬移資料；RDMA 在相容的軟硬體堆疊下讓遠端節點以少量 CPU 介入完成記憶體資料傳輸。Ethernet 上的 RoCEv2 要和對端、交換拓樸與流控一起驗證。[PCIe retimer](/next?focus=product-retimer)可改善前段電通道，交換 ASIC 則負責在多埠間轉送。

## 採用條件與限制

### 配好 PCIe、機構與網路埠

- **Broadcom BCM957708-P1800GOL02**。PCIe Gen6 x16、低背 PCIe CEM。單埠 800GbE OSFP-RHS，57708-PB103；OCP 3.0 型式另有料號。
- **NVIDIA 900-9X81E-00EX-ST0**。C8180 HHHL，PCIe 6 x16，支援另接 Socket Direct 擴充。單 OSFP cage，所讀 FW 清單列 800G XDR InfiniBand 或 2×400GbE，依 OPN、FW 及端口配置。
- **研華 PCIE-2711NP-MEA1E**。PCIe 4 x16、低背。單 200GbE QSFP56，有效光模組清單需另取得，2022-10-17 型錄。

用每埠配置、封包負載與 PCIe 實際協商結果核對可用吞吐。CEM 和 OCP 3.0 各有插槽、風道與更換條件。導入成本包括卡、線組／收發器、交換器對端、驅動維護、壅塞控制整合及上線驗證。單一最大速率無法代表完整路徑。

### 替代條件由資料路徑決定

若需要原生單埠 800GbE，上表 BCM57708 料號有相應型錄，C8180 的 2×400GbE 需要不同對端模式與佈線。若應用可用兩條 400G，把雙埠、光／電介質、RDMA 功能與壅塞條件實測後才有比較意義。SmartNIC／DPU 還得逐項查 CPU、記憶體及可執行哪些卸載工作，不能憑行銷名稱認定等價。

## 供應角色與公司

屬於[主機網路介面卡](/next?focus=role-host-network-adapter)。[博通](/next?focus=company-avgo)提供 BCM57708 控制器架構與公開可訂購成卡；[輝達](/next?focus=company-nvda)在 ConnectX-8 OPN 表列不同卡及配置。研華的 200GbE 卡是板卡整合例，控制器由輝達提供。公司能力按實際交付層次紀錄，終端採用、料號合格與量產從相應文件另核。

### 需求如何傳到主機端

**Inference。** 當叢集新增主機或要更多網路端點、備援網域，通過板端與網路對端條件的 NIC 可能增加。若單卡提供更高帶寬及多埠而可整併原方案，卡數未必等比成長。追每主機卡／埠數、PCIe 實際 lane 配置、合格韌體和線組、交換器互通與改版進度。
