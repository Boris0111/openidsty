---
segment: odm
name_zh: 系統組裝與機櫃整合
layer: ai-server
position: 5
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2317.TW"
    name_zh: 鴻海
    role: 機櫃與系統組裝
    tier: 1
  - ticker: "2382.TW"
    name_zh: 廣達
    role: AI 伺服器代工
    tier: 1
  - ticker: "3231.TW"
    name_zh: 緯創
    role: AI 伺服器代工
    tier: 1
  - ticker: "6669.TW"
    name_zh: 緯穎
    role: 雲端業者專用伺服器
    tier: 1
  - ticker: "2376.TW"
    name_zh: 技嘉
    role: 伺服器品牌與代工
    tier: 2
  - ticker: "2356.TW"
    name_zh: 英業達
    role: 伺服器代工
    tier: 2
  - ticker: "SMCI"
    name_zh: 美超微
    role: 伺服器品牌與整合
    tier: 1
  - ticker: "DELL"
    name_zh: 戴爾
    role: 伺服器品牌
    tier: 2
upstream: [advanced-packaging, networking, pcb, thermal, power, interconnect]
downstream: [datacenter]
themes: [liquid-cooling, 800vdc]
kpis:
  - 機櫃出貨量與機櫃平均單價
  - 系統組裝毛利率
  - 各客戶專案的份額分配
signals:
  - 機櫃世代轉換與規格變更
  - 專案份額在代工廠之間的移轉
---
