---
segment: foundry
name_zh: 晶圓代工
layer: semiconductor
position: 2
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2330.TW"
    name_zh: 台積電
    role: 先進製程代工主要供應者
    tier: 1
  - ticker: "005930.KS"
    name_zh: 三星電子
    role: 先進製程代工
    tier: 2
  - ticker: "2303.TW"
    name_zh: 聯電
    role: 成熟製程代工
    tier: 2
  - ticker: "GFS"
    name_zh: 格羅方德
    role: 特殊製程代工
    tier: 3
  - ticker: "0981.HK"
    name_zh: 中芯國際
    role: 成熟製程代工
    tier: 3
upstream: [materials, equipment]
downstream: [compute, networking, test, power-discrete]
themes: [advanced-node-2nm]
kpis:
  - 先進製程營收佔比
  - 產能利用率與資本支出
  - 各節點報價走勢
signals:
  - 新節點量產時程與良率進展
  - 資本支出指引與擴廠地點
downstream-relations:
  compute:
    kind: supply
    summary: 晶圓代工至運算晶片：運算晶片的晶圓製造服務與待封裝 die。
    items:
    - 運算晶片的晶圓製造服務與待封裝 die
    dependencies:
    - 製程 PDK、良率、產能及後段封裝匹配
    conditions:
    - 設計在目標節點完成 tape-out、量產驗證與產能承諾
    confidence: inference
    evidence: []
    gaps:
    - 缺少個別 GPU／ASIC 的良率、晶圓投入及交付份額，不能從節點名稱推定性能或訂單。
    reviewed: '2026-10-16'
  networking:
    kind: supply
    summary: 晶圓代工至網通與光通訊：網路 ASIC／DSP 等晶片的晶圓製造服務。
    items:
    - 網路 ASIC／DSP 等晶片的晶圓製造服務
    dependencies:
    - 高速介面、PDK、熱設計及封裝整合
    conditions:
    - 特定晶片設計、製程與客戶驗證條件成立
    confidence: inference
    evidence: []
    gaps:
    - 未取得具名交換器 ASIC／DSP 的代工節點、產能及良率，不把系統廠視為同一晶片設計角色。
    reviewed: '2026-10-16'
  test:
    kind: supply
    summary: 晶圓代工至測試與探針：晶圓及 die 交付測試的作業介面。
    items:
    - 晶圓及 die 交付測試的作業介面
    dependencies:
    - 晶圓圖、測試程式、接觸介面與資料回饋
    conditions:
    - 測試流程、良品判準與製造責任已約定
    confidence: inference
    evidence: []
    gaps:
    - 缺少具名製程的 wafer map、test coverage 與測試委外合約；不由代工產能推定全部測試公司收入。
    reviewed: '2026-10-16'
  power-discrete:
    kind: supply
    summary: 晶圓代工至功率與分離式元件：功率／分離式元件所需晶圓製造能力。
    items:
    - 功率／分離式元件所需晶圓製造能力
    dependencies:
    - 材料、元件結構、特殊製程與可靠度要求
    conditions:
    - 具名元件與製程相容並完成認證
    confidence: inference
    evidence: []
    gaps:
    - 未取得各功率產品的實際代工／IDM 比例與晶圓材料，不把先進邏輯代工視為所有功率元件供應者。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 依客戶設計提供晶圓製造，先進邏輯、成熟及特殊製程分開；封裝服務即使由同公司提供，仍是另一供應角色。
  adoption-conditions:
  - 設計規則、PDK、IP 與製程版本需匹配，並核對實際 tape-out、良率與客戶驗收。
  bottlenecks:
  - 可交付良品受製程爬坡、材料設備、設施及封裝配套限制，不能只看名目晶圓產能。
  substitution-limits:
  - 不同廠商節點名稱不等於相同性能；新節點與背面供電等變體不能無條件互換設計。
  claims:
  - id: node-technology-scope
    statement: 台積電官方技術入口將 N2 nanosheet 與後續 A 系列分開介紹；平台描述不揭露各客戶良率。
    confidence: well-supported
    evidence:
    - source-id: tsmc-public-technology
      url: https://www.tsmc.com/english/dedicatedFoundry/technology/logic/l_2nm
      locator: 2nm Technology／N2 與後續技術入口
      read-scope: 已讀指定公開說明；沒有取得客戶完整設計、測試或認證檔
  evidence-gaps:
  - 未取得各客戶、節點及廠區的良率、wafer starts 與成本；後續變體按實際驗收另核對。
  reviewed: '2026-10-16'
---

## 環節定義

依客戶設計製造晶圓，以製程平台、良率、產能及交付品質收取代工費。先進邏輯、成熟製程與特殊製程的競爭集合不同；不能把節點數字相同視為性能相同，也不能以先進節點地位概括全部晶圓市場。代工在此歸 `foundry`，即使同公司同時提供封裝，封裝服務仍歸 `advanced-packaging`。

## 技術變數

FinFET 轉 GAA nanosheet、背面供電、設計規則與 SRAM 縮放，影響功耗、性能、面積、可製造性及每顆良品成本。High-NA EUV 是微影選項，不表示所有 2nm 製程都已採用；新節點必須看實際量產與客戶導入。**well-supported**：台積電 2026 Q2 已揭露 2nm 晶圓營收占比，支持 N2 已進入商業出貨；後續變體的時程仍須逐次核對。[台積電季度資料](https://investor.tsmc.com/english/quarterly-results/2026/q2)、[官方財報新聞稿](https://pr.tsmc.com/japanese/news/3326)。

## 玩家格局

台積電（2330.TW）是先進邏輯代工主要供應者；三星電子（005930.KS）同時具有 IDM 與代工業務，須只比較代工角色。聯電（2303.TW）偏向成熟／特殊製程，格羅方德（GFS）偏向特殊製程平台，中芯國際（0981.HK）涵蓋成熟與部分先進製程。`led_by: [TW]` 表示台灣在外部客戶先進代工的重要地位；`tier` 為此地圖的供應角色排序，不是五家公司全製程市佔的精確比較。

## 傳導鏈

`materials / equipment → foundry → compute / networking`：材料純度、設備交期及製程良率影響可交付的邏輯晶片，再傳到加速器與網路 ASIC。`foundry → test → advanced-packaging` 表示良品篩選後才進行昂貴整合；`foundry → power-discrete → power` 表示特殊製程亦承載供電元件需求。2nm 題材把設備與材料連起來，但 AI 需求增長不代表每一成熟製程廠都同步受惠。

## 監測指標

追蹤節點營收組合、產能利用率、capex 類別、良品交付時程及客戶 tape-out 轉量產。優先使用公司季度財報、法說會、年報及官方技術平台資料；沒有公開良率數字時標 **needs verification**，不以媒體傳聞填入。**inference**：晶圓報價上升能否改善毛利，還取決於折舊、海外生產成本與良率。

## 風險

先進節點的投資與客戶集中使利用率敏感；設計延遲、良率落後或 IP 尚未認證都可能延後收入。地緣、出口管制、電水供應及跨區擴廠成本影響交付與獲利。成熟製程的產能過剩與價格競爭，不能用先進 AI 晶片短缺的邏輯掩蓋。
