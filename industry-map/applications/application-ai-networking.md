---
schema-version: research-v1
entity-id: application-ai-networking
kind: application
name-zh: AI 叢集網路
aliases:
- AI networking
summary: 連接加速器、伺服器與機房的電訊號與光通訊路徑。
question: AI 叢集的資料，怎麼在機櫃內、機櫃間與機房之間傳？
reviewed: '2026-11-24'
definition: 連接加速器、伺服器與機房的電訊號與光通訊路徑。
purpose: 先分 scale-up、scale-out 與跨機房，再拆交換晶片、DSP、連接晶片、光元件、模組與系統。
boundary: 交換晶片、DSP、電訊號連接晶片、光晶片、光模組與交換器系統是不同交付；管理介面、電氣通道與光學傳輸是不同證據範圍。
adoption-conditions:
- 依協議、拓樸、距離、錯誤修正、管理與熱條件驗證整條鏈路
bottlenecks:
- 光／電測試點、雷射與散熱整合及維修流程可能限制採用
substitution-limits:
- 銅、可插拔、LPO 與 CPO 需分別核對端點與系統互通，不能宣稱普遍優勝
flow-steps:
- label: 機櫃內
  note: 依加速器／主機拓樸查板端 PCIe／CXL 與短距媒介。
  products: [product-retimer, product-active-electrical-cable, product-datacenter-network-adapter]
- label: 機櫃間
  note: 交換端依架構用光模組或銅纜。DSP 與雷射屬模組內外的元件，磊晶是晶粒上游。
  products: [product-ethernet-switch-asic, product-datacenter-switch, product-optical-transceiver, product-fiber-cable-assembly, product-optical-dsp, product-inp-laser-chip, product-optical-epiwafer]
- label: 跨機房
  note: 長距光通訊
claims: []
gaps:
- status: not-researched
  reason: 應用頁提供研究路徑，具體產品的認證與下游採用在相關產品及公司頁分別驗證。
---

## 定義與用途

從主機的[網路介面卡](/next?focus=product-datacenter-network-adapter)開始，可沿 PCIe 插槽、NIC 網路埠、線組及交換系統追蹤端點連線。

機櫃間光鏈路可接續閱讀[資料中心光纖連接組件](/next?focus=product-fiber-cable-assembly)。從收發模組的 MPO／LC 端面回推纖芯、極性及配線損耗。

連接加速器、伺服器與機房的電訊號與光通訊路徑。先分 scale-up、scale-out 與跨機房，再拆交換晶片、DSP、連接晶片、光元件、模組與系統。對應既有環節：[網通與光通訊](/next?focus=segment-networking)。

可比較的供應角色：[交換器晶片](/next?focus=role-switch-silicon)、[光通訊 DSP](/next?focus=role-optical-dsp)、[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)、[光通訊磊晶片](/next?focus=role-optical-epiwafer)、[光通訊雷射與光電晶片](/next?focus=role-optical-chip)、[光收發模組](/next?focus=role-optical-module)、[資料中心交換器系統](/next?focus=role-switch-system)。

## 採用條件與限制

先確定通訊域，再用[光／電互連比較與 800GbE 需求案例](/next?focus=research-ai-networking-optical-electrical)依端口與實際佈線，逐步讀到產品、公司與來源。

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
