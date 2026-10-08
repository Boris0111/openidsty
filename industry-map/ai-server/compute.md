---
segment: compute
name_zh: 運算晶片
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [US]
companies:
  - ticker: "NVDA"
    name_zh: 輝達
    role: GPU 與機櫃級規格定義者
    tier: 1
  - ticker: "AMD"
    name_zh: 超微
    role: MI 系列 GPU
    tier: 1
  - ticker: "AVGO"
    name_zh: 博通
    role: 客製 ASIC 設計與交付
    tier: 1
  - ticker: "MRVL"
    name_zh: 邁威爾
    role: 客製 ASIC 設計
    tier: 1
  - ticker: "GOOGL"
    name_zh: 谷歌
    role: 自研 TPU
    tier: 1
  - ticker: "INTC"
    name_zh: 英特爾
    role: Gaudi 加速器與伺服器 CPU
    tier: 2
  - ticker: "3661.TW"
    name_zh: 世芯
    role: 客製 ASIC 設計服務
    tier: 2
  - ticker: "3443.TW"
    name_zh: 創意
    role: 客製 ASIC 設計服務
    tier: 2
upstream: [eda-ip, foundry, datacenter]
downstream: [advanced-packaging]
themes: [cpo-silicon-photonics, hbm4, custom-asic-vs-gpu]
kpis:
  - 加速器出貨量與單價
  - 客製 ASIC 佔整體加速器比重
  - 下世代平台量產時程
signals:
  - 新世代平台發表與量產時程變動
  - 雲端業者自研晶片專案得標歸屬
---

## 環節定義

AI 伺服器的運算核心：設計加速器晶片並定義整機櫃規格。本節描述公司在設計與平台上的角色；晶圓製造、先進封裝另依對應環節判讀。多數供應者委外製造，但不能由此推定清單中的 IDM 沒有自有晶圓廠。

輝達除晶片之外還定義機櫃級參考架構，使本環節的決策會一路約束到散熱、電源與互連的規格。

## 技術變數

兩條路線並行，分歧點在於工作負載是否足夠穩定：

- **通用加速器（GPU）** —— 軟體生態系與開發工具鏈是重要護城河，支援多種工作負載
- **客製 ASIC／XPU** —— 針對特定工作負載設計，在規模與利用率足夠時可能取得成本優勢，但須負擔設計及軟體整合成本

**inference**：穩定且大量重複的工作負載有利客製化，但訓練與推論都可能採用 GPU 或 ASIC，不能以工作負載名稱判定唯一硬體。其他關鍵變數是封裝內記憶體容量與頻寬、功耗、互連及軟體效率；機櫃互連也改變「運算單元」是單顆晶片或整座機櫃。商業需求與量產須用公司財報及客戶部署驗證。[Broadcom 商業需求與財報](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)。

## 玩家格局

- **通用加速器**：輝達主導，超微以 MI 系列競逐
- **客製 ASIC**：博通與邁威爾承接雲端業者專案；谷歌的自研 TPU 已大規模自用
- **英特爾**以 Gaudi 加速器與伺服器 CPU 參與，位階相對弱
- **台廠以設計服務形式參與**：世芯與創意承接客製 ASIC 的實作與量產導入，在「替雲端業者把晶片做出來」這個可替換的角色上，與博通、邁威爾正面競爭

EDA 工具與矽智財屬 `eda-ip`，不在本環節。

## 傳導鏈

**上游**：`eda-ip` 的工具與矽智財決定設計週期；`foundry` 的節點可用性與產能分配直接決定能否如期出貨；`datacenter` 的資本支出是需求源頭 —— 這條邊讓本環節與下游構成回路，遍歷時必須記錄已訪問節點。

**下游**：本環節的規格決定 `advanced-packaging` 的中介層尺寸與 HBM 堆疊數，再往 `substrate` 與 `memory` 擴散；機櫃級規格一旦變動，`thermal`、`power`、`interconnect` 必須同步改版。

因此**本環節的新平台發表，是整張地圖擴散面最廣的事件起點**。

## 監測指標

加速器出貨量與單價、客製 ASIC 佔整體加速器的比重、下世代平台的量產時程。雲端業者的自研比重揭露在 `datacenter` 一側取得。

判讀時優先看法說會問答而非開場簡報 —— 時程變動通常在問答中才會鬆口。

## 風險

客戶高度集中於少數雲端業者，而這些客戶同時是自研晶片的競爭者 —— **客戶與對手是同一批人**。出口管制使特定市場可銷售的規格受限。若標準化介面削弱了軟體生態系的鎖定效果，通用路線的護城河會變薄。
