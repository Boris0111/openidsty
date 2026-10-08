---
theme: power-bottleneck
name_zh: 資料中心電力瓶頸
status: scaling
segments: [datacenter, power]
beneficiaries:
  - "VRT"
  - "2308.TW"
  - "MSFT"
milestones:
  - date: 2026
    event: 核實電網與設施交付對機房部署的限制
    evidence: IEA 能源與 AI 報告、具名公用事業併網時程及雲端業者新建案交付說明，區分電力與其他設備限制
  - date: 2026-Q4
    event: 待核對具名 PPA／自備電力方案與實際投產
    evidence: 合約公告、許可、併網與上線 IT 容量交叉核對；簽 PPA 不等於取得即時可用電力，不宣稱已成全市場標準
  - date: 2027
    event: 追蹤供電效率與負載彈性是否改變採購
    evidence: 具名機房標案的效率／備援／調度要求與設備訂單；技術建議不能代替正式採購規格
---

## 題材範圍

追蹤併網、輸配電、備援與電力轉換的限制，以及解除限制所形成的設備採購。狀態指「瓶頸對應的商業投資」，不是電網問題本身的產品成熟度；更高 capex 也不代表瓶頸已解決。[IEA 能源與 AI](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)。

## 傳導與受惠條件

`power → datacenter → compute` 連接設施供電、部署與晶片採購。VRT、2308.TW 為設備方案候選；MSFT 是部署瓶頸解除後的需求端候選，同時承擔能源、折舊及資本成本，不能一律視為正面受惠。**inference**：電力不足可能增加供電改善投資，也可能延後所有機櫃供應鏈收入，方向需按個案判斷。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`，範圍限定在供電與關鍵基礎設施採購。**well-supported**：IEA 報告及微軟法說會提供需求與部署限制脈絡；Vertiv 的 2026 Q2 財報則量化商業收入、訂單與 backlog，支持已有持續採購和交付。[微軟法說會](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)、[Vertiv 財報](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)。Vertiv 財務口徑包含熱管理與服務，不能全額當成電力瓶頸收入；各案瓶頸是否真是併網、以及 PPA 是否已供電，仍列 **needs verification**。
