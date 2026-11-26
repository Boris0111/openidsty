---
schema-version: research-v1
entity-id: product-datacenter-busway
kind: product
name-zh: "設施母線槽與分接盒"
aliases:
- "busway"
- "busduct"
- "tap-off box"
summary: "封閉的母線及分接設施配電。"
definition: "封閉的母線及分接設施配電。"
purpose: "將電力從開關盤或 UPS 下游運送到配電點。"
boundary: "ORv3 DC 母線、AC 幹線與 rPDU 位置分開。"
adoption-conditions:
- "依安裝方向、持續電流、熱、短路和分接規格驗證。"
bottlenecks:
- "接頭溫升、停機改線及保護協調。"
substitution-limits:
- "間距、配接、絕緣、故障電流及環境溫升對齊後方可比較。"
reviewed: "2026-11-24"
claims:
- id: tecobar-busway-delivery
  statement: "東元子公司 TECOBAR 的 LB 低壓鑄樹脂銅母線用於 1 kV 以下，部分料號額定最高 6,300 A。"
  confidence: well-supported
  conditions:
  - "另依組件、配置及標準驗收，交付主體為 TECOBAR。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: tecobar-lb-busway
    url: https://www.tecobar.com.tw/en/product-396369/LV-Cast-Resin-Insulated-Busway-Copper-Busway-LB-Series.html
    locator: "LB Series／Technical Data"
    read-scope: "查 1 kV 以下、6,300 A 規格列。"
    stance: supporting
    applicable-period: "查核日 LB 系列"
  - source-id: teco-2026-tecobar-affiliation
    url: https://www.teco.com.tw/en-us/press/news/TECO-Showcases-Integrated-Modular-Data-Center-Solutions-in-Singapore--Targeting-Southeast-Asia-s-AI-Infrastructure-Opportunities?tags=1014
    locator: "Exhibition／its subsidiary TECOBAR"
    read-scope: "確認集團歸屬及子公司展示的母線類型。"
    stance: supporting
    applicable-period: "2026 年公告"
- id: powerbar-impb-delivery
  statement: "Vertiv PowerBar iMPB 北美版為 3 相 600 VAC、160–800 A 系統，銅導體上限 600 A、鋁導體上限 800 A。"
  confidence: well-supported
  conditions:
  - "與分接盒、當地認證、故障額定和各分路限制配套。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-powerbar-impb-datasheet
    url: https://www.vertiv.com/492f82/globalassets/shared/vertiv-powerbar-impb-data-sheet-sl-70397.pdf
    locator: "p.1 Overview、Standard features"
    read-scope: "查 AC、額定、可配置 tap-off box。"
    stance: supporting
    applicable-period: "SL-70397，北美版"
- id: busway-project-demand
  statement: "增添機櫃時，配電路線與可用分接容量可能帶動母線與分接箱需求。"
  confidence: inference
  conditions:
  - "既有母線及分接備用容量、固定管線與其他配置可抵銷。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-powerbar-impb-datasheet
    url: https://www.vertiv.com/492f82/globalassets/shared/vertiv-powerbar-impb-data-sheet-sl-70397.pdf
    locator: "Overview"
    read-scope: "查可新增分支與更改配置的用途。"
    stance: supporting
    applicable-period: "SL-70397"
gaps:
- status: not-obtained
  reason: "同場址運行數據、價格、維護工時及具名採用仍缺。"
- status: not-public
  reason: "資料未列個別料號收入。"
---

## 定義與用途

設施 busway 是幹線，分接盒將電力送往各機櫃或盤。機櫃中的 48／50 V DC busbar 則屬另一段，需分別驗收。

## 規格與成本

北美 iMPB 3 相 600 VAC、160–800 A；TECOBAR LB 是低於 1 kV 的銅母線，另有最高 6,300 A 配置。這些只是各自產品級距。分路受 tap-off 保護、接點溫升、敷設與當地標準限制。

## 採用條件與限制

同一幹線位置可比較固定線纜及母線槽，重點為可增設分支、故障耐受、空間、停機成本與相同安裝條件。相異級距不要相加。

## 供應角色與公司

[東元](/next?focus=company-1504-tw)集團由 TECOBAR 供應 LB；[Vertiv](/next?focus=company-vertiv)供應 iMPB。跨地區須重新核對安裝和認證，IEC 與北美配置各自列。

## 需求如何傳導

推論：新增列或變更機櫃配置可增加母線與分接箱，既有備用分路或改以固定線纜會抵銷。追蹤核定幹線長度、分路和故障設計。
