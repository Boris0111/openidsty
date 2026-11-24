---
schema-version: research-v1
entity-id: product-fiber-cable-assembly
kind: product
name-zh: "資料中心光纖連接組件"
aliases:
- "MPO cable assembly"
- "MTP trunk"
- "光纖跳線"
summary: "用已端接的光纖跳線、主幹或分接線組連接收發器與配線架。"
definition: "預先裝妥接頭與光纖的被動組件，依指定纖芯配置、極性與損耗級別交付。"
purpose: "在資料中心傳遞光訊號，讓模組與另一端或配線盤對接。"
boundary: "此產品含預端接跳線、主幹、分接組件。裸纖、單獨接頭、光模組及內部光引擎的光纖耦合另分。"
adoption-conditions:
- "核對單／多模、芯數分佈、MPO／LC、導引針、APC／UPC、極性與實際鏈路預算。"
bottlenecks:
- "端面污染或偏移、組件插入損耗、彎曲及多處配接會消耗光預算。"
substitution-limits:
- "同是 MPO 也需核對芯數排列、導引針與端面。平行光與 WDM 要配相應模組。"
reviewed: "2026-11-24"
claims:
- id: fiber-passive-interconnect
  statement: "MPO 主幹或跳線以多纖芯接頭配接平行光埠，MTP 至 LC 組件可把主幹的纖芯分到 LC 跳線。Cisco QDD-8X100G-FR 用平行單模與 MPO-12 APC，QDD-2X400G-FR4 用兩組雙工 LC，並在模組內做 WDM。"
  confidence: well-supported
  conditions:
  - "以指定模組的纖芯、接頭與光規格選線。Cisco 線材通用註記與 VR8 個別段對 APC 的描述有出入，選 VR8 料號需向平台確認。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: corning-aen163-edge8-loss
    url: https://www.corning.com/catalog/coc/documents/application-engineering-notes/AEN163.pdf
    locator: "p.3 Table 3 與 MTP-LC module 範例"
    read-scope: "已讀如何以指定的成對接頭計算插入損耗；不沿用整份 FICON 的系統預算。"
    stance: supporting
    applicable-period: "AEN163 Rev 1，2020-04-21"
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "表 2、QDD-8X100G-FR 與 QDD-2X400G-FR4 段、表 5"
    read-scope: "已讀同總體埠速下的平行單模及雙 LC WDM 光路。"
    stance: supporting
    applicable-period: "2026-09-21 版"
- id: fiber-budget-and-mechanical
  statement: "Corning GE7E796GLZDDU030M 是 30 m、96 芯的 OS2 主幹，每端有多組 8 芯 pinned MTP，Type B，安裝和運轉期的最小彎曲半徑分別為 178.5 與 59.5 mm。Amphenol 公開 MPO 組件含 8／12／24 芯及不同損耗級別。"
  confidence: well-supported
  conditions:
  - "單一 SKU 的機構限制不能套用其他線徑。單對接頭損耗與工廠整線測試值分開使用。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: corning-edge8-ge7e796glzddu030m
    url: https://ecatalog.corning.com/optical-communications/EMEA/en/Fiber-Optic-Cable-Assemblies/Indoor-Cable-Assemblies/Multifiber-Indoor-Cable-Assemblies/EDGE8%C2%AE-MTP%C2%AE-Trunk/p/GE7E796GLZDDU030M
    locator: "Design、Mechanical Specifications、Connector A/B"
    read-scope: "已讀 96 芯 OS2、30 m、Type B、安裝與使用最小彎曲半徑。"
    stance: supporting
    applicable-period: "GE7E796GLZDDU030M，2026-11-24 查閱"
  - source-id: aph-mpo-cable-assemblies
    url: https://www.amphenol-fop.com/indoor-cable-assemblies/mpo-cable-assemblies
    locator: "Features、Specifications"
    read-scope: "已讀 8／12／24 芯、A/B/C 極性、插入與回波損耗型錄。"
    stance: supporting
    applicable-period: "MPO Cable Assemblies，2026-11-24 查閱"
  - source-id: corning-aen163-edge8-loss
    url: https://www.corning.com/catalog/coc/documents/application-engineering-notes/AEN163.pdf
    locator: "p.3 Table 3 與 MTP-LC module 範例"
    read-scope: "已讀如何以指定的成對接頭計算插入損耗；不沿用整份 FICON 的系統預算。"
    stance: supporting
    applicable-period: "AEN163 Rev 1，2020-04-21"
