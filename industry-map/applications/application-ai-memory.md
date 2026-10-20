---
schema-version: research-v1
entity-id: application-ai-memory
kind: application
name-zh: AI 記憶體頻寬與容量
aliases:
- AI memory
summary: 供應加速器旁的高頻寬記憶體，以及伺服器主記憶體與儲存控制。
question: AI 加速器的記憶體頻寬從哪裡來？
reviewed: '2026-10-18'
definition: 供應加速器旁的高頻寬記憶體，以及伺服器主記憶體與儲存控制。
purpose: 區分 HBM、伺服器 DRAM、利基型記憶體與 NAND 控制，避免把同環節公司視為同一供應者。
boundary: HBM DRAM stack、邏輯 base die、伺服器 DRAM 與 NAND／控制器是不同產品與製造分工。
adoption-conditions:
- 依指定控制器、封裝與客戶平台核對共同認證
- 容量、頻寬、功耗與熱限制須在同一產品世代比較
bottlenecks:
- 堆疊、鍵合、測試與封裝配合共同影響良品供給
substitution-limits:
- DRAM、HBM 與 NAND 不能直接互替
flow-steps:
- label: DRAM 堆疊
  note: 多層 DRAM die 疊在一起
  products: [product-hbm-stack]
- label: 邏輯底層
  note: base die 負責堆疊與外部的訊號
- label: 共同封裝
  note: HBM 與加速器放進同一個封裝
- label: 主記憶體對照
  note: 伺服器 DRAM 模組插在主機板上供 CPU 使用
  products: [product-server-dram-module]
claims: []
gaps:
- status: not-researched
  reason: 代表公司依既有環節角色列出；各公司在此應用的產品能力、客戶與收入尚待逐家深研。
---

## 定義與用途

供應加速器旁的高頻寬記憶體，以及伺服器主記憶體與儲存控制。區分 HBM、伺服器 DRAM、利基型記憶體與 NAND 控制，避免把同環節公司視為同一供應者。對應既有環節：[記憶體](/next?focus=segment-memory)。

可比較的供應角色：[HBM 堆疊供應](/next?focus=role-hbm-stack-supply)、[伺服器 DRAM](/next?focus=role-server-dram)、[利基型記憶體](/next?focus=role-specialty-memory)、[NAND 控制晶片與模組](/next?focus=role-nand-controller)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
