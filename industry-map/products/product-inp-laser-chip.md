---
schema-version: research-v1
entity-id: product-inp-laser-chip
kind: product
name-zh: "磷化銦雷射晶片"
aliases:
- "InP laser"
summary: "裝入光模組發送端或外置光源的 InP 雷射晶粒，依架構提供調變訊號或連續光。"
definition: "由 III-V 族磊晶結構加工成的 InP 雷射晶粒，含 EML、DML 或 CW 光源等例。"
purpose: "在光鏈路發送端產生光，供直接或外部調變後耦合到光路。"
boundary: "上游交付磊晶片。此頁追到可測試的雷射晶粒，後續 carrier 搭載、光引擎組裝與模組驗證分屬不同交付。"
adoption-conditions:
- "依設計核對波長、每 lane 符號率、輸出功率、溫度與可靠度，並確認 driver 或外置調變器的介面。"
bottlenecks:
- "磊晶層與光柵影響波長，端面劈裂、鍍膜、篩測與光耦合影響良品成本。"
substitution-limits:
- "EML 與 DML 的調變位置不同，CW 光源須配外部調變器。替代前需以同光路、速率及溫度重驗。"
reviewed: "2026-11-24"
claims:
- id: inp-eml-transmit-path
  statement: "Lumentum HL13B5CP00-Ln 在同一 EML 晶粒結合 DFB 雷射與電吸收調變器（EAM），對應 50 GBd PAM4 及 1271／1291／1311／1331 nm CWDM4 選項。Coherent 列出 56 與 112 GBd PAM4 的 CWDM EML 家族。"
  confidence: well-supported
  conditions:
  - "波長及符號率限於所列型號或產品家族。晶粒的速率、溫度與驗證聲明不能推到任意成品模組。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: lumentum-hl13b5cp00-eml
    url: https://www.lumentum.com/en/products/eml-100g-pam4-cwdm-laser
    locator: "Overview"
    read-scope: "已讀 DFB／EAM、50 GBd PAM4、CWDM4 波長、應用與 GR-468 聲明。"
    stance: supporting
    applicable-period: "HL13B5CP00-Ln，2026-11-24 查閱"
  - source-id: coherent-100g-200g-eml
    url: https://www.coherent.com/100-gbps-and-200-gbps-eml.html
    locator: "Description、Specifications"
    read-scope: "已讀 56／112 GBd PAM4、CWDM、50–60 °C 及非氣密封裝相容描述。"
    stance: supporting
    applicable-period: "100G／200G 產品家族，2026-11-24 查閱"
- id: inp-die-processing
  statement: "InP 元件在磊晶後仍需加工，劈裂形成端面後可以鍍膜控制反射，並依流程在 bar 層級測試、再分割為個別晶粒。"
  confidence: well-supported
  conditions:
  - "依 IPSR-I 的典型 III-V 製程；各廠的切割、鍍膜及篩選順序仍依產品核對。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ipsr-inp-iii-v-roadmap
    url: https://www.ipsr-i.org/03-technologies/indium-phosphide-and-iii-v-compounds
    locator: "§2.2.5 Grinding, cleaving, coating and testing"
    read-scope: "已讀磊晶完成後的薄化、劈裂、端面鍍膜與 bar 級測試。"
    stance: supporting
    applicable-period: "IPSR-I 線上技術章，2026-11-24 查閱"
- id: inp-source-architecture
  statement: "DML 以電訊號直接調變雷射；EML 將光生成與調變分成同晶粒上的雷射及 EAM；Coherent CW DFB 雷射以連續光供矽光子調變器使用。"
  confidence: well-supported
  conditions:
  - "Lumentum 100G DML 的資料是 2020 年送樣公告，其成本與量產狀態不能從公告外推。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: lumentum-100g-dml-sampling
    url: https://investor.lumentum.com/financial-news-releases/news-details/2020/Lumentum-Announces-Industry-First-100g-PAM4-DMLs-Available-For-Sampling-2020-12-7/default.aspx
    locator: "公告開頭、About the Product"
    read-scope: "已讀 53 GBd PAM4 DML 樣品及適用的模組設計。"
    stance: supporting
    applicable-period: "2020-12-07 送樣公告"
  - source-id: lumentum-hl13b5cp00-eml
    url: https://www.lumentum.com/en/products/eml-100g-pam4-cwdm-laser
    locator: "Overview"
    read-scope: "已讀 DFB／EAM、50 GBd PAM4、CWDM4 波長、應用與 GR-468 聲明。"
    stance: supporting
    applicable-period: "HL13B5CP00-Ln，2026-11-24 查閱"
  - source-id: coherent-cw-inp-silicon-photonics
    url: https://www.coherent.com/news/press-releases/high-efficiency-lasers-for-silicon-photonics-transceivers
    locator: "產品介紹"
    read-scope: "已讀 O-band CW DFB 雷射晶片與矽光子調變器的搭配用途。"
    stance: supporting
    applicable-period: "2024-08-28 的 CW InP 雷射公告"
