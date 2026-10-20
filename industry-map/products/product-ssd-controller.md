---
schema-version: research-v1
entity-id: product-ssd-controller
kind: product
name-zh: SSD 控制晶片
aliases:
- NAND controller
- SSD
summary: 管理 NAND 讀寫與錯誤修正的控制器。
reviewed: '2026-10-18'
definition: 控制 NAND 存取、壽命管理與介面的晶片。
purpose: 讓伺服器與資料中心使用固態儲存。
boundary: 不含 NAND 顆粒製造。
adoption-conditions:
- 介面世代與韌體驗證
bottlenecks:
- NAND 顆粒供給
substitution-limits:
- 不同控制器需重新驗證韌體與耐久度
claims: []
gaps:
- status: not-researched
  reason: 尚未逐家核對代表公司在此產品的具體型號、客戶與收入；列名來自既有環節角色。
---

## 定義與用途

控制 NAND 存取、壽命管理與介面的晶片。讓伺服器與資料中心使用固態儲存。

## 採用條件與限制

不含 NAND 顆粒製造。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[NAND 控制晶片與模組](/next?focus=role-nand-controller)。依既有環節角色列入的代表公司：[群聯](/next?focus=company-8299-two)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
