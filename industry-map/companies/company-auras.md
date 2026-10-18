---
schema-version: research-v1
entity-id: company-auras
kind: company
name-zh: 雙鴻
aliases: [Auras, 雙鴻科技, AURAS Technology]
summary: 散熱模組廠轉向液冷系統方案；年報未拆分液冷營收，三家匿名 EMS／代工客戶各占約一成五。
legacy-keys:
- 3324.TW
listings:
- ticker: 3324.TW
  market: TW
  exchange: ROCO
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
    - source-id: auras-annual-report-2025
      url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
      locator: 114 年度年報第 64 頁（PDF 第 68 頁）主要產品類別及其營業比重，113 年度與 114 年度並列；第 10 頁表格基準日 114 年 12 月 31 日
      read-scope: 已讀年度營業收入表與年底基準日，未讀個體財報附註
      stance: supporting
      applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-thermal
  description: 液冷冷板、歧管與冷卻液分配單元
  tier: 1
  baseline-path: ai-server/thermal.md
claims:
  - id: cold-plate-portfolio
    statement: 雙鴻 2025 展會新聞明列冷板、歧管與 CDU，並介紹直接液冷的客製化設計。
    confidence: well-supported
    conditions: [此證據支持公司公開產品範圍，不指認客戶與訂單]
    reviewed: '2026-10-16'
    evidence:
      - source-id: auras-ocp-2025-reading
        url: https://www.auras.com.tw/News/NewsContent/14-10/en
        locator: OCP Global Summit 2025／液冷產品及直接液冷段落
        read-scope: 以瀏覽器讀取公開新聞內文，非僅 HTTP 200 的 JavaScript 外殼
        stance: supporting
        applicable-period: '2025-10-15 展會新聞；不是 2026 出貨資料'
  - id: development-is-not-shipment
    statement: 該新聞對液對液 CDU 使用研發措辭，不能據此判定已量產或帶來多少收入。
    confidence: inference
    conditions: [限於這篇 2025 新聞的證據範圍，不推定後續沒有商業進展]
    reviewed: '2026-10-16'
    evidence:
      - source-id: auras-ocp-2025-reading
        url: https://www.auras.com.tw/News/NewsContent/14-10/en
        locator: OCP Global Summit 2025／In-Row L2L CDU 段落
        read-scope: 已讀研發描述，未取得本輪後續出貨與收入查核
        stance: supporting
        applicable-period: '2025-10-15 新聞的產品規劃'
  - id: liquid-cooling-system-scope
    statement: 114 年度年報列出分歧管、水對水／水對氣及一對一／一對多冷水分配裝置、GPU／CPU／DIMM 水冷板，並提供機櫃型 In-rack CDU／RPU 與一對多 In-Row CDU／Sidecar。
    confidence: well-supported
    conditions: [年報描述的是可提供的產品方案，未揭露各產品的出貨量、客戶或收入]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 66 頁（PDF 第 70 頁）「在液冷系統解決方案中」；第 69 頁（PDF 第 73 頁）「在直接式液冷方面」
        read-scope: 已讀產業上中下游與液冷方案段落
        stance: supporting
        applicable-period: 114 年度年報（2026-04-30 上傳）
  - id: pump-and-connector-strategy
    statement: 年報稱水泵浦由公司設計自製生產，快接頭由公司設計開發後交由策略夥伴生產，並把兩者視為重要戰略物資。
    confidence: well-supported
    conditions: [自製範圍以年報敘述為準，未揭露自製比例或成本影響]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 66 頁（PDF 第 70 頁）「液冷應用部分，公司目前水泵浦設計自製生產」段
        read-scope: 已讀關鍵零組件自製策略段落
        stance: supporting
        applicable-period: 114 年度年報
  - id: revenue-not-split-by-cooling
    statement: 年報的主要產品類別只列「散熱模組」一類，114 年度營業收入 23,276,344 仟元、占 100%，沒有拆出液冷或伺服器營收。
    confidence: well-supported
    conditions: [液冷占比若見於法說會或新聞，屬不同口徑，不能當成年報數字]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 64 頁（PDF 第 68 頁）「主要產品類別及其營業比重」表
        read-scope: 已讀該表；113 年度為 15,778,909 仟元
        stance: supporting
        applicable-period: 113 至 114 年度
  - id: customers-ems-and-odm
    statement: 年報說明集團以母公司接單為主，客源以國際知名 EMS 及代工廠為主，公司評估沒有銷售集中風險。
    confidence: well-supported
    conditions: [這是公司自評；直接客戶是 EMS／代工廠，不等於終端雲端業者]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 85 頁（PDF 第 89 頁）風險管理分析第 9 點「進貨或銷貨集中所面臨之風險」
        read-scope: 已讀銷貨與進貨集中兩小段
        stance: supporting
        applicable-period: 114 年度年報
  - id: anonymous-major-customers
    statement: 114 年度占銷貨 10% 以上的客戶以代號揭露：Q 占 15.37%、U 占 14.80%、T 占 14.35%；U 占比上升主因是 Server 新機種水冷及氣冷銷售增加。
    confidence: well-supported
    conditions: [客戶以代號揭露，年報未提供名稱；不能把代號對應到特定公司]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 77 頁（PDF 第 81 頁）主要進銷貨客戶名單第 2 項
        read-scope: 已讀 113、114 年度主要客戶表與增減變動原因
        stance: supporting
        applicable-period: 113 至 114 年度
  - id: diversified-materials
    statement: 年報稱主要原料為熱導管、風扇、沖壓件、壓鑄件、銅管及鋁擠型散熱片，各有三家以上合格供應商，單一供應商進貨比重未逾 20%。
    confidence: well-supported
    conditions: [114 年度最大單一供應商占進貨 5.09%（代號 G），供應商名稱未揭露]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 85 頁（PDF 第 89 頁）第 9 點進貨方面；第 77 頁（PDF 第 81 頁）主要供應商表
        read-scope: 已讀原料、供應商集中與供應商表
        stance: supporting
        applicable-period: 114 年度
  - id: production-location
    statement: 年報的生產策略寫「拓展大陸及泰國生產據點」，原料段寫主要產地已移轉至大陸、泰國之轉投資公司；風險段則寫產線已全數移轉至大陸子公司。
    confidence: well-supported
    conditions: [同一年報內的兩種說法並列引用，不自行判定泰國產線的實際規模]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 72 頁（PDF 第 76 頁）生產策略；第 76 頁（PDF 第 80 頁）主要原料之供應狀況；第 85 頁（PDF 第 89 頁）進貨方面
        read-scope: 已讀三處產地敘述
        stance: supporting
        applicable-period: 114 年度年報
  - id: competition-unnamed
    statement: 年報稱伺服器市場主要競爭對手來自台、美業者，PC／VGA 競爭主要來自台、陸業者，但未列出公司名稱。
    confidence: well-supported
    conditions: [只有來源地區描述，不能據此列出具名競爭者]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 68 頁（PDF 第 72 頁）「B.產品競爭情形」
        read-scope: 已讀產品競爭情形段落
        stance: supporting
        applicable-period: 114 年度年報
  - id: usd-export-exposure
    statement: 年報稱公司及子公司銷售多以外銷並採美元報價為主，進貨採購也以美元為主。
    confidence: well-supported
    conditions: [匯率對損益的實際影響需看當期資產負債部位]
    reviewed: '2026-10-18'
    evidence:
      - source-id: auras-annual-report-2025
        url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3324&year=115&mtype=F&
        locator: 114 年度年報第 84 頁（PDF 第 88 頁）風險管理分析（一）匯率變動
        read-scope: 已讀匯率段落
        stance: supporting
        applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未拆分液冷、伺服器或個別產品營收，也未揭露客戶名稱；液冷占比不以法說會或新聞數字代替。
