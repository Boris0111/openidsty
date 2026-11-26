---
schema-version: research-v1
entity-id: product-facility-ups
kind: product
name-zh: "設施不斷電系統（UPS）"
aliases:
- "UPS"
- "uninterruptible power supply"
summary: "在設施 AC 路徑上提供受控電力及電池續供。"
definition: "在設施 AC 路徑上提供受控電力及電池續供。"
purpose: "短暫維持選定的關鍵負載，支援電力中斷或切換。"
boundary: "連線式 UPS 保護 AC 饋線與選定負載，BBU 多為接續單架 DC 母線。"
adoption-conditions:
- "確認 kW、kVA、負載功因、雙路與旁路、電池末期備援時間。"
bottlenecks:
- "電池老化、過載、維護旁路與共用故障。"
substitution-limits:
- "UPS 與架側備援可搭配；需同時涵蓋負載、介面與失效模式才有比較基礎。"
reviewed: "2026-11-24"
claims:
- id: trinergy-ups-delivery
  statement: "Vertiv Trinergy 480 VAC 規格列 1,500／2,000／2,500 kW 標稱及 35°C 最大有功功率。"
  confidence: well-supported
  conditions:
  - "這是指定機型與溫度的功率能力，續航取決於電池配置。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-trinergy-ups-brochure
    url: https://www.vertiv.com/4a095b/globalassets/shared/vertiv-trinergy-ups-brochure-sl-71331.pdf
    locator: "Technical Data，Active power／Output"
    read-scope: "查 35°C、480 VAC 的 1,500／2,000／2,500 kW 配置。"
    stance: supporting
    applicable-period: "SL-71331、該機型表"
- id: modulon-dph-ups-delivery
  statement: "台達 Modulon DPH v3.2 提供模組化三相 UPS，含可熱插拔關鍵模組，規格列 300／500／600 kVA 級距。"
  confidence: well-supported
  conditions:
  - "需按型號、功率因數與當地版核對 kW 及旁路。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: delta-modulon-dph-ups
    url: https://filecenter.deltaww.com/Products/download/07/070103/Catalogue/Leaflet_UPS_DPH-300-500-600kVA_en_v3.2.pdf
    locator: "Features／Technical Specifications"
    read-scope: "查 DPH 輸出額定、可熱插拔模組和 normal／ECO 分列。"
    stance: supporting
    applicable-period: "v3.2"
- id: ups-backup-path-and-maintenance
  statement: "Galaxy VX 操作文件區分在線雙變換、電池與外部維修旁路；在該產品的維修旁路中，電池不可作為備用電源。"
  confidence: well-supported
  conditions:
  - "旁路、雙路冗餘與模組熱插拔須逐一看失效時可用的供電路徑。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: schneider-galaxy-vx-ups-modes
    url: https://productinfo.se.com/galaxyvx_ul/990-914303-energy-storage-system-for-ul9540-galaxy-vx-ups-and-galaxy-lithium-ion-battery-cabinets-operation/English/990-914303_EN.pdf
    locator: "Operation Modes、Maintenance Bypass、Battery Test"
    read-scope: "查雙變換及電池供電，維護旁路的備援界線。"
    stance: supporting
    applicable-period: "990-914303_EN，Galaxy VX 1250／1500 kW I/O"
  - source-id: delta-modulon-dph-ups
    url: https://filecenter.deltaww.com/Products/download/07/070103/Catalogue/Leaflet_UPS_DPH-300-500-600kVA_en_v3.2.pdf
    locator: "Features／Technical Specifications"
    read-scope: "查 DPH 輸出額定、可熱插拔模組和 normal／ECO 分列。"
    stance: supporting
    applicable-period: "v3.2"
- id: ups-demand-capacity-and-runtime
  statement: "若需要維持相同的備援時間與維修容錯，受保護的 IT 與設施負載提升可增加 UPS 功率級和電池需求。"
  confidence: inference
  conditions:
  - "負載分級、架側備援、既有容量和供電拓樸可抵銷。需核對實配末期續航及實際故障域。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-trinergy-ups-brochure
    url: https://www.vertiv.com/4a095b/globalassets/shared/vertiv-trinergy-ups-brochure-sl-71331.pdf
    locator: "Technical Data，Active power／Output"
    read-scope: "查 35°C、480 VAC 的 1,500／2,000／2,500 kW 配置。"
    stance: supporting
    applicable-period: "SL-71331、該機型表"
  - source-id: schneider-galaxy-vx-ups-modes
    url: https://productinfo.se.com/galaxyvx_ul/990-914303-energy-storage-system-for-ul9540-galaxy-vx-ups-and-galaxy-lithium-ion-battery-cabinets-operation/English/990-914303_EN.pdf
    locator: "Operation Modes、Maintenance Bypass、Battery Test"
    read-scope: "查雙變換及電池供電，維護旁路的備援界線。"
    stance: supporting
    applicable-period: "990-914303_EN，Galaxy VX 1250／1500 kW I/O"
gaps:
- status: not-obtained
  reason: "同案場電池容量、溫度、末期測試、維修可用率和 TCO 未取得。"
- status: not-public
  reason: "型錄未揭露個別訂單及備援配置的產品營收。"
---

## 定義與用途

典型在線雙變換 UPS 以整流器、DC link 和逆變器向 AC 應用供電。電源中斷時，電池接手餵入 DC link；設施輸入、維護旁路和受保護饋線的故障域各需核對。

## 規格與成本

同一負載情境先對齊 kW、kVA、功因、波形和運行溫度，再用電池化學、端電壓、溫度與老化條件對照續航。例：600 kW 連續運行 5 分鐘至少需 50 kWh 的 AC 輸出能量，實際儲能還要計入逆變損耗、放電能力及末期容量。Trinergy 規格中的 35°C 機型功率須與可用電池配置配對。

## 採用條件與限制

對照同一負載及備援時間，再看一個模組／整個輸入路徑失效後能否繼續供電。Galaxy VX 的外部維護旁路不提供電池續供。UPS 與 BBU 比較還需核對受保護負載是否含網路、泵與控制設備，以及市電回復和發電機接手時序。

## 供應角色與公司

[台達電](/next?focus=company-delta-electronics)的 Modulon DPH 與 [Vertiv](/next?focus=company-vertiv)的 Trinergy 均提供設施端三相成品。Schneider Electric Galaxy VX 作同功能比較，需按案場對齊電壓、容量、旁路和電池標準。

## 需求如何傳導

推論：新增受保護容量與續航要求可拉動 UPS 和電池。若既有 UPS 仍有合格容量、現場分級備援或部分負載由架側備援，既有設備的增量會收斂。應追蹤受保護清單、末期續航與切換驗收。
