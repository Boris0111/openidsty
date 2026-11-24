---
schema-version: research-v1
entity-id: product-rack-pdu
kind: product
name-zh: "機櫃配電單元（rPDU）"
aliases:
- "rack PDU"
- "rPDU"
- "power distribution unit"
summary: "於機架內分配 AC 供電與監控分路。"
definition: "於機架內分配 AC 供電與監控分路。"
purpose: "把單一或分離的 A/B 路由分至指定插座和負載。"
boundary: "與設施 PDU／母線、架內 DC busbar 和機櫃電源架分工。"
adoption-conditions:
- "對齊相別、持續承載、插座、過流保護、通訊與熱。"
bottlenecks:
- "單相超載、插座降額及雙線故障。"
substitution-limits:
- "同一介面、承載、監控和維修權限才比較。"
reviewed: "2026-11-24"
claims:
- id: geist-rpdu-delivery
  statement: "Vertiv Geist UU30009L 垂直 rPDU 提供插座切換及監控，型錄列三相星形 230／415 V、16 A 選項及 C13／C19 插座。"
  confidence: well-supported
  conditions:
  - "須配合正確進線纜、地區規格、相別與分路降額。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-geist-universal-rpdu
    url: https://www.vertiv.com/globalassets/products/critical-power/power-distribution/vertiv-geist-rpdu---brochure.pdf
    locator: "Universal Rack PDU Model Chart，UU30009L"
    read-scope: "查接線選項、額定、分路和插座。"
    stance: supporting
    applicable-period: "該型錄料號"
- id: delta-vilink-rpdu-delivery
  statement: "台達 ViLink Metered rPDU 為架內成品，提供 Ethernet 輸入／分路監測。"
  confidence: well-supported
  conditions:
  - "官方使用手冊描述系列能力；額定與地區版需依個別資料表。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: delta-vilink-rpdu-manual
    url: https://filecenter.deltaww.com/rPDU_Selector/Files/Manual-1-PDUA117BSA23500.pdf
    locator: "§2.1 General Overview"
    read-scope: "查安裝位置、單／三相輸入和監控內容。"
    stance: supporting
    applicable-period: "ViLink Metered 手冊"
- id: rpdu-interface-rating
  statement: "APDU10350ME 同料號的公開配置列 400 V／32 A 與 415 V／30 A 不同 kW 額定。"
  confidence: well-supported
  conditions:
  - "取對應地區接頭與持續載流的額定，不用最大電流乘任意電壓。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: apc-apdu10350me-rpdu
    url: https://www.se.com/sg/en/product/APDU10350ME/apc-netshelter-rack-pdu-advanced-metered-3phase-22-1kw-400v-32a-or-17-3kw-415v-30a-48-outlets-iec309/
    locator: "APDU10350ME Specifications"
    read-scope: "查 400 V 32 A 的 22.1 kW、415 V 30 A 的 17.3 kW 及 48 個插座。"
    stance: supporting
    applicable-period: "APC 料號與區域配置"
- id: rpdu-rack-design-demand
  statement: "若架內 AC 插座、雙路或計量需求增多，可推升相應 rPDU 需求。"
  confidence: inference
  conditions:
  - "整架彙整 DC 供電可減少逐台 AC 插座需求。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: apc-apdu10350me-rpdu
    url: https://www.se.com/sg/en/product/APDU10350ME/apc-netshelter-rack-pdu-advanced-metered-3phase-22-1kw-400v-32a-or-17-3kw-415v-30a-48-outlets-iec309/
    locator: "APDU10350ME Specifications"
    read-scope: "查 400 V 32 A 的 22.1 kW、415 V 30 A 的 17.3 kW 及 48 個插座。"
    stance: supporting
    applicable-period: "APC 料號與區域配置"
gaps:
- status: not-obtained
  reason: "同場址運行數據、價格、維護工時及具名採用仍缺。"
- status: not-public
  reason: "未見產品收入及客戶採用占比。"
---

## 定義與用途

rPDU 把上游 AC 饋線分到機櫃設備插座，可帶分段保護、電表或遙控。設施 PDU／busway 送電到機櫃附近，DC power shelf 提供轉換。

## 規格與成本

UU30009L 的 16 A 星形 230／415 V 與 APC APDU10350ME 的 400 V／32 A 22.1 kW 或 415 V／30 A 17.3 kW 是各自列示的配置。連續負載、每相及插座降額、A/B 路各自餘裕和插座類型需一起查。

## 採用條件與限制

對比 basic、計量及可遙控 rPDU 必須核對功率、監控與作業權限。A/B 兩路做容錯時，單路需獨立負擔目標負載。串接式幹線、吊掛分支與機櫃 PDU 的容量受共同瓶頸，不累加。

## 供應角色與公司

[台達電](/next?focus=company-delta-electronics)供應 ViLink Metered；[Vertiv](/next?focus=company-vertiv)Geist 提供插座管理與多種配接。Schneider Electric 旗下 APC 料號用於同介面比較。

## 需求如何傳導

推論：機櫃增加或計量顆粒度變細可能帶動 rPDU。若系統集中到 DC 母線、並降低伺服器逐台 AC 供電，部分需求會轉往整流和直流配接。
