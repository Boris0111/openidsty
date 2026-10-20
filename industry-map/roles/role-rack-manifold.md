---
schema-version: research-v1
entity-id: role-rack-manifold
kind: role
name-zh: 機櫃歧管
aliases:
- manifold
summary: 在機櫃內分配冷卻液流量的角色。
reviewed: '2026-10-18'
definition: 製造把冷卻液分配到各伺服器的歧管。
purpose: 辨認可彼此替換的供應者，再進入產品與公司研究。
boundary: 不含冷板與 CDU 的換熱控制。
adoption-conditions:
- 與冷板、CDU 以同一迴路驗證流量分布
bottlenecks:
- 壓降與流量分布
substitution-limits:
- 歧管與 CDU 功能不同
claims: []
gaps:
- status: not-applicable
  reason: 此頁是研究分類；公司產品能力與來源見各公司研究。
---

## 定義與用途

製造把冷卻液分配到各伺服器的歧管。主要產品類別：[機櫃歧管](/next?focus=product-rack-manifold)。

依既有環節角色列入的代表公司：[雙鴻](/next?focus=company-auras)。

## 採用條件與限制

不含冷板與 CDU 的換熱控制。同一角色內的公司可互相比較，但列名不代表已供貨給同一客戶或具相同料號。
