---
schema-version: research-v1
entity-id: product-power-shelf-psu
kind: product
name-zh: "電源供應器與電源架"
aliases:
- "PSU"
- "power shelf"
summary: "將輸入電力轉換成機櫃或伺服器母線電壓。"
definition: "含系統 PSU 及多顆 PSU 並聯供電的機櫃架。"
purpose: "提供機櫃或伺服器的持續與瞬態負載電力。"
boundary: "上游設施備援、機櫃 BBU 與板端轉換有各自交付界線。"
adoption-conditions:
- "對齊輸入、輸出、接頭、運行環境、備援與負載曲線。"
bottlenecks:
- "瞬態、低壓母線電流、氣流與保護協調。"
substitution-limits:
- "配接與輸入類型一致才可比較直接替換；HVDC 需重新驗證整條路徑。"
reviewed: "2026-11-24"
claims:
- id: orv3-shelf-capacity
  statement: "台達 18 kW 1OU AC/DC 電源架滿配 6×3 kW、5+1 時 15 kW，輸出 48／50 VDC。其 33 kW 方案在 5+1 時為 27.5 kW。"
  confidence: well-supported
  conditions:
  - "以所述滿配與單顆 PSU 備援計算。實際可用功率還受輸入、溫度、匯流排與故障域限制。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ocp-delta-18kw-power-shelf
    url: https://www.opencompute.org/marketplace/facilities-physical-infrastructure/delta-18kw-1ou-open-rack-v3-power-shelf/
    locator: "Product Details"
    read-scope: "六槽、最大輸出、5+1、直流輸出。"
    stance: supporting
    applicable-period: "官網列示規格"
  - source-id: delta-33kw-power-shelf
    url: https://www.deltaww.com/en-US/products/power-solutions
    locator: "Power Shelf"
    read-scope: "滿配、PSU 單顆額定及備援容量。"
    stance: supporting
    applicable-period: "所列 33 kW 平台"
- id: power-shelf-efficiency-conditions
  statement: "康舒 19 吋 33 kW 電源架宣稱峰值效率 97.5%；Diablo 400 則把整條電源轉換路徑的最低效率按負載及 AC 輸入分開。"
  confidence: well-supported
  conditions:
  - "整條路徑的要求值與單產品的峰值、實測值口徑不同。須對齊負載點、輸入、供電邊界與風扇損耗才可比較。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ocp-acbel-33kw-power-shelf
    url: https://www.opencompute.org/marketplace/facilities-physical-infrastructure/acbel-19-33kw-power-shelf/
    locator: "Product Details"
    read-scope: "查三相輸入、50 VDC、六顆熱插拔 PSU 和峰值口徑。"
    stance: supporting
    applicable-period: "該 19 吋 1RU 產品"
  - source-id: ocp-diablo-400-power-spec
    url: https://www.opencompute.org/documents/ocp-specification-diablo-400-v0-7-0-final-pdf
    locator: "§7.3.4 End to End Output Power Conversion Efficiency"
    read-scope: "核對 400、415、480 VAC 與 20%、50%、100% 負載表。"
    stance: supporting
    applicable-period: "v0.7.0"
- id: shelf-topology-and-transient
  statement: "台達 33 kW 方案的單顆 PSU 公布 150%／20 ms 瞬態能力。OCP 的另一種 ORV3 設計使用兩組高壓直流輸入，由 shelf 轉換至 48 V 等級。"
  confidence: well-supported
  conditions:
  - "短時間過載不能計入持續輸出。比較兩者須核對上游 AC/DC 的轉換位置、絕緣、保護、接頭及維修程序。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: delta-33kw-power-shelf
    url: https://www.deltaww.com/en-US/products/power-solutions
    locator: "Power Shelf"
    read-scope: "查 PSU 過載時間、熱插拔與 PMC。"
    stance: supporting
    applicable-period: "33 kW 方案"
  - source-id: ocp-orv3-hvdc-100kw-shelf
    url: https://www.opencompute.org/documents/orv3-hvdc-lvdc-100kw-power-shelf-spec-1-0-0-pdf
    locator: "§§3.1、4.2、5.3.1–5.3.3"
    read-scope: "查兩組 DC 輸入、100 kW 輸入接頭上限及輸出 busbar。"
    stance: supporting
    applicable-period: "Rev 1.0"
