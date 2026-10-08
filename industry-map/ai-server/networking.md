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
