---
schema-version: research-v1
entity-id: role-hbm-stack-supply
kind: role
name-zh: HBM 堆疊供應
aliases:
- HBM supply
summary: 供應高頻寬記憶體堆疊的角色。
reviewed: '2026-10-18'
definition: 製造 DRAM 堆疊並與 base die、封裝共同交付 HBM。
purpose: 辨認可彼此替換的供應者，再進入產品與公司研究。
boundary: 不含伺服器 DIMM、NAND 與封裝代工。
adoption-conditions:
- 依指定控制器、封裝與客戶平台共同認證
bottlenecks:
- 堆疊、鍵合與測試良率
substitution-limits:
- 不同世代與堆疊高度需重新認證
claims: []
gaps:
- status: not-applicable
  reason: 此頁是研究分類；公司產品能力與來源見各公司研究。
---

## 定義與用途

製造 DRAM 堆疊並與 base die、封裝共同交付 HBM。主要產品類別：[HBM 高頻寬記憶體](/next?focus=product-hbm-stack)。

依既有環節角色列入的代表公司：[SK 海力士](/next?focus=company-000660-ks)、[三星電子](/next?focus=company-005930-ks)、[美光](/next?focus=company-mu)。

## 採用條件與限制

不含伺服器 DIMM、NAND 與封裝代工。同一角色內的公司可互相比較，但列名不代表已供貨給同一客戶或具相同料號。