- id: fiber-company-deliveries
  statement: "Amphenol Fiber Optic Products 列出完整 MPO 線組；貿聯透過子公司取得 XFS 的跳線、主幹型多芯纜與高密度 MTP／MPO 組件能力，貿聯產品頁另列 MPO／APC 光纜。SENKO 的產品證據支持獨立 MPO 接頭。"
  confidence: well-supported
  conditions:
  - "公司目錄範圍與料號級採用分開，XFS 仍是不同法律主體。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: aph-mpo-cable-assemblies
    url: https://www.amphenol-fop.com/indoor-cable-assemblies/mpo-cable-assemblies
    locator: "Features、Specifications"
    read-scope: "已讀 8／12／24 芯、A/B/C 極性、插入與回波損耗型錄。"
    stance: supporting
    applicable-period: "MPO Cable Assemblies，2026-11-24 查閱"
  - source-id: bizlink-xfs-optical-acquisition
    url: https://www.bizlinktech.com/news/bizlink-completes-acquisition-of-xfs-communications-inc-advancing-optical-interconnect-leadership-for-ai-and-data-center-applications
    locator: "公告開頭與 XFS 產品段落"
    read-scope: "已讀 3665、收購主體和 XFS 的跳線及高密度組件範圍。"
    stance: supporting
    applicable-period: "2026-01-05，收購完成公告"
  - source-id: bizlink-mpo-assemblies
    url: https://www.bizlinktech.com/product-categories/mpo-connectors
    locator: "All Products"
    read-scope: "已讀 MPO／APC Optical Cable 和 PPB Connector 名稱。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
  - source-id: senko-mpo-plus-standard
    url: https://www.senko.com/product/mpo-plus-standard-connector/
    locator: "Key Features／FAQ"
    read-scope: "已讀 guide pin、MPO 多芯 ferrule 與殼體規格。"
    stance: supporting
    applicable-period: "MPO-PLUS Standard Connector，2026-11-24 查閱"
- id: fiber-port-to-assembly-demand
  statement: "若新增許多採平行光的埠，可能增加已端接多芯組件需求。若改用 WDM、沿用既有主幹或改為短距 AEC，纖芯與線組需求可能下降。"
  confidence: inference
  conditions:
  - "追蹤已核准的收發器與配線表、前後端纖芯用量，以及插入損耗及極性驗收結果。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "表 2、QDD-8X100G-FR 與 QDD-2X400G-FR4 段、表 5"
    read-scope: "已讀同總體埠速下的平行單模及雙 LC WDM 光路。"
    stance: supporting
    applicable-period: "2026-09-21 版"
  - source-id: corning-edge8-ge7e796glzddu030m
    url: https://ecatalog.corning.com/optical-communications/EMEA/en/Fiber-Optic-Cable-Assemblies/Indoor-Cable-Assemblies/Multifiber-Indoor-Cable-Assemblies/EDGE8%C2%AE-MTP%C2%AE-Trunk/p/GE7E796GLZDDU030M
    locator: "Design、Mechanical Specifications、Connector A/B"
    read-scope: "已讀 96 芯 OS2、30 m、Type B、安裝與使用最小彎曲半徑。"
    stance: supporting
    applicable-period: "GE7E796GLZDDU030M，2026-11-24 查閱"
gaps:
- status: not-public
  reason: "所讀型錄和公告未揭露特定客戶、組件收入或平台資格。"
- status: not-obtained
  reason: "未取得貿聯與安費諾的同長度、同介面、同測試方法的整線插損、工時及價格。"
---

## 定義與用途

光收發器把脈衝光送進已端接的跳線；需要集中配線時，配線架與主幹可把多條光路集中布設。MPO 用導引針與 ferrule 對準多根纖芯，LC 雙工則把發送與接收安排在一對纖芯。兩端的極性必須讓發射對應接收。MTP 是 MPO 介面的品牌族，配對仍需核對導引針、纖芯排列、凸鍵及端面。

## 採用條件與限制

### 線組成本取決於安裝和驗收

用同一波長加總光纖長度損耗、各配接面與分接組件的插入損耗，再拿結果對照[光收發模組](/next?focus=product-optical-transceiver)允許的最大通道損耗。Corning 主幹 GE7E796GLZDDU030M 各接頭表列 0.35 dB，註明工廠預端接件透過兩對接頭量測；依 AEN163 第 3 頁的元件方法估算前，應確認是否已包含整線測試的配對損耗。實際驗收需測整條路徑，包含面板、跳線、端面清潔及極性。該主幹為 30 m、96 芯 OS2，直徑約 11.9 mm，安裝時需 178.5 mm 彎曲半徑；配線盤空間與牽引工序也會影響安裝成本。

### 先對照模組，才能換組件

Cisco QDD-8X100G-FR 用平行單模光與 MPO-12 APC，QDD-2X400G-FR4 在模組內把四個波長多工到雙工光纖，每個 400G 分支用一組 LC。兩款的標稱聚合容量接近，佈線芯數、端面與對端光路仍不同。選用 MPO 的 VR8 時，Cisco 2026-09 型錄的一般線材註記與個別 VR8 段的 APC 標示有分歧，採購前須核對平台配線。若替換同種線組，先對照光纖等級、端面、極性、完整通道損耗與機械規格。

## 供應角色與公司

屬於[資料中心被動光纖互連](/next?focus=role-passive-fiber-connectivity)。[安費諾](/next?focus=company-aph)有可選芯數與極性的 MPO 完整線組，[貿聯](/next?focus=company-3665-tw)的團隊透過 XFS 供應光纖跳線及 MTP／MPO 組件，另有 MPO／APC 光纜產品入口。Corning EDGE8 是主幹和配線系統的技術參照。SENKO MPO-PLUS 型錄的標準連接器是端接零件，採購時與完整線組分別核對。

### 需求如何傳到光纖組件

**Inference。** 當多芯平行光連線增加且既有配線芯數不足，才會增加多芯跳線、主幹及分接需求。縮短鏈路改用銅，轉 WDM 或沿用已達標的光纖主幹都可能抵銷新購置量。應按光埠與布線表追蹤每條鏈路的纖芯、接頭對數、配線位置和通過驗收的組件。
