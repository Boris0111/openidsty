---
segment: advanced-packaging
name_zh: 先進封裝
layer: ai-server
position: 4
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2330.TW"
    name_zh: 台積電
    role: CoWoS 與 SoIC 先進封裝
    tier: 1
  - ticker: "3711.TW"
    name_zh: 日月光投控
    role: 委外封測與先進封裝
    tier: 1
  - ticker: "6239.TW"
    name_zh: 力成
    role: 記憶體與邏輯封測
    tier: 2
  - ticker: "AMKR"
    name_zh: 艾克爾
    role: 委外封測
    tier: 2
upstream: [materials, equipment, test, substrate, memory, compute]
downstream: [odm]
themes: [cpo-silicon-photonics, hbm4]
kpis:
  - 先進封裝月產能與擴產進度
  - 良率與中介層尺寸世代
  - 產能分配給各客戶的比重
signals:
  - 擴產計畫與資本支出調整
  - 封裝技術世代轉換（中介層轉面板級）
downstream-relations:
  odm:
    kind: supply
    summary: 先進封裝至系統組裝與機櫃整合：封裝後運算／記憶體模組的整機整合介面。
    items:
    - 封裝後運算／記憶體模組的整機整合介面
    dependencies:
    - 封裝尺寸、散熱接觸、板級供電與訊號逃線
    conditions:
    - 封裝與整機平台完成共同驗證
    confidence: inference
    evidence: []
    gaps:
    - 缺少指定封裝料號與整機主板、散熱模組的驗收對照，不能推定每家封裝商都供應同一 ODM。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 中介層／RDL、封裝載板、D2D 與 HBM 控制／實體介面是不同層次；UCIe 封裝內介面不能替代全部封裝或記憶體標準。
  adoption-conditions:
  - 先核對 die／記憶體介面、封裝材料與製程、供電散熱及測試方案；互通需要指定版本與實測。
  - 量產需同時有已知良品 die、封裝良率、可靠度、可交付產能與客戶驗收證據。
  bottlenecks:
  - 大型封裝的路由、翹曲、熱應力、測試可及性及材料／設備配置會共同限制整合，不能只看名目產能。
  substitution-limits:
  - CoWoS-S／R／L 的互連結構不同；晶圓轉面板是加工方式，玻璃核心是載板材料，不能當同一層必然互斥選項。
  - 採用替代方案需重新核對設計規則、良率、可靠度與成本；roadmap 不能支持客戶已量產。
  claims:
  - id: packaging-layers
    statement: 台積電公開 CoWoS 頁區分矽中介層及 R／L 等互連組合，支持產品層次區分，不提供每位客戶良率。
    confidence: well-supported
    evidence:
    - source-id: tsmc-public-technology
      url: https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm
      locator: CoWoS-S／CoWoS-R／CoWoS-L
      read-scope: 已讀指定公開段落，未取得完整設計／認證檔
  - id: die-to-die-scope
    statement: UCIe 公開介紹涉及封裝內 D2D 與測試管理；未取得全文，不能由介紹推定 HBM 相容或跨廠合規。
    confidence: well-supported
    evidence:
    - document-id: ucie-public-specifications
      version-id: public-overview-20261016
      locator: package-interface
    - document-id: ucie-public-specifications
      version-id: public-overview-20261016
      locator: test-manageability
  evidence-gaps:
  - 未取得具名封裝平台的良率分解、KGD 測試覆蓋、玻璃／面板替代的客戶認證與同口徑成本。
  - UCIe 全文須 REQUEST；JEDEC 個別 HBM 規格未取得，不以公開介紹補成條文已核實。
  reviewed: '2026-10-16'
---

## 環節定義

把運算晶粒、HBM 與中介層整合為單一封裝體，是加速器從「晶片」變成「可用元件」的關鍵一步。

與傳統封測的根本差別：它決定了封裝體能容納多少運算與多少記憶體，因此**已成為效能的直接限制，而不是後段加工**。

## 技術變數

中介層面積（以光罩倍數計）決定能放幾顆運算晶粒與幾堆 HBM。良率隨面積上升而惡化，所以「面積與良率的取捨」是本環節的核心工程問題。

中介層可採矽、RDL 及局部矽互連等不同組合；晶圓轉面板是加工尺寸與經濟性的變化，玻璃核心載板則涉及另一個材料層次，不能當成同一條互斥路線。**well-supported**：CoWoS-S／R／L 的結構與分工可由官方產品資料查核；面板級或玻璃方案的客戶量產仍須另有證據。[台積電 CoWoS 技術](https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm)。

## 玩家格局

台積電以 CoWoS 與 SoIC 在高階領先，並藉製程與代工的綁定取得分配權。日月光投控與力成承接委外封測與部分先進封裝，艾克爾為美系委外選項。

產能分配影響加速器出貨節奏，但由供應商、客戶承諾、認證與長期合約共同決定，不能宣稱加速器廠完全沒有分配議價能力。

## 傳導鏈

**上游最寬的環節**，同時牽動六個方向：`materials`、`equipment`、`test`、`substrate`、`memory`、`compute`。

因此擴產消息的候選影響面包括設備、載板、測試與材料。看到擴產，應往上游六個方向各走一步；**inference** 的個股受惠仍取決於實際材料、設備料號、客戶認證及訂單，不能把關聯直接當已確認收入。

**下游**：封裝完成品進入 `odm` 組裝。本環節是整條鏈最常出現的瓶頸，產能缺口會直接壓制 `odm` 與 `datacenter` 的實際交付量，即使終端需求無虞。

## 監測指標

先進封裝月產能與擴產進度、良率與中介層尺寸世代、產能分配給各客戶的比重。

**供需缺口的收斂程度比絕對產能數字更能反映景氣位置** —— 產能翻倍但缺口未縮，代表需求同步放大；缺口收斂才是鬆動的訊號。

## 風險

產能高度集中於單一廠商與單一地理區域。擴產週期長，判斷失準會造成長期閒置或長期缺貨。若競爭者先在面板級封裝取得經濟性，現有的領先地位可能被侵蝕。
