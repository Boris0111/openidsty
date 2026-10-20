---
segment: datacenter
name_zh: 資料中心與雲端業者
layer: ai-server
position: 6
market_coverage:
  tw: none
  us: present
  led_by: [US]
companies:
  - ticker: "MSFT"
    name_zh: 微軟
    role: 超大規模雲端業者
    tier: 1
  - ticker: "GOOGL"
    name_zh: 谷歌
    role: 超大規模雲端業者
    tier: 1
  - ticker: "AMZN"
    name_zh: 亞馬遜
    role: 超大規模雲端業者
    tier: 1
  - ticker: "META"
    name_zh: Meta
    role: 自用大規模運算
    tier: 1
  - ticker: "ORCL"
    name_zh: 甲骨文
    role: 雲端業者
    tier: 2
  - ticker: "CRWV"
    name_zh: CoreWeave
    role: 新興 AI 雲端業者
    tier: 2
upstream: [odm, power]
downstream: [compute]
themes: [liquid-cooling, 800vdc, power-bottleneck]
kpis:
  - 資本支出金額與年增率
  - 新增機房電力容量
  - 自研晶片佔自身部署比重
signals:
  - 財報與法說會的資本支出指引調整
  - 新建案選址與電力併網時程
downstream-relations:
  compute:
    kind: demand-feedback
    summary: 資料中心的算力部署需求與預算回頭形成運算晶片採購需求。
    items:
    - 可交付算力與平台部署所需的 GPU／客製 ASIC 需求
    dependencies:
    - 供電與冷卻容量、平台軟體相容性、機櫃及網路整合
    conditions:
    - 預算確實用於運算設備且完成採購部署，不能只依土地建物 capex 指引推定
    confidence: inference
    evidence: []
    gaps:
    - 尚未逐一拆出各雲端業者的 GPU／ASIC 採購金額、料號、交付及收入認列，不由總 capex 倒推。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 取得並營運可用 IT 算力與設施容量；土地建築、供電冷卻、設備與租賃投入分開，需求回饋不表示供應晶片。
  adoption-conditions:
  - 核對電網接入、可用電力／冷卻、網路、運維及實際負載，不能把簽約 MW 當已上線容量。
  bottlenecks:
  - 電網併接、許可、場址與供應鏈交付可能限制投產；capex 增長不能直接換算 GPU 收入。
  substitution-limits:
  - 自建、託管、租賃及雲端容量有不同責任與可用性；GPU／ASIC 配置需依工作負載與軟體另驗證。
  claims:
  - id: grid-deployment-gap
    statement: IEA 公開摘要討論電網瓶頸、併接排隊與彈性資源；這不是個別場址完成併網的證明。
    confidence: well-supported
    evidence:
    - source-id: iea-energy-ai-technical
      url: https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary
      locator: Executive summary／grid bottlenecks and connection queues
      read-scope: 僅核讀公開摘要，未核讀報告全文
  evidence-gaps:
  - 未取得各場址接電、驗收、可售容量與服務收入的完整對照，亦缺 GPU／ASIC capex 拆分。
  reviewed: '2026-10-16'
---

## 環節定義

雲端與大規模運算業者是算力、機櫃及設施採購的需求源頭，透過自有機房、租賃或託管取得可用容量。此處的市場覆蓋以具規模的雲端部署與算力採購角色為邊界；台灣伺服器製造商歸 `odm`，電源設備歸 `power`，不因參與機房建設就列為 hyperscaler。`tw: none` 表示本清單沒有對等的台股大型需求主體，並非台灣沒有機房或雲端服務。

## 技術變數

資本支出必須拆成土地／建築、電力／冷卻、伺服器／網路，以及融資租賃；各自投產速度與使用年限不同。新增 MW 要辨認是申請、簽約、接電還是已上線 IT 負載，不能把承諾容量當可售算力。AI 工作負載的利用率、GPU 與自研 ASIC 組合、網路拓樸及機櫃密度，決定投入何時形成服務收入。**well-supported**：微軟的公開法說會區分短期設備與長期建物投資；IEA 指出機房負載成長與電網／供應鏈限制須同時評估。[微軟 FY2026 Q4 法說會](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)、[IEA 能源與 AI 摘要](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)。

## 玩家格局

微軟（MSFT）、谷歌（GOOGL）及亞馬遜（AMZN）兼有大型雲端平台與自用部署；Meta（META）主要以自用運算支撐廣告、推薦與 AI 服務，不能直接套用公有雲收入模型。甲骨文（ORCL）以雲端服務擴充為需求角色；CoreWeave（CRWV）偏向 AI 算力服務，需額外看客戶集中、融資及租賃承諾。美股需求端居主導，故 `led_by: [US]`，台股以明確 `none` 表態。

## 傳導鏈

`odm → datacenter` 與 `power → datacenter` 表示整櫃及供電設備進入設施；`datacenter → compute` 表示部署預算與算力需求回頭驅動 GPU／ASIC 採購。因此 `compute → advanced-packaging → odm → datacenter → compute` 是需求回饋的真實回路，遍歷必須記錄已訪問節點。經液冷與 800VDC 題材可跳到散熱、電源及機櫃介面。**inference**：capex 指引調升擴大供應鏈機會，但若增量主要是土地、建物或租賃，不能直接換算當季晶片或 ODM 收入。

## 監測指標

追蹤 capex 及其現金／租賃口徑、財報指引與實際交付差異、已接電 IT 容量、併網等待時間、設施使用率、AI 收入與算力需求，以及自研晶片部署比重。優先使用公司 10-K／10-Q、財報新聞稿、免費法說會及公用事業／能源官方資料；PPA 只是購電安排，不代表電網接入已完成。管理層需求敘述列 **needs verification**，須以收入、履約義務與投產資料交叉確認。

## 風險

電力、土地、設備與施工任何一項延誤都可能讓已買晶片無法使用。過度建設會壓低利用率與回報，融資與長期租賃放大固定承諾。自研 ASIC 改變供應商分配，不必然降低全部晶片支出；出口管制、資料主權及電價則改變選址和經濟性。需求擴張是供應鏈機會，對採購方同時也是折舊、能源與資本成本壓力。
