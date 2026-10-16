---
theme: cpo-silicon-photonics
name_zh: 共同封裝光學與矽光子
status: validating
segments:
- networking
- advanced-packaging
- compute
beneficiaries:
- AVGO
- MRVL
- 2330.TW
- 3081.TWO
- 4979.TWO
milestones:
- date: 2026
  event: 核對商用 CPO 交換器及具名採用者的導入階段
  evidence: NVIDIA 2026-05-31 公告列出 Spectrum-X Photonics 生產與 CoreWeave、Lambda、Oracle 採用者；逐案補客戶驗收及實際部署資料
  id: commercial-adoption
- date: 2026-Q4
  event: 待確認 CPO 封裝的量產訂單與出貨量化
  evidence: 封裝廠財報或法說會明確區分 CPO 訂單、出貨或收入；僅有產能投入不足以視為完成
  id: packaging-volume
- date: 2027
  event: 觀察可插拔光模組與 CPO 的方案分工
  evidence: 具名雲端業者採購規格、光學連接距離及光模組廠產品收入，需對照相同平台與使用場景
  id: optics-mix
assessment:
  summary: 商用 CPO 產品已出貨及生產；原 validating 表示量化放量證據仍有限，不能把商業出貨描述成純研究，也不能以 AI 網路總收入升級狀態。
  confidence: well-supported
  evidence:
  - id: broadcom-shipping
    source_id: broadcom-cpo-release
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024
    excerpt: now shipping Tomahawk® 6 – Davisson
    period: Broadcom TH6-Davisson 商用 CPO 交換器公告
    published: '2025-10-08'
  - id: nvidia-production
    source_id: nvidia-photonics-release
    url: https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory
    excerpt: NVIDIA Spectrum-X Ethernet Photonics — now in production
    period: NVIDIA 2026-05-31 生產／採用公告，非 CPO 獨立收入
    published: '2026-05-31'
  claims:
  - id: commercial-cpo
    statement: Broadcom 公告出貨、NVIDIA 公告生產，支持已有商業產品；尚不能推出所有採用者已完成現場驗收或量化大規模部署。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - broadcom-shipping
    - nvidia-production
  conditions:
  - 具名客戶的實際驗收與部署可確認
  - 平台距離、功耗、良率及維修條件適配
  - 財報或法說會能區分 CPO 訂單／出貨與其他網路產品
  gaps:
  - 未取得可分辨 CPO 的量化財報收入或放量訂單
  - 候選光通訊公司的實際產品適配與得標尚待核實
  - 未取得具名客戶轉回可插拔方案的可核對反向證據
  next_checks:
  - question: 生產公告是否轉為具名客戶量化部署？
    evidence_required: 客戶驗收、部署量與可區分 CPO 的收入／出貨
  paths:
  - id: optics-to-packaging
    steps:
    - from: networking
      to: advanced-packaging
      type: theme
      via: cpo-silicon-photonics
    mechanism: 光學引擎靠近封裝可能增加整合需求，同時改變可插拔產品分工。
    direction: mixed
    conditions:
    - 採用共同封裝方案
    - 封裝供應商取得真實訂單
    claim_ids:
    - commercial-cpo
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: commercial-adoption
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 已有產品生產公告，但逐案客戶驗收及實際部署仍未核對。
    evidence_ids:
    - broadcom-shipping
    - nvidia-production
    occurred: null
  - milestone_id: packaging-volume
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 產能投入與生產公告不等於封裝收入量化。
    evidence_ids: []
    occurred: null
  - milestone_id: optics-mix
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 需同平台與距離口徑的採購及產品收入。
    evidence_ids: []
    occurred: null
technical-profile:
  product-boundary: 交換 ASIC、DSP、光引擎／模組、封裝與系統整合分層；CPO 是整合路線，CMIS 是管理介面。
  adoption-conditions:
  - 按 scale-up／scale-out／跨機房的距離、拓樸與通道預算確認適用性。
  - 核對熱介面、測試點、管理能力、維修策略及系統互通，不能只比光引擎耗電。
  bottlenecks:
  - 共同封裝良率、光纖連接、散熱與可維修性會限制整機交付；模組介面存在不是客戶驗收證明。
  substitution-limits:
  - 銅纜、可插拔、LPO 與 CPO 需比較完整鏈路及維護成本；不能由單一 CPO 出貨推定全體光模組被替代。
  claims:
  - id: cpo-interface-scope
    statement: OIF 的 3.2T CPO IA 定義特定模組範圍與熱／測試介面；不是所有網路範圍的通用採用保證。
    confidence: well-supported
    evidence:
    - document-id: oif-cpo-module
      version-id: module-01-0
      locator: module-scope
    - document-id: oif-cpo-module
      version-id: module-01-0
      locator: thermal-interface
  - id: cmis-is-management
    statement: CMIS 的 Purpose and Scope 處理管理互動；不能替代光學、電氣與系統互通測試。
    confidence: well-supported
    evidence:
    - document-id: oif-cmis
      version-id: revision-5-4
      locator: management-scope
  evidence-gaps:
  - 尚未取得候選平台的完整通道、良率、維修／互通報告與分產品量化收入；只核讀所列章節。
  assessment-claim-ids:
  - commercial-cpo
  reviewed: '2026-10-16'
---

## 題材範圍

將光學引擎靠近交換器／運算封裝，以縮短高功耗的電氣傳輸路徑。矽光子是實現光學整合的技術，CPO 是封裝配置，兩者不是同義詞；可插拔光模組、LPO 與 CPO 仍可能按距離和可維修性分工。[Broadcom CPO 技術](https://www.broadcom.com/info/optics/cpo)。

## 傳導與受惠條件

`networking ↔ cpo-silicon-photonics ↔ advanced-packaging / compute` 是題材擴散，並非新增上下游邊。AVGO、MRVL 對應交換器／光學訊號處理，2330.TW 對應封裝整合；3081.TWO、4979.TWO 是光通訊候選角色。**inference**：光學布局轉換增加某些元件需求，也可能替代既有可插拔產品；`beneficiaries` 表示追蹤候選，個別 CPO 訂單與產品適配仍列 **needs verification**。

## 狀態判定依據

查核日期：2026-10-07。保留 `validating` 作為本檔可核對的公開證據等級。**well-supported**：Broadcom 已公告 CPO 商用品出貨，NVIDIA 亦公告生產及具名採用者，故不能描述成只有研究或樣品。仍未取得可分辨 CPO 的財報／法說會量化放量資料，不以 AI 網路總收入代替 CPO 收入，也不升為 `scaling`；這是證據限制，不是宣稱完全沒有商業出貨。[Broadcom 商用 CPO 公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)、[NVIDIA 生產與採用者公告](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory)。後續取得 CPO 訂單及量化出貨證據才升級；維修成本或客戶轉回可插拔方案則重新評估。