- id: shelf-demand-transmission
  statement: "若架構與供電邊界相同，備援後需求高於單架可用容量，可能增加電源架或單顆 PSU 容量需求。"
  confidence: inference
  conditions:
  - "改用更高額定 PSU、降低峰均比、提升轉換效率或移動轉換位置，可抵銷單機櫃使用台數。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ocp-delta-18kw-power-shelf
    url: https://www.opencompute.org/marketplace/facilities-physical-infrastructure/delta-18kw-1ou-open-rack-v3-power-shelf/
    locator: "Product Details"
    read-scope: "以額定和備援降額作推論基準。"
    stance: supporting
    applicable-period: "所列 18 kW 方案"
  - source-id: ocp-orv3-hvdc-100kw-shelf
    url: https://www.opencompute.org/documents/orv3-hvdc-lvdc-100kw-power-shelf-spec-1-0-0-pdf
    locator: "§§3.1、4.2"
    read-scope: "作為不同轉換位置的反向情境。"
    stance: supporting
    applicable-period: "Rev 1.0"
gaps:
- status: not-obtained
  reason: "同架構、同負載點和相同溫度的實測功耗、價格與現場換修時間未取得。"
- status: not-public
  reason: "型錄未揭露各客戶合格量、單價與料號收入。"
---

## 定義與用途

機架式 AC/DC power shelf 將多顆 PSU 並聯，經 DC 母線供應同一機櫃的 IT 設備。PSU 做電力轉換，機框負責配接、電流分攤與管理。伺服器內置 PSU 把轉換點移到單機，維修和故障域也跟著改變。板端還有[DC/DC 模組](/next?focus=product-power-module)與[電壓調節晶片](/next?focus=product-pmic-voltage-regulator)。

## 容量、效率與熱

- 台達 18 kW 1OU：6×3 kW，5+1 時供 15 kW，48／50 VDC。台達 33 kW 公布 6×5.5 kW，5+1 時供 27.5 kW。兩者按指定架構核算，還要查機櫃散熱、輸入和保護。
- 康舒的 19 吋 1RU 33 kW 為三相 AC 至 50 VDC，官方列出的 97.5% 是峰值。Diablo 400 v0.7.0 在 400 VAC 的端到端要求於 20%、50%、100% 負載分別為 >95%、>97%、>96.5%。比較成本宜以同一季節與各負載點，換算每小時轉換損耗、冷卻負擔與備用 PSU 數。
- 台達 5.5 kW PSU 的 150%／20 ms 規格用於短暫突波。容量規劃另驗證負載步階、備援切換後的可用瓦數、輸出電壓偏移及保護是否連鎖跳脫。

## 採用條件與限制

熱插拔允許換單顆 PSU，但通常仍要確定有剩餘可用容量、電流分攤、故障隔離與安全程序。5+1 可應付一顆 PSU 失效的設計；兩路市電／UPS 冗餘則看輸入路徑與共用故障點。高壓 DC 架構把前段 AC/DC 移到上游，OCP 的 100 kW HVDC-LVDC 範例仍用架側 DC/DC 給 48 V 等級母線。它與三相 AC shelf 的相容性需逐案驗證。

## 供應角色與公司

[機櫃與系統電源](/next?focus=role-rack-power-supply)內，[台達電](/next?focus=company-delta-electronics)的 18／33 kW 方案與[康舒](/next?focus=company-6282-tw) 19 吋 33 kW 方案提供電源架及 PSU。[光寶科](/next?focus=company-2301-tw)展示 ORv3 電源架、電源模組與備援方案，依相符機架及電氣介面核對指定平台採用。

## 需求如何傳到電源架

推論：若 5+1 後架側供電掉到長時間負載以下，導入可能轉向更多 shelf、每顆更高瓦數或重新分配機櫃。集中式高壓 DC 或更高單顆額定可減少低壓 shelf 數，故應追蹤單架 IT 平均／短暫尖峰、備援規格、通過平台驗證的模組與實際出貨。
