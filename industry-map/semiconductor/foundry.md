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
