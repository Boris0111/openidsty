---
segment: equipment
name_zh: 半導體設備
layer: semiconductor
position: 1
market_coverage:
  tw: present
  us: present
companies:
  - ticker: "ASML"
    name_zh: 艾司摩爾
    role: 商用 EUV 微影設備獨家供應與 DUV 微影
    tier: 1
  - ticker: "AMAT"
    name_zh: 應用材料
    role: 薄膜與蝕刻設備
    tier: 1
  - ticker: "LRCX"
    name_zh: 科林研發
    role: 蝕刻與沉積設備
    tier: 1
  - ticker: "KLAC"
    name_zh: 科磊
    role: 量測與檢測設備
    tier: 1
  - ticker: "8035.T"
    name_zh: 東京威力科創
    role: 塗佈顯影與蝕刻設備
    tier: 1
  - ticker: "3131.TWO"
    name_zh: 弘塑
    role: 濕製程設備
    tier: 2
  - ticker: "3583.TW"
    name_zh: 辛耘
    role: 濕製程設備與代理
    tier: 2
upstream: []
downstream: [foundry, advanced-packaging, test, memory]
themes: [advanced-node-2nm]
kpis:
  - 設備訂單與出貨比
  - 各地區營收組合
  - 先進製程設備佔比
signals:
  - 客戶資本支出指引調整
  - 出口管制範圍變動
---

## 環節定義

提供製造、封裝與檢測所需的微影、沉積、蝕刻、清洗、塗佈顯影及製程控制設備，收入包含新機台與安裝基礎的服務／零件。設備採購受客戶 capex 驅動，通常早於新增產能的晶片收入。本環節的製程與設備供應歸 `equipment`，測試服務、ATE 及接觸介面主要歸 `test`，避免把同一測試機台重複統計。

## 技術變數

EUV／High-NA 影響解析度與製程整合，GAA 與 3D 結構增加高選擇性蝕刻、沉積及檢測需求；先進封裝另有濕製程、清洗與大型基板處理。技術步驟增加能提高設備強度，但需配合 throughput、良率與客戶驗收。**well-supported**：商用 EUV 的獨家供應地位屬於 EUV，不能寫成所有微影設備皆獨家。[ASML EUV 產品說明](https://www.asml.com/en/products/euv-lithography-systems)。

## 玩家格局

艾司摩爾（ASML）為荷蘭公司，本地圖以美國上市代號識別，供應 EUV 與 DUV；應用材料（AMAT）覆蓋薄膜等製程設備，科林研發（LRCX）偏重蝕刻與沉積，科磊（KLAC）偏重製程控制、量測與檢測。東京威力科創（8035.T）覆蓋塗佈顯影及蝕刻等設備。台股弘塑（3131.TWO）提供濕製程設備，辛耘（3583.TW）兼有自製設備、設備代理及晶圓再生服務，不能把總營收全部當自製封裝設備收入；其官方資料確認為上市公司，故使用 `.TW`。[辛耘公司概況](https://www.scientech.com.tw/zh-hant/Investor/Finance/Fundamentals)。

## 傳導鏈

`equipment → foundry / memory / advanced-packaging / test`：設備與量測能力限制新增製程、記憶體及封裝產能的爬坡。從 CoWoS 擴產事件反查 `advanced-packaging.upstream` 能找到設備玩家；2nm 題材連到晶圓代工與材料。**inference**：capex 上調增加潛在訂單，但土建支出、未驗收訂單及重複採購不等同設備當期認列收入。

## 監測指標

追蹤新訂單、出貨、驗收及收入認列的差距，book-to-bill 僅在公司實際揭露時使用；比較地區、客戶與製程別收入，以及服務收入和裝機基礎。以各公司 IR、公開申報和客戶 capex 法說會交叉確認。High-NA 展示或新廠公告列 **needs verification**，要等訂單、安裝與量產驗收，不能單憑 roadmap 判定商業放量。

## 風險

客戶集中與景氣循環會放大訂單波動，零件供應、現場安裝及良率驗收可能延後認列。出口許可限制會改變區域組合；不同國家與產品的規定須在事件發生時重新查核。台廠自製、代理及服務的毛利結構不同，不能僅以設備總營收推估獲利。
