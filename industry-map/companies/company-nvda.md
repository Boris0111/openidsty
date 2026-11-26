---
schema-version: research-v1
entity-id: company-nvda
kind: company
name-zh: 輝達
aliases:
- NVIDIA
- Nvidia
- 英偉達
summary: 輝達供應加速運算平台，ConnectX-8 提供資料中心網路介面卡；此頁本批深研範圍為主機網路。
legacy-keys:
- NVDA
listings:
- ticker: NVDA
  market: US
  exchange: XNAS
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1045810'
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-compute
  description: GPU 與機櫃級規格定義者
  tier: 1
  baseline-path: ai-server/compute.md
claims:
- id: connectx8-host-adapter-delivery
  statement: "NVIDIA 的 C8180 900-9X81E-00EX-ST0 是 PCIe Gen6 x16、單 OSFP cage 的 ConnectX-8 成卡。所讀韌體相容清單列 800G XDR InfiniBand 或 2×400GbE。"
  confidence: well-supported
  conditions:
  - "型號、韌體、端點及機箱散熱是適用範圍的組成。未延伸為一個 800GbE 網路埠或特定客戶採用。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: nvidia-connectx8-compatible-opns
    url: https://networking-docs.nvidia.com/connectx8fwrn/40451020/firmware-compatible-products
    locator: "Firmware Compatible Products：C8180 900-9X81E-00EX-ST0、-DT0"
    read-scope: "已讀 800G XDR IB 或 2×400GbE、OSFP 及 PCIe 6 x16。"
    stance: supporting
    applicable-period: "ConnectX-8 Firmware Release Notes v40.45.1020"
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
- id: networking-platform-and-manufacturing
  statement: "FY2026 10-K 把網路產品列為 NVLink、Ethernet 與 InfiniBand 的介面卡、線纜、DPU、晶片、交換器及軟體；公司採 fabless 委外模式，且說明市場需求與容量錯配風險。"
  confidence: well-supported
  conditions:
  - "10-K 描述集團營運，無法拆到 ConnectX-8 料號或其特定整機製造商。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: nvda-10k-fy2026
    url: https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm
    locator: "Item 1. Business：Data Center、Manufacturing；Item 1A Demand, Supply and Manufacturing；Item 7 Customer Concentration"
    read-scope: "已讀平台產品線、委外製造、需求／產能調配風險與未具名直接客戶。"
    stance: supporting
    applicable-period: "FY2026，2026-01-25 結束"
gaps:
- status: not-researched
  reason: 本批深研聚焦主機網路介面卡。GPU 與其他系統的產品線、客戶、競爭及成本未在此批核查。
- status: not-public
  reason: 所讀 FY2026 10-K 及型錄未揭露 ConnectX-8 料號收入、具名驗證客戶或出貨規模。
- status: not-obtained
  reason: 未取得與其他 NIC 在同主機、協定、流量與光／電配置下的尾端延遲、功耗與成本。
---

## 供應角色

- GPU 與機櫃級規格定義者
- [主機網路介面卡](/next?focus=role-host-network-adapter)：ConnectX-8 C8180 提供可裝到伺服器的板卡。

## 研究界線

2026-11-24 以 ConnectX-8 硬體手冊、FW 相容表及 FY2026 10-K 核對公開交付。產品能力、整機供應與終端採用各依來源判定。

## 產品與用途

C8180 900-9X81E-00EX-ST0 在單 OSFP cage 上依 OPN 與韌體提供 800G XDR InfiniBand 或 2×400GbE。主機為 PCIe 6 x16，可另核 Socket Direct 擴充。支援的 RDMA、網路與插槽組態須按韌體和節點設計查證。

## 商業模式

FY2026 10-K 將 NIC、DPU、交換晶片、整機及軟體列在整合式網路能力中；採 fabless 委外。卡有公開 OPN，也可能和平台整合，個別模式的比重未披露。

## 客戶與供應商

10-K 列直接客戶含 ODM、OEM、雲端業者及整合商，並披露集團層級集中情形。未揭露所讀料號的驗證客戶、出貨或卡級委託組裝名單。

## 競爭與替代

在帶 RDMA 的主機成卡角色，可與[博通](/next?focus=company-avgo) BCM57708 系列做條件式比較。當 Ethernet 拓樸允許 2×400GbE 才可比較總吞吐；需要單 800GbE 時應另找符合規格型號。IB 模式還需對應 IB fabric。同機箱、負載與驅動下的尾端延遲或功耗未取得。

## 業務曝險

當系統新增合格的高速主機端點與網路 fabric，才可能增加 ConnectX 卡的採用。FY2026 10-K 的資料中心網路範圍還包括 NVLink、交換器等，沒有單列所讀 OPN 的營收。

## 風險

連線效能取決於板端頻寬、PCIe 拓樸、散熱、對端及驅動。FY2026 10-K 另揭露產能前置承諾、長交期與客戶需求變化風險。

## 財務可取性

SEC FY2026 Form 10-K 可查集團營運、分部及財報。所讀文件未提供 ConnectX-8 卡、特定 Ethernet 模式或客戶的收入。
