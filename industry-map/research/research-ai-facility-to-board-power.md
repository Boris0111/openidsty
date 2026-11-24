---
schema-version: research-v1
entity-id: research-ai-facility-to-board-power
kind: research
name-zh: "AI 資料中心從設施到板端的供電"
aliases:
- "facility to board power"
- "資料中心供電鏈"
summary: "分層比較設施、機架與板端，追蹤容量、架構、交期和負載的需求傳導。"
related-ids:
- "application-ai-rack-power"
- "segment-power"
- "segment-datacenter"
- "theme-power-bottleneck"
- "product-datacenter-transformer"
- "product-datacenter-switchgear"
- "product-facility-ups"
- "product-datacenter-busway"
- "product-rack-pdu"
- "product-rack-battery-backup"
- "product-power-shelf-psu"
- "product-power-module"
- "product-pmic-voltage-regulator"
reviewed: "2026-11-24"
claims:
- id: facility-rack-board-boundaries
  statement: "資料中心供電鏈至少要分開場址 AC 接入、UPS 備援、機架整流、架側備援及板端轉換的交付邊界。"
  confidence: well-supported
  conditions:
  - "套用在單線圖上，確認每一段是否存在及哪些設備共用故障域。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-transformer-spec-guide
    url: https://www.teco.com.tw/upload/userfiles/files/%E8%AE%8A%E5%A3%93%E5%99%A8%E5%9E%8B%E9%8C%84%E8%8B%B1%E6%96%87%E7%89%88_251210_final_TECO_Transformers.pdf
    locator: "DRY CAST RESIN 22.8kV／380V"
    read-scope: "查設施一次／二次側。"
    stance: supporting
    applicable-period: "2025-12 型錄"
  - source-id: schneider-galaxy-vx-ups-modes
    url: https://productinfo.se.com/galaxyvx_ul/990-914303-energy-storage-system-for-ul9540-galaxy-vx-ups-and-galaxy-lithium-ion-battery-cabinets-operation/English/990-914303_EN.pdf
    locator: "Operation Modes"
    read-scope: "核對 UPS 分路與旁路。"
    stance: supporting
    applicable-period: "990-914303_EN"
  - source-id: ocp-orv3-bbu-module
    url: https://www.opencompute.org/documents/open-rack-v3-bbu-module-spec-1-4-pdf/
    locator: "§§4.2、4.3"
    read-scope: "查架側放電介面。"
    stance: supporting
    applicable-period: "v1.4"
- id: rack-load-scenario
  statement: "在同一帶 5+1 PSU 備援的 33 kW 案例，單 shelf 可用 27.5 kW。若原先 60 kW 的需求升到 100 kW 且可按 shelf 均分，理想化最少由三組增加到四組。"
  confidence: inference
  conditions:
  - "假設只容許每 shelf 一顆 PSU 失效；若要容許整組 shelf 失效則需額外算。機架、輸入、母線、散熱和突波在合格範圍的前提另驗。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: delta-33kw-power-shelf
    url: https://www.deltaww.com/en-US/products/power-solutions
    locator: "Power Shelf"
    read-scope: "查 5+1 後 27.5 kW。"
    stance: supporting
    applicable-period: "指定 33 kW 方案"
  - source-id: ocp-orv3-hvdc-100kw-shelf
    url: https://www.opencompute.org/documents/orv3-hvdc-lvdc-100kw-power-shelf-spec-1-0-0-pdf
    locator: "§§3.1、4.2"
    read-scope: "轉換位置或規格改變為反向情境。"
    stance: counter
    applicable-period: "Rev.1.0"
gaps:
- status: not-obtained
  reason: "本例是假設負載，未取得同案場交期、整段效率、電壓與容錯餘裕。"
- status: not-public
  reason: "平台數量及指定組件採用和收入未公開。"
---

## 研究問題

AI 機櫃功率增加時，哪些設備需要加量，哪些僅改規格？從[AI 機櫃供電](/next?focus=application-ai-rack-power)讀到設備、公司與原始規格。

## 判斷與限制

### 設施接入、配電與備援

- 場址批准電壓及 MVA 決定接入。[變壓器](/next?focus=product-datacenter-transformer)變換電壓，[開關與配電盤](/next?focus=product-datacenter-switchgear)負責出線、隔離及保護。按單線圖核對變壓一次、二次側與受保護饋線。
- [設施 UPS](/next?focus=product-facility-ups)的 kW、kVA 和末期續航需拆算，確認網路、冷卻泵及控制等受保護負載。[母線槽與分接](/next?focus=product-datacenter-busway)與[機櫃 rPDU](/next?focus=product-rack-pdu)依幹線、分路、插座、相別及熱選型；同路徑的容量受最小限制，A/B 故障接手另算。

### 機櫃與板端

- 低壓機櫃內，[電源架](/next?focus=product-power-shelf-psu)可整流至 48／50 V，[機櫃 BBU](/next?focus=product-rack-battery-backup)在指定路徑失電時續供。若用集中式 800 VDC，先核對上游 AC/DC 與各架 DC/DC 所在位置，再核對監控與維修。
- 板端依走線、電流、溫度和瞬態選[DC/DC 模組](/next?focus=product-power-module)或由[電壓調節晶片](/next?focus=product-pmic-voltage-regulator)與功率級、電感組成的電路。比較同輸出時要將整條供電路徑的損耗、面積、輸入電壓與保護納入。

### 案例：同一機房由 60 kW 升到 100 kW 的機櫃

1. **確立情境。** 60／100 kW 都是假設的單架持續 IT 負載，尖峰另核。前段 AC/DC 及 50 V 母線架構維持。5+1 保一顆 PSU，每 shelf 27.5 kW。理想均分時算得 3 → 4 組；若須承受整組失效，該配置另算。此案不假定單架有相應接點、散熱或備援能力。
2. **追到設施與交期。** 若有 10 架且同時達 100 kW，只能先推算 1 MW IT 輸出需求。受電申請還要加轉換損失和非 IT 負載，按功因、使用率和設備降額校核。依已核准 MVA、站房預留容量、送電、變壓器與開關櫃出廠驗收逐項排時程。設備交付與上電可落在不同期。
3. **追到備援及板端。** 同等續航和溫度下，負載增長會增加儲能與轉換容量需求。若實際方案以 BBU 只保加速器，仍要核對控制、網路、冷卻等允許的故障。板端要從每顆加速器的峰值與熱查看相數、電源模組或兩段轉換。
4. **反向情境。** 既有設施有餘裕可推遲新增變壓器。更大功率的 shelf、平台削峰、集中式 HVDC、維持低負載插座等均可改變新增數量和受惠位置。驗證實際架規、合格型號、前段拓樸、電池末期測試與驗收後出貨。可比較[台達電](/next?focus=company-delta-electronics)及[Vertiv](/next?focus=company-vertiv)的跨設備交付，再區分 MPS 的晶片與 Vicor 的模組。
