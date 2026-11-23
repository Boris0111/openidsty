---
schema-version: research-v1
entity-id: product-optical-transceiver
kind: product
name-zh: 光收發模組
aliases:
- optical transceiver
- pluggable optics
summary: 在交換器或網卡埠完成電／光雙向轉換。選型要對齊主機介面、光路、距離、功耗與兩端相容性。
reviewed: '2026-11-24'
definition: 整合發射、接收與電介面的可插拔光通訊模組。
purpose: 用光纖連接交換器與網卡，或連接不同層級的交換器。
boundary: 本頁以資料中心內的 Ethernet 可插拔模組為主。長距離相干模組另有光路條件，CPO 的光引擎隨交換系統整合。
adoption-conditions:
- 兩端須對齊 Ethernet 光介面、傳輸速率、lane 配置、FEC、光纖及接頭。
- 核對主機平台支援的料號、埠模式、韌體、最大功耗與滿插散熱。
bottlenecks:
- 光路的接頭與配線損耗會占用 link budget，受到模組光功率與接收容限約束。
- 平行光路需要更多纖芯，波分光路增加模組內的合分波與測試要求。
substitution-limits:
- LPO 需合規的主機 SerDes 與端到端光電驗證。
- CPO 須按交換系統設計與維修方式評估，AEC 則須落在銅通道與兩端相容的範圍。
claims:
- id: electrical-optical-boundary
  statement: 光收發模組在主機電介面與光纖間完成雙向轉換。採用模組內 DSP 的設計可在模組內重定時，FEC 的位置仍依介面而定，例如 Cisco 的 VR8 和 DR8-2 例子由主機執行。
  confidence: well-supported
  conditions: [分別核對轉換功能、DSP 位置與 FEC 責任。]
  reviewed: '2026-11-24'
  evidence:
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: 第 12 頁 §§6.1–6.2
    read-scope: 已讀規格的光發送／接收方向。
    stance: supporting
    applicable-period: 100G-DR-LPO Revision 1.0
  - source-id: marvell-spica-gen2-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-spica-gen2-product-brief.pdf
    locator: Features、Description
    read-scope: 已讀 PAM4 DSP retimer、直接驅動與模組應用。
    stance: supporting
    applicable-period: MV-CD822 Product Brief，Revised 12/22
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: QDD-800G-VR8 與 QDD-8X100G-FR 產品段落
    read-scope: 已讀各料號的主機 FEC 與光路。
    stance: supporting
    applicable-period: 2026-09-21 更新版
- id: cisco-800g-media-and-power
  statement: Cisco 同系列 QSFP-DD800 料號的接頭、光纖、距離與模組最大功耗各有條件。QDD-800G-VR8 為 30 m OM3 或 50 m OM4／OM5，上限 15 W。QDD-8X100G-FR 的平行單模光路標示 2 km，上限 17 W。QDD-2X400G-FR4 為雙 400G 與兩個雙工 LC，各光路以四個波長傳輸，標示 2 km，上限 17 W。
  confidence: well-supported
  conditions:
  - VR8 的距離以產品段落與表 3／4 為主，表 5 的描述欄另有不一致。
  - 數字為指定型號的資料表上限，不構成同光路、同條件的實測功耗比較。
  reviewed: '2026-11-24'
  evidence:
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: 表 2–5、三個料號的產品說明與 Platform support
    read-scope: 已交叉核對速率、光纖、距離、波長、接頭與最大功耗，記錄矛盾處。
    stance: supporting
    applicable-period: 2026-09-21 更新版
- id: lpo-and-cpo-integration
  statement: 100G-DR-LPO 把數位訊號處理留在主機，搭配 100 Gb/s 每 lane 的線性可插拔光介面。Broadcom TH6-Davisson 則把光引擎與交換晶片置於共同封裝，用於改變交換系統內的電路與光路配置。
  confidence: well-supported
  conditions:
  - LPO 的 500 m 是本規格的單模光路範圍，須符合主機電通道與 RS-FEC 條件。
  - TH6 的 200 Gb/s 每 lane 是另一產品世代，不能直接套用到 100G-DR-LPO。
  reviewed: '2026-11-24'
  evidence:
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: 摘要、§6、§7.2–7.3
    read-scope: 已讀單模距離、主機 SerDes／FEC、模組收發與主機輸出測試條件。
    stance: supporting
    applicable-period: 100G-DR-LPO Revision 1.0，2025-03
  - source-id: broadcom-cpo-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024
    locator: Link Stability、Bandwidth Improvement and Interoperability
    read-scope: 已讀共同封裝與 200 Gb/s 每通道的廠商公告。
    stance: supporting
    applicable-period: TH6-Davisson，2025-10-08 公告
