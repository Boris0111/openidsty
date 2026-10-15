---
theme: liquid-cooling
name_zh: 液冷散熱
status: scaling
segments:
- thermal
- odm
- datacenter
- power
beneficiaries:
- 3017.TW
- 3324.TW
- VRT
- 2308.TW
milestones:
- date: 2026-Q1
  event: 核對具名高密度平台的液冷配置與交付
  evidence: 平台正式規格、客戶交付或 ODM 法說會區分液冷機櫃出貨；不把單一平台配置擴大為全市場預設
  id: platform-delivery
- date: 2026
  event: 核對冷板與 CDU 的商業出貨、收入及產能利用
  evidence: 供應商財報明確量化液冷產品收入，並與產能爬坡／客戶訂單交叉核對；月營收總額不能代替液冷收入
  id: product-revenue
- date: 2027
  event: 待比較新建案與改造案的 L2L／L2A 方案組合
  evidence: 同口徑的具名機房採購規格及熱管理供應商產品收入；沒有完整樣本時不宣稱一種方案已超越另一種
  id: cooling-mix
assessment:
  summary: 液冷已有具名產品收入，支持放量基準；個別冷板、CDU 與設施水路供應商能否受惠，仍取決於採購項目與產品口徑。
  confidence: well-supported
  evidence:
  - id: aaon-q3-product-sales
    source_id: aaon-liquid-cooling-filing
    url: https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm
    excerpt: $46.5 million in BASX-branded liquid cooling product sales
    period: AAON 2025 Q3，單季 BASX 液冷產品
    published: '2025-11-06'
  - id: aaon-q3-margin
    source_id: aaon-liquid-cooling-filing
    url: https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm
    excerpt: Gross profit margin in the quarter was 27.8%
    period: AAON 2025 Q3，公司整體毛利，非液冷產品毛利
    published: '2025-11-06'
  - id: aaon-q4-product-sales
    source_id: aaon-liquid-cooling-filing
    url: https://www.sec.gov/Archives/edgar/data/824142/000082414226000003/liveaaonpressreleaseexs.htm
    excerpt: $75.3 million in BASX-branded liquid cooling sales
    period: AAON 2025 Q4，單季 BASX 液冷產品
    published: '2026-03-02'
  claims:
  - id: commercial-product-sales
    statement: AAON 已量化 BASX 液冷產品銷售，支持產業商業放量；不能替代四家候選公司各自的產品收入。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - aaon-q3-product-sales
    - aaon-q4-product-sales
  - id: growth-not-margin
    statement: AAON 同季整體毛利率低於前一年，顯示收入擴張不保證公司整體利潤率同步上升；不把整體毛利歸因於液冷本身。
    stance: counter
    confidence: well-supported
    evidence_ids:
    - aaon-q3-margin
  conditions:
  - 具名平台採購冷板／CDU 與相應設施水路
  - 候選供應商具有該平台的實際料號、驗收及交付
  - 量化收入須區分液冷、氣冷與混合設備
  gaps:
  - 四家候選公司的液冷收入與毛利尚未逐一核對
  - 缺少同口徑的 L2L／L2A 與改造案樣本
  next_checks:
  - question: 收入是否隨新平台交付持續放量？
    evidence_required: 具名採購／交付與分產品財報，不以總月營收代替
  paths:
  - id: rack-to-pcb
    steps:
    - from: thermal
      to: pcb
      type: sibling
      via: odm
    mechanism: 液冷整櫃規格可能同時改變 PCB／CCL 採購。
    direction: positive
    conditions:
    - 同一 ODM 平台提高板材規格
    - 取得實際 PCB 料號及訂單
    claim_ids:
    - commercial-product-sales
  - id: rack-to-power
    steps:
    - from: thermal
      to: power
      type: theme
      via: liquid-cooling
    mechanism: 高密度液冷平台可能同時增加供電與冷卻設備採購。
    direction: positive
    conditions:
    - 同一平台提高每櫃功率
    - 電源供應商實際得標
    claim_ids:
    - commercial-product-sales
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: platform-delivery
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 尚未逐案取得具名平台交付；產業收入不是所有平台的交付證據。
    evidence_ids: []
    occurred: null
  - milestone_id: product-revenue
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 僅 AAON 產品收入有基準證據；冷板／CDU 分項、候選公司及產能利用仍待核對。
    evidence_ids:
    - aaon-q3-product-sales
    - aaon-q4-product-sales
    occurred: null
  - milestone_id: cooling-mix
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 尚缺同口徑新建與改造案資料。
    evidence_ids: []
    occurred: null
---

## 題材範圍

以 direct-to-chip 冷板、歧管與 CDU 為主要追蹤範圍，同時觀察設施水路改造及其他冷卻路線。冷板、機櫃 CDU 與機房側設備是不同收入層次，液冷滲透率須說明分母。高密度 AI 平台的採用不表示一般伺服器已全部轉液冷。[Supermicro 液冷方案](https://www.supermicro.com/en/solutions/liquid-cooling)。

## 傳導與受惠條件

題材橫向連接 `thermal / odm / datacenter / power`，透過 ODM 的共同上游再取得 PCB 與連接介面。3017.TW、3324.TW 是散熱零組件候選，VRT 偏熱管理系統，2308.TW 同時有供電／冷卻方案。**inference**：液冷配置可能增加每櫃價值量，但個別受惠須看實際採購項目；`beneficiaries` 不代表已核實每家的液冷收入或保證毛利上升。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`，以產業商業出貨及已實現液冷設備收入為依據。**well-supported**：AAON 的 2025 Q3 公開財報單獨量化 BASX 液冷產品銷售，證據不是示範機或未來市場預估；2025 Q4 財報亦確認冷卻設備訂單與出貨增長。[液冷產品收入證據](https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm)、[後續財報佐證](https://www.sec.gov/Archives/edgar/data/824142/000082414226000003/liveaaonpressreleaseexs.htm)。這是題材狀態的業界證據，不能替代上述四個候選公司的各自財報；冷板廠收入占比與 L2L／L2A 分配仍需另查。尚未達到全市場標準配置，故不採 `mature`。
