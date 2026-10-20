---
schema-version: research-v1
entity-id: application-ai-acceleration
kind: application
name-zh: AI 加速運算
aliases:
- AI accelerator
summary: 提供訓練與推論所需算力的晶片與平台。
question: AI 運算晶片有哪幾種來源？
reviewed: '2026-10-18'
definition: 提供訓練與推論所需算力的晶片與平台。
purpose: 從加速器的供應方式（商用、客製設計、雲端自研）找到可比較的供應角色。
boundary: 只涵蓋運算晶片的設計與平台；晶圓製造、封裝、記憶體與網路各有獨立角色。
adoption-conditions:
- 依實際工作負載、軟體移植與利用率評估平台
- 設計須與記憶體、封裝、供電及網路共同驗證
bottlenecks:
- 記憶體頻寬、通訊與軟體效率可能限制有效吞吐
substitution-limits:
- 客製 ASIC 與 GPU 的取捨需攤提設計與軟體成本，不能由單一工作負載名稱斷言
flow-steps:
- label: 商用加速器
  note: 晶片廠設計並銷售通用的 GPU 加速器
  products: [product-ai-gpu-accelerator]
- label: 客製 ASIC
  note: 設計服務與晶片廠為雲端業者打造專用晶片
  products: [product-custom-ai-asic]
- label: 雲端自研
  note: 雲端業者自行定義架構的加速器
  products: [product-cloud-in-house-accelerator]
claims: []
gaps:
- status: not-researched
  reason: 已有 2 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

提供訓練與推論所需算力的晶片與平台。從加速器的供應方式（商用、客製設計、雲端自研）找到可比較的供應角色。對應既有環節：[運算晶片](/next?focus=segment-compute)。

可比較的供應角色：[商用 AI 加速器](/next?focus=role-merchant-accelerator)、[客製 ASIC 設計與交付](/next?focus=role-custom-asic-partner)、[雲端業者自研加速器](/next?focus=role-in-house-accelerator)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
