---
schema-version: research-v1
entity-id: product-optical-epiwafer
kind: product
name-zh: "III-V 族光通訊磊晶片"
aliases:
- "InP epiwafer"
- "GaAs epiwafer"
- "磷化銦磊晶片"
summary: "在 InP 或 GaAs 基板成長主動層及其他功能層，供雷射和檢光晶片加工。"
definition: "以 MOCVD 等方法在 III-V 族基板上成長多層結構的光電元件用晶圓。"
purpose: "提供雷射增益、調變或檢光功能所需的材料層堆疊。"
boundary: "交付為成長後的晶圓或指定加工晶圓，後段晶粒篩測、光引擎與模組另有驗證。"
adoption-conditions:
- "依下游設計核對晶圓尺寸、結構、光致發光（PL）波長與均勻性、缺陷及批次重現性。"
bottlenecks:
- "反應爐條件、基板尺寸、層厚及組成均勻性共同限制可用晶圓面積。"
substitution-limits:
- "DFB、EML、VCSEL 及檢光器需各自匹配基板、層結構與後段加工；材料名相同仍須做下游驗證。"
reviewed: "2026-11-24"
claims:
- id: iii-v-epi-stack
  statement: "InP 光電元件可用 MOCVD 成長多層結構，材料組成及層厚會影響光學功能。InP 的單片整合可能用局部再成長形成不同區域的層結構。"
  confidence: well-supported
  conditions:
  - "依 IPSR-I 的 III-V 製程範圍；實際產品的材料配方與疊層按各設計。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ipsr-inp-iii-v-roadmap
    url: https://www.ipsr-i.org/03-technologies/indium-phosphide-and-iii-v-compounds
    locator: "§§2.2.1、2.3 及 Epitaxial growth/layer deposition 表"
    read-scope: "已讀 MOCVD、材料組成與厚度、批次重現性、缺陷及量測口徑。"
    stance: supporting
    applicable-period: "IPSR-I 線上技術章，2026-11-24 查閱"
- id: epi-process-window
  statement: "IPSR-I 分列層厚、組成（可用 PL 波長量測）、摻雜的片內均勻性與跨批重現性。聯亞資料中心頁列出帶光柵或 p-metal 加工選項的 DFB／CW 磊晶與 850 nm VCSEL 磊晶。"
  confidence: well-supported
  conditions:
  - "路線圖指標是技術目標。聯亞公開項目限產品類別與選項，未提供該晶圓的合格公差。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ipsr-inp-iii-v-roadmap
    url: https://www.ipsr-i.org/03-technologies/indium-phosphide-and-iii-v-compounds
    locator: "§§2.2.1、2.3 及 Epitaxial growth/layer deposition 表"
    read-scope: "已讀 MOCVD、材料組成與厚度、批次重現性、缺陷及量測口徑。"
    stance: supporting
    applicable-period: "IPSR-I 線上技術章，2026-11-24 查閱"
  - source-id: landmark-datacenter-epiwafer
    url: https://www.lmoc.com.tw/index.php?id=110&index=2&lang=en&option=module&task=pageinfo
    locator: "Data center：DFB Epiwafer、VCSEL Epiwafer、High Power CW laser Epiwafer、Silicon Photonics Epiwafer、GaAs PD Epiwafer"
    read-scope: "已讀 DFB 光柵及 p-metal 選項、850 nm VCSEL、CW 與檢光磊晶分類。"
    stance: supporting
    applicable-period: "聯亞資料中心產品分類，2026-11-24 查閱"
- id: epi-commercial-granularity
  statement: "聯亞列 DFB、CW、VCSEL 與 GaAs PD 磊晶家族；IQE 官方 InP 清單列 FP、DFB、EML 及 APD／PD 磊晶結構。兩者可在同元件功能和結構條件下比較供應範圍。"
  confidence: well-supported
  conditions:
  - "已讀資料不揭露結構料號、相同公差、客戶端驗證或供貨關係。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: landmark-datacenter-epiwafer
    url: https://www.lmoc.com.tw/index.php?id=110&index=2&lang=en&option=module&task=pageinfo
    locator: "Data center：DFB Epiwafer、VCSEL Epiwafer、High Power CW laser Epiwafer、Silicon Photonics Epiwafer、GaAs PD Epiwafer"
    read-scope: "已讀 DFB 光柵及 p-metal 選項、850 nm VCSEL、CW 與檢光磊晶分類。"
    stance: supporting
    applicable-period: "聯亞資料中心產品分類，2026-11-24 查閱"
  - source-id: iqe-inp-epiwafer
    url: https://www.iqep.com/products/inp/
    locator: "Wafer structures offered"
    read-scope: "已讀 DFB／EML 及 APD／PD 可供應結構分類。"
    stance: supporting
    applicable-period: "IQE InP 產品家族，2026-11-24 查閱"
