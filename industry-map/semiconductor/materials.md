---
segment: materials
name_zh: 半導體材料
layer: semiconductor
position: 1
market_coverage:
  tw: present
  us: present
  led_by: [JP]
companies:
  - ticker: "3436.T"
    name_zh: SUMCO
    role: 矽晶圓
    tier: 1
  - ticker: "6488.TWO"
    name_zh: 環球晶
    role: 矽晶圓
    tier: 1
  - ticker: "5483.TWO"
    name_zh: 中美晶
    role: 矽晶圓與材料
    tier: 2
  - ticker: "4186.T"
    name_zh: 東京應化
    role: 光阻材料
    tier: 1
  - ticker: "ENTG"
    name_zh: 恩特格里斯
    role: 製程材料與過濾
    tier: 1
  - ticker: "LIN"
    name_zh: 林德
    role: 特殊氣體
    tier: 2
upstream: []
downstream: [foundry, advanced-packaging, substrate, pcb]
themes: [advanced-node-2nm]
kpis:
  - 矽晶圓出貨面積與長約價格
  - 先進製程材料的認證進度
  - 特殊氣體與耗材供給穩定度
signals:
  - 長約簽訂條件與價格調整
  - 新製程世代的材料規格切換
---

## 環節定義

供應晶圓、光阻、特殊氣體、製程化學品與過濾／純化等消耗性材料，收入受加工量、材料規格及認證資格共同驅動。此為跨製程的材料群組，各子類供應商只在同一規格內互相替換；矽晶圓不等於 ABF 膜或 PCB 的 CCL。`materials → substrate / pcb` 表示材料規格傳導，不能因此宣稱清單上的每家材料商都供應 ABF 或低損耗銅箔基板。

## 技術變數

先進節點及異質整合提高顆粒、金屬污染、薄膜均勻性與材料相容性的要求；矽晶圓的尺寸、平坦度和缺陷密度，光阻的解析度與缺陷，以及氣體／化學品的純度，都影響良率。認證過程長，替換需要重新驗證。**well-supported**：製程與先進封裝均需要污染控制，但各製程所用材料及規格不同。[Entegris 污染控制](https://www.entegris.com/en/home/our-science/by-solution-area/contamination-control.html)、[封裝廠材料與設施控制](https://www.entegris.com/en/home/our-science/by-industry/microelectronics/semiconductor/advanced-packaging/facility.html)。

## 玩家格局

日本 SUMCO（3436.T）與台股環球晶（6488.TWO）供應矽晶圓；中美晶（5483.TWO）具有矽晶圓相關集團布局，與環球晶的集團關係意味著投資分析不能把兩者收入直接相加。東京應化（4186.T）提供光阻等材料，美股恩特格里斯（ENTG）覆蓋製程材料與污染控制，林德（LIN）供應工業及電子氣體。`led_by: [JP]` 表示日本在多項關鍵材料的供應地位，並非所有材料子類的市佔都由日本領先。

## 傳導鏈

`materials → foundry`：材料純度、認證與交期影響晶圓產量及良率；`materials → advanced-packaging`：封裝材料與製程污染控制影響大型封裝可靠度。`materials → substrate / pcb`：規格升級先形成材料資格認證，再形成載板與板材供應。透過 2nm 題材取得 `equipment`，表示新節點同時改變材料與設備需求。**inference**：封裝擴產增加材料機會，但環球晶等矽晶圓公司是否取得增量，要確認是否涉及矽中介層等實際用料；不能把全清單當直接受惠者。

## 監測指標

追蹤矽晶圓出貨面積、長約條件、客戶庫存、產能利用率，新材料認證至量產的進度，以及氣體／耗材供應穩定度。公司 IR、公開申報及客戶法說會提供財務與採購線索；產品規格確認材料用途。**needs verification**：未揭露的特定客戶、先進節點收入與長約價格不能以整體營收代替。

## 風險

半導體材料同時受去庫存、長約調整與擴產影響；認證壁壘不保證價格永不下降。供應中斷、純度缺陷或單一原料來源可能造成客戶停線及賠償。集團持股、能源成本、匯率與地緣限制影響收益；將所有材料概括為 AI 受惠會忽略非 AI 終端的循環。
