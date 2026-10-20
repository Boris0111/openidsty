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
downstream-relations:
  foundry:
    kind: supply
    summary: 半導體材料至晶圓代工：矽晶圓、光阻、氣體、化學品與污染控制等材料子類。
    items:
    - 矽晶圓、光阻、氣體、化學品與污染控制等材料子類
    dependencies:
    - 純度、缺陷、製程配方與供應認證
    conditions:
    - 材料在指定製程及供應批次完成資格驗證
    confidence: inference
    evidence: []
    gaps:
    - 缺少客戶材料清單、純度／缺陷限值與用量；不能把所有材料公司視為同種耗材供應者。
    reviewed: '2026-10-16'
  advanced-packaging:
    kind: supply
    summary: 半導體材料至先進封裝：封裝材料與製程污染控制的供應角色。
    items:
    - 封裝材料與製程污染控制的供應角色
    dependencies:
    - 封裝材料、製程、熱機械應力及可靠度
    conditions:
    - 材料符合指定封裝路線並完成可靠度驗證
    confidence: inference
    evidence: []
    gaps:
    - 尚缺各封裝平台對矽中介層、封裝化學品及污染控制的實際用料，不能由擴產推定全清單受惠。
    reviewed: '2026-10-16'
  substrate:
    kind: supply
    summary: 半導體材料至ABF 載板：材料資格與規格傳導，尚非本清單公司直接交易證據。
    items:
    - 材料資格與規格傳導，尚非本清單公司直接交易證據
    dependencies:
    - 載板樹脂、銅材、製程化學品與設計規則
    conditions:
    - 先核對具名材料與載板認證，才判定直接供應
    confidence: needs-verification
    evidence: []
    gaps:
    - 目前半導體材料公司清單不足以證明 ABF 膜或其他載板材料的直接供應，缺具名材料料號與供應商資格。
    reviewed: '2026-10-16'
  pcb:
    kind: supply
    summary: 半導體材料至印刷電路板與銅箔基板：材料規格傳導，需另核對板材及製程材料子角色。
    items:
    - 材料規格傳導，需另核對板材及製程材料子角色
    dependencies:
    - CCL／樹脂／銅箔、損耗、加工及可靠度
    conditions:
    - 具名材料適用 PCB 堆疊且完成板廠資格驗證
    confidence: needs-verification
    evidence: []
    gaps:
    - 本材料清單不直接代表低損耗 CCL／銅箔供應商；尚缺板材配方、料號與實際供應對照。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 矽晶圓、光阻、特殊氣體、化學品及污染控制是不同材料子類；本清單不直接證明供應 ABF 膜或 CCL。
  adoption-conditions:
  - 按製程、純度、顆粒／金屬污染、接液相容與批次品質完成材料資格認證。
  bottlenecks:
  - 純化、過濾、交期與批次穩定性要連同製程良率驗證，名目供給不等於合格供給。
  substitution-limits:
  - 不同製程配方與污染控制條件限制直接換料；矽晶圓、樹脂與板材不能因同屬材料就互替。
  claims:
  - id: contamination-control-role
    statement: Entegris 公開說明涵蓋液體、氣體與空氣的純化／過濾，支持污染控制角色；不揭露各客戶認證。
    confidence: well-supported
    evidence:
    - source-id: entegris-materials-technical
      url: https://www.entegris.com/en/home/our-science/by-solution-area/contamination-control.html
      locator: Contamination Control／purification and filtration
      read-scope: 已讀指定公開說明；沒有取得客戶完整設計、測試或認證檔
  evidence-gaps:
  - 缺少指定客戶的材料限值、實際用量與資格測試；材料到載板／PCB 僅保留具體待核實供應缺口。
  reviewed: '2026-10-16'
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
