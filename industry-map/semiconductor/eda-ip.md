---
segment: eda-ip
name_zh: EDA 工具與矽智財
layer: semiconductor
position: 1
market_coverage:
  tw: present
  us: present
  led_by: [US]
companies:
  - ticker: "CDNS"
    name_zh: 益華
    role: EDA 工具
    tier: 1
  - ticker: "SNPS"
    name_zh: 新思
    role: EDA 工具與矽智財
    tier: 1
  - ticker: "ARM"
    name_zh: 安謀
    role: 處理器架構授權
    tier: 1
  - ticker: "3529.TWO"
    name_zh: 力旺
    role: 記憶體矽智財授權
    tier: 2
  - ticker: "6643.TWO"
    name_zh: M31
    role: 介面矽智財
    tier: 3
upstream: []
downstream: [compute, networking]
themes: [custom-asic-vs-gpu]
kpis:
  - 權利金與授權金營收組合
  - 先進節點矽智財的導入數量
  - 客戶設計案件數
signals:
  - 新製程節點的工具與矽智財認證完成
  - 客製晶片專案啟動數量變化
---

## 環節定義

EDA 工具支援晶片設計、驗證與實體實現；矽智財（IP）以可重用的架構、電路及介面降低設計風險。工具訂閱、IP 授權金、NRE 與量產權利金的收入節奏不同，應分開分析。客製 ASIC 設計服務業者創意（3443.TW）與世芯（3661.TW）整合整顆晶片及交付專案，依可替換的供應角色歸 `compute`，不因使用 EDA 工具就成為 EDA 供應商。

## 技術變數

先進節點需要對應 PDK、時序／功耗驗證及 silicon-proven IP；高速 SerDes、PCIe 與安全／嵌入式非揮發性記憶體 IP 的價值取決於認證與客戶導入。工具中的 AI 功能可能提高設計效率，但須看實際付費採用。**well-supported**：力旺提供嵌入式非揮發性記憶體及安全 IP，M31 提供高速介面 IP，兩者支持台廠以 IP 角色參與。[力旺技術與商業模式](https://www.ememory.com.tw/neoee.aspx/Investor/IR_QA)、[M31 產品](https://www.m31tech.com/products/)。

## 玩家格局

益華（CDNS）與新思（SNPS）為主要 EDA 工具供應商，新思亦提供 IP；安謀（ARM）以處理器架構及核心 IP 授權參與。台股力旺（3529.TWO）及 M31（6643.TWO）分別以記憶體／安全與介面 IP 參與，故合併環節的 `tw: present` 有明確依據。EDA 工具本身在此地圖未列台股實質供應商；不能以台廠 IP 的存在推論台灣有對等 EDA 工具。客製 ASIC 設計服務依可替換性規則歸 `compute`（代表公司見環節定義），不放入本節授權玩家清單。

## 傳導鏈

`eda-ip → compute / networking`：工具、核心與高速介面 IP 的認證影響加速器及網路 ASIC 的 tape-out，設計案件先帶來工具／授權收入，量產後才可能形成權利金。透過 `custom-asic-vs-gpu` 題材取得客製運算與網路需求。**inference**：案件數增加可能提高授權需求，但失敗或延後的設計不必然產生量產權利金，且不同供應商收費基礎不同。

## 監測指標

分開追蹤授權金、權利金、訂閱續約、在手合約及收入認列，觀察先進節點 IP 認證、design win 與量產轉換。公司 IR、公開申報、免費法說會及晶圓廠生態系公告可交叉核對。**needs verification**：客戶尚未具名、tape-out 尚未完成或沒有量產證據時，不把合作公告當持續權利金收入。

## 風險

授權合約與權利金稽核影響認列，客戶可改用自研或替代 IP。新節點驗證成本、出口限制與專利爭議可能提高銷售門檻；工具集中讓設計生態系有較高轉換成本，也增加客戶對單一供應商的依賴。ASIC 專案增長與 GPU 需求可同時存在，不能用題材名稱推定兩者完全替代。
