---
segment: advanced-packaging
name_zh: 先進封裝
layer: ai-server
position: 4
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2330.TW"
    name_zh: 台積電
    role: CoWoS 與 SoIC 先進封裝
    tier: 1
  - ticker: "3711.TW"
    name_zh: 日月光投控
    role: 委外封測與先進封裝
    tier: 1
  - ticker: "6239.TW"
    name_zh: 力成
    role: 記憶體與邏輯封測
    tier: 2
  - ticker: "AMKR"
    name_zh: 艾克爾
    role: 委外封測
    tier: 2
upstream: [materials, equipment, test, substrate, memory, compute]
downstream: [odm]
themes: [cpo-silicon-photonics, hbm4]
kpis:
  - 先進封裝月產能與擴產進度
  - 良率與中介層尺寸世代
  - 產能分配給各客戶的比重
signals:
  - 擴產計畫與資本支出調整
  - 封裝技術世代轉換（中介層轉面板級）
---

## 環節定義

把運算晶粒、HBM 與中介層整合為單一封裝體，是加速器從「晶片」變成「可用元件」的關鍵一步。

與傳統封測的根本差別：它決定了封裝體能容納多少運算與多少記憶體，因此**已成為效能的直接限制，而不是後段加工**。

## 技術變數

中介層面積（以光罩倍數計）決定能放幾顆運算晶粒與幾堆 HBM。良率隨面積上升而惡化，所以「面積與良率的取捨」是本環節的核心工程問題。

中介層可採矽、RDL 及局部矽互連等不同組合；晶圓轉面板是加工尺寸與經濟性的變化，玻璃核心載板則涉及另一個材料層次，不能當成同一條互斥路線。**well-supported**：CoWoS-S／R／L 的結構與分工可由官方產品資料查核；面板級或玻璃方案的客戶量產仍須另有證據。[台積電 CoWoS 技術](https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm)。

## 玩家格局

台積電以 CoWoS 與 SoIC 在高階領先，並藉製程與代工的綁定取得分配權。日月光投控與力成承接委外封測與部分先進封裝，艾克爾為美系委外選項。

產能分配影響加速器出貨節奏，但由供應商、客戶承諾、認證與長期合約共同決定，不能宣稱加速器廠完全沒有分配議價能力。

## 傳導鏈

**上游最寬的環節**，同時牽動六個方向：`materials`、`equipment`、`test`、`substrate`、`memory`、`compute`。

因此擴產消息的候選影響面包括設備、載板、測試與材料。看到擴產，應往上游六個方向各走一步；**inference** 的個股受惠仍取決於實際材料、設備料號、客戶認證及訂單，不能把關聯直接當已確認收入。

**下游**：封裝完成品進入 `odm` 組裝。本環節是整條鏈最常出現的瓶頸，產能缺口會直接壓制 `odm` 與 `datacenter` 的實際交付量，即使終端需求無虞。

## 監測指標

先進封裝月產能與擴產進度、良率與中介層尺寸世代、產能分配給各客戶的比重。

**供需缺口的收斂程度比絕對產能數字更能反映景氣位置** —— 產能翻倍但缺口未縮，代表需求同步放大；缺口收斂才是鬆動的訊號。

## 風險

產能高度集中於單一廠商與單一地理區域。擴產週期長，判斷失準會造成長期閒置或長期缺貨。若競爭者先在面板級封裝取得經濟性，現有的領先地位可能被侵蝕。
