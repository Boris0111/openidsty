---
schema-version: research-v1
entity-id: application-chip-manufacturing
kind: application
name-zh: 晶圓製造
aliases:
- wafer fabrication
summary: 依設計製造晶圓，並由設備與材料支撐製程。
question: 晶圓從材料到完成晶片，要經過哪些設備與材料？
reviewed: '2026-10-18'
definition: 依設計製造晶圓，並由設備與材料支撐製程。
purpose: 把代工、設備與材料分成可替換的供應角色，避免用同屬「製造」就互相比較。
boundary: 先進邏輯、成熟與特殊製程代工分開；設備依微影、塗佈顯影、沉積蝕刻、濕製程與製程控制分工；材料依矽晶圓、光阻、氣體與污染控制分類。
adoption-conditions:
- 設計規則、PDK、IP 與製程版本需匹配
- 機台與材料須完成指定製程的安裝與資格認證
bottlenecks:
- 製程爬坡、設備節拍與材料批次穩定性共同限制可交付良品
substitution-limits:
- 不同廠商節點名稱不等於相同性能
- 不同設備與材料類別不互替
flow-steps:
- label: 材料
  note: 矽晶圓、光阻、特殊氣體與過濾純化材料
  products: [product-silicon-wafer, product-photoresist, product-specialty-gas, product-filtration-purification]
- label: 微影
  note: 塗佈顯影與曝光定義電路圖形
  products: [product-coater-developer, product-lithography-system]
- label: 沉積、蝕刻與清洗
  note: 長出並蝕刻薄膜，再以濕製程清洗
  products: [product-deposition-etch-tool, product-wet-process-tool]
- label: 量測檢測
  note: 量測線寬與缺陷，控制良率
  products: [product-inspection-metrology]
- label: 代工產出
  note: 先進邏輯與成熟、特殊製程代工交付晶圓
  products: [product-advanced-logic-wafer, product-mature-specialty-wafer]
claims: []
gaps:
- status: not-researched
  reason: 已有 1 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

依設計製造晶圓，並由設備與材料支撐製程。把代工、設備與材料分成可替換的供應角色，避免用同屬「製造」就互相比較。對應既有環節：[晶圓代工](/next?focus=segment-foundry)、[半導體設備](/next?focus=segment-equipment)、[半導體材料](/next?focus=segment-materials)。

可比較的供應角色：[先進邏輯代工](/next?focus=role-advanced-logic-foundry)、[成熟與特殊製程代工](/next?focus=role-mature-specialty-foundry)、[微影曝光](/next?focus=role-lithography)、[塗佈與顯影](/next?focus=role-lithography-track)、[沉積與蝕刻](/next?focus=role-deposition-etch)、[量測與檢測](/next?focus=role-process-control)、[濕製程設備](/next?focus=role-wet-process)、[矽晶圓](/next?focus=role-silicon-wafer)、[光阻材料](/next?focus=role-photoresist)、[污染控制與純化](/next?focus=role-contamination-control)、[特殊氣體](/next?focus=role-specialty-gas)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
