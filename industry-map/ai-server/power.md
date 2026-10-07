---
segment: power
name_zh: 電源與供電架構
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2308.TW"
    name_zh: 台達電
    role: 伺服器電源與供電架構
    tier: 1
  - ticker: "2301.TW"
    name_zh: 光寶科
    role: 伺服器電源
    tier: 1
  - ticker: "6282.TW"
    name_zh: 康舒
    role: 電源供應器
    tier: 2
  - ticker: "MPWR"
    name_zh: 芯源系統
    role: 電源管理晶片
    tier: 1
  - ticker: "VICR"
    name_zh: Vicor
    role: 高密度電源模組
    tier: 2
upstream: [power-discrete]
downstream: [odm, datacenter]
themes: [liquid-cooling, 800vdc, power-bottleneck]
kpis:
  - 單機櫃供電價值量
  - 高壓直流架構採用比重
  - 電源轉換效率等級
signals:
  - 供電架構世代轉換的規格定案
  - 備援電池模組規格變動
---
