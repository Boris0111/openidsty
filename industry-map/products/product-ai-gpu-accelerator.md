---
schema-version: research-v1
entity-id: product-ai-gpu-accelerator
kind: product
name-zh: AI GPU 加速器
aliases:
- GPU accelerator
summary: 以大量平行運算處理訓練與推論的加速器。
reviewed: '2026-10-18'
definition: 整合運算核心、記憶體介面與互連的通用加速器晶片或模組。
purpose: 提供可程式化的通用 AI 算力。
boundary: 晶片本身不含 HBM 製造、封裝代工與整櫃整合。
adoption-conditions:
- 軟體框架與工作負載完成移植與驗證
- 封裝、HBM、供電與散熱同步就緒
bottlenecks:
- HBM 與先進封裝供給
- 整櫃供電與散熱條件
substitution-limits:
- 與客製 ASIC 的取捨依工作負載與總持有成本，不能一概而論
claims: []
gaps:
- status: not-researched
  reason: 尚未逐家核對代表公司在此產品的具體型號、客戶與收入；列名來自既有環節角色。
---

## 定義與用途

整合運算核心、記憶體介面與互連的通用加速器晶片或模組。提供可程式化的通用 AI 算力。

## 採用條件與限制

晶片本身不含 HBM 製造、封裝代工與整櫃整合。採用與替代判斷是研究分類推論，須以指定平台、料號與驗收資料核對。

## 供應角色與公司

屬於[商用 AI 加速器](/next?focus=role-merchant-accelerator)。依既有環節角色列入的代表公司：[輝達](/next?focus=company-nvda)、[超微](/next?focus=company-amd)、[英特爾](/next?focus=company-intc)。這是分類基準，各公司在此產品的具體型號、客戶與收入待逐家深研核對。
