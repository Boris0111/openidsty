---
schema-version: research-v1
entity-id: research-ai-networking-optical-electrical
kind: research
name-zh: "AI 網路光／電互連與需求傳導"
aliases:
- "800G 光電互連比較"
- "AI networking optical and copper"
summary: "以 800GbE scale-out 埠為例，比較 AEC、可插拔光模組、LPO 與 CPO，追到產品交付及公司能力。"
related-ids:
- "application-ai-networking"
- "segment-networking"
- "theme-cpo-silicon-photonics"
- "product-datacenter-network-adapter"
- "product-datacenter-switch"
- "product-ethernet-switch-asic"
- "product-active-electrical-cable"
- "product-optical-transceiver"
- "product-optical-dsp"
- "product-inp-laser-chip"
- "product-optical-epiwafer"
- "product-fiber-cable-assembly"
reviewed: "2026-11-24"
claims:
- id: ethernet-800g-media-options
  statement: "800GbE 可用多種合格光路、外型及線組；Credo SPAN 型錄列 3–7 m 直連，Cisco 的 QDD-2X400G-FR4 列 2 km 單模分接。100G-DR-LPO 把 DSP SerDes 與 FEC 放在相應主機端，須符合指定電與光條件。"
  confidence: well-supported
  conditions:
  - "只比較同拓樸、埠模式、目標速率與使用環境。同樣標示 800G 仍需確認能否互通。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 SPAN 800G OSFP／OSFP-RHS、3–7 m、外殼溫度及 QPRBS31。"
    stance: supporting
    applicable-period: "REV 100924"
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "表 2、表 3 與產品段落"
    read-scope: "已讀 800G／2×400G 模組選項與 2 km 單模例。"
    stance: supporting
    applicable-period: "2026-09-21 版"
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: "§§5–8、圖 3、表 12"
    read-scope: "已讀主機 RS-FEC、16 dB 傳輸限制與 SMF 0.5–500 m。"
    stance: supporting
    applicable-period: "100G-DR-LPO Rev 1.0"
- id: cpo-and-dci-boundaries
  statement: "TH6-Davisson 在交換端把光引擎移入共同封裝，公告配置含可更換 ELSFP。OIF 800ZR 規格則定義 80–120 km 放大型單跨 DWDM 的相干介面。"
  confidence: well-supported
  conditions:
  - "兩種產品的距離與維修依賴須各自核對。TH6-Davisson 內文列早期晶片送樣。800ZR IA 的距離不證明各廠料號已驗證。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: broadcom-cpo-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024
    locator: "Product Highlights、Availability"
    read-scope: "已讀 TH6-Davisson 共同封裝光引擎、每通道 200 Gb/s、可換 ELSFP 與 early-access 晶片。"
    stance: supporting
    applicable-period: "2025-10-08 公告"
  - source-id: oif-800zr-ia
    url: https://www.oiforum.com/wp-content/uploads/OIF-800ZR-01.0.pdf
    locator: "§1 Introduction、§2 800ZR Use Cases"
    read-scope: "已讀單跨 DWDM 距離與相干線側。"
    stance: supporting
    applicable-period: "OIF-800ZR-01.0，2024-10"
- id: network-port-upgrade-demand
  statement: "若 scale-out 已驗證的光埠增加並使用 DSP 可插拔模組，可能提高相應模組、DSP、光纖以及雷射／磊晶用量。實際傳導會因 AEC、LPO、CPO、光源路線及外購比重改變。"
  confidence: inference
  conditions:
  - "按啟用埠數與介質統計。須確認 lane、合格料號、維修及出貨，不從總頻寬推算具名收入。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀 64×800GbE、分接與交換 ASIC。"
    stance: supporting
    applicable-period: "E092023-AP-R01"
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "表 2、表 3 與產品段落"
    read-scope: "已讀 800G／2×400G 模組選項與 2 km 單模例。"
    stance: supporting
    applicable-period: "2026-09-21 版"
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 SPAN 800G OSFP／OSFP-RHS、3–7 m、外殼溫度及 QPRBS31。"
    stance: supporting
    applicable-period: "REV 100924"
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: "§§5–8、圖 3、表 12"
    read-scope: "已讀主機 RS-FEC、16 dB 傳輸限制與 SMF 0.5–500 m。"
    stance: supporting
    applicable-period: "100G-DR-LPO Rev 1.0"
  - source-id: broadcom-cpo-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024
    locator: "Product Highlights、Availability"
    read-scope: "已讀 TH6-Davisson 共同封裝光引擎、每通道 200 Gb/s、可換 ELSFP 與 early-access 晶片。"
    stance: supporting
    applicable-period: "2025-10-08 公告"
gaps:
- status: not-obtained
  reason: "未取得同部署兩端、介質及環境下的端到端 BER、功耗、故障停機時間與完整布建成本。"
- status: not-public
  reason: "各來源的產品能力或出貨階段未足以識別本案例的具名訂單或各公司料號收入。"
---

## 研究問題

同一場址把 scale-out 網路從 400GbE 升級到 800GbE，什麼會帶動線材、光模組與晶片需求？先從[AI 叢集網路](/next?focus=application-ai-networking)找到 NIC、交換器與兩端埠，再按距離、端口模式、可用的光路與機房維修策略判斷。以下是條件式案例，未採用任何真實資料中心的採購數字。

