---
theme: custom-asic-vs-gpu
name_zh: 客製 ASIC 與通用 GPU 的路線競爭
status: scaling
segments:
- compute
- eda-ip
- networking
beneficiaries:
- AVGO
- MRVL
- 3661.TW
- 3443.TW
milestones:
- date: 2026
  event: 核對客製加速器的商業收入及客戶部署
  evidence: Broadcom FY2026 Q3 財報量化 AI 半導體收入並說明客製加速器需求；自研部署占比另需雲端客戶揭露
  id: custom-commercial-sales
- date: 2026-Q2
  event: 待核實設計服務廠的新案歸屬與 tape-out
  evidence: 具名專案公告、客戶確認及 NRE／量產收入；供應鏈傳聞與設計洽談不足以確認得標
  id: design-projects
- date: 2027
  event: 比較特定工作負載下 GPU／ASIC 的採購與總成本
  evidence: 同工作負載、軟體及利用率口徑的性能／能耗與具名採購組合；供應商毛利率不能代替客戶 TCO
  id: workload-tco
assessment:
  summary: Broadcom 量化已實現 AI 半導體收入並連結客製加速器需求，支持原放量基準；ASIC 與 GPU 可同時擴張，個別設計服務商得標及成本優勢仍待核對。
  confidence: well-supported
  evidence:
  - id: broadcom-ai-revenue
    source_id: broadcom-earnings-research
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial
    excerpt: Q3 AI semiconductor revenue of $16.7 billion
    period: Broadcom FY2026 Q3，截至 2026-08-02；包含網路
    published: '2026-09-02'
  - id: broadcom-custom-demand
    source_id: broadcom-earnings-research
    url: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial
    excerpt: Demand for our custom AI accelerators and networking continues to be very strong.
    period: Broadcom FY2026 Q3，管理層對客製加速器與網路的需求描述
    published: '2026-09-02'
  claims:
  - id: commercial-custom-ai
    statement: 量化 AI 半導體收入及客製加速器需求支持已有商業採購；收入包含網路，不宣稱全額是純 ASIC 收入。
    stance: supporting
    confidence: well-supported
    evidence_ids:
    - broadcom-ai-revenue
    - broadcom-custom-demand
  conditions:
  - 相同工作負載下具有可核對的軟體、利用率及 TCO 優勢
  - 客戶專案實際完成 tape-out 與量產採購
  - 設計服務、NRE 與量產收入分開
  gaps:
  - 缺少各雲端 ASIC／GPU 實際採購分配與台廠具名得標資料
  - 尚未取得同口徑專案取消或量產延後的反向證據
  next_checks:
  - question: 客製需求是否轉成具名專案與量產收入？
    evidence_required: 客戶確認、NRE／量產收入與可比較工作負載成本
  paths:
  - id: accelerator-to-ip
    steps:
    - from: compute
      to: eda-ip
      type: upstream
    mechanism: 新 ASIC 專案可能先產生 IP／EDA 需求，再進入量產。
    direction: positive
    conditions:
    - 真實客戶專案啟動
    - 供應商授權與設計收入可核對
    claim_ids:
    - commercial-custom-ai
  reviewed: '2026-10-07'
  change_reason: 首次將既有查核基準結構化，保留證據期間與未取得項目。
  milestone_reviews:
  - milestone_id: custom-commercial-sales
    state: unconfirmed
    reviewed: '2026-10-07'
    note: AI 半導體收入已量化，但 ASIC／網路分項及客戶部署占比未完整取得。
    evidence_ids:
    - broadcom-ai-revenue
    occurred: null
  - milestone_id: design-projects
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 洽談或供應鏈傳聞不足以確認台廠得標與 tape-out。
    evidence_ids: []
    occurred: null
  - milestone_id: workload-tco
    state: unconfirmed
    reviewed: '2026-10-07'
    note: 須同工作負載、利用率、軟體與採購口徑。
    evidence_ids: []
    occurred: null
technical-profile:
  product-boundary: GPU、客製加速器、設計服務與 IP 是不同產品及收入角色；AI 半導體總收入不等於客製運算單一產品收入。
  adoption-conditions:
  - 比較必須固定工作負載、軟體、精度、利用率、網路及部署規模。
  - 客製晶片須完成設計、IP／PDK、流片與系統軟體整合；洽談不等於得標或 tape-out。
  bottlenecks:
  - 軟體移植、開發攤提、HBM／封裝與互連會影響可用效能及交付時間。
  substitution-limits:
  - 特定工作負載的客製效益不能推定通用 GPU 需求全被替代；跨系統比較需計入開發及維運成本。
  claims:
  - id: network-domain-boundary
    statement: NVIDIA 的公開網路介紹分開 GPU scale-up、scale-out 與跨站範圍；不能以單一互連數字代表完整加速器系統。
    confidence: well-supported
    evidence:
    - source-id: nvidia-networking-technical
      url: https://www.nvidia.com/en-us/networking/
      locator: NVLink／Quantum／Spectrum-X／Spectrum-XGS domain descriptions
      read-scope: 已讀指定公開段落；未取得客戶設計、認證或量產測試文件。
  evidence-gaps:
  - 缺少同工作負載獨立 TCO 與利用率資料；UCIe 全文未取得，不能據公開介紹宣稱任意 chiplet 可互換。
  assessment-claim-ids:
  - commercial-custom-ai
  reviewed: '2026-10-16'
---

## 題材範圍

比較可程式化 GPU 與為特定工作負載設計的 ASIC 在性能、軟體、生產規模及總成本上的分工。客製晶片不必然取代通用 GPU；需求成長時兩者可同時擴張，train／inference 也不是兩種硬體的絕對界線。

## 傳導與受惠條件

題材連接 `compute / eda-ip / networking`：專案先帶來設計服務及 IP 授權，量產再傳到製造、封裝與網路。AVGO、MRVL 是客製與連接方案候選，3661.TW、3443.TW 是設計服務候選。**inference**：案件增多不等於每家都得標，`beneficiaries` 需逐案確認客戶、NRE 與量產收入；總 AI 網路收入不能全算 ASIC 收入。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`。**well-supported**：Broadcom FY2026 Q3 財報量化已實現 AI 半導體收入，並明確把需求與客製加速器及網路業務連結，支持商業採購與出貨，不再只是設計提案。[Broadcom FY2026 Q3 財報](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)。財務口徑包含網路，未將全額稱為純 ASIC 收入；各雲端自研比重與台灣設計服務廠得標仍列 **needs verification**。若專案取消、量產延後或成本優勢消失，需重新校準狀態。
