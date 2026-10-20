---
schema-version: research-v1
entity-id: application-ai-rack-cooling
kind: application
name-zh: AI 機櫃液冷
aliases: [AI rack cooling]
summary: 從晶片取熱、回路控制到設施換熱，理解產品角色與可核對的公司能力。
question: AI 機櫃的熱，怎麼送出去？
reviewed: '2026-10-20'
definition: 本供應鏈以冷板、機櫃歧管與液對液 CDU 組成的直接晶片液冷為研究情境。
purpose: 由系統功能找到產品、公司與原始來源。
boundary: 不代表所有液冷架構，也不把功能相接當作兩家公司存在交易。
adoption-conditions: [平台與場址已選擇相容的直接晶片及設施水路架構]
bottlenecks: [取熱、水路與設施能力需要共同成立]
substitution-limits: [其他液冷或氣冷架構需按不同採用條件另行比較]
flow-steps:
- label: 伺服器二次側
  note: 冷板貼著晶片取熱，機櫃歧管把冷卻液分到各伺服器
  products: [product-cold-plate, product-rack-manifold]
- label: 液對液 CDU
  note: 控制回路，並在兩個回路之間換熱
  products: [product-liquid-to-liquid-cdu]
- label: 設施散熱
  note: 設施側水路與排熱設備把熱帶走
claims: []
gaps:
- status: not-researched
  reason: 已核對雙鴻、奇鋐與建準的冷板，雙鴻的機櫃歧管，以及 Vertiv 與雙鴻的液對液 CDU 產品資料；並非完整供應商名單，也不代表已確認客戶或出貨。
---

## 定義與用途

先辨認每一段交付什麼，再查誰有產品證據。這條供應鏈連接冷板、機櫃歧管、液對液 CDU 與兩個冷卻回路的圖解。對應既有環節：[散熱](/next?focus=segment-thermal)。

可比較的供應角色：[晶片端取熱](/next?focus=role-chip-heat-capture)、[機櫃歧管](/next?focus=role-rack-manifold)、[回路控制與換熱](/next?focus=role-coolant-distribution)。

## 採用條件與限制

產品能相接不等於已形成採購關係。判斷商業影響時，還需具體平台驗證、訂單與收入資料。
