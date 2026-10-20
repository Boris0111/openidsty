---
schema-version: research-v1
entity-id: product-pmic-voltage-regulator
kind: product
name-zh: 電源管理與電壓調節晶片
aliases:
- PMIC
- VRM
summary: 在板上供應處理器所需電壓的晶片。
reviewed: '2026-10-18'
definition: 板端多相電壓調節與電源管理晶片。
purpose: 以高電流低電壓供應加速器。
boundary: 與電源架、功率開關元件分工。
adoption-conditions:
- 負載與瞬態驗證
bottlenecks:
- 電流密度
substitution-limits:
- 不同轉換架構不能直接互換
claims: []
gaps:
- status: not-researched
  reason: 已有芯源系統的能力連結附原文主張（見公司頁）；具體型號、平台、客戶與其他列名公司尚未研究。
---

## 定義與用途

板端多相電壓調節與電源管理晶片。以高電流低電壓供應加速器。

## 採用條件與限制

與電源架、功率開關元件分工。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[板端電源轉換](/next?focus=role-board-power-conversion)。依既有環節角色列入的代表公司：[芯源系統](/next?focus=company-mpwr)、[Vicor](/next?focus=company-vicr)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
