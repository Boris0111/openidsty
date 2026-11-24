---
schema-version: research-v1
entity-id: product-rack-battery-backup
kind: product
name-zh: "機櫃電池備援單元（BBU）"
aliases:
- "BBU"
- "battery backup unit"
summary: "帶有電池、BMS、充放電和控制功能的機架備援單元。"
definition: "帶有電池、BMS、充放電和控制功能的機架備援單元。"
purpose: "在主要供電中斷後短暫維持指定 DC 母線。"
boundary: "電源架持續供電與回充，BBU 接管架側供電；UPS 保護的設施回路另列。"
adoption-conditions:
- "對齊母線電壓、接頭、備援信號、末期放電及場址安全要求。"
bottlenecks:
- "電池老化、健康檢測、共享母線容量和熱。"
substitution-limits:
- "需核對保護範圍與故障時間窗才比較 UPS／BBU／CBU。"
reviewed: "2026-11-24"
claims:
- id: orv3-bbu-runtime-and-health
  statement: "ORv3 v1.4 電池包要求在 35°C、至少四年期間、達 PCM 輸入門檻時可 3 kW 放電至少四分鐘。SOH 測試中／後另外設計 3 kW 至少 90 秒條件。"
  confidence: well-supported
  conditions:
  - "電池包設計窗口、健康檢查保留量與案場驗收條件應分列。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ocp-orv3-bbu-module
    url: https://www.opencompute.org/documents/open-rack-v3-bbu-module-spec-1-4-pdf/
    locator: "§§4.2.1、4.2.4、4.3 Table 2 與 SOH"
    read-scope: "查 3 kW 電池包壽命條件、DC 輸出與測試排程。"
    stance: supporting
    applicable-period: "v1.4，2023-09-12"
- id: liteon-rack-bbu-delivery
  statement: "光寶 2025 Datacloud 展示 72 kW BBU，與獨立 capacitor shelf 及電源架分項列出。"
  confidence: well-supported
  conditions:
  - "展示支持產品範圍，續航、電池狀態及指定平台採用另核。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: liteon-datacloud-2025-power
    url: https://www.liteon.com/en/news/press-center/content/liteon-datacloudglobalcongress
    locator: "2025 Datacloud 產品列表"
    read-scope: "查 72 kW BBU 與另一 capacitor shelf。"
    stance: supporting
    applicable-period: "2025-06 活動公告"
- id: vertiv-power-rack-bbu-design
  statement: "Vertiv 公布 800 VDC power rack 內建 BBU，設計 hold-up 至少 50 秒。"
  confidence: well-supported
  conditions:
  - "源為整合設計，與機櫃低壓 BBU、同負載實測、銷售及出貨分開。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: vertiv-800vdc-power-rack-2026
    url: https://www.vertiv.com/en-in/about/news-and-events/news-releases/2026/vertiv-advances-800-vdc-power-architectures-to-support-growing-ai-data-center-demands/
    locator: "800 VDC power rack"
    read-scope: "查整合 BBU、設計 hold-up 時間及機架與 IT 轉換的分離。"
    stance: supporting
    applicable-period: "2026 供應商公告"
- id: bbu-design-demand
  statement: "若備援由設施移到架側，維持同一保護時間與故障容錯可增加有 BMS 的架側電池組需求。"
  confidence: inference
  conditions:
  - "保留集中式 UPS、降低需續供負載或採其他合格儲能，可抵銷新增；查同等失效情境。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ocp-orv3-bbu-module
    url: https://www.opencompute.org/documents/open-rack-v3-bbu-module-spec-1-4-pdf/
    locator: "§§4.2.1、4.2.4、4.3 Table 2 與 SOH"
    read-scope: "查 3 kW 電池包壽命條件、DC 輸出與測試排程。"
    stance: supporting
    applicable-period: "v1.4，2023-09-12"
  - source-id: liteon-datacloud-2025-power
    url: https://www.liteon.com/en/news/press-center/content/liteon-datacloudglobalcongress
    locator: "2025 Datacloud 產品列表"
    read-scope: "查 72 kW BBU 與另一 capacitor shelf。"
    stance: supporting
    applicable-period: "2025-06 活動公告"
  - source-id: vertiv-800vdc-power-rack-2026
    url: https://www.vertiv.com/en-in/about/news-and-events/news-releases/2026/vertiv-advances-800-vdc-power-architectures-to-support-growing-ai-data-center-demands/
    locator: "800 VDC power rack"
    read-scope: "查整合 BBU、設計 hold-up 時間及機架與 IT 轉換的分離。"
    stance: supporting
    applicable-period: "2026 供應商公告"
gaps:
- status: not-obtained
  reason: "公開資料未取得一致負載、溫度及末期續航價格。"
- status: not-public
  reason: "展示或設計公告未提供具名驗收、料號出貨與收入。"
---

## 定義與用途

電池平時由系統維持電量，依母線狀態與管理訊號在中斷時啟動放電。BMS 監測溫度、荷電與健康度。[電源架](/next?focus=product-power-shelf-psu)偵測或傳遞供電失效，兩者驗證切換、回充與遠端告警。

## 規格與成本

ORv3 v1.4 該 3 kW 模組的 47.75 V 是 50% 負載設計值。電池包四分鐘規格附 35°C、PCM 門檻及壽命條件；90 秒是 SOH 檢測期間或剛完成的另外要求。比較成本另核對備用顆數、換修、消防及回充週期。

## 採用條件與限制

同架 5+1 等級需考慮正在做 SOH 的模組、接頭熱、電芯老化及告警。若以機櫃 BBU 承接部分備援，必須核對 UPS 原先保護的網路／控制／冷卻是否另有供電。CBU 依負載與時間窗比較。

## 供應角色與公司

[光寶科](/next?focus=company-2301-tw)公開展示 72 kW BBU；[Vertiv](/next?focus=company-vertiv)公布的是較高電壓 power rack 的整合 BBU。兩者交付條件不同。OCP 文件提供 ORv3 基準，供應商自稱符合仍需料號與整合驗收。

## 需求如何傳導

推論：轉向架側備援可增加 BBU 配置，集中式備援或可用 CBU 儲能也可承接部分需求。追蹤負載階躍、合格續航、SOH 時的餘裕及維護策略。
