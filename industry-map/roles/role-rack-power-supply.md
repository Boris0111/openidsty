---
schema-version: research-v1
entity-id: role-rack-power-supply
kind: role
name-zh: 機櫃與系統電源
aliases:
- power shelf
summary: 供應伺服器與機櫃電源的角色。
reviewed: '2026-10-18'
definition: 製造伺服器電源供應器與機櫃電源架。
purpose: 辨認可彼此替換的供應者，再進入產品與公司研究。
boundary: 不含板端 DC/DC 與功率元件。
adoption-conditions:
- 確認轉換位置、負載曲線與保護
bottlenecks:
- 瞬態負載與保護協調
substitution-limits:
- 集中 AC/DC 會改變收入位置，不能等比例受惠
claims: []
gaps:
- status: not-applicable
  reason: 此頁是研究分類；公司產品能力與來源見各公司研究。
---

## 定義與用途

製造伺服器電源供應器與機櫃電源架。主要產品類別：[電源供應器與電源架](/next?focus=product-power-shelf-psu)。

依既有環節角色列入的代表公司：[台達電](/next?focus=company-delta-electronics)、[光寶科](/next?focus=company-2301-tw)、[康舒](/next?focus=company-6282-tw)。

## 採用條件與限制

不含板端 DC/DC 與功率元件。同一角色內的公司可互相比較，但列名不代表已供貨給同一客戶或具相同料號。
