---
schema-version: research-v1
entity-id: product-datacenter-switch
kind: product
name-zh: "資料中心交換器"
aliases:
- "network switch"
summary: "把 ASIC、面板埠、管理軟體、機箱、供電與散熱整合成可部署的乙太網路交換器。"
definition: "依機房拓樸規劃埠、網管及電熱設計，搭載 Ethernet 交換 ASIC 的系統。"
purpose: "在資料中心連接 NIC、leaf 與 spine；依平台服務不同運算或存取網路。"
boundary: "整機可接入線組或光模組。ASIC 能力、伺服器 NIC、端點光模組與跨站傳輸均須各自驗證。"
adoption-conditions:
- "先核對面板埠型與上／下行配置、可用 breakout、NOS 與管理需求，再驗證電源、滿載熱與維修方式。"
bottlenecks:
- "實際埠密度、配線管理、光電功耗、風道、軟體與互通可能限制可用交換容量。"
substitution-limits:
- "不同 OSFP／QSFP-DD 或 NOS／光電架構的同容量系統，須重新驗證配線、管理及設備維修。"
reviewed: "2026-11-24"
claims:
- id: switch-system-accton-64o
  statement: "智邦 AS9817-64O 使用 Broadcom BCM78900（Tomahawk 5）並將 51.2 Tb/s 晶片整合到 2RU 機箱、64×800GbE OSFP800、ONIE、冗餘電源與風扇。"
  confidence: well-supported
  conditions:
  - "限 E092023-AP-R01。2×400／4×200／8×100 分接仍需符合已裝 NOS、模組和對端。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀前面板 OSFP800、breakout、BCM78900、ONIE 與電熱機構。"
    stance: supporting
    applicable-period: "AS9817-64O，E092023-AP-R01"
- id: switch-system-spec-conditions
  statement: "Arista 7060X6-64PE／-64PE-B 是 64×800GbE OSFP 及 EOS 的 2RU 系統。Arista 的典型功耗條件為 25 °C、50% 負載、DAC；最大功耗條件採 46 °C、滿載及高功率光模組。"
  confidence: well-supported
  conditions:
  - "同埠數仍需核對全部邏輯介面上限、媒介與電熱。廠商的 PSU 額定不可與實測整機功耗比較。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: arista-7060x6-datasheet
    url: https://www.arista.com/assets/data/pdf/Datasheets/7060X6-Datasheet.pdf
    locator: "Model Overview、Arista EOS、Technical Specifications 腳註"
    read-scope: "已讀 -64PE／-64PE-B 埠數差異及功耗條件。"
    stance: supporting
    applicable-period: "7060X6，2025-06-24，04-0053-08"
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀前面板 OSFP800、breakout、BCM78900、ONIE 與電熱機構。"
    stance: supporting
    applicable-period: "AS9817-64O，E092023-AP-R01"
- id: switch-system-design-demand
  statement: "當新平台有更多合格的 800G leaf／spine 連線，整機需求取決於每台可用埠數、上行與備援比例及布線限制。"
  confidence: inference
  conditions:
  - "若同箱提供更多合格埠、拓樸減少一層或使用 breakout，機箱數未必與總頻寬同步。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀前面板 OSFP800、breakout、BCM78900、ONIE 與電熱機構。"
    stance: supporting
    applicable-period: "AS9817-64O，E092023-AP-R01"
  - source-id: arista-7060x6-datasheet
    url: https://www.arista.com/assets/data/pdf/Datasheets/7060X6-Datasheet.pdf
    locator: "Model Overview、Arista EOS、Technical Specifications 腳註"
    read-scope: "已讀 -64PE／-64PE-B 埠數差異及功耗條件。"
    stance: supporting
    applicable-period: "7060X6，2025-06-24，04-0053-08"
gaps:
- status: not-obtained
  reason: "未取得 AS9817-64O 與 7060X6-64PE 在相同負載、封包、風道、溫度、NOS 功能及光電料號下的耗電、延遲、散熱與價格。"
- status: not-public
  reason: "兩份型錄未揭露具名終端客戶、實際採用台數或單型號收入。"
---

## 定義與用途

機房內 leaf 接伺服器 NIC，有的放在機櫃頂端（ToR）；spine 接各 leaf 的上行，提供跨架傳輸。交換器提供面板接頭，透過[銅線組](/next?focus=product-active-electrical-cable)或[光收發模組](/next?focus=product-optical-transceiver)構成實體連線。包在機箱內的[交換 ASIC](/next?focus=product-ethernet-switch-asic)決定可支援的轉送能力，再由面板佈局、NOS、散熱及電源實現。以智邦 AS9817-64O 為例，資料表從晶片到實際面板列出 BCM78900、64 個 800GbE 埠、機構、電源與 NOS 安裝環境。

## 採用條件與限制

### 同一埠數還要對照 NOS 和電熱條件

- **智邦 AS9817-64O，E092023-AP-R01**。2RU、64×800G OSFP800、前進後出；機型附 ONIE，支援安裝相容 NOS。搭配合格 NOS、分接型態與透過該 NOS 可用的管理功能。
- **Arista 7060X6-64PE，04-0053-08**。2RU、64×800G OSFP、Arista EOS；同家族 -64PE-B 的邏輯介面上限另列。需要的 EOS 功能、合格模組、輸入電壓及風向均按組態核對。

先以實際 uplink 與 downlink 配置盤點可用埠，再驗證收發器、FEC、拆分與遠端 NIC 的互通。智邦資料表的 3000 W 是 PSU 額定，不能當整機負載。Arista 的典型功耗用 25 °C／50% 負載／DAC，最大值用 46 °C／滿載／高功率光模組。比較成本和冷卻前，需統一傳輸介質、負載與進風條件，並計入軟體授權、備品與操作。

### 依用途選整機

上述高密度機房機型可依型錄規劃為 leaf／spine，屬 scale-out 的系統例。若要放入緊耦合 scale-up，性能需包含端點協定、同層流控、尾端延遲與拓樸。若要跨機房，需另查距離、加密、光傳輸、壅塞與故障轉移設計。兩站加總交換容量無法描述可用的跨站速率。機房內 CPO 系統把光引擎移到 ASIC 封裝附近，選型時另核光源、裝機及現場更換範圍。

## 供應角色與公司

屬於[資料中心交換器系統](/next?focus=role-switch-system)。[智邦](/next?focus=company-2345-tw)的 AS9817-64O 是布建交換器硬體與安裝環境的可查產品。Arista 7060X6-64PE 是同埠數的交換器及 EOS 例，軟體、部署與維護條件需要比對。ASIC、交換器硬體、NOS、端點互通與站點交付可能分由不同供應者負責。型錄支持實際整機設計，未揭露下游採購量或收入。

### 需求如何傳到整機

**Inference。** 伺服器增加、提高上行容量或增加備援，若超出合格交換器的可用埠數，可能增加整機需求。相同端點也可能用更高密度的機箱整併，或由上行佈線與電熱空間限制新增埠。追蹤拓樸每層的上／下行比例、NOS release、合格介質與同時上線的埠數，才能判斷硬體增量。
