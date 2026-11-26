---
schema-version: research-v1
entity-id: product-datacenter-switchgear
kind: product
name-zh: "資料中心開關與配電盤"
aliases:
- "switchgear"
- "switchboard"
summary: "組合斷路器、隔離、母線及保護的案場配電設備。"
definition: "組合斷路器、隔離、母線及保護的案場配電設備。"
purpose: "切換和隔離饋線、保護局部故障並支援配電分段。"
boundary: "變壓器改變電壓，UPS 提供調節及暫時續供，機櫃 PDU 下放插座。"
adoption-conditions:
- "核對電壓、連續電流、故障耐受／開斷、保護協調和現場測試。"
bottlenecks:
- "案場短路電流、電弧風險、停電維修與交期。"
substitution-limits:
- "在同一電壓及防護級距內比較，接線位置改變時重新審查。"
reviewed: "2026-11-24"
claims:
- id: powerboard-switchgear-delivery
  statement: "Vertiv PowerBoard 低壓開關設備可配置 800–6,300 A，含分隔及依案場配置的保護。"
  confidence: well-supported
  conditions:
  - "是低壓產品範圍；額定、預期短路電流及分隔型式須按選型。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-powerboard-lv-switchgear
    url: https://www.vertiv.com/en-asia/products-catalog/critical-power/switchgear/vertiv-ei-low-voltage-switchgear-iec/
    locator: "Overview、Features"
    read-scope: "核對低壓額定電流範圍與保護繼電器、箱體。"
    stance: supporting
    applicable-period: "PowerBoard 低壓產品頁"
- id: teco-switchgear-delivery
  statement: "東元交付資料中心中低壓開關設備，公開頁列設計、製造、安裝與維護。"
  confidence: well-supported
  conditions:
  - "資料中心解決方案可支持能力，指定案場型號和容量須另驗。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-datacenter-solutions
    url: https://www.teco.com.tw/en-us/solution/data-center/
    locator: "MV & LV Switchgear"
    read-scope: "查製造、安裝、維修與整合責任。"
    stance: supporting
    applicable-period: "東元查核日解決方案頁"
- id: switchgear-fault-coordination
  statement: "Schneider MCSeT 24 kV 櫃列最高 31.5 kA／3 s 短時耐受；這一值用於故障電流及保護協調，連續容量須看另一額定。"
  confidence: well-supported
  conditions:
  - "中壓短時耐受與低壓連續 A 的口徑不同。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: schneider-mcset-24kv-ratings
    url: https://productinfo.se.com/mcset_24kv_installation_guide/bqt6904400_mcset_installation-guide/English/BQT6904400_MCSeT4_Installation_Guide_DD00597955.xml/%24/TPC_MCSeT4IG_MCSeTCubicleRatingsCPT_DD00739416
    locator: "MCSeT Cubicle Ratings"
    read-scope: "核對 24 kV 櫃與最高 31.5 kA／3 s，按型號適用。"
    stance: supporting
    applicable-period: "MCSeT 24 kV 安裝指南"
  - source-id: vertiv-powerboard-lv-switchgear
    url: https://www.vertiv.com/en-asia/products-catalog/critical-power/switchgear/vertiv-ei-low-voltage-switchgear-iec/
    locator: "Overview、Features"
    read-scope: "核對低壓額定電流範圍與保護繼電器、箱體。"
    stance: supporting
    applicable-period: "PowerBoard 低壓產品頁"
- id: switchgear-demand-by-feeders
  statement: "新增變壓器、備援匯流排或出線可能增加開關櫃需求。"
  confidence: inference
  conditions:
  - "可沿用既有備用櫃或整併出線時，新增量可較小；需確認單線圖及送電交期。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: schneider-mcset-24kv-ratings
    url: https://productinfo.se.com/mcset_24kv_installation_guide/bqt6904400_mcset_installation-guide/English/BQT6904400_MCSeT4_Installation_Guide_DD00597955.xml/%24/TPC_MCSeT4IG_MCSeTCubicleRatingsCPT_DD00739416
    locator: "MCSeT Cubicle Ratings"
    read-scope: "核對 24 kV 櫃與最高 31.5 kA／3 s，按型號適用。"
    stance: supporting
    applicable-period: "MCSeT 24 kV 安裝指南"
  - source-id: teco-datacenter-solutions
    url: https://www.teco.com.tw/en-us/solution/data-center/
    locator: "MV & LV Switchgear"
    read-scope: "查製造、安裝、維修與整合責任。"
    stance: supporting
    applicable-period: "東元查核日解決方案頁"
gaps:
- status: not-obtained
  reason: "未取得同案場短路試驗、價格及進場組裝工時。"
- status: not-public
  reason: "所讀型錄未揭露合格專案／型號收入。"
---

## 定義與用途

中壓櫃可位於接入後、[變壓器](/next?focus=product-datacenter-transformer)一次側，低壓櫃可位於二次側及 UPS 前後。由出線、母聯和保護繼電器分隔故障；場址配電盤跟架內插座有不同驗收範圍。

## 規格與成本

Vertiv PowerBoard 低壓列 800–6,300 A。MCSeT 24 kV 的最高 31.5 kA／3 s 是短時耐受。估成本要對齊可用容量、短路等級、隔間、電弧防護、插拔與停電維修，並另計保護整定及測試。

## 採用條件與限制

GIS／AIS 或同級抽出式方案須逐一對齊接頭、接地、絕緣、故障開斷及運維。不同電壓的櫃各有適用位置，UPS 旁路也只是同系統另一條供電路徑。

## 供應角色與公司

[東元](/next?focus=company-1504-tw)提供中低壓設備、設計至維護；[Vertiv](/next?focus=company-vertiv)PowerBoard 提供低壓成套交付。Schneider Electric 的 MCSeT 24 kV 作中壓級距比較，對照單線圖、規範和料號當地適用性。

## 需求如何傳導

推論：新增設備需求取決於變壓器、饋線與冗餘分段數。既有備用間隔或整併出線可延緩新增，需追蹤案場接入條件、核定單線圖、開關櫃製造測試與通電。
