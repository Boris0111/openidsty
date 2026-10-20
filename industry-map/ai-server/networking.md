---
segment: networking
name_zh: 網通與光通訊
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
companies:
  - ticker: "AVGO"
    name_zh: 博通
    role: 交換器晶片
    tier: 1
  - ticker: "MRVL"
    name_zh: 邁威爾
    role: 光通訊數位訊號處理晶片
    tier: 1
  - ticker: "CRDO"
    name_zh: Credo
    role: 高速連接晶片與線材
    tier: 2
  - ticker: "ALAB"
    name_zh: Astera Labs
    role: 連接橋接晶片
    tier: 2
  - ticker: "2345.TW"
    name_zh: 智邦
    role: 資料中心交換器
    tier: 1
  - ticker: "3081.TWO"
    name_zh: 聯亞
    role: 光通訊磷化銦晶片
    tier: 2
  - ticker: "4979.TWO"
    name_zh: 華星光
    role: 光收發模組
    tier: 2
upstream: [eda-ip, foundry]
downstream: [odm]
themes: [cpo-silicon-photonics, custom-asic-vs-gpu]
kpis:
  - 交換器埠速世代與出貨量
  - 光模組速率組合與單價
  - 每台加速器搭配的網通價值量
signals:
  - 交換器晶片世代轉換時程
  - 共同封裝光學的導入與試產進度
downstream-relations:
  odm:
    kind: supply
    summary: 網通與光通訊至系統組裝與機櫃整合：交換器／網路模組、光電轉換與系統介面。
    items:
    - 交換器／網路模組、光電轉換與系統介面
    dependencies:
    - 通道、控制管理、散熱與網路拓樸
    conditions:
    - 所需協議、距離、功耗及維修方式在整機驗證通過
    confidence: inference
    evidence: []
    gaps:
    - 缺少特定 ASIC／DSP／模組與 ODM 平台的互通實測與採購證據，不能由同一環節推定相同產品。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 先區分 scale-up、scale-out 與跨機房；再拆 switch ASIC、DSP、光元件、模組及系統。CMIS
    管理層、電氣通道及光學傳輸是不同證據範圍。
  adoption-conditions:
  - 按所需協議、拓樸、距離、錯誤修正、管理與熱條件驗證整條鏈路，不只看交換容量。
  - 銅、可插拔、LPO／CPO 須分別核對端點、模組與系統的互通、測試及維修責任。
  bottlenecks:
  - 光／電測試點、雷射與散熱整合、管理能力和維修流程都可能限制採用，單一介面相容不能代表系統互通。
  substitution-limits:
  - OIF 這份 CPO 模組含 DSP 功能，不能把 CPO 概括為所有 DSP 消失；LPO 的系統條件需另查。
  - 整體耗電需含雷射、交換器、控制與冷卻；本輪沒有跨路線同口徑每 bit／距離實測，不能宣稱普遍優勝。
  claims:
  - id: network-domains
    statement: NVIDIA 公開網路介紹區分 NVLink scale-up、InfiniBand／Ethernet scale-out 與跨資料中心；是其平台分工說明。
    confidence: well-supported
    evidence:
    - source-id: nvidia-networking-technical
      url: https://www.nvidia.com/en-us/networking/
      locator: Introduction／Networking Purpose-Built
      read-scope: 已讀指定公開段落，未取得完整設計／認證檔
  - id: cpo-module-interfaces
    statement: OIF CPO Module IA 描述特定模組與 ASIC 間電氣、光學及熱介面；不能據此推定全產業採用。
    confidence: well-supported
    evidence:
    - document-id: oif-cpo-module
      version-id: module-01-0
      locator: module-scope
    - document-id: oif-cpo-module
      version-id: module-01-0
      locator: thermal-interface
    - document-id: oif-cpo-module
      version-id: module-01-0
      locator: test-points
  - id: cmis-scope
    statement: CMIS 5.4 的核讀範圍是 host／module 管理互動，不代替光學或電氣性能驗證。
    confidence: well-supported
    evidence:
    - document-id: oif-cmis
      version-id: revision-5-4
      locator: management-scope
  evidence-gaps:
  - 缺少同拓樸、距離與流量負載下銅／可插拔／LPO／CPO 的系統功耗、BER 與現場維修比較。
  - 未取得候選公司逐料號、客戶導入與產品收入對照；本輪僅核讀 IA 的指定章節。
  reviewed: '2026-10-16'