- id: short-copper-and-port-demand
  statement: 800G 可用主動銅纜服務合格的短距離直連。若新增連線超出銅纜相容距離且兩端維持可插拔光埠，通常每條新增光鏈路需要兩個光端。改用 breakout、LPO 或 CPO 時，模組與 DSP 的數量可能各自變動。
  confidence: inference
  conditions:
  - AEC 例子限 Arista E-D800-D800-xM 的直連料號及合格平台，不能用標稱 800G 推定跨廠牌相容。
  - 光端與模組的換算須依拓樸、breakout 組態及兩端的維修／備援配置。
  reviewed: '2026-11-24'
  evidence:
  - source-id: arista-800g-cables-qa
    url: https://www.arista.com/assets/data/pdf/Datasheets/Arista-800G_Optics_FAQ.pdf
    locator: 第 3 頁，800G Straight Through Active Electrical Cables
    read-scope: 已核對指定 QSFP-DD 直連料號的 1、2、3 m 選項。
    stance: supporting
    applicable-period: 2026-09，文件 04-0046-07，指定 800G AEC
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: QDD-8X100G-FR 產品段落
    read-scope: 已讀光端介面及 8×100G 與雙 400G 分接支援。
    stance: supporting
    applicable-period: 2026-09-21 更新版
  - source-id: broadcom-cpo-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024
    locator: Link Stability
    read-scope: 已讀交換晶片與光引擎共同封裝的配置，作為可插拔模組用量外推的反向條件。
    stance: counter
    applicable-period: TH6-Davisson，2025-10-08 公告
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: 摘要、§7.2
    read-scope: 已讀主機 DSP SerDes 條件，作為模組內 DSP 用量外推的反向條件。
    stance: counter
    applicable-period: 100G-DR-LPO Revision 1.0
gaps:
- status: not-obtained
  reason: 所讀 Cisco、Arista、LPO MSA 與 Broadcom 文件沒有同平台、同速率、同距離下的雙端功耗、安裝與維修成本，無法做整體成本排名。
- status: not-obtained
  reason: Cisco 表 5 的 VR8 描述出現 500 m，和同版產品段落及表 3／4 不一致。採購前應以目標料號與設備相容清單確認。
- status: not-public
  reason: 所讀 Cisco 料號資料表與 Spica Gen2 brief 未揭露彼此的供應關係、終端客戶或產品收入。
---

## 定義與用途

### 從電埠到光纖

交換晶片或網卡先將資料送到高速電介面。模組發射端驅動光源或調變器，把訊號送入光纖。另一端由檢光器及接收電路還原成電訊號，再交給主機。帶 DSP 的模組可在模組內等化、重定時或轉換 lane 配置。FEC 責任另看介面，Cisco 下列料號由主機執行。來源：[100G-DR-LPO §§6.1–6.2](https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf)、[Spica Gen2 brief](https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-spica-gen2-product-brief.pdf)、[Cisco 資料表](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html)。

資料中心內常見的閱讀起點是 [AI networking](/next?focus=application-ai-networking) 的伺服器到交換器、交換器到交換器光鏈路。以下案例適用資料中心內 Ethernet，跨機房相干傳輸及其他 scale-up 協定需另查其光路和介面。

## 採用條件與限制

### 同一個 800G 埠，可能需要不同光路

| Cisco 料號 | 光路與連接器 | 標示距離 | 模組最大功耗 |
|---|---|---|---|
| QDD-800G-VR8 | 800GBASE-VR8，8 對平行 MMF，雙 MPO-12。標稱 850 nm | OM3 30 m，OM4／OM5 50 m | 15 W |
| QDD-8X100G-FR | 800GBASE-DR8-2，8 對平行 SMF，雙 MPO-12 APC。每 lane 一個標稱 1310 nm 波長 | G.652 SMF 2 km。分接到 100G-DR 時上限 500 m | 17 W |
| QDD-2X400G-FR4 | 兩組 400GBASE-FR4，雙 duplex LC。每組用 1270／1290／1310／1330 nm 四個 CWDM 波長 | G.652 SMF 2 km | 17 W |