- id: epi-qualified-area-demand
  statement: "出貨架構若增加符合規格的 InP 元件，可拉動相應磊晶需求。擴大晶圓直徑的成本效益取決於均勻性、可用面積與後段合格率。"
  confidence: inference
  conditions:
  - "追蹤設備及下游導入驗證。若客戶內製磊晶或改用另一光源路線，外購磊晶需求可與晶粒出貨脫鉤。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ipsr-inp-iii-v-roadmap
    url: https://www.ipsr-i.org/03-technologies/indium-phosphide-and-iii-v-compounds
    locator: "§§2.2.1、2.3 及 Epitaxial growth/layer deposition 表"
    read-scope: "已讀 MOCVD、材料組成與厚度、批次重現性、缺陷及量測口徑。"
    stance: supporting
    applicable-period: "IPSR-I 線上技術章，2026-11-24 查閱"
  - source-id: landmark-datacenter-epiwafer
    url: https://www.lmoc.com.tw/index.php?id=110&index=2&lang=en&option=module&task=pageinfo
    locator: "Data center：DFB Epiwafer、VCSEL Epiwafer、High Power CW laser Epiwafer、Silicon Photonics Epiwafer、GaAs PD Epiwafer"
    read-scope: "已讀 DFB 光柵及 p-metal 選項、850 nm VCSEL、CW 與檢光磊晶分類。"
    stance: supporting
    applicable-period: "聯亞資料中心產品分類，2026-11-24 查閱"
gaps:
- status: not-obtained
  reason: "未取得聯亞與 IQE 在相同基板直徑、層結構及邊緣排除條件下的 PL、厚度、缺陷公差、價格或下游良率。"
- status: not-public
  reason: "已讀產品頁未揭露具名晶片客戶、指定模組的認證或交付量。"
---

## 定義與用途

磊晶把成分及厚度受控的晶體層成長在基板上。用來發光的層提供光增益，調變區與檢光區則按各自光吸收需求設計。MOCVD（有機金屬化學氣相沉積）是 IPSR-I 所述常見方法。把雷射與調變器單片整合時，可用選區再成長等方法為不同區域配置層結構。晶圓進下游後還要經光刻、電極與端面加工、切割及篩測，才形成可交付的[雷射晶粒](/next?focus=product-inp-laser-chip)。

## 採用條件與限制

### 先看晶圓上的可用面積

PL（光致發光）波長可觀察片內材料組成是否一致，層厚則會影響調變或導光結構。單片量測還需區分中心與邊緣；跨批重現性再用相同量測條件逐批比較。若放大晶圓直徑時邊緣偏差或顆粒增加，需要扣除不合格面積與後段損失，才看得出合格晶粒成本是否下降。IPSR-I 的均勻性數值是路線圖目標，採購公差以雙方規格為準。

### 同用途才比較磊晶來源

聯亞列出 DFB 及高功率 CW 磊晶的光柵與 p-metal 選項，也列出 850 nm VCSEL 與 GaAs 檢光磊晶。已完成光柵的晶圓可把一道加工移到供應端，但須先核對光柵週期、電極及後段流程是否一致。850 nm VCSEL 的垂直發射結構與特定 InP DFB／EML 晶片的材料及後段設計不同。若要換同類 DFB 磊晶來源，仍需要用同一基板、結構與後段流程對照波長分布、晶粒篩測和可靠度。

## 供應角色與公司

屬於[光通訊磊晶片](/next?focus=role-optical-epiwafer)。[聯亞](/next?focus=company-3081-two)的資料中心頁列出各種磊晶與指定加工選項；英國 IQE 另列 InP DFB／EML、APD／PD 磊晶。兩份資料可用來確認各自供應範圍，尚不足以確認相同片徑、指定客戶或實際替換資格。外售的磊晶片、晶片廠內部的磊晶製程與外售的成品晶粒各有不同交付節點，同一片材料的內部流轉只計一次。

### 需求如何傳到磊晶

**Inference。** 先由模組設計確認光源採 DFB、EML 或 CW，再看晶粒廠是否外購相符結構的磊晶，以及晶圓有多少面積可產出合格晶粒。若晶片廠改成內製、優化版圖、提高良率或切換光路，外購磊晶片可能沒有跟上模組總頻寬。用供應商所列加工範圍、晶片端來料驗收、試產合格率與後續採購確認傳導。
