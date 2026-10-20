---
schema-version: research-v1
entity-id: product-server-dram-module
kind: product
name-zh: 伺服器 DRAM 模組
aliases:
- RDIMM
- server DRAM
summary: 伺服器 CPU 使用的主記憶體。
reviewed: '2026-10-18'
definition: 安裝於伺服器主機板、供 CPU 存取的 DRAM 模組。
purpose: 提供系統主記憶體容量。
boundary: 與加速器旁的 HBM 用途與封裝不同。
adoption-conditions:
- 符合平台記憶體世代與控制器規格
bottlenecks:
- 容量與頻寬世代轉換
substitution-limits:
- 不能以 HBM 需求直接推估 DIMM 需求
claims: []
gaps:
- status: not-researched
  reason: 尚未逐家核對代表公司在此產品的具體型號、客戶與收入；列名來自既有環節角色。
---

## 定義與用途

安裝於伺服器主機板、供 CPU 存取的 DRAM 模組。提供系統主記憶體容量。

## 採用條件與限制

與加速器旁的 HBM 用途與封裝不同。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[伺服器 DRAM](/next?focus=role-server-dram)。依既有環節角色列入的代表公司：[SK 海力士](/next?focus=company-000660-ks)、[三星電子](/next?focus=company-005930-ks)、[美光](/next?focus=company-mu)、[南亞科](/next?focus=company-2408-tw)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
