---
theme: cpo-silicon-photonics
name_zh: 共同封裝光學與矽光子
status: validating
segments: [networking, advanced-packaging, compute]
beneficiaries:
  - "AVGO"
  - "MRVL"
  - "2330.TW"
  - "3081.TWO"
  - "4979.TWO"
milestones:
  - date: 2026
    event: 核對商用 CPO 交換器及具名採用者的導入階段
    evidence: NVIDIA 2026-05-31 公告列出 Spectrum-X Photonics 生產與 CoreWeave、Lambda、Oracle 採用者；逐案補客戶驗收及實際部署資料
  - date: 2026-Q4
    event: 待確認 CPO 封裝的量產訂單與出貨量化
    evidence: 封裝廠財報或法說會明確區分 CPO 訂單、出貨或收入；僅有產能投入不足以視為完成
  - date: 2027
    event: 觀察可插拔光模組與 CPO 的方案分工
    evidence: 具名雲端業者採購規格、光學連接距離及光模組廠產品收入，需對照相同平台與使用場景
---

## 題材範圍

將光學引擎靠近交換器／運算封裝，以縮短高功耗的電氣傳輸路徑。矽光子是實現光學整合的技術，CPO 是封裝配置，兩者不是同義詞；可插拔光模組、LPO 與 CPO 仍可能按距離和可維修性分工。[Broadcom CPO 技術](https://www.broadcom.com/info/optics/cpo)。

## 傳導與受惠條件

`networking ↔ cpo-silicon-photonics ↔ advanced-packaging / compute` 是題材擴散，並非新增上下游邊。AVGO、MRVL 對應交換器／光學訊號處理，2330.TW 對應封裝整合；3081.TWO、4979.TWO 是光通訊候選角色。**inference**：光學布局轉換增加某些元件需求，也可能替代既有可插拔產品；`beneficiaries` 表示追蹤候選，個別 CPO 訂單與產品適配仍列 **needs verification**。

## 狀態判定依據

查核日期：2026-10-07。保留 `validating` 作為本檔可核對的公開證據等級。**well-supported**：Broadcom 已公告 CPO 商用品出貨，NVIDIA 亦公告生產及具名採用者，故不能描述成只有研究或樣品。仍未取得可分辨 CPO 的財報／法說會量化放量資料，不以 AI 網路總收入代替 CPO 收入，也不升為 `scaling`；這是證據限制，不是宣稱完全沒有商業出貨。[Broadcom 商用 CPO 公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)、[NVIDIA 生產與採用者公告](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory)。後續取得 CPO 訂單及量化出貨證據才升級；維修成本或客戶轉回可插拔方案則重新評估。
