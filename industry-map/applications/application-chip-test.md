---
schema-version: research-v1
entity-id: application-chip-test
kind: application
name-zh: 晶片測試與篩選
aliases:
- semiconductor test
summary: 在晶圓、封裝前後與系統層篩出不良品。
question: 晶片出貨前要經過哪幾道測試？
reviewed: '2026-10-18'
definition: 在晶圓、封裝前後與系統層篩出不良品。
purpose: 分開測試服務、測試機台與探針／測試座三種收入單位。
boundary: wafer sort、final test、SLT、ATE 與探針／socket 各有角色；測試服務、設備及接觸介面不能互相加總。
adoption-conditions:
- 依目標失效機制、電力／溫控、接觸介面與測試程式核對覆蓋率
bottlenecks:
- 測試時間、並行度、接觸壽命與熱控可能限制產能
substitution-limits:
- SLT 補充系統環境驗證，不能直接替代全部 ATE 或封裝前篩選
flow-steps:
- label: 晶圓測試
  note: 探針卡接觸晶圓上的晶片，由自動測試設備（ATE）量測
  products: [product-probe-card, product-ate-system]
- label: 封裝
  note: 通過晶圓測試的晶片進入封裝
- label: 成品測試
  note: 封裝後以測試座接上 ATE；測試服務廠承接晶圓與成品測試
  products: [product-test-socket, product-chip-test-service]
- label: 系統層測試
  note: SLT 在接近實際使用的系統環境中測試
claims: []
gaps:
- status: not-researched
  reason: 已有 3 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

在晶圓、封裝前後與系統層篩出不良品。分開測試服務、測試機台與探針／測試座三種收入單位。對應既有環節：[測試與探針](/next?focus=segment-test)。

可比較的供應角色：[晶圓與成品測試服務](/next?focus=role-test-service)、[探針卡與測試座](/next?focus=role-test-contact-interface)、[測試機台](/next?focus=role-ate-system)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
