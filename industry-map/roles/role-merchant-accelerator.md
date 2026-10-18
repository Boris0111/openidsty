---
schema-version: research-v1
entity-id: role-merchant-accelerator
kind: role
name-zh: 商用 AI 加速器
aliases:
- merchant accelerator
summary: 對外銷售 GPU 等加速器與平台的供應角色。
reviewed: '2026-10-18'
definition: 自行設計並對外銷售 AI 加速器與配套軟體平台。
purpose: 辨認可彼此替換的供應者，再進入產品與公司研究。
boundary: 不含客製 ASIC 設計服務與雲端業者自研晶片。
adoption-conditions:
- 以實際模型、精度、批次與延遲比較平台
bottlenecks:
- 記憶體與互連頻寬、軟體生態影響有效吞吐
substitution-limits:
- 不同平台需重新移植與驗證軟體，不能只比峰值算力
claims: []
gaps:
- status: not-applicable
  reason: 此頁是研究分類；公司產品能力與來源見各公司研究。
---

## 定義與用途

自行設計並對外銷售 AI 加速器與配套軟體平台。主要產品類別：[AI GPU 加速器](/next?focus=product-ai-gpu-accelerator)。

依既有環節角色列入的代表公司：[輝達](/next?focus=company-nvda)、[超微](/next?focus=company-amd)、[英特爾](/next?focus=company-intc)。

## 採用條件與限制

不含客製 ASIC 設計服務與雲端業者自研晶片。同一角色內的公司可互相比較，但列名不代表已供貨給同一客戶或具相同料號。
