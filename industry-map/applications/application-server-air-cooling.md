---
schema-version: research-v1
entity-id: application-server-air-cooling
kind: application
name-zh: 伺服器氣冷散熱
aliases:
- server air cooling
summary: 以均熱板、散熱模組與風扇處理仍由空氣帶走的熱。
question: 氣冷伺服器的熱，怎麼排出去？
reviewed: '2026-10-18'
definition: 以均熱板、散熱模組與風扇處理仍由空氣帶走的熱。
purpose: 與直接晶片液冷分開研究，避免把氣冷元件當成液冷供應證據。
boundary: 氣冷模組、均熱板與風扇處理空氣側散熱；冷板、歧管與 CDU 屬液冷情境。
adoption-conditions:
- 依熱負載、允許溫度與機箱風道核對
bottlenecks:
- 風道空間、噪音與功耗限制可用散熱能力
substitution-limits:
- 氣冷與液冷涉及不同流體與維修條件，不能只依 TDP 宣稱必然替代
flow-steps:
- label: 晶片端導熱
  note: 均熱板與散熱鰭片把晶片的熱擴散出去
  products: [product-vapor-chamber-air-module]
- label: 風扇送風
  note: 系統風扇把熱空氣排出機箱
  products: [product-server-fan]
claims: []
gaps:
- status: not-researched
  reason: 已有 2 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

以均熱板、散熱模組與風扇處理仍由空氣帶走的熱。與直接晶片液冷分開研究，避免把氣冷元件當成液冷供應證據。對應既有環節：[散熱](/next?focus=segment-thermal)。

可比較的供應角色：[氣冷模組與均熱板](/next?focus=role-air-cooling-module)、[散熱風扇](/next?focus=role-server-fan)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
