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

## 環節定義

把運算封裝、主板、網通、散熱、電源與線材整合成可交付的伺服器或機櫃，並完成韌體、測試、燒機及客戶驗收。本檔以系統交付角色歸類，包含 ODM 與品牌整合商；兩者的設計責任、採購模式與服務範圍仍有差異。

從單機組裝走向整櫃交付後，驗收單位擴大到電力、液路、互連及軟體共同運作的系統。[Supermicro 機櫃與液冷整合方案](https://www.supermicro.com/en/solutions/liquid-cooling)

## 技術變數

關鍵在平台世代的量產導入、整櫃互連、散熱／供電協同設計與工廠測試。液冷要核對冷板、CDU、manifold、快接頭及機房水路的接口；高功率機櫃要處理供電保護、韌體調校與動態負載。

要分清整櫃出廠、到貨、完成機房接線與正式驗收；不同階段的瓶頸及收入認列時點不同。800VDC 等架構變動須看認證與客戶配置，不能把 roadmap 直接當作當期出貨。

## 玩家格局

台廠列入 **鴻海（2317.TW）**、**廣達（2382.TW）**、**緯創（3231.TW）**、**緯穎（6669.TW）**，以及參與品牌／代工交付的 **技嘉（2376.TW）**、**英業達（2356.TW）**。美股對照 **美超微（SMCI）**與 **戴爾（DELL）**的品牌及系統整合角色。

比較重點是客戶專案、設計與物料採購責任、單機或整櫃交付範圍。品牌商與 ODM 的營收可能包含不同程度的高價晶片成本，不能直接用營收規模推論組裝份額或毛利能力。

## 傳導鏈

**第 4 組上游路徑**：`compute` 的晶粒與 `memory` 的 HBM 經 `advanced-packaging` 整合後進入本環節；任何一項供給或認證延遲，都可能使組裝廠有訂單但缺料。

其餘直接上游為 `networking`、`pcb`、`thermal`、`power`、`interconnect`。整櫃交付取決於整份 BOM 的齊料與驗收，不以最高價元件到貨就視為完成。

**本環節 → `datacenter` → `compute`**：組裝交付決定終端部署；資料中心的追加資本支出又回頭形成新平台需求。這是地圖的回路，遍歷須記錄已訪問節點。份額移轉對個別廠商的影響屬 **inference**，需客戶採購或公司法說會佐證。

## 監測指標

看機櫃出貨量、平均單價、系統組裝毛利率與專案份額，另查缺料、工廠驗收、應收帳款／存貨週轉及液冷產線爬坡。金額型指標需拆出晶片轉售成本與交付範圍。

台廠用月營收、財報及 IR 法說會交叉核對；美廠用 SEC 公開申報及 earnings call。出貨指引、實際交付與客戶正式上線應各自記錄。

## 風險

客戶／平台集中、低毛利組裝、缺料造成資金占用、液冷漏液與整櫃售後責任，可能放大專案風險。客戶取消或延後驗收時，高價存貨與應收帳款會承壓；機房電力或水路未就緒，也可能讓已完成組裝的機櫃延後部署。
