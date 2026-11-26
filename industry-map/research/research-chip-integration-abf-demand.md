---
schema-version: research-v1
entity-id: research-chip-integration-abf-demand
kind: research
name-zh: "先進封裝與 ABF 載板的規格傳導"
aliases: ["advanced packaging substrate demand","封裝載板有效產出"]
summary: "沿中介層、封裝、載板與系統板比較交付，追蹤增層、微孔、細線與良率。"
related-ids: ["application-chip-integration","segment-advanced-packaging","segment-substrate","segment-pcb","segment-materials","segment-equipment","segment-test","product-2p5d-interposer-package","product-flip-chip-package-service","product-abf-substrate","product-substrate-build-up-dielectric","product-substrate-laser-microvia-drill","product-substrate-patterning-lithography"]
reviewed: '2026-11-24'
claims:
- id: substrate-scaling-and-stage
  statement: "Ibiden 以 80×80 mm／約 18 層示意 CY2025，90×90 mm／至少 20 層為 CY2026 的較高一級。Shinko 公開 DLL／DLL3 的 SAP 與微孔，玻璃核心仍依其原型證據。"
  confidence: well-supported
  conditions: ["尺度是報告示意，並非相同客戶實際規格，也不能用兩種尺度讀出同版良率。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-integrated-report-2026
    url: https://www.ibiden.com/ir/items/IntegratedReport2026_en.pdf
    locator: "Special Feature 1 p.9，Larger Size and Higher Layer Count"
    read-scope: "查參考尺度、層數與翹曲的關聯。"
    stance: supporting
    applicable-period: "Integrated Report 2026"
  - source-id: shinko-dll-dll3-substrate
    url: https://www.shinko.co.jp/english/product/package/substrate/dll.php
    locator: "Features"
    read-scope: "核對 SAP、stack vias 與 coreless。"
    stance: supporting
    applicable-period: "DLL／DLL3"
  - source-id: shinko-glass-core-tgv-prototype
    url: https://www.shinko.co.jp/english/news/2026/07/b2e0e1c9fadd06989a3ba3940788615cdb6ddaf4.php
    locator: "Abstract"
    read-scope: "核對玻璃 TGV 的試驗階段與切割風險。"
    stance: supporting
    applicable-period: "ECTC 2025 研究"
- id: qualified-unit-demand-example
  statement: "當尺寸由 80×80 mm 增至 90×90 mm 且布線層需增加，若面板排版與合格率同步下降，固定加工面積的合格載板出貨可減少。"
  confidence: inference
  conditions: ["算例須固定外形、面板可用區、翹曲及客戶驗收條件。實際以排版、毛坯數與終檢合格率估量，不將面積換算收入。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-integrated-report-2026
    url: https://www.ibiden.com/ir/items/IntegratedReport2026_en.pdf
    locator: "p.9 變形與細線工序"
    read-scope: "查較大、多層載板及翹曲。"
    stance: supporting
    applicable-period: "Integrated Report 2026"
  - source-id: shinko-dll-dll3-substrate
    url: https://www.shinko.co.jp/english/product/package/substrate/dll.php
    locator: "Features"
    read-scope: "查微孔與 SAP 可用工序。"
    stance: supporting
    applicable-period: "DLL 產品頁"
- id: capacity-reservation-versus-output
  statement: "NVIDIA 與景碩公布幼獅廠專屬 ABF 擴充，供應計畫列 2027 下半年開始生產及 2028 Q3 額外產能。"
  confidence: well-supported
  conditions: ["這些為有日期的目標，未提供良率、基期合格量、實際出貨或料號單價。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: nvidia-nov2026-substrate-capacity
    url: https://nvidianews.nvidia.com/news/nvidia-expands-commitments-with-supply-chain-partners-to-support-ai-infrastructure-buildout
    locator: "Increasing Substrate Capacity and Production Capabilities"
    read-scope: "查景碩及專屬 ABF 交付、時程和條件。"
    stance: supporting
    applicable-period: "2026-11-17"
gaps:
- status: not-obtained
  reason: "未取得同一平台尺寸、實際排版、合格率、測試費用與價格；算例為假設。"
- status: not-public
  reason: "無指定料號和良品量／獨立收入。"
---


## 研究問題

邏輯 die 與 HBM 的互連需求上升時，如何辨認哪些製程吃掉有效產出，哪些公司具有相應交付能力？

## 判斷與限制

### 依交付層與驗收分工

- [2.5D 中介層封裝](/next?focus=product-2p5d-interposer-package)的矽／RDL 負責 D2D 細線。全矽、聚合物 RDL 與局部矽橋按布局、I/O、熱與備援供應比較。CoWoS reticle 數指中介層，ASE FOCoS 2/2 μm 的線寬距指 test vehicle 中的 RDL。
- [覆晶與委外封裝服務](/next?focus=product-flip-chip-package-service)把 die 接到中介層或有機載板，底填與測試範圍依合約。[ABF 封裝載板](/next?focus=product-abf-substrate)提供從封裝接點到主板的配線，[伺服器多層 PCB](/next?focus=product-server-multilayer-pcb)承載板級電力及訊號。封裝產量受合格晶粒、載板、組裝與測試的共同制約。
- 製造載板時，[載板增層介電膜](/next?focus=product-substrate-build-up-dielectric)決定介電與加工窗口，[載板雷射微孔設備](/next?focus=product-substrate-laser-microvia-drill)影響孔徑、落點與底銅，[載板線路曝光設備](/next?focus=product-substrate-patterning-lithography)影響多層套位。SAP 還要核對去膠渣、種子層、光阻與填鍍。電性、回焊及翹曲的驗收由成品和封測工序完成。

### 案例：封裝需要更大載板及更多布線層

1. **規格事實。** Ibiden 的尺度例從 80×80 mm／約 18 層到 90×90 mm／至少 20 層。相較前一例，單片名目面積增加約 27%。這組比較示範尺寸對工序的影響；不同客戶和平台的層數、孔徑與密度須另查。
2. **製程推論。** 假設相同有芯載板、良品標準、工序及設備。增加層數可能拉長壓合與曝光、鑽孔、鍍銅循環，較大的板對翹曲與套位容許更敏感。在固定可用面板上還需實際排版、邊距和良品數。例如每面板可排 12 → 9 片、終檢合格率 90% → 80%（純假設），平均有效 10.8 → 7.2 片。不能從面積或名目設備速度直接算某公司的產出。
3. **公司證據。** [Ibiden](/next?focus=company-4062-t)有 SAP／微孔與大尺寸研究，[Shinko](/next?focus=company-private-shinko)有 DLL／DLL3。[景碩](/next?focus=company-3189-tw)的幼獅擴充另有 NVIDIA 具名的協議與投產目標。規格能力、合格量與產品收入分開讀，且設備或膜料供應商需依個別型號及材料批准。
4. **失效與查核。** 改用局部矽橋或縮小 RDL、優化面板排版、減少相鄰層或改善良率，可能移動瓶頸或抵銷用量。玻璃核心原型仍要驗證 TGV、切割與熱可靠度。需要可核的同版尺寸和層數、出廠良率、溫循／翹曲和客戶資格，再看合格出貨、出貨時程與收入。
