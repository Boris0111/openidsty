---
theme: power-bottleneck
name_zh: 資料中心電力瓶頸
status: scaling
segments:
- datacenter
- power
beneficiaries:
- VRT
- 2308.TW
- MSFT
milestones:
- date: 2026
  event: 核實電網與設施交付對機房部署的限制
  evidence: IEA 能源與 AI 報告、具名公用事業併網時程及雲端業者新建案交付說明，區分電力與其他設備限制
  id: grid-deployment-limit
- date: 2026-Q4
  event: 待核對具名 PPA／自備電力方案與實際投產
  evidence: 合約公告、許可、併網與上線 IT 容量交叉核對；簽 PPA 不等於取得即時可用電力，不宣稱已成全市場標準
  id: ppa-delivery
- date: 2027
  event: 追蹤供電效率與負載彈性是否改變採購
  evidence: 具名機房標案的效率／備援／調度要求與設備訂單；技術建議不能代替正式採購規格
  id: flexible-power-procurement
assessment:
  summary: 供電與關鍵基礎設施採購已有商業收入脈絡，保留原 scaling 範圍；設備收入不表示電網瓶頸已解決，也不能把所有雲端容量限制都歸因於電力。
  confidence: inference
  evidence:
  - id: vertiv-infrastructure-sales
    source_id: sec-search
    url: https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm
    excerpt: Net sales of $3,274 million
    period: Vertiv 2026 Q2，含熱管理與服務的公司整體收入
    published: '2026-07-29'
  - id: microsoft-capacity-limit
    source_id: ir-microsoft
    url: https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4
    excerpt: demand continues to exceed available supply
    period: Microsoft FY2026 Q4，2026-07-29 法說會；整體部署容量限制
    published: '2026-07-29'
  claims:
  - id: equipment-commercial-context
    statement: Vertiv 已有關鍵基礎設施商業收入，支持設備持續採購脈絡；資料口徑含熱管理與服務，不能全算電力瓶頸收入。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - vertiv-infrastructure-sales
  - id: capacity-not-resolved
    statement: 微軟仍描述整體供需容量限制，不能因設備收入或投資成長便判定部署瓶頸已解除；法說措辭亦未將全部限制歸因電力。
    stance: counter
    confidence: well-supported
    evidence_ids:
    - microsoft-capacity-limit
  conditions:
  - 具名機房限制確實來自併網、供電或相應設施
  - 採購與設備交付能對應該瓶頸
  - PPA、許可、併網與實際上線容量分開確認
  gaps:
  - 缺少逐案電力與其他設備限制的分解
  - 未取得候選設備公司各自的電力產品收入與 PPA 即時可用容量
  next_checks:
  - question: 供電改善是否讓具名機房如期上線？
    evidence_required: 公用事業併網、許可、交付及 IT 上線容量的同案紀錄
  paths:
  - id: power-to-deployment
    steps:
    - from: power
      to: datacenter
      type: downstream
    mechanism: 供電改善可能解除部署限制；交付延遲也可能延後機櫃需求。
    direction: mixed
    conditions:
    - 同案確屬電力限制
    - 供電方案可交付且取得許可
    claim_ids:
    - equipment-commercial-context
    - capacity-not-resolved
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: grid-deployment-limit
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 雲端整體容量限制有描述，仍缺逐案電網／其他設施限制分解。
    evidence_ids:
    - microsoft-capacity-limit
    occurred: null
  - milestone_id: ppa-delivery
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 簽約不等於可立即供電，仍需許可／併網與實際容量。
    evidence_ids: []
    occurred: null
  - milestone_id: flexible-power-procurement
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 技術建議不足以證明正式標案採購。
    evidence_ids: []
    occurred: null
technical-profile:
  product-boundary: 電網併接、設施供電、機櫃電源與 IT 上線是不同交付節點；PPA 簽約不是即時可用電力。
  adoption-conditions:
  - 逐案核對許可、併網排程、備援、設備交付與實際 IT 上線容量。
  - 負載彈性與儲能須符合電網及場址條件，技術建議尚需轉為採購與操作要求。
  bottlenecks:
  - 電網排隊、變壓器／開關設備及施工交付均可能限制部署；雲端總容量限制不能全歸因於電力。
  substitution-limits:
  - 效率改善或提高配電電壓不能自動代替新增併網容量；發電、儲能與 PPA 的時間及許可條件不同。
  claims:
  - id: grid-and-flexibility
    statement: IEA 公開摘要討論電網瓶頸與負載彈性，屬跨案分析及建議，不能證明個別機房已獲許可。
    confidence: well-supported
    evidence:
    - source-id: iea-energy-ai-technical
      url: https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary
      locator: Grid bottlenecks and flexibility
      read-scope: 已讀指定公開段落；未取得客戶設計、認證或量產測試文件。
  evidence-gaps:
  - 缺少同案公用事業併網、許可、交付與上線 IT 容量串接紀錄；設備總收入與單案限制分開。
  assessment-claim-ids:
  - equipment-commercial-context
  - capacity-not-resolved
  reviewed: '2026-10-16'
---

## 題材範圍

追蹤併網、輸配電、備援與電力轉換的限制，以及解除限制所形成的設備採購。狀態指「瓶頸對應的商業投資」，不是電網問題本身的產品成熟度；更高 capex 也不代表瓶頸已解決。[IEA 能源與 AI](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)。

## 傳導與受惠條件

`power → datacenter → compute` 連接設施供電、部署與晶片採購。VRT、2308.TW 為設備方案候選；MSFT 是部署瓶頸解除後的需求端候選，同時承擔能源、折舊及資本成本，不能一律視為正面受惠。**inference**：電力不足可能增加供電改善投資，也可能延後所有機櫃供應鏈收入，方向需按個案判斷。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`，範圍限定在供電與關鍵基礎設施採購。**well-supported**：IEA 報告及微軟法說會提供需求與部署限制脈絡；Vertiv 的 2026 Q2 財報則量化商業收入、訂單與 backlog，支持已有持續採購和交付。[微軟法說會](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)、[Vertiv 財報](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)。Vertiv 財務口徑包含熱管理與服務，不能全額當成電力瓶頸收入；各案瓶頸是否真是併網、以及 PPA 是否已供電，仍列 **needs verification**。
