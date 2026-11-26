---
schema-version: research-v1
entity-id: product-substrate-patterning-lithography
kind: product
name-zh: "載板線路曝光設備"
aliases: ["panel lithography","direct imaging","IC substrate patterning"]
summary: "在 IC 載板光阻上定義導線開口的曝光設備。"
definition: "在 IC 載板光阻上定義導線開口的曝光設備。"
purpose: "以合格套位與線寬距支援後段圖形電鍍。"
boundary: "曝光、光阻、濕製程和成品載板各擔任不同交付。"
adoption-conditions: ["核對光阻、面板翹曲、對位、焦深及鍍後線路。"]
bottlenecks: ["面板變形、缺陷尾端、下游鍍層均勻與合格面積。"]
substitution-limits: ["直接成像或光罩投影依同操作窗口比較。"]
reviewed: '2026-11-24'
claims:
- id: jetstep-x500-substrate-exposure
  statement: "Onto 的 JetStep X500 面板曝光設備適用於先進 IC 載板及有機 laminate 面板，支援板變形補償。"
  confidence: well-supported
  conditions: ["該產品交付為曝光設備。解像、焦深、套位及吞吐量以實配基板與光阻驗證。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: onto-jetstep-x500
    url: https://ontoinnovation.com/products/jetstep-x500/
    locator: "Overview、Key Features"
    read-scope: "查 AICS 適用範圍及面板尺寸／厚度／翹曲考量。"
    stance: supporting
    applicable-period: "X500 產品頁"
  - source-id: onto-fy2025-10k
    url: https://www.sec.gov/Archives/edgar/data/704532/000119312526066937/onto-20260103.htm
    locator: "Item 1 Our Products、封面"
    read-scope: "核對封裝光刻與股票身分。"
    stance: supporting
    applicable-period: "FY2025 10-K（截至 2026-01-03）"
- id: sap-line-formation-interfaces
  statement: "SAP 將表面處理／種子層、光阻曝光顯影及圖形鍍銅分開。SCREEN 列 Ledia Qs 5/5 μm 級距；Atotech G-Plate 帶去膠與化學銅，Qnity Riston 屬曝光光阻。"
  confidence: well-supported
  conditions: ["設備成像與填鍍後的線寬距不可互換評價；相關型錄須依實際用料及量測。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: screen-ir-day-2025-lithography
    url: https://hdjp-corporateweb-files.screen.co.jp/7417/6603/8973/20251216_Mtg_E.pdf
    locator: "PE 設備品項／Ledia Qs"
    read-scope: "確認 5/5 μm 產品列。"
    stance: supporting
    applicable-period: "2025-12-16 IR Day"
  - source-id: atotech-gplate-ultrafine
    url: https://www.atotech.com/products/electronics/electronics-equipment/
    locator: "G-Plate advanced substrate platform"
    read-scope: "查去膠與無電鍍銅工序。"
    stance: supporting
    applicable-period: "查核日產品頁"
  - source-id: qnity-ic-substrate-materials
    url: https://www.qnityelectronics.com/ic-substrates.html
    locator: "IC Substrates、Photoresists"
    read-scope: "查 Riston dry film 耗材。"
    stance: supporting
    applicable-period: "查核日型錄"
- id: patterning-demand-by-overlay
  statement: "載板變大與 L/S 縮小可增加面板變形補償及套位量測需求。"
  confidence: inference
  conditions: ["若可用更快的曝光策略、面板多機併行或設計減層，可能抵銷新增設備；另查鍍銅而非把曝光當唯一瓶頸。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: onto-jetstep-x500
    url: https://ontoinnovation.com/products/jetstep-x500/
    locator: "Panel distortion compensation"
    read-scope: "查光刻取像與補償。"
    stance: supporting
    applicable-period: "X500"
  - source-id: screen-ledia-qs-package
    url: https://www.screen.co.jp/pe/en/info/PE240603E
    locator: "Ledia Qs announcement"
    read-scope: "查直接成像與精度位置。"
    stance: supporting
    applicable-period: "2024-06"
gaps:
- status: not-obtained
  reason: "未取得同光阻、面板與鍍後 L/S 的有效產速、良率及成本。"
- status: not-public
  reason: "設備案場、批次驗收、產品收入未公開。"
---

## 定義與用途

典型 SAP 先處理膜與微孔，敷薄銅種子後貼光阻、曝光及顯影，在開口鍍銅，剝除光阻並去除剩餘種子層。電性與檢驗需看整條線。

## 規格與成本

X500 針對面板厚度與翹曲補償。SCREEN Ledia Qs 公告為載板直接成像，IR 列 5/5 μm。對照同面板和光阻下的套位、焦深、曝光圖形與鍍銅後尺寸，另計光罩、維護和工時。

## 採用條件與限制

多點變形補償的直寫與帶光罩的面板曝光可依工藝評估，需相同光阻、圖案密度、面板及驗收；清潔、種子層與鍍層也可限制最終 L/S。

## 供應角色與公司

[Onto Innovation](/next?focus=company-onto)提供 JetStep X500；SCREEN PE 提供 Ledia Qs。Atotech G-Plate 做去膠與鍍銅，Qnity 供光阻與化學品，台灣志聖公開的對準、防焊、軟板與壓膜是不同工序。

## 需求如何傳導

推論：板尺寸和微縮可增補償／曝光投入，仍要看瓶頸是否在濕製程、缺陷或機台可用率。追蹤合格面板數、線寬距、套位與每小時產出。