- id: inp-laser-delivery
  statement: "博通 FY2025 10-K 揭露自有晶圓廠生產光通訊 InP 雷射；華星光 114 年度年報自述 CW DFB 晶粒量產及未具名採用，並列出 EML 研發項目。"
  confidence: well-supported
  conditions:
  - "可確認公司揭露到上述層次；不由此認定任何具名模組採購，也不把 EML 研發當量產。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: avgo-10k-fy2025
    url: https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm
    locator: "Item 1. Business（Manufacturing）"
    read-scope: "參照博通公司頁已讀的自有晶圓廠光通訊雷射製造段落。"
    stance: supporting
    applicable-period: "FY2025 10-K"
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: "第 72、81 頁（PDF 73、82）"
    read-scope: "參照華星光公司頁已讀的 CW DFB 晶粒及 EML 研發段落。"
    stance: supporting
    applicable-period: "華星光 114 年度年報"
- id: inp-architecture-demand
  statement: "較高光 lane 速率可能提高符合頻寬與驗證條件的 EML 需求；若平台選用 CW 加矽光子調變，相應需求會轉向功率與耦合條件不同的 CW 光源。"
  confidence: inference
  conditions:
  - "追蹤已驗證的模組架構、每埠 lane 數、實際光源拓樸及良率。共享光源或合併 lane 可抵銷晶粒顆數。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: coherent-100g-200g-eml
    url: https://www.coherent.com/100-gbps-and-200-gbps-eml.html
    locator: "Description、Specifications"
    read-scope: "已讀 56／112 GBd PAM4、CWDM、50–60 °C 及非氣密封裝相容描述。"
    stance: supporting
    applicable-period: "100G／200G 產品家族，2026-11-24 查閱"
  - source-id: coherent-cw-inp-silicon-photonics
    url: https://www.coherent.com/news/press-releases/high-efficiency-lasers-for-silicon-photonics-transceivers
    locator: "產品介紹"
    read-scope: "已讀 O-band CW DFB 雷射晶片與矽光子調變器的搭配用途。"
    stance: supporting
    applicable-period: "2024-08-28 的 CW InP 雷射公告"
gaps:
- status: not-obtained
  reason: "未取得相同波長、BER、溫度與鏈路預算下的 EML／DML／CW 系統成本、功耗及晶粒合格率。"
- status: not-public
  reason: "已讀產品頁、製造段落與研發段落未提供可核對的雷射晶粒料號別收入或指定模組客戶。"
---

## 定義與用途

光發送端用雷射產生載波，並把 driver 的電訊號轉成光強度變化。以 HL13B5CP00-Ln 為例，DFB 雷射提供特定波長，單片整合的電吸收調變器（EAM）依輸入改變光的吸收量。DML 將調變施加在雷射本身。CW 雷射則輸出連續光，交給矽光子等外部調變器。模組還要整合 driver、耦合光路及接收端，才構成可上線的[光收發模組](/next?focus=product-optical-transceiver)。[光通訊 DSP](/next?focus=product-optical-dsp)處理電訊號，發光與光調變由此處的元件承擔。

## 採用條件與限制

### 晶粒規格、製程與成本

Lumentum HL13B5CP00-Ln 的四個 CWDM4 波長為 1271、1291、1311、1331 nm，產品頁列 50 GBd PAM4 與 DR／FR 設計，並聲明取得 GR-468 資格。Coherent 的 CWDM EML 家族列出 56／112 GBd PAM4、112／224 Gb/s 與產品頁所列 50–60 °C；這是晶片家族的公開規格。比較前要釐清標稱每 lane 速率、線路位元率、外殼及溫度定義，並重驗整條鏈路的輸出功率、消光比及收端裕度。

磊晶先決定可用的材料與主動層結構。依 IPSR-I 的典型流程，後段仍須圖形加工、薄化、劈裂、端面鍍膜與篩測。若鍍膜或端面使反射離開目標，晶粒即使前段合格也可能無法出貨。評估成本應從合格晶粒的產出看，並把篩測、光耦合與載體組裝分開。

### EML、DML 與 CW 的替代條件

同一個短距 100G/lane 模組可把 EML 和 DML 當方案評估。Lumentum 2020 年 53 GBd PAM4 DML 公告以 DR4 為送樣用途，點出簡化晶片的成本動機。選型還要對照傳輸距離、調變產生的頻率偏移及光路容限。Coherent 的 2024 年 O-band CW DFB 家族面向 800G／1.6T 矽光子模組，使用矽光子調變時需重新核對雷射功率、耦合損失及光源放置位置。三路沒有同條件整機數據可排名。

## 供應角色與公司

屬於[光通訊雷射與光電晶片](/next?focus=role-optical-chip)。Lumentum 的 HL13B5CP00-Ln 與 Coherent 的兩種符號率 EML 是公開晶粒產品例。[博通](/next?focus=company-avgo)揭露自有晶圓廠製造 InP 雷射，未在所讀 10-K 拆出型號。[華星光](/next?focus=company-4979-two)年報的 CW DFB 晶粒、光引擎代工與模組屬不同交付；列於研發段落的 EML 應另核其驗證及出貨狀態。[聯亞](/next?focus=company-3081-two)的[磊晶片](/next?focus=product-optical-epiwafer)供後段加工，與晶粒分開記錄。

### 需求如何傳到晶粒

**Inference。** 200G/lane 升級若採高速 EML，需求首先落到能通過頻寬、光路與可靠度驗證的晶粒。若相同模組速率改用較少 lane，或改成搭配 CW 光源的矽光子架構，晶粒數與單顆規格都會變。先追平台的光 lane 配置，再查雷射族型、合格率與出貨。模組需求、晶粒需求及被整合進晶粒的磊晶使用量須按各自交付層次觀察。
