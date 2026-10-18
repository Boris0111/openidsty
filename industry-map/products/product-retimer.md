---
schema-version: research-v1
entity-id: product-retimer
kind: product
name-zh: 重定時與橋接晶片
aliases:
- retimer
summary: 在高速電路中恢復訊號品質的晶片。
reviewed: '2026-10-18'
definition: 延伸 PCIe、CXL 等高速電訊號距離的重定時與橋接晶片。
purpose: 讓伺服器內部高速連線可靠。
boundary: 與光模組、交換晶片分工。
adoption-conditions:
- 協議與通道驗證
bottlenecks:
- 功耗與板空間
substitution-limits:
- 不同協議世代需重新驗證
claims: []
gaps:
- status: not-researched
  reason: 已有Astera Labs、Credo、邁威爾的能力連結附原文主張（見公司頁）；具體型號、平台、客戶與其他列名公司尚未研究。
---

## 定義與用途

延伸 PCIe、CXL 等高速電訊號距離的重定時與橋接晶片。讓伺服器內部高速連線可靠。

## 採用條件與限制

與光模組、交換晶片分工。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)。依既有環節角色列入的代表公司：[Credo](/next?focus=company-crdo)、[Astera Labs](/next?focus=company-alab)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