- status: not-researched
  reason: 營業現金流、資本支出與現金餘額可由年報合併財報人工核對補錄，本輪尚未匯入。
---

## 供應角色

雙鴻在[散熱環節](/next?focus=segment-thermal)提供晶片端[液冷冷板](/next?focus=product-cold-plate)、[機櫃歧管](/next?focus=product-rack-manifold)與[液對液 CDU](/next?focus=product-liquid-to-liquid-cdu)等液冷零部件，也保留筆電、桌機與顯示卡的氣冷模組。年報形容公司從氣冷模組零組件製造商轉為液冷系統解決方案商（第 67 頁）。

## 研究界線

本頁以 114 年度股東會年報與 2025 展會新聞為依據。年報描述的是可提供的產品方案；出貨量、具名客戶與各產品收入都沒有揭露，本頁不以媒體或法說會的液冷占比代替。

## 產品與用途

- **直接液冷**：依晶片設計的客製化串聯／並聯開放式水冷板，薄型水冷板用於記憶體，另有單／雙泵浦的封閉式液冷（第 69 頁）。
- **機櫃與分配**：一對一機櫃型 CDU／RPU、一對多 In-Row CDU／Sidecar，以及具流量調節、溫度監控與洩漏管理功能的分歧管（第 69 頁）。
- **浸沒式**：客製化單相／兩相浸沒式散熱模組（第 69 頁）。
- **氣冷**：以熱導管、風扇與鋁或銅鰭片組成的 NB／PC／VGA 散熱模組（第 66 頁）。

