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
