---
theme: hbm4
name_zh: HBM4 世代轉換
status: scaling
segments:
- memory
- advanced-packaging
- compute
beneficiaries:
- 000660.KS
- 005930.KS
- MU
- 2330.TW
milestones:
- date: 2026-Q1
  event: 核對 HBM4 的客戶認證與商業出貨
  evidence: Micron FY2026 Q3 財報公告確認 HBM4 高量出貨；SK hynix 2026 Q2 財報說明客戶規格與出貨，不能用 HBM3E 認證代替 HBM4
  id: customer-shipment
- date: 2026-Q3
  event: 待確認不同 HBM4 供應商的實際分配與收入
  evidence: 供應商分世代收入／出貨及客戶認證揭露；HBM 整體市佔、送樣或合作備忘錄不足以證明 HBM4 份額
  id: supplier-allocation
- date: 2026
  event: 檢查轉產 HBM 是否排擠其他 DRAM 供給
  evidence: 供應商晶圓產能配置與其他 DRAM 出貨／價格揭露交叉核對；不因 HBM 缺貨就推定所有利基記憶體漲價
  id: dram-displacement
assessment:
  summary: 原 scaling 基準有 HBM4 高量出貨及量化收入依據；各供應商份額、堆疊規格與 HBM4E 路線仍需分別驗證。
  confidence: well-supported
  evidence:
  - id: micron-volume-shipments
    source_id: micron-earnings-research
    url: https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx
    excerpt: HBM4, built on 1-beta DRAM technology, is in high-volume shipments for our lead customer's platform
    period: Micron FY2026 Q3，財報期末 2026-05-28；不是曆年第三季
    published: '2026-06-24'
  - id: micron-hbm4-revenue
    source_id: micron-hbm4-remarks
    url: https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe
    excerpt: we have already shipped over $1 billion in HBM4 revenue
    period: Micron FY2026 Q3 prepared remarks；累計措辭，非單季專屬收入
    published: '2026-06-24'
  - id: hynix-commercial-shipment
    source_id: sk-hynix-earnings-research
    url: https://news.skhynix.com/en/q2-2026-business-results/
    excerpt: The company began mass shipments of HBM4 in the second quarter
    period: SK hynix 2026 Q2，產品出貨，非逐客戶份額
    published: '2026-07-29'
  claims:
  - id: commercial-hbm4
    statement: Micron 與 SK hynix 的公開揭露支持 HBM4 商業出貨；Micron 法說會原段落另有已實現收入措辭，不能把它換算成未揭露的單季收入。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - micron-volume-shipments
    - micron-hbm4-revenue
    - hynix-commercial-shipment
  conditions:
  - 供應商實際完成特定平台的 HBM4 規格與認證
  - base die／先進封裝產能及良率能支援交付
  - 各世代收入與各客戶分配採同一口徑
  gaps:
  - 尚未取得逐供應商 HBM4 份額、16-Hi 認證與 HBM4E 交付資料
  - 尚未取得同口徑反向商業出貨證據
  - 法說會量化措辭的原檔與精確收入起迄仍需再次核對，不能改為未揭露的單季值
  next_checks:
  - question: 高量出貨是否擴及更多已認證平台？
    evidence_required: 分世代收入／出貨、具名客戶認證與原始法說文件
  paths:
  - id: memory-to-packaging
    steps:
    - from: memory
      to: advanced-packaging
      type: downstream
    mechanism: HBM4 平台轉換可能增加共同封裝與 base die 需求。
    direction: positive
    conditions:
    - 採用該封裝方案
    - 實際採購與良率可核對
    claim_ids:
    - commercial-hbm4
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: customer-shipment
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 高量出貨有基準證據，但原預期時間與各客戶認證未完整核對。
    evidence_ids:
    - micron-volume-shipments
    - hynix-commercial-shipment
    occurred: null
  - milestone_id: supplier-allocation
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 整體 HBM 或公司總營收不能證明 HBM4 分配。
    evidence_ids: []
    occurred: null
  - milestone_id: dram-displacement
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 需晶圓配置與其他 DRAM 供給／價格交叉核對。
    evidence_ids: []
    occurred: null
---

## 題材範圍

追蹤 HBM4 的介面、邏輯 base die、堆疊與客戶平台轉換，不將 HBM4E 或更高堆疊層數的 roadmap 混成已完成的 HBM4 量產。財報年度與曆年季度不同，里程碑按曆年安排，來源保留原財報期間。

## 傳導與受惠條件

`memory → advanced-packaging ← compute` 表示記憶體及運算晶片匯入共同封裝，題材把記憶體廠及晶片平台連起來；圖上的實際上下游仍依各環節 frontmatter 遍歷。000660.KS、005930.KS、MU 對應 HBM 供應，2330.TW 的機會取決於 base die 與封裝分工。**inference**：更高記憶體需求不保證每一家供應商有同等份額，台灣傳統 DRAM／控制器公司也不因此變成 HBM4 製造商。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`。**well-supported**：Micron FY2026 Q3 公告明確確認 HBM4 高量出貨，其同次法說會 prepared remarks 另量化已實現的 HBM4 收入，滿足商業出貨及財務量化門檻；SK hynix 2026 Q2 資料提供另一供應商的商業出貨佐證。[Micron 財報公告](https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx)、[同次法說會量化資料](https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe)、[SK hynix 財報](https://news.skhynix.com/en/q2-2026-business-results/)。本檔保留證據期間與來源，不複製收入數字。供應商份額、16-Hi 認證與 HBM4E 時程各自待查，不能由題材整體放量推定全部達成。
