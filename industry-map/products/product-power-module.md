---
schema-version: research-v1
entity-id: product-power-module
kind: product
name-zh: "高密度電源模組"
aliases:
- "power module"
- "DC/DC module"
- "point of load"
summary: "在單一封裝或子組件整合電力轉換電路的模組。"
definition: "在單一封裝或子組件整合電力轉換電路的模組。"
purpose: "在有限板空間提供中間端電壓或在近負載處提供大電流。"
boundary: "整合範圍依料號，與單顆 PWM controller、單獨開關元件及機櫃 AC/DC 區分。"
adoption-conditions:
- "對齊輸入、輸出、控制、瞬態與環境降額。"
bottlenecks:
- "模組熱密度、堆疊高度與板級迴路阻抗。"
substitution-limits:
- "只在同一轉換段及相同保護、熱條件下比較。"
reviewed: "2026-11-24"
claims:
- id: module-current-and-integration
  statement: "MPS MPM3698 整合雙迴路控制、三組 MOSFET 與電感；三相並聯時 120 A 峰值或 90 A 連續。"
  confidence: well-supported
  conditions:
  - "每相 40 A 峰值、30 A 連續；平台仍依熱、輸入／輸出電壓及保護條件降額。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: mps-mpm3698-datasheet
    url: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MPM3698GBH/document_id/11450/
    locator: "Operation、Recommended Operating Conditions、Protection Features"
    read-scope: "查三相連續／峰值、控制／MOSFET／電感整合以及保護。"
    stance: supporting
    applicable-period: "MPM3698GBH datasheet"
- id: module-conversion-position
  statement: "Vicor 的 95 A VTM 案例以 1/24 固定比率做近負載轉換，配合上游 PRM；台達 RBC 的 40–60 V 至 12 V 則形成中間端電源。"
  confidence: well-supported
  conditions:
  - "VTM 舊料號標註 NRND。中間端、調節端和固定變比端的電流額定不可直接互比。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vicor-vtm-095ba0-datasheet
    url: https://www.vicorpower.com/documents/datasheets/VTM48K_020_095BA0.pdf
    locator: "p.1 Features & Benefits／Product Ratings"
    read-scope: "標稱 43.2 V → 1.8 V、K=1/24、95 A nominal，分離 PRM；封面 NRND。"
    stance: supporting
    applicable-period: "Rev.1.5，2019-10"
  - source-id: delta-rbc-ubc-ai-converters
    url: https://brandnews.deltaww.com/en/BrandCircleDetail/12476
    locator: "RBC／UBC 產品段落"
    read-scope: "核對 RBC 40–60 V 到 12 V，UBC 再搭配電壓調節器。"
    stance: supporting
    applicable-period: "2023-10"
- id: module-design-demand
  statement: "若板端可用面積減少、低壓大電流走線損失升高，具合格的近負載模組可能增加採用。"
  confidence: inference
  conditions:
  - "散熱、成本或板上彈性不足時，客戶可保留相容的分立方案；同一功率也可由單顆更大模組供應。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: mps-mpm3698-datasheet
    url: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MPM3698GBH/document_id/11450/
    locator: "Operation、Recommended Operating Conditions、Protection Features"
    read-scope: "查三相連續／峰值、控制／MOSFET／電感整合以及保護。"
    stance: supporting
    applicable-period: "MPM3698GBH datasheet"
  - source-id: vicor-vtm-095ba0-datasheet
    url: https://www.vicorpower.com/documents/datasheets/VTM48K_020_095BA0.pdf
    locator: "p.1 Features & Benefits／Product Ratings"
    read-scope: "標稱 43.2 V → 1.8 V、K=1/24、95 A nominal，分離 PRM；封面 NRND。"
    stance: supporting
    applicable-period: "Rev.1.5，2019-10"
gaps:
- status: not-obtained
  reason: "未取得同一核心負載下的總板端效率、相同冷卻及單機成本。"
- status: not-public
  reason: "來源未揭露指定加速器採用、客戶、料號出貨或收入。"
---

## 定義與用途

從[電源架](/next?focus=product-power-shelf-psu)的低壓 DC 到核心供電可採多段轉換。整合模組可置於中間匯流排或 point of load；是否內建控制、功率開關和電感依料號。靠近負載可縮短低壓大電流路徑。

## 規格與成本

MPS MPM3698 三相併聯的規格為 120 A 峰值、90 A 連續，雙 rail 模式又不同。Vicor VTM48KP020T095BA0 是 43.2 V 至 1.8 V、95 A 標稱的舊例，採固定變比，需加上 PRM 評估。選型按實際輸入、冷卻、機板高度、瞬態與過流／過溫保護核算。

## 採用條件與限制

多相分立方案可依空間自行放置功率級與磁件。整合方案簡化部分佈局，但仍要核對輸入紋波、電容、負載步階和散熱。12 V 中間端 RBC 與 near-load 輸出服務不同位置，替代需重新分配電力轉換。

## 供應角色與公司

[板端電源轉換](/next?focus=role-board-power-conversion)下，[芯源系統](/next?focus=company-mpwr)供應 MPM3698 含控制／磁件模組；[Vicor](/next?focus=company-vicr)供應 PRM／VTM 方案，其中資料表案例標 NRND。[台達電](/next?focus=company-delta-electronics)公布 RBC 系列 40–60 V → 12 V 方案。比較前固定轉換段。

## 需求如何傳導

推論：單一加速器功率提升且板面受限時，近負載低阻抗方案的採用可能提升；若成本、熱阻或高度受限，也可改用分立或重新分配轉換位置。追蹤採用的平台設計、合格料號和散熱實測。
