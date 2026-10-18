---
schema-version: research-v1
entity-id: application-chip-integration
kind: application
name-zh: 晶片與記憶體整合封裝
aliases:
- advanced packaging
summary: 把運算晶片、HBM 與載板整合成可上板的封裝。
reviewed: '2026-10-18'
definition: 把運算晶片、HBM 與載板整合成可上板的封裝。
purpose: 分開中介層整合、委外封裝與封裝載板三層，辨認各自的供應者。
boundary: 中介層／RDL、封裝載板、D2D 介面與系統電路板是不同層次；封裝能力不等於載板或系統板能力。
adoption-conditions:
- 量產需同時有已知良品 die、封裝良率、可靠度與客戶驗收
- 載板線寬／線距、micro-via、翹曲與可靠度需配合指定封裝認證
bottlenecks:
- 大型封裝的路由、翹曲、熱應力與測試可及性共同限制整合
- 大尺寸多層載板的有效產出要扣除良率與認證
substitution-limits:
- 不同中介層與互連結構不能當同一選項比較
- 玻璃核心等材料方案不能由樣品推定已替換既有有機載板
claims: []
gaps:
- status: not-researched
  reason: 已有 4 家深研公司在此應用的角色附能力連結（見各角色與公司頁）；其餘列名公司依既有環節角色列出，產品能力、客戶與收入尚未研究。
---

## 定義與用途

把運算晶片、HBM 與載板整合成可上板的封裝。分開中介層整合、委外封裝與封裝載板三層，辨認各自的供應者。對應既有環節：[先進封裝](/next?focus=segment-advanced-packaging)、[ABF 載板](/next?focus=segment-substrate)。

可比較的供應角色：[中介層與 2.5D／3D 整合](/next?focus=role-interposer-integration)、[委外封裝](/next?focus=role-osat-assembly)、[IC 封裝載板](/next?focus=role-ic-substrate)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
