---
schema-version: research-v1
entity-id: product-hbm-stack
kind: product
name-zh: HBM 高頻寬記憶體
aliases:
- HBM
- HBM4
summary: 堆疊在加速器旁、提供高頻寬的 DRAM。
reviewed: '2026-10-18'
definition: 多層 DRAM die 堆疊並連接邏輯 base die 的記憶體。
purpose: 提供加速器所需的記憶體頻寬與容量。
boundary: DRAM stack、base die 製程與 CoWoS 類封裝是不同分工；同環節公司不一定都是 HBM4 供應商。
adoption-conditions:
- 與指定加速器、封裝完成共同認證
- 容量、頻寬、功耗與熱限制在同一世代核對
bottlenecks:
- 堆疊與鍵合良率
- 封裝配合與測試
substitution-limits:
- HBM 與伺服器 DRAM、NAND 不能直接互替
claims: []
gaps:
- status: not-researched
  reason: 尚未逐家核對代表公司在此產品的具體型號、客戶與收入；列名來自既有環節角色。
---

## 定義與用途

多層 DRAM die 堆疊並連接邏輯 base die 的記憶體。提供加速器所需的記憶體頻寬與容量。

## 採用條件與限制

DRAM stack、base die 製程與 CoWoS 類封裝是不同分工；同環節公司不一定都是 HBM4 供應商。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[HBM 堆疊供應](/next?focus=role-hbm-stack-supply)。依既有環節角色列入的代表公司：[SK 海力士](/next?focus=company-000660-ks)、[三星電子](/next?focus=company-005930-ks)、[美光](/next?focus=company-mu)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