## 商業模式

集團以母公司接單為主，產品在大陸與泰國的轉投資公司生產，母公司購回製成品後出售（第 76、85 頁）。水泵浦自行設計生產，快接頭自行設計、委由策略夥伴生產，公司把兩者視為提高液冷可靠度的關鍵零組件（第 66 頁）。

## 客戶與供應商

直接客戶以國際知名 EMS 及代工廠為主（第 85 頁）。114 年度三家匿名客戶 Q、U、T 各占銷貨約 14%–15%，合計約四成五；U 的占比上升與 Server 新機種的水冷及氣冷銷售有關（第 77 頁）。年報沒有客戶名稱，本頁不把代號對應到特定公司。

供應端以熱導管、風扇、沖壓件、壓鑄件、銅管與鋁擠型散熱片為主，各有三家以上合格供應商；114 年度最大單一供應商只占進貨 5.09%（第 77、85 頁）。

## 競爭與替代

年報只說伺服器市場競爭者來自台、美業者，PC／VGA 來自台、陸業者（第 68 頁），沒有具名公司。研究上可比較的是同一[晶片端取熱](/next?focus=role-chip-heat-capture)與[冷卻液分配](/next?focus=role-coolant-distribution)角色中的其他供應者，但列在同一角色不代表互相爭取同一客戶專案。

## 業務曝險

年報的產品類別只有「散熱模組」一類，114 年度合併營業收入 23,276,344 仟元，較 113 年度 15,778,909 仟元成長（第 64 頁），但沒有拆出液冷或伺服器收入。液冷曝險只能從產品方案與客戶變動原因定性判斷，不能換算成金額。

## 風險

- **客戶結構**：三家匿名客戶合計約四成五，公司自評無銷售集中風險；但客戶多為 EMS／代工廠，終端平台變動會經由它們傳導。
- **匯率**：銷售多以外銷並採美元報價，進貨也以美元為主（第 84 頁）。
- **產地**：生產集中在大陸，年報同時提及泰國據點；兩處敘述不一致，泰國產能規模需另查（第 72、76、85 頁）。

## 財務可取性

- 官方月營收、損益與負債摘要可由櫃買中心公開資料自動取得；公司在櫃買掛牌（MIC `ROCO`），舊 listing 誤記為上市市場，本輪已更正。
- 年度合併營業收入可由年報核對。
- 營業現金流、資本支出與現金餘額不在自動摘要內，需由年報合併財報人工補錄，尚未匯入。
- 液冷產品營收：年報未公開。
