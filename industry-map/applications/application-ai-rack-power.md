---
schema-version: research-v1
entity-id: application-ai-rack-power
kind: application
name-zh: AI 機櫃供電
aliases:
- AI rack power
summary: 把設施電力轉換成晶片可用的電壓，並由功率元件執行轉換。
question: 電力怎麼從設施一路降到晶片？
reviewed: '2026-10-18'
definition: 把設施電力轉換成晶片可用的電壓，並由功率元件執行轉換。
purpose: 分開機櫃電源、板端電源轉換與功率／控制元件。
boundary: PSU／power shelf 處理系統供電，板端 DC/DC 供晶片電壓；功率開關、整流保護、控制晶片與磊晶製程屬元件層。800VDC 是架構，不是 GPU 工作電壓。
adoption-conditions:
- 確認轉換位置、負載曲線、保護、接地與維修條件
- 元件依拓樸、電壓電流、頻率、損耗與熱設計選型
bottlenecks:
- 瞬態負載、保護協調與元件材料缺陷都可能限制採用
substitution-limits:
- BBU、UPS 與設施儲能功能不同
- Si、SiC、GaN 適用條件不同，不是單一材料必勝
flow-steps:
- label: 設施
  note: 市電或設施電力進入機櫃
- label: AC/DC
  note: 電源架或 PSU 把交流電轉成直流
  products: [product-power-shelf-psu]
- label: 母線
  note: 機櫃直流母線把電力分到各伺服器
- label: 板端
  note: DC/DC 電壓調節到晶片工作電壓
  products: [product-pmic-voltage-regulator, product-power-module]
claims: []
gaps:
- status: not-researched
  reason: 已有 5 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

把設施電力轉換成晶片可用的電壓，並由功率元件執行轉換。分開機櫃電源、板端電源轉換與功率／控制元件。對應既有環節：[電源與供電架構](/next?focus=segment-power)、[功率與分離式元件](/next?focus=segment-power-discrete)。

可比較的供應角色：[機櫃與系統電源](/next?focus=role-rack-power-supply)、[板端電源轉換](/next?focus=role-board-power-conversion)、[功率開關元件](/next?focus=role-power-switch-device)、[控制與電源管理晶片](/next?focus=role-power-control-mcu)、[整流與保護元件](/next?focus=role-discrete-rectifier)、[功率材料、磊晶與特殊製程](/next?focus=role-power-materials-process)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
