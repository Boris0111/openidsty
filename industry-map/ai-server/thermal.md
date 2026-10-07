---
segment: thermal
name_zh: 散熱
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "3017.TW"
    name_zh: 奇鋐
    role: 均熱板與氣冷散熱模組
    tier: 1
  - ticker: "3324.TW"
    name_zh: 雙鴻
    role: 液冷冷板與分流單元
    tier: 1
  - ticker: "2421.TW"
    name_zh: 建準
    role: 散熱風扇
    tier: 2
  - ticker: "VRT"
    name_zh: Vertiv
    role: 資料中心熱管理與分流單元
    tier: 1
  - ticker: "PRIVATE:boyd"
    name_zh: Boyd
    role: 液冷冷板
    tier: 2
upstream: [interconnect]
downstream: [odm]
themes: [liquid-cooling]
kpis:
  - 液冷方案滲透率
  - 單機櫃散熱價值量
  - 冷板與分流單元的產能與交期
signals:
  - 機櫃世代的散熱架構轉換
  - 雲端業者新建案的液冷標案歸屬
---
