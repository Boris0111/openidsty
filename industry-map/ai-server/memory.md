---
segment: memory
name_zh: 記憶體
layer: ai-server
position: 2
market_coverage:
  tw: present
  us: present
  led_by: [KR]
companies:
  - ticker: "000660.KS"
    name_zh: SK 海力士
    role: HBM 主要供應者
    tier: 1
  - ticker: "005930.KS"
    name_zh: 三星電子
    role: HBM 與 DRAM
    tier: 1
  - ticker: "MU"
    name_zh: 美光
    role: HBM 與 DRAM
    tier: 1
  - ticker: "2408.TW"
    name_zh: 南亞科
    role: 利基型 DRAM
    tier: 2
  - ticker: "2344.TW"
    name_zh: 華邦電
    role: 利基型記憶體
    tier: 2
  - ticker: "8299.TWO"
    name_zh: 群聯
    role: NAND 控制晶片與模組
    tier: 2
upstream: [equipment]
downstream: [advanced-packaging]
themes: [hbm4]
kpis:
  - HBM 位元出貨量與供給分配
  - 傳統 DRAM 合約價走勢
  - HBM 佔營收比重
signals:
  - 次世代 HBM 認證通過與供給分配變動
  - 傳統記憶體轉產 HBM 造成的排擠
---

## 環節定義

提供加速器所需的高頻寬記憶體（HBM）與伺服器主記憶體。HBM 以堆疊方式與運算晶片共同封裝，因此本環節與 `advanced-packaging` 的耦合遠高於傳統記憶體 —— 它不是「賣一顆料給客戶」，而是必須配合封裝製程一起認證。

業者多為整合元件製造商，自有晶圓廠，不依賴代工。

## 技術變數

HBM 的競爭變數是堆疊層數、頻寬，以及散熱與良率之間的取捨 —— 層數越高越難散熱、良率越低。

下一個分歧點是基底晶片是否改由邏輯代工廠製造：若成真，晶圓代工會被拉進 HBM 的價值分配，改變本環節與 `foundry` 的關係。

傳統 DRAM 與 NAND 則是標準品循環，變數在供需與各廠的資本支出紀律。

## 玩家格局

HBM 由韓廠主導：SK 海力士在認證進度上領先，三星電子與美光競逐份額。三家都受制於與加速器廠的認證節奏，**份額變動往往一次性地大幅移轉**，而非逐季緩慢消長。

台廠不在 HBM 主戰場。位置在利基型記憶體（南亞科、華邦電）與 NAND 控制晶片與模組（群聯）。這使台廠的受益方式是**間接的** —— 見下方傳導鏈。

## 傳導鏈

**上游**：`equipment` 的設備交期決定 HBM 擴產速度。

**下游**：HBM 產出直接進入 `advanced-packaging` 與運算晶片共同封裝。供給不足會成為整條鏈的瓶頸 —— 即使 `foundry` 與 `advanced-packaging` 都有餘裕，缺 HBM 一樣出不了貨。

**環節內部的排擠效應**：HBM 擠壓標準型 DRAM 產能 → 利基型記憶體供給緊縮、價格上揚 → 南亞科、華邦電受惠。這條路徑不經上下游，而發生在環節內部，是最容易被漏掉的一條。

## 監測指標

HBM 位元出貨量與各廠供給分配、傳統 DRAM 合約價走勢、HBM 佔各廠營收比重。

認證進度須以**供應商法說會點名客戶**為準；供應商單方面宣稱「已送樣」不足以採信。

## 風險

供給高度集中於韓國，地緣風險與單一廠區事故難以分散。認證失敗或延後會讓份額一次性流失。若加速器廠轉向「較少層數、較多顆」的配置，單價結構會改變。傳統記憶體部分仍受標準品循環擺動，與 AI 需求不同調。
