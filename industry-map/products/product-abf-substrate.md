---
schema-version: research-v1
entity-id: product-abf-substrate
kind: product
name-zh: "ABF 封裝載板"
aliases:
- "ABF substrate"
- "organic FC-BGA substrate"
summary: "以增層膜等介電材料形成精細多層布線的有機封裝載板。"
definition: "以增層膜等介電材料形成精細多層布線的有機封裝載板。"
purpose: "把晶粒或中介層的細密接點扇出到較粗的封裝 BGA 與 PCB。"
boundary: "ABF 是膜料，載板是驗收後的成品，2.5D 中介層及 PCB 是不同層。"
adoption-conditions:
- "對齊外框、層數、孔徑、L/S、翹曲、溫循與電性驗證。"
bottlenecks:
- "細線開短路、微孔填鍍、層間套位、熱壓與翹曲。"
substitution-limits:
- "coreless 或玻璃核心需重新驗證整體堆疊、接口及良率。"
reviewed: "2026-11-24"
claims:
- id: organic-substrate-build-up
  statement: "覆晶載板以增層介電材料和銅線形成多層布線，微孔串聯相鄰層。Shinko DLL 系列分列 SAP、CO₂／UV laser 和 stacked vias，DLL3 為 coreless 方案。"
  confidence: well-supported
  conditions:
  - "DLL 設計屬同類架構範例，資料頁未指定全系列使用同一 ABF 料號。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: shinko-dll-dll3-substrate
    url: https://www.shinko.co.jp/english/product/package/substrate/dll.php
    locator: "Introduction／Features／Structure"
    read-scope: "查 CO₂／UV、stacked vias、SAP、coreless 構造。"
    stance: supporting
    applicable-period: "DLL／DLL3 型錄"
  - source-id: ajinomoto-abf-innovation
    url: https://www.ajinomoto.com/innovation/our_innovation/buildupfilm
    locator: "Precision circuitry、Processing and optimization expertise"
    read-scope: "核對增層膜、雷射成孔、直接鍍銅。"
    stance: supporting
    applicable-period: "查核日技術介紹"
- id: substrate-size-layer-and-warpage
  statement: "Ibiden 的 CY2025 路徑圖示例是 80×80 mm、約 18 層。其技術報告指出面積與層數提升使翹曲更難控制。"
  confidence: well-supported
  conditions:
  - "路徑圖是公司對級距的呈現，單一客戶型號、層數、L/S、孔徑及測試窗口另驗。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-integrated-report-2026
    url: https://www.ibiden.com/ir/items/IntegratedReport2026_en.pdf
    locator: "Special Feature 1，p.9 Larger Size and Higher Layer Count、Miniaturization"
    read-scope: "查 80×80、約 18 層的 CY2025 例與後續趨勢；樹脂翹曲。"
    stance: supporting
    applicable-period: "Integrated Report 2026"
- id: glass-core-evidence-stage
  statement: "Shinko 的玻璃核心原型測試記載 CTE 失配及切割裂紋，原型經 260°C 回焊相關試驗；Intel 與 Lens Technology 公告是共同開發。"
  confidence: well-supported
  conditions:
  - "玻璃換的是 core 層，仍可能使用增層樹脂。公開原型測試和合作需另外核對量產資格與良率。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: shinko-glass-core-tgv-prototype
    url: https://www.shinko.co.jp/english/news/2026/07/b2e0e1c9fadd06989a3ba3940788615cdb6ddaf4.php
    locator: "Abstract for a Conference Presentation"
    read-scope: "核對玻璃核心原型、CTE 裂紋、260°C 及 TGV daisy chain 阻值。"
    stance: supporting
    applicable-period: "ECTC 2025 研究，2026 年公告"
  - source-id: intel-lens-glass-substrate-2026
    url: https://www.intel.com/content/www/us/en/newsroom/news/corporate/intel-and-lens-technology-collaborate-to-enable-advanced-semiconductor-packaging-for-the-ai-era.html
    locator: "Intel and Lens Technology collaboration"
    read-scope: "查聯合開發與應用探索階段。"
    stance: supporting
    applicable-period: "2026-07-24"
