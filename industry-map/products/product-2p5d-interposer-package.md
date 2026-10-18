---
schema-version: research-v1
entity-id: product-2p5d-interposer-package
kind: product
name-zh: 2.5D 中介層封裝
aliases:
- CoWoS class
- interposer package
summary: 把運算晶片與 HBM 放在中介層上的先進封裝。
reviewed: '2026-10-18'
definition: 以矽中介層或重布線層連接多顆 die 與 HBM 的封裝形式。
purpose: 提供晶片間與 HBM 的高密度連線。
boundary: 中介層、封裝載板與系統板是不同層次。
adoption-conditions:
- 已知良品 die、封裝良率與可靠度驗證
- 載板與測試方案同步
bottlenecks:
- 大尺寸封裝翹曲與熱應力
- 產能配置
substitution-limits:
- CoWoS-S／R／L 等互連結構不同，不能當同一選項
claims: []
gaps:
- status: not-researched
  reason: 已有台積電、日月光投控、艾克爾的能力連結附原文主張（見公司頁）；具體型號、平台、客戶與其他列名公司尚未研究。
---

## 定義與用途

以矽中介層或重布線層連接多顆 die 與 HBM 的封裝形式。提供晶片間與 HBM 的高密度連線。

## 採用條件與限制

中介層、封裝載板與系統板是不同層次。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[中介層與 2.5D／3D 整合](/next?focus=role-interposer-integration)。依既有環節角色列入的代表公司：[台積電](/next?focus=company-tsmc)、[日月光投控](/next?focus=company-3711-tw)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
