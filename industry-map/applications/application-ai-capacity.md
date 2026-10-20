---
schema-version: research-v1
entity-id: application-ai-capacity
kind: application
name-zh: AI 算力容量營運
aliases:
- AI capacity
summary: 取得、建置並營運可用的 IT 算力與設施容量。
question: AI 算力最後由誰建置、怎麼提供給使用者？
reviewed: '2026-10-18'
definition: 取得、建置並營運可用的 IT 算力與設施容量。
purpose: 分開自用超大規模業者與 AI 雲端租用業者，辨認需求回饋的來源。
boundary: 土地建築、供電冷卻、設備與租賃投入分開；需求回饋不表示供應晶片。
adoption-conditions:
- 核對電網接入、可用電力與冷卻、網路與實際負載
bottlenecks:
- 電網併接、許可、場址與供應鏈交付可能限制投產
substitution-limits:
- 自建、託管、租賃與雲端容量的責任與可用性不同
flow-steps:
- label: 自建算力
  note: 超大規模雲端與網路業者自建資料中心算力
  products: [product-hyperscale-ai-capacity]
- label: 雲端租用
  note: AI 雲端業者以 GPU 雲端服務出租算力
  products: [product-gpu-cloud-service]
claims: []
gaps:
- status: not-researched
  reason: 代表公司依既有環節角色列出；各公司在此應用的產品能力、客戶與收入尚待逐家深研。
---

## 定義與用途

取得、建置並營運可用的 IT 算力與設施容量。分開自用超大規模業者與 AI 雲端租用業者，辨認需求回饋的來源。對應既有環節：[資料中心與雲端業者](/next?focus=segment-datacenter)。

可比較的供應角色：[超大規模雲端與自用運算](/next?focus=role-hyperscale-operator)、[AI 雲端租用業者](/next?focus=role-ai-cloud-provider)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
