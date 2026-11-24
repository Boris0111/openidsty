---
schema-version: research-v1
entity-id: product-flip-chip-package-service
kind: product
name-zh: "覆晶與委外封裝服務"
aliases:
- "flip chip"
- "OSAT service"
summary: "以覆晶等組裝工序將裸晶與基板或中介層連接。"
definition: "以覆晶等組裝工序將裸晶與基板或中介層連接。"
purpose: "交付符合尺寸、連接、可靠度與相應測試的封裝件。"
boundary: "與提供裸載板、封裝材料或只執行測試的服務分工。"
adoption-conditions:
- "核對 wafer node、bump 節距、I/O、外框、underfill、溫循及測試責任。"
bottlenecks:
- "結合良率、熱／翹曲、合格基板與測試時間。"
substitution-limits:
- "只有工作範圍及驗收相等時比較廠商與替代組裝路徑。"
reviewed: "2026-11-24"
claims:
- id: flip-chip-assembly-and-envelope
  statement: "覆晶將裸晶的連接面朝向基板／中介層。Amkor FCBGA 頁列 4–18 層 laminate、封裝 10–67.5 mm、85 mm 開發中，以及 90 μm 最小陣列凸塊節距。"
  confidence: well-supported
  conditions:
  - "尺寸、凸塊及節點資格為頁面能力，不代表其最大值可同時用於一個產品。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ase-kaohsiung-flip-chip
    url: https://asekh.aseglobal.com/products-services/flip-chip.html
    locator: "What is Flip Chip／Flip Chip Package Offerings"
    read-scope: "查面朝基板覆晶與 FCBGA／FOCoS／CoW 三類用途。"
    stance: supporting
    applicable-period: "查核日 ASE 高雄頁"
  - source-id: amkor-fcbga-product-spec
    url: https://amkor.com/packaging/laminate/fcbga/
    locator: "Technology Solutions、Features、Additional Package Options"
    read-scope: "查封裝、凸塊與基板的尺寸，節點認證及開發狀態。"
    stance: supporting
    applicable-period: "查核日 FCBGA 頁"
- id: flip-chip-service-qualification
  statement: "Amkor 該頁列 ≥7 nm 已取得資格、5 nm 仍在 qualification，ASE 高雄另列 FCBGA、FOCoS 與 CoW 交付。"
  confidence: well-supported
  conditions:
  - "以該公開頁的服務能力為準，專案認證、測試與跨廠移轉要獨立驗證。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: amkor-fcbga-product-spec
    url: https://amkor.com/packaging/laminate/fcbga/
    locator: "Technology Solutions、Features、Additional Package Options"
    read-scope: "查封裝、凸塊與基板的尺寸，節點認證及開發狀態。"
    stance: supporting
    applicable-period: "查核日 FCBGA 頁"
  - source-id: ase-kaohsiung-flip-chip
    url: https://asekh.aseglobal.com/products-services/flip-chip.html
    locator: "What is Flip Chip／Flip Chip Package Offerings"
    read-scope: "查面朝基板覆晶與 FCBGA／FOCoS／CoW 三類用途。"
    stance: supporting
    applicable-period: "查核日 ASE 高雄頁"
- id: flip-chip-service-demand
  statement: "若相同封裝分工下的高 I/O 裝置與多晶粒增加，委外封裝需求可能隨組裝、基板與測試的資格量提升。"
  confidence: inference
  conditions:
  - "若設計簡化、良率改善，或整合工序移至晶圓廠或由另一交付者承擔，委外量可被抵銷。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: ase-kaohsiung-flip-chip
    url: https://asekh.aseglobal.com/products-services/flip-chip.html
    locator: "What is Flip Chip／Flip Chip Package Offerings"
    read-scope: "查面朝基板覆晶與 FCBGA／FOCoS／CoW 三類用途。"
    stance: supporting
    applicable-period: "查核日 ASE 高雄頁"
  - source-id: amkor-fcbga-product-spec
    url: https://amkor.com/packaging/laminate/fcbga/
    locator: "Technology Solutions、Features、Additional Package Options"
    read-scope: "查封裝、凸塊與基板的尺寸，節點認證及開發狀態。"
    stance: supporting
    applicable-period: "查核日 FCBGA 頁"
gaps:
- status: not-obtained
  reason: "同 I/O、晶粒、溫循與尺寸的良率、工時與報價未取得。"
- status: not-public
  reason: "已讀資料未列個別客戶驗收、封裝料號收入或合格出貨。"
---

## 定義與用途

覆晶將晶粒接點面朝基板，透過 solder bump 或銅柱連接。依規格再加底膠、封蓋／模封、BGA 與電性測試。測試可由同服務包或另案承擔。

## 規格與成本

Amkor FCBGA 產品頁以 4–18 層 laminate、10–67.5 mm 封裝、90 μm 最小陣列節距示意；85 mm 仍標開發，≥7 nm 認證與 5 nm 進行中都限該頁口徑。採購前查量產線、封裝堆疊、可靠度和設計來源。

## 採用條件與限制

同規格可比較 ASE 和 Amkor 的 FCBGA 組裝。若要晶粒間大量極細布線，再評估 fan-out 或[2.5D 中介層](/next?focus=product-2p5d-interposer-package)；此時交付增加中介層／重布線工序。單純終測與材料／基板交付按原責任分開。

## 供應角色與公司

[日月光投控](/next?focus=company-3711-tw)集團 ASE 高雄提供 FCBGA、FOCoS 及 CoW。[艾克爾](/next?focus=company-amkr)提供 laminate 或陶瓷基板的 FCBGA 組裝。[力成](/next?focus=company-6239-tw)的記憶體、倒裝與測試依各服務核對。

## 需求如何傳導

推論：高 I/O、大基板、多 die 可提高封裝工序、重工限制與測試工時；改善良率、改由晶圓廠整合及架構簡化可抵銷。查正式驗證機具、客戶核准和放量。