---

## 環節定義

讓加速器、伺服器與機櫃交換資料，涵蓋 switch ASIC、交換器系統、光通訊 DSP、光元件與收發模組，以及高速連接橋接晶片。晶片、模組與系統供應商在 `role` 中分別標示，不能把交換器晶片出貨直接當成光模組訂單。

判讀時先確認是機櫃內的 scale-up、機櫃間的 scale-out，還是跨機房連結；三者的距離、拓樸、延遲與可靠性要求不同。

## 技術變數

交換容量、單埠速率、SerDes、每 bit 耗電與壅塞控制共同決定網路能否餵飽運算核心。光模組則需分清雷射、調變／接收元件與 DSP 的角色，並核對模組速率、傳輸距離與互通性。[Marvell 光通訊 DSP 說明](https://www.marvell.com/solutions/data-center/optical-dsp.html)

可插拔模組、LPO 與 CPO 是不同整合方式。CPO 把光引擎靠近交換器 ASIC，縮短電訊號路徑，但也提高封裝、測試、雷射供應與現場維修的整合要求。已有供應商公告出貨，不能將整個題材一律視為概念，也不能把單一產品出貨等同全產業採用。[Broadcom TH6-Davisson 出貨公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)

## 玩家格局

**博通（AVGO）**提供交換器 ASIC 與 CPO 平台；**邁威爾（MRVL）**參與光通訊 DSP；**Credo（CRDO）**與 **Astera Labs（ALAB）**代表高速連接、retimer／橋接角色。各公司產品範圍可能重疊，應按特定接口與料號比較。

台廠以 **智邦（2345.TW）**的交換器系統、**聯亞（3081.TWO）**的磷化銦光元件，以及 **華星光（4979.TWO）**的光收發產品對照。這些是價值鏈位置，不代表已取得同一 CPO 客戶或可以彼此替換；特定客戶導入仍屬 **needs verification**。

## 傳導鏈

**`eda-ip`、`foundry` → 本環節**：工具／介面 IP 與製程的認證和產能，影響 switch ASIC、DSP 及連接晶片的上市、供給與成本。

**本環節 → `odm` → `datacenter`**：網通料件交期與新速率平台的互通測試影響整機櫃交付。加速器數量增長是否帶動更多網通價值量，還取決於拓樸、每個交換器可承載的規模與重用比例，屬 **inference**。

從 `cpo-silicon-photonics` 題材可橫向走到 `advanced-packaging` 與 `compute`；從共同下游 `odm` 可查 `pcb`、`power` 與 `thermal` 的配套。光學整合改版可能改變既有 DSP／模組的內容量，不能將所有名單公司都視為同方向受惠。

## 監測指標

看交換器埠速世代與出貨量、光模組速率／單價組合、每台加速器搭配的網通價值量。新路線須區分展示、送樣、客戶認證、出貨，以及法說會量化的商業收入。

來源優先採原廠產品文件、財報／法說會與系統廠公開導入資訊；聯展或合作名單只能證明參與，無法證明份額。題材狀態依 `themes/cpo-silicon-photonics.md` 的證據門檻校準。

## 風險

客戶高度集中、拓樸／接口變更、光學測試良率與維修成本，可能改變供應商分工。較高交換容量可能降低每台加速器所需的交換器數量；可插拔與 CPO 的替代也可能讓某些產品內容量下降。需以整個網路的成本、耗電與可靠性判讀，而非單一晶片規格。
