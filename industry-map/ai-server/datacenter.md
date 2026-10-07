---
segment: datacenter
name_zh: 資料中心與雲端業者
layer: ai-server
position: 6
market_coverage:
  tw: none
  us: present
  led_by: [US]
companies:
  - ticker: "MSFT"
    name_zh: 微軟
    role: 超大規模雲端業者
    tier: 1
  - ticker: "GOOGL"
    name_zh: 谷歌
    role: 超大規模雲端業者
    tier: 1
  - ticker: "AMZN"
    name_zh: 亞馬遜
    role: 超大規模雲端業者
    tier: 1
  - ticker: "META"
    name_zh: Meta
    role: 自用大規模運算
    tier: 1
  - ticker: "ORCL"
    name_zh: 甲骨文
    role: 雲端業者
    tier: 2
  - ticker: "CRWV"
    name_zh: CoreWeave
    role: 新興 AI 雲端業者
    tier: 2
upstream: [odm, power]
downstream: [compute]
themes: [liquid-cooling, 800vdc, power-bottleneck]
kpis:
  - 資本支出金額與年增率
  - 新增機房電力容量
  - 自研晶片佔自身部署比重
signals:
  - 財報與法說會的資本支出指引調整
  - 新建案選址與電力併網時程
---
