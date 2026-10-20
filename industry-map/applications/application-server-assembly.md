---
schema-version: research-v1
entity-id: application-server-assembly
kind: application
name-zh: 伺服器與整櫃整合
aliases:
- server and rack integration
summary: 把板、連接、機構與次系統組成可交付的伺服器或整櫃。
question: 一台 AI 伺服器與整櫃，從板材到出貨經過哪些環節？
reviewed: '2026-10-18'
definition: 把板、連接、機構與次系統組成可交付的伺服器或整櫃。
purpose: 分開整櫃代工、品牌整合、電路板與連接／機構子角色。
boundary: 整機整合、系統電路板、板材、高速與電力連接、液路快接頭與機構滑軌各自負責不同交付；出廠與場址驗收是不同階段。
adoption-conditions:
- 整份 BOM 齊料並共同驗證電氣、液路、機構與韌體
- 高速介面按實際通道核對損耗與串音
bottlenecks:
- 缺料、工廠測試、液路完整性與維修空間可能推遲交付
substitution-limits:
- 品牌整合與 ODM 的責任不同，不能以含高價晶片的總營收推估組裝份額
flow-steps:
- label: 板材
  note: 銅箔、樹脂與玻纖組成銅箔基板（CCL）
  products: [product-high-speed-ccl]
- label: 電路板
  note: 層疊壓合、鑽孔電鍍，做成高多層伺服器板
  products: [product-server-multilayer-pcb]
- label: 連接與線材
  note: 高速連接器、插槽與線束把板卡和機櫃接起來
  products: [product-high-speed-connector, product-cable-assembly]
- label: 機構與液路
  note: 滑軌與液路快接頭讓伺服器可抽換、可接上液冷
  products: [product-server-slide-rail, product-liquid-quick-disconnect]
- label: 整櫃整合
  note: 代工廠組裝伺服器與整櫃，品牌商以自有品牌出貨
  products: [product-ai-rack-system, product-branded-ai-server]
claims: []
gaps:
- status: not-researched
  reason: 已有 5 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

把板、連接、機構與次系統組成可交付的伺服器或整櫃。分開整櫃代工、品牌整合、電路板與連接／機構子角色。對應既有環節：[系統組裝與機櫃整合](/next?focus=segment-odm)、[印刷電路板與銅箔基板](/next?focus=segment-pcb)、[連接器、線材與滑軌](/next?focus=segment-interconnect)。

可比較的供應角色：[高速銅箔基板](/next?focus=role-high-speed-laminate)、[伺服器電路板](/next?focus=role-server-pcb)、[高速與處理器連接器](/next?focus=role-high-speed-connector)、[高速線材與線束](/next?focus=role-cable-harness)、[液路快接頭](/next?focus=role-liquid-quick-disconnect)、[伺服器滑軌與理線](/next?focus=role-server-rail)、[整櫃與伺服器代工整合](/next?focus=role-rack-system-integration)、[伺服器品牌整合](/next?focus=role-server-brand)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
