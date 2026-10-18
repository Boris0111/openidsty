---
schema-version: research-v1
entity-id: application-chip-manufacturing
kind: application
name-zh: 晶圓製造
aliases:
- wafer fabrication
summary: 依設計製造晶圓，並由設備與材料支撐製程。
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
claims: []
gaps:
- status: not-researched
  reason: 代表公司依既有環節角色列出；各公司在此應用的產品能力、客戶與收入尚待逐家深研。
---

## 定義與用途

依設計製造晶圓，並由設備與材料支撐製程。把代工、設備與材料分成可替換的供應角色，避免用同屬「製造」就互相比較。對應既有環節：[晶圓代工](/next?focus=segment-foundry)、[半導體設備](/next?focus=segment-equipment)、[半導體材料](/next?focus=segment-materials)。

可比較的供應角色：[先進邏輯代工](/next?focus=role-advanced-logic-foundry)、[成熟與特殊製程代工](/next?focus=role-mature-specialty-foundry)、[微影曝光](/next?focus=role-lithography)、[塗佈與顯影](/next?focus=role-lithography-track)、[沉積與蝕刻](/next?focus=role-deposition-etch)、[量測與檢測](/next?focus=role-process-control)、[濕製程設備](/next?focus=role-wet-process)、[矽晶圓](/next?focus=role-silicon-wafer)、[光阻材料](/next?focus=role-photoresist)、[污染控制與純化](/next?focus=role-contamination-control)、[特殊氣體](/next?focus=role-specialty-gas)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
