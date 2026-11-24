---
schema-version: research-v1
entity-id: application-ai-rack-power
kind: application
name-zh: AI 機櫃供電
aliases:
- AI rack power
summary: 把設施電力轉換成晶片可用的電壓，並由功率元件執行轉換。
question: 電力怎麼從設施一路降到晶片？
reviewed: '2026-11-24'
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
- label: 接入與配電
  note: 由設施受電、變壓與保護
  products: [product-datacenter-transformer, product-datacenter-switchgear]
- label: 設施備援與分接
  note: 依單線圖選 UPS 和幹線
  products: [product-facility-ups, product-datacenter-busway]
- label: 機櫃供電與備援
  note: 依 AC 插座或 DC 母線配置，BBU 確認故障域
  products: [product-rack-pdu, product-power-shelf-psu, product-rack-battery-backup]
- label: 板端轉換
  note: DC/DC 與多相電壓調節供應處理器
  products: [product-power-module, product-pmic-voltage-regulator]
claims: []
gaps:
- status: not-obtained
  reason: 已讀產品文件可追溯設備與板端交付；案場同負載、同電壓及同冗餘的配置、整段成本與個別供應商驗收仍待查。
---

## 定義與用途

從[變壓器](/next?focus=product-datacenter-transformer)、[開關與配電盤](/next?focus=product-datacenter-switchgear)和[設施 UPS](/next?focus=product-facility-ups)開始讀，往下連到[母線槽與分接](/next?focus=product-datacenter-busway)、[機櫃 rPDU](/next?focus=product-rack-pdu)、[電源架](/next?focus=product-power-shelf-psu)與[機櫃 BBU](/next?focus=product-rack-battery-backup)，最後到架內運算板。完整見[設施、機櫃與板端的供電比較與需求案例](/next?focus=research-ai-facility-to-board-power)。

把設施電力轉換成晶片可用的電壓，並由功率元件執行轉換。分開機櫃電源、板端電源轉換與功率／控制元件。對應既有環節：[電源與供電架構](/next?focus=segment-power)、[功率與分離式元件](/next?focus=segment-power-discrete)。

可比較的供應角色：[機櫃與系統電源](/next?focus=role-rack-power-supply)、[板端電源轉換](/next?focus=role-board-power-conversion)、[功率開關元件](/next?focus=role-power-switch-device)、[控制與電源管理晶片](/next?focus=role-power-control-mcu)、[整流與保護元件](/next?focus=role-discrete-rectifier)、[功率材料、磊晶與特殊製程](/next?focus=role-power-materials-process)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