表格依 Cisco 2026-09-21 版產品說明與表 2–4。VR8 的表 5 描述另列 500 m，和其他段落及表格不一致。正式選型需確認設備支援、接頭端面及通道測試。上述功耗是資料表最大值。

**成本與驗證因素（inference）。** 平行單模使用較多纖芯，既有 MPO 配線可影響工程成本。四波長 FR4 每組只需一對光纖，模組內需合分波，還要驗證各波長的光功率與接收條件。距離須連同跳線、配線架與接頭的總插入損耗評估，表 5 提供兩個單模料號的預算例。QSFP-DD 外型相同也須核對雙端埠模式、分接支援與韌體。機櫃滿插時再用額定功耗核對風道與散熱。

### 路線比較

| 路線 | 適用前提 | 容易失效的假設 |
|---|---|---|
| 帶 DSP 的可插拔光模組 | 光介面、光纖及主機相容。故障可依設備流程換單顆模組 | 同為 800G 或同外型即互通。實際仍須核對對端介面與光路 |
| LPO | 仍可獨立插拔。100G-DR-LPO Rev 1.0 定義每 lane 100 Gb/s PAM4、單模最遠 500 m，主機須提供符合條件的 DSP SerDes 與 RS-FEC | 不能只拔掉模組內 DSP 就沿用原主機設計。§7.2 的電通道損耗上限為 16 dB，量測頻率 26.56 GHz，主機與模組還須通過端到端互通驗證 |
| CPO | 交換設備採用共同封裝的光引擎。TH6-Davisson 公告列示 200 Gb/s 每通道，屬該平台配置 | 可直接換同速率可插拔模組，或假設光源與光引擎的維修範圍相同。須確認平台的更換單位與備援流程 |
| 800G 主動電纜 | Arista E-D800-D800-xM 提供 1／2／3 m QSFP-DD 直連選項，適合兩端相容的短距離連接 | 將例示長度外推到其他平台或跨機櫃路由。須核對實際走線、彎折、埠模式與散熱 |

比較雙端耗電、成本與維修前，先對齊協定、速率、距離、埠密度、負載及環境。可插拔方案通常需計入兩顆模組和光纖，AEC 計入整條線纜，CPO 計入交換系統的光引擎與光源維護。上述文件未提供同條件的完整成本與功耗資料。來源：[LPO MSA 規格](https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf)、[Broadcom TH6-Davisson 公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)、[Arista 800G 線纜 Q&A](https://www.arista.com/assets/data/pdf/Datasheets/Arista-800G_Optics_FAQ.pdf)。

### 需求如何傳到模組與元件

1. **事實。** Cisco QDD-8X100G-FR 支援 800G 光鏈路及多種分接。Arista 的 QSFP-DD 直連 AEC 例子則只列 1–3 m。先用設備相容清單、實際走線與埠模式確認可行組合。
2. **Inference。** 若 GPU 叢集擴充帶來更多超出銅纜合格距離的 Ethernet 連線，且兩端採 DSP 型可插拔光模組，新增光鏈路會增加模組及其內部 DSP 的需求。追蹤交換器／網卡埠配置、合格模組料號、各路徑距離與平台驗證。
3. **反向條件。** 若僅提高單埠速率、沿用既有埠數，或用 breakout 重新配置，模組數未必隨總頻寬同比增加。短距離可能由 AEC 承接。LPO 仍有可插拔模組需求，但模組內 DSP 用量可能減少。CPO 若只在交換端導入，另一端仍可能使用可插拔模組。追蹤已採用的埠組態與兩端架構，再判斷實際曝險。

## 供應角色與公司

### 交付界線

- **成品模組。** Cisco 資料表列出可訂購模組料號、光纖接頭與主機相容性入口，示範採購成品時如何界定交付。[華星光](/next?focus=company-4979-two) 已有[光模組角色](/next?focus=role-optical-module)能力證據，公司頁分別記錄光引擎、次模組與相干模組。
- **模組內晶片。** [邁威爾 Marvell](/next?focus=company-mrvl) 的 Spica Gen2 MV-CD822 交付的是 8×100G PAM4 [光 DSP](/next?focus=product-optical-dsp)，供模組廠整合驅動、光元件與封裝。其型號 brief 支持晶片能力，未揭露上表 Cisco 料號的內部用料。
