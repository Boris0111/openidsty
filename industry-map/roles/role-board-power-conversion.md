---
schema-version: research-v1
entity-id: role-board-power-conversion
kind: role
name-zh: 板端電源轉換
aliases:
- board power
summary: 把母線電壓轉成晶片電壓的角色。
reviewed: '2026-10-18'
definition: 設計板端電壓調節、電源管理晶片與電源模組。
purpose: 辨認可彼此替換的供應者，再進入產品與公司研究。
boundary: 不含系統電源架與功率元件製造。
adoption-conditions:
- 依負載電流、瞬態與板空間驗證
bottlenecks:
- 電流密度與散熱
substitution-limits:
- 不同轉換架構需重新設計
claims: []
gaps:
- status: not-applicable
  reason: 此頁是研究分類；公司產品能力與來源見各公司研究。
---

## 定義與用途

設計板端電壓調節、電源管理晶片與電源模組。主要產品類別：[電源管理與電壓調節晶片](/next?focus=product-pmic-voltage-regulator)、[高密度電源模組](/next?focus=product-power-module)。

依既有環節角色列入的代表公司：[芯源系統](/next?focus=company-mpwr)、[Vicor](/next?focus=company-vicr)。

## 採用條件與限制

不含系統電源架與功率元件製造。同一角色內的公司可互相比較，但列名不代表已供貨給同一客戶或具相同料號。
