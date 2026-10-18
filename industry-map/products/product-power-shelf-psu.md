---
schema-version: research-v1
entity-id: product-power-shelf-psu
kind: product
name-zh: 電源供應器與電源架
aliases:
- PSU
- power shelf
summary: 把輸入電力轉成機櫃或伺服器母線電壓的設備。
reviewed: '2026-10-18'
definition: 伺服器 PSU 與機櫃電源架。
purpose: 提供系統級供電。
boundary: 板端 DC/DC、BBU 與設施 UPS 是不同角色。
adoption-conditions:
- 轉換位置與保護協調驗證
bottlenecks:
- 瞬態負載
substitution-limits:
- 800VDC 等架構改變轉換位置，需逐案核對
claims: []
gaps:
- status: not-researched
  reason: 尚未逐家核對代表公司在此產品的具體型號、客戶與收入；列名來自既有環節角色。
---

## 定義與用途

伺服器 PSU 與機櫃電源架。提供系統級供電。

## 採用條件與限制

板端 DC/DC、BBU 與設施 UPS 是不同角色。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[機櫃與系統電源](/next?focus=role-rack-power-supply)。依既有環節角色列入的代表公司：[台達電](/next?focus=company-delta-electronics)、[光寶科](/next?focus=company-2301-tw)、[康舒](/next?focus=company-6282-tw)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