## 判斷與限制

### 先固定通訊域與線組

- **Scale-up** 服務同一緊耦合運算域。先確定端點協定、集體通訊與延遲要求。PCIe／CXL 板端通道與 Ethernet 線材的速率或距離不可互用。
- **Scale-out** 連接多台運算節點。比較同一 NIC 至 leaf 或 leaf 至 spine 的 Ethernet 埠模式與佈線，並核對 FEC、已驗證的上行比例與故障轉移。
- **跨機房** 須另查調變、光預算、加密、放大／波分及跨站流控。OIF 800ZR §1 的用途是 80–120 km 放大型單跨 DWDM，相干介面需搭配實際線路，不沿用機房內 DR／FR 距離。

- **DAC／[AEC](/next?focus=product-active-electrical-cable)**。被動 DAC 先查完整銅損耗；Credo 800G SPAN OSFP 直連 3–7 m，依料號及 CMIS。實際線長與銅損耗、走線半徑、兩端供電、FEC 及外殼溫度。
- **DSP [可插拔光模組](/next?focus=product-optical-transceiver)**。Cisco QDD-2X400G-FR4 為 2 km 單模例；Credo 800G 2×DR4 以平行 SMF 500 m 為例，端面與光路不同。對齊端點分接模式、率及 FEC；合計兩顆模組、光纖及配線、換件工時。
- **LPO**。MSA 100G-DR-LPO Rev 1.0 為 100G/lane、0.5–500 m SMF，主機端至模組連接器限制 16 dB＠26.56 GHz，FEC 在主機。查主機 SerDes 及 RS-FEC、整個電通道、雙端互通及診斷。若端點未達規格，保留 DSP 方案。
- **CPO**。TH6-Davisson 是 200 Gb/s per channel 的交換端共同封裝光引擎例，ELSFP 光源可現場更換。先核對光引擎、遠端網卡與光路相容，再查光纖配線、交換設備換件範圍、服務備援和故障時間。

交付比較以同一對端點和同一網路組態為準。即使兩種路線同寫 800G，FEC、光路與分接模式也可能不同。目前缺同環境、同流量負載的雙端功耗、誤碼與維修成本。型錄的最大功耗與不同環境的典型量測應分開讀取。

### 案例：從啟用埠數追到供應角色

**1. 端點與交換容量**

- **事實**。智邦 AS9817-64O 有 64×800G OSFP800 與多種 breakout；[主機 NIC](/next?focus=product-datacenter-network-adapter) 的單埠 800G、雙 400G 與 IB 須按料號辨認。
- **Inference**。在節點數、上行比例上升且要原生 800GbE 時，新系統需求可能增加。若以每埠更高頻寬整併、減少交換層或分接給原端點，箱數與實體埠可能下降。
- **後續可核對**。核對機型、上下行 port map、NIC OPN／韌體及驗證通過的埠。

**2. 介質與實際佈線**

- **事實**。SPAN 的 3–7 m 限指定 OSFP AEC，FR4 與 100G-DR-LPO 各有光、電條件。
- **Inference**。若新增的合格埠距離超過銅線料號範圍或需配線架，光埠占比可能提高。若改用相鄰機架、DAC 或 AEC，新增模組數下降。
- **後續可核對**。看實際連線長度分布、介質表、光纖插損、線組料號與埠互通結果。

**3. 光埠內的設計變化**

- **事實**。LPO 把訊號處理移到主機，CPO 把光引擎放在交換封裝；EML 或 CW 光源有各自用途。
- **Inference**。若上線的光埠增加且沿用 DSP 可插拔，模組與 DSP 用量可能增加。換用 LPO／CPO 或把多條 lane 整併後，模組及 DSP 顆數可能少於原估；CW 與 EML 的占比也取決於平台設計。
- **後續可核對**。查[DSP](/next?focus=product-optical-dsp)、[雷射](/next?focus=product-inp-laser-chip)與[磊晶](/next?focus=product-optical-epiwafer)所支援的 lane、光源與主機驗證。

**4. 公司能力與實際曝險**

- **事實**。[智邦](/next?focus=company-2345-tw)為交換整機，[博通](/next?focus=company-avgo)與[邁威爾](/next?focus=company-mrvl)有晶片交付證據，[Credo](/next?focus=company-crdo)有線組與光模組；[華星光](/next?focus=company-4979-two)交付晶粒／光引擎及相干模組，[聯亞](/next?focus=company-3081-two)供應磊晶。
- **Inference**。需證明所採用的型號、通過驗證、採購與交付。若出貨結構不同、客戶內製磊晶或沒有取得料號，產業規格上升未必形成該公司營收。
- **後續可核對**。回到各公司產品主張、資料表、量產公告及可核對的具名交易；估算時把整機、晶片與外購材料分開。

作為算例，32 條 400GbE 升為 16 條 800GbE，在忽略協定開銷及備援時，兩者標稱容量同為 12.8 Tb/s，實體鏈路數減半。若新增 32 條 800GbE 並採兩端各一顆可插拔模組，才會新增 64 個模組位置。是否買足並出貨仍需通過埠配置、備品率及光路驗證，不能只看標稱頻寬。
