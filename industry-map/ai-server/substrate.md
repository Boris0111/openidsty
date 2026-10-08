---
segment: substrate
name_zh: ABF 載板
layer: ai-server
position: 2
market_coverage:
  tw: present
  us: none
  led_by: [JP]
companies:
  - ticker: "4062.T"
    name_zh: Ibiden
    role: 高階 ABF 載板主要供應者
    tier: 1
  - ticker: "PRIVATE:shinko"
    name_zh: Shinko
    role: 高階 ABF 載板
    tier: 1
  - ticker: "3037.TW"
    name_zh: 欣興
    role: ABF 載板
    tier: 1
  - ticker: "8046.TW"
    name_zh: 南電
    role: ABF 載板
    tier: 1
  - ticker: "3189.TW"
    name_zh: 景碩
    role: ABF 載板
    tier: 2
upstream: [materials]
downstream: [advanced-packaging]
themes: []
kpis:
  - 高層數載板產能與稼動率
  - 載板層數與尺寸世代
  - 單位面積售價
signals:
  - 擴產計畫與交期變化
  - 玻璃基板等替代技術的導入進度
---

## 環節定義

ABF 載板位於晶粒／中介層與系統 PCB 之間，負責把封裝內的細密訊號與供電接點引出到主板。它是封裝體的一部分，與 `pcb` 的整機電路板分工不同；也不能把有機載板與矽中介層視為同一產品。

本環節以可供封裝廠替換、但需要重新認證的 IC 封裝載板供應角色切分。ABF 是增層絕緣材料體系，競爭重點在供應商能否穩定製造高密度、多層、大尺寸載板。[Ibiden 產品說明](https://www.ibiden.com/product/electronics/merchandise/fliptippkg/)

## 技術變數

晶粒與 HBM 整合規模提高，會增加封裝載板的佈線密度、層數與供電需求。需一起看線寬／線距、micro-via 可靠性、銅層對位、翹曲與熱膨脹控制；只比較名目產能，會忽略良率與客戶認證限制。

大尺寸載板的有效產出還取決於每片製造面板可切出的數量。玻璃核心等替代路線須分別確認材料、製程與封裝認證，不能由試作公告直接推論既有 ABF 產線被取代。

## 玩家格局

日本以 **Ibiden（4062.T）** 與 **Shinko（PRIVATE:shinko）** 對照高階封裝載板能力；台灣列入 **欣興（3037.TW）**、**南電（8046.TW）** 與 **景碩（3189.TW）**。比較時看高階產品組合、認證進度與良率，不能把各廠全部載板營收等同 AI 曝險。

Shinko 已於 2025-06-06 下市，仍是供應鏈玩家，故用未上市識別鍵保留；原 `6967.T` 不再代表可交易股票。[Shinko 官方 FAQ](https://www.shinko.co.jp/english/ir/faq/)

`market_coverage.us: none` 表示本圖沒有列入美股的主要 ABF 載板量產供應者。美系晶片設計商是需求方，不因採用載板就屬於此供應角色；日本主導標記由仍上市的 Ibiden 支撐。

## 傳導鏈

**上游 `materials` → 本環節**：樹脂、銅材與相關材料的交期、品質或規格變動，透過材料認證、製程良率與成本影響可交付產出。

**本環節 → 下游 `advanced-packaging` → `odm`**：載板尺寸或層數升級提高製造難度；若合格載板供給落後，封裝廠即使已有晶粒與 HBM，也可能無法完成交付。反向看到封裝擴產時，應沿封裝的 `upstream` 查載板配套，而不能把封裝名目產能直接當成載板訂單。

以上是依地圖關係與工程限制的 **inference**；實際受惠廠商仍需核對料號認證、客戶採購與出貨證據。

## 監測指標

對應 `kpis` 追蹤高層數載板的有效產能與稼動率、層數／尺寸世代，以及單位面積售價。交期與擴產公告要同時看量產爬坡、折舊負擔與良率；按片計價的單價上升可能只是面積變大。

台廠資訊查公司 IR 與公開資訊觀測站；日廠查 [Ibiden 財務與法說資料](https://www.ibiden.com/ir/news/financial/)。指標記錄觀察項目，不在地圖保存當期數字。

## 風險

客戶／平台集中、長認證週期、擴產折舊與良率不及預期，都可能使需求成長無法轉成獲利。一般載板與 AI 高階載板可能處於不同供需週期，不能合併判讀。替代核心材料的量產時程屬 **needs verification**，以客戶採用與持續出貨確認。