- id: substrate-yield-and-demand
  statement: "同外形規格下布線變細或同設計的面積變大，曝光、套位、微孔與翹曲檢驗可能限制可交付載板。"
  confidence: inference
  conditions:
  - "改走 coreless、局部互連、簡化層數或提高良率可抵銷設備時間或面積需求；以合格出貨核算。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-integrated-report-2026
    url: https://www.ibiden.com/ir/items/IntegratedReport2026_en.pdf
    locator: "Special Feature 1，p.9 Larger Size and Higher Layer Count、Miniaturization"
    read-scope: "查 80×80、約 18 層的 CY2025 例與後續趨勢；樹脂翹曲。"
    stance: supporting
    applicable-period: "Integrated Report 2026"
  - source-id: shinko-dll-dll3-substrate
    url: https://www.shinko.co.jp/english/product/package/substrate/dll.php
    locator: "Introduction／Features／Structure"
    read-scope: "查 CO₂／UV、stacked vias、SAP、coreless 構造。"
    stance: supporting
    applicable-period: "DLL／DLL3 型錄"
gaps:
- status: not-obtained
  reason: "未取得同層數、面積、L/S、hole pitch、翹曲測法的交付良率及價格。"
- status: not-public
  reason: "雙方公告已有具名產能合作；各料號採用、驗收、實際出貨及收入仍未揭露。"
---

## 定義與用途

成品載板在[中介層／封裝整合](/next?focus=product-2p5d-interposer-package)與[系統 PCB](/next?focus=segment-pcb)之間。以有芯架構為例，核心兩側反覆疊介電層及銅線，雷射通孔下接 pad、種子層與填孔鍍銅連通；SAP 形成細線，再完成阻焊與終端測試。

## 規格與成本

增層材料規格與牌號見[載板增層介電膜](/next?focus=product-substrate-build-up-dielectric)。載板合格率還要合併壓合、成孔與 SAP 驗證。

Shinko DLL 指定 CO₂／UV 微孔、stack via 與 SAP；DLL3 為 coreless。Ibiden 報告的 80×80 mm／約 18 層是 CY2025 尺度例，同板的線寬距與孔徑要回到客戶合格規格。較大和多層通常增加套位、回焊翹曲及通孔可靠度負擔，單報名目面積會漏掉良品率與返工。

## 採用條件與限制

線寬距變小可沿[載板線路曝光設備](/next?focus=product-substrate-patterning-lithography)核對曝光套位、光阻、種子層、鍍銅與檢查條件。

縮孔時可比較[載板雷射微孔設備](/next?focus=product-substrate-laser-microvia-drill)的材料、孔錐角、底部殘膠與合格產速。

同外形、互連、翹曲測試及冷卻運行條件，比較有機 core、coreless 與 glass core。Shinko 玻璃原型有 260°C 回焊與 TGV 研究，另揭示切割裂紋；Intel／Lens 為合作開發。玻璃 core 可繼續搭配增層膜，量產、交期與適用良率須獨立驗證。

## 供應角色與公司

[揖斐電](/next?focus=company-4062-t)的 AI 伺服器載板資料與[新光電氣](/next?focus=company-private-shinko)DLL／DLL3 可比成品。台灣有[欣興](/next?focus=company-3037-tw)、[南電](/next?focus=company-8046-tw)、[景碩](/next?focus=company-3189-tw)，依各產品範圍及認證跟進。材料供應與雷射、曝光、電鍍設備的證據另列。

## 需求如何傳導

比較同版規格與良率的算例，見[先進封裝與 ABF 載板的規格傳導](/next?focus=research-chip-integration-abf-demand)。有具名產能承諾的景碩與只揭露型錄能力的料號需要分別解讀。

推論：同一平台若外形和層數增加，面板切數、設備時數與有效出貨可能被良率制約。替代堆疊或提高通孔與套位良率會改變瓶頸。追蹤合格的尺寸×層數、客戶認證、量產規格與產出。
