---
schema-version: research-v1
entity-id: product-ethernet-switch-asic
kind: product
name-zh: 交換器晶片
aliases:
- switch ASIC
summary: 在網路中轉送封包的核心晶片。
reviewed: '2026-10-18'
definition: 資料中心交換器使用的交換 ASIC。
purpose: 決定交換容量與埠速。
boundary: 與交換器系統、光模組分工。
adoption-conditions:
- 協議、拓樸與管理驗證
bottlenecks:
- 功耗與散熱
substitution-limits:
- 不能只看交換容量判斷整條鏈路
claims: []
gaps:
- status: not-researched
  reason: 已有博通、邁威爾的能力連結附原文主張（見公司頁）；具體型號、平台、客戶與其他列名公司尚未研究。
---

## 定義與用途

資料中心交換器使用的交換 ASIC。決定交換容量與埠速。

## 採用條件與限制

與交換器系統、光模組分工。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[交換器晶片](/next?focus=role-switch-silicon)。依既有環節角色列入的代表公司：[博通](/next?focus=company-avgo)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
