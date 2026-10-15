---
theme: advanced-node-2nm
name_zh: 先進製程節點推進
status: scaling
segments:
- foundry
- equipment
- materials
beneficiaries:
- 2330.TW
- ASML
- 6488.TWO
milestones:
- date: 2026-Q2
  event: 台積電 N2 商業出貨反映於晶圓營收
  evidence: 台積電 2026 Q2 官方財報新聞稿明確揭露 2nm 晶圓營收占比，量產與財務證據可同時核對
  id: n2-commercial-sales
- date: 2026-Q3
  event: 核對後續節點設備採購與製程準備
  evidence: 具名晶圓廠 capex／量產計畫及設備商訂單與驗收；High-NA 合作研發公告不等於量產採用
  id: equipment-readiness
- date: 2027
  event: 待確認 N2 後續變體及背面供電的商業爬坡
  evidence: 晶圓廠逐節點量產揭露、客戶產品交付及營收組合；不再把 GAA 首次商用寫成 2027 才發生
  id: node-variants
assessment:
  summary: 台積電已揭露當季 2nm 晶圓營收占比，支持原商業放量基準；上游採購份額、海外產能與後續節點的良率不能由單季占比推定。
  confidence: well-supported
  evidence:
  - id: tsmc-q2-node-sales
    source_id: tsmc-quarterly-pr
    url: https://pr.tsmc.com/japanese/news/3326
    excerpt: shipments of 2-nanometer accounted for 3% of total wafer revenue
    period: TSMC 2026 Q2，當季晶圓營收占比；期末 2026-06-30
    published: '2026-07-16'
  claims:
  - id: commercial-n2
    statement: 台積電當季已實現 2nm 晶圓收入，支持節點商業出貨；百分比的分母是晶圓營收，不是全部公司營收或市場市占。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - tsmc-q2-node-sales
  conditions:
  - 客戶產品與該節點良率／產能匹配
  - 上游設備與材料具有實際驗收及採購份額
  - 逐節點收入與後續變體不得合併
  gaps:
  - 未公開的逐客戶良率、上游供應商份額與海外廠爬坡仍待核實
  - 未取得同口徑節點商業收入下滑的反向證據
  next_checks:
  - question: 節點放量是否轉為具名上游採購及後續變體收入？
    evidence_required: capex／驗收、逐節點收入與客戶產品交付
  paths:
  - id: foundry-to-equipment
    steps:
    - from: foundry
      to: equipment
      type: upstream
    mechanism: 節點擴產可能驅動已驗收製程設備採購。
    direction: positive
    conditions:
    - 晶圓廠實際擴產
    - 設備供應商有可核對料號與訂單
    claim_ids:
    - commercial-n2
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: n2-commercial-sales
    state: confirmed
    reviewed: '2026-10-07'
    note: 僅確認台積電 2026 Q2 已實現 2nm 晶圓營收，不推定後續變體、各上游公司或海外廠已放量。
    evidence_ids:
    - tsmc-q2-node-sales
    occurred: null
  - milestone_id: equipment-readiness
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 研發與合作不足以證明已驗收的量產設備採購。
    evidence_ids: []
    occurred: null
  - milestone_id: node-variants
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 後續變體及背面供電仍須逐節點交付／收入證據。
    evidence_ids: []
    occurred: null
---

## 題材範圍

以台積電 N2 的 GAA 世代為已商用起點，另追蹤後續變體、背面供電及微影選項。不同廠商的節點名稱不能直接當等效性能比較；2nm 商用也不表示 High-NA EUV 已成必需配置。

## 傳導與受惠條件

題材連接 `foundry / equipment / materials`，再沿 foundry 的下游到運算與網路。2330.TW 對應代工，ASML 對應微影，6488.TWO 對應矽晶圓供應候選。**inference**：節點擴產可能提升設備及材料需求，但認證、採購份額與單位用量需各別查核，不由代工營收推定所有上游公司受惠。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`。**well-supported**：台積電 2026 Q2 官方財報已單列 2nm 晶圓營收占比，滿足商業出貨與量化門檻；因此原先「2027 才達 GAA 量產經濟性」的表述已修為後續變體檢核。[台積電官方財報新聞稿](https://pr.tsmc.com/japanese/news/3326)、[季度資料](https://investor.tsmc.com/english/quarterly-results/2026/q2)。客戶平台、海外產能及後續節點的良率與時程不能由此一次推定；未公開的數字列 **needs verification**。
