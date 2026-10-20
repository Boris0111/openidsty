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
    role: DRAM 製造
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
downstream-relations:
  advanced-packaging:
    kind: supply
    summary: 記憶體至先進封裝：HBM 等記憶體 die／stack 與整合需求。
    items:
    - HBM 等記憶體 die／stack 與整合需求
    dependencies:
    - 記憶體控制器、封裝內互連、熱與測試介面
    conditions:
    - 堆疊與基底 die、封裝製程及客戶平台完成共同驗證
    confidence: inference
    evidence: []
    gaps:
    - 未取得指定 HBM stack／base die 組合的客戶認證、測試覆蓋與封裝良率，不能由送樣推定量產。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: HBM DRAM stack、邏輯 base die、伺服器 DRAM 與 NAND／控制器是不同產品與製造分工；同環節不表示都是
    HBM4 供應商。
  adoption-conditions:
  - 按指定控制器、封裝與客戶平台核對 HBM stack／base die 的共同認證。
  - 容量、頻寬、功耗與熱限制須在同一產品世代核對。
  bottlenecks:
  - 堆疊、鍵合、測試與封裝配合共同影響良品供給，不能只看晶圓或層數。
  substitution-limits:
  - DRAM、HBM 與 NAND 不能直接互替；產線排擠幅度仍取決於實際製程與資本配置。
  claims:
  - id: base-die-partnership
    statement: SK hynix 2024 年公開合作公告區分 HBM base die、DRAM 堆疊與台積電製程／CoWoS 合作；計畫不是目前每位客戶的量產證據。
    confidence: well-supported
    evidence:
    - source-id: skhynix-hbm-technical
      url: https://news.skhynix.com/en/sk-hynix-partners-with-tsmc-to-strengthen-hbm-technological-leadership/
      locator: 2024-04-19 公告／base die 與 CoWoS 段落
      read-scope: 已讀指定公開說明；沒有取得客戶完整設計、測試或認證檔
  evidence-gaps:
  - 未取得 HBM4 指定客戶、stack／base die 組合的良率與驗證報告。
  - JEDEC 搜尋頁可讀不等於 HBM4 規格全文已取得；尚不能核對完整介面條文。
  reviewed: '2026-10-16'
---

## 環節定義

提供加速器所需的高頻寬記憶體（HBM）與伺服器主記憶體。HBM 以堆疊方式與運算晶片共同封裝，因此本環節與 `advanced-packaging` 的耦合遠高於傳統記憶體 —— 它不是「賣一顆料給客戶」，而是必須配合封裝製程一起認證。

記憶體晶粒業者多為整合元件製造商，自有晶圓廠；HBM 的邏輯 base die 可另與代工廠分工，不能把 DRAM 自製推論成整個 HBM 模組完全不依賴代工。

## 技術變數

HBM 的競爭變數是堆疊層數、頻寬，以及散熱與良率之間的取捨。更多堆疊提高製程與熱管理難度，實際良率仍取決於製程成熟度、鍵合及封裝方案，不能只由層數決定。

**well-supported**：SK 海力士與台積電已公開 HBM4 邏輯 base die 的製程合作，不能再當成未出現的假設。個別客戶、世代與製造分工仍需查核。[SK hynix 與台積電合作公告](https://news.skhynix.com/sk-hynix-partners-with-tsmc-to-strengthen-hbm-technological-leadership/)。本圖透過 `memory → advanced-packaging ← compute ← foundry` 的既有關聯找到代工角色；這是遍歷路徑，並未宣告直接的 `foundry → memory` 邊。

傳統 DRAM 與 NAND 則是標準品循環，變數在供需與各廠的資本支出紀律。

## 玩家格局

HBM 的主要供應者包含韓廠 SK 海力士、三星電子及美股美光；各世代須配合加速器廠認證。認證、量產良率與客戶平台會改變分配，不能以整體 HBM 市佔或送樣先後直接推定 HBM4 的實際份額。

台廠不在本清單的 HBM 製造主戰場：南亞科供應 DRAM，華邦電偏向利基記憶體，群聯供應 NAND 控制晶片與模組。它們的相關機會是記憶體供需、控制器與儲存需求的間接傳導，不能因同屬本環節就視為 HBM4 供應商。

## 傳導鏈

**上游**：`equipment` 的設備交期決定 HBM 擴產速度。

**下游**：HBM 產出直接進入 `advanced-packaging` 與運算晶片共同封裝。供給不足會成為整條鏈的瓶頸 —— 即使 `foundry` 與 `advanced-packaging` 都有餘裕，缺 HBM 一樣出不了貨。

**inference：環節內部的排擠效應**：轉產 HBM 可能影響其他 DRAM 的可用產能，再影響價格與南亞科、華邦電的供需；是否發生須查產能配置、客戶庫存及價格。群聯的機會另取決於 NAND 與儲存需求，不能套用 DRAM 排擠即受惠。這些公司應進入影響範圍，影響方向仍須查核。

## 監測指標

HBM 位元出貨量與各廠供給分配、傳統 DRAM 合約價走勢、HBM 佔各廠營收比重。

認證進度須以**供應商法說會點名客戶**為準；供應商單方面宣稱「已送樣」不足以採信。

## 風險

供給高度集中於韓國，地緣風險與單一廠區事故難以分散。認證失敗或延後會讓份額一次性流失。若加速器廠轉向「較少層數、較多顆」的配置，單價結構會改變。傳統記憶體部分仍受標準品循環擺動，與 AI 需求不同調。
