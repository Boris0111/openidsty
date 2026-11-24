---
schema-version: research-v1
entity-id: product-2p5d-interposer-package
kind: product
name-zh: "2.5D 中介層封裝"
aliases:
- "CoWoS class"
- "interposer package"
summary: "以中介層支援運算晶粒與記憶體之間的高密度橫向互連。"
definition: "以中介層支援運算晶粒與記憶體之間的高密度橫向互連。"
purpose: "將多個已知良品 die 與 HBM 整合至可上板的封裝。"
boundary: "中介層、封裝整合、封裝載板及主板各有獨立交付。"
adoption-conditions:
- "查中介層級距、I/O、功耗、跨層接口、可靠度及客戶驗收。"
bottlenecks:
- "大面積翹曲、互連缺陷和組裝良率。"
substitution-limits:
- "全矽、RDL 或局部矽橋須通過相同功能與互連驗收。"
reviewed: "2026-11-24"
claims:
- id: cowos-architecture-and-production
  statement: "CoWoS-S 為大面積矽中介層，CoWoS-R 為 RDL 中介層，CoWoS-L 提供 RDL 加局部矽互連。台積電稱首款 3.5× reticle CoWoS-L 自 2024 年量產。"
  confidence: well-supported
  conditions:
  - "公開量產階段限指定家族／級距。reticle 倍數計的是中介層面積級距，和封裝外框、載板面積分開。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: tsmc-3dfabric-cowos
    url: https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm
    locator: "CoWoS-S／R／L"
    read-scope: "查全尺寸矽、聚合物銅 RDL、RDL 加局部 LSI 與量產描述。"
    stance: supporting
    applicable-period: "查核日 3DFabric 平台"
  - source-id: tsmc-2025-rd-packaging
    url: https://investor.tsmc.com/static/annualReports/2025/english/pdf/2025_tsmc_ar_e_ch5.pdf
    locator: "Research and Development／CoWoS"
    read-scope: "查 3.5× 量產與 5.5× 資格計畫。"
    stance: supporting
    applicable-period: "FY2025 年報"
- id: cowos-qualification-scope
  statement: "關於 5.5×，FY2025 年報列 CoWoS-L 資格將於 2026 年完成，HPC 頁另說 2025 年完成 Q&R。"
  confidence: needs-verification
  conditions:
  - "來源描述的項目及資格閘門無法由公開內容確認相同，保留口徑差異；不能判定交付狀態。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: tsmc-2025-rd-packaging
    url: https://investor.tsmc.com/static/annualReports/2025/english/pdf/2025_tsmc_ar_e_ch5.pdf
    locator: "Research and Development／CoWoS"
    read-scope: "查 3.5× 量產與 5.5× 資格計畫。"
    stance: supporting
    applicable-period: "FY2025 年報"
  - source-id: tsmc-3dfabric-hpc-qualification
    url: https://www.tsmc.com/english/dedicatedFoundry/technology/platform_HPC_tech_WLSI
    locator: "CoWoS／2025 Q&R"
    read-scope: "查 5.5× Q&R 與 2026 volume production 計畫。"
    stance: counter
    applicable-period: "平台頁 2025 認證描述"
- id: focos-and-tsv-boundaries
  statement: "ASE FOCoS-CL 示範件含 ASIC、兩顆 HBM 及 2/2 μm L/S RDL；Amkor 另列薄化、露出已有 TSV 與背面金屬化的後段。"
  confidence: well-supported
  conditions:
  - "示範結構的 L/S 屬 RDL，不能套用到有機載板；Amkor 資料明示其後段從具有 blind TSV 的晶圓開始。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ase-focos-test-vehicles
    url: https://ase.aseglobal.com/focos/
    locator: "FOCoS Package Offerings／CF、CL、Bridge"
    read-scope: "查 2/2 μm、chiplet／HBM 配置與局部矽橋。"
    stance: supporting
    applicable-period: "所列 test vehicles"
  - source-id: amkor-tsv-backend
    url: https://amkor.com/technology/25d-3d-tsv/
    locator: "MEOL production tooling and processes"
    read-scope: "查既形成的 blind TSV、薄化、露孔及背面金屬化。"
    stance: supporting
    applicable-period: "查核日產品頁"
- id: interposer-yield-demand
  statement: "同一代平台若增加 HBM 或 chiplet，可能需要更大或更密的中介層、更多組裝工序及測試。"
  confidence: inference
  conditions:
  - "採局部矽橋、縮短互連、調整 HBM 或提升合格率均可改變有效單位需求與成本。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: tsmc-3dfabric-cowos
    url: https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm
    locator: "CoWoS-S／R／L"
    read-scope: "查全尺寸矽、聚合物銅 RDL、RDL 加局部 LSI 與量產描述。"
    stance: supporting
    applicable-period: "查核日 3DFabric 平台"
  - source-id: ase-focos-test-vehicles
    url: https://ase.aseglobal.com/focos/
    locator: "FOCoS Package Offerings／CF、CL、Bridge"
    read-scope: "查 2/2 μm、chiplet／HBM 配置與局部矽橋。"
    stance: supporting
    applicable-period: "所列 test vehicles"
gaps:
- status: not-obtained
  reason: "同 I/O、晶粒、溫循與尺寸的良率、工時與報價未取得。"
- status: not-public
  reason: "已讀資料未列個別客戶驗收、封裝料號收入或合格出貨。"
---

## 定義與用途

把已知良品邏輯 die 與 HBM 橫向佈置，由中介層作細線互連，再經[封裝載板](/next?focus=product-abf-substrate)扇出到 PCB。TSV 等垂直互連與 RDL 橫向互連各做一段，成品交付以整合後封裝為單位。

## 規格與成本

CoWoS-S 使用全矽、CoWoS-R 採聚合物銅 RDL、CoWoS-L 在 RDL 嵌較密的 LSI。3.5× reticle 的 CoWoS-L 有供應商量產說明。5.5× 的年報與 HPC 頁資格年份口徑不同，需核對型號與閘門。成本看中介層面積、良品晶粒、工序缺陷、熱與翹曲，不可用 reticle 倍數替代載板面積。

## 採用條件與限制

相同互連密度、D2D 延遲、位置、熱與可靠度要求下，可評估全矽、RDL 或局部矽橋。FOCoS-CL 的 2/2 μm 屬示範件 fan-out RDL；不自動對應相同 HBM 數或溫度。

## 供應角色與公司

[台積電](/next?focus=company-tsmc)提供 CoWoS 整合。[日月光投控](/next?focus=company-3711-tw)集團 ASE 提供 FOCoS 與 TSV 2.5D。[艾克爾](/next?focus=company-amkr)有既有 blind TSV 的晶圓後段與組裝平台，其加工範圍須與晶圓廠交付分開。

## 需求如何傳導

推論：晶粒與 HBM 增加可能拉高中介層密度、尺寸、載板及測試複雜度。架構打散、採矽橋或良率改善可抵銷用量，追蹤資格、良品組裝與可交付成品。
