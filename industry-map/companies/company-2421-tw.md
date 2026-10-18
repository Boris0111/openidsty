---
schema-version: research-v1
entity-id: company-2421-tw
kind: company
name-zh: 建準
aliases:
- Sunon
- 建準電機
- SUNON
summary: 散熱風扇為主的供應商，已延伸到液冷模組；沒有單一客戶超過一成，年報自述伺服器散熱約兩成市占。
legacy-keys:
- 2421.TW
listings:
- ticker: 2421.TW
  market: TW
  exchange: XTAI
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
  calendar-valid-from: '2025-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 79 頁（PDF 第 83 頁）業務主要內容營業比重（114 年度）
    read-scope: 已讀 114 年度營業比重表
    stance: supporting
    applicable-period: 114 年度（2025 曆年）
roles:
- segment-id: segment-thermal
  description: 散熱風扇
  tier: 2
  baseline-path: ai-server/thermal.md
claims:
- id: revenue-mix
  statement: 年報 114 年度營業比重為 DC 散熱風扇、散熱模組、鼓風扇 77.22%，AC 散熱風扇 2.36%，原物料及零組件 20.42%。
  confidence: well-supported
  conditions:
  - 液冷模組未單獨列示，不能由此推算液冷收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 79 頁（PDF 第 83 頁）業務主要內容營業比重
    read-scope: 已讀營業比重表
    stance: supporting
    applicable-period: 114 年度
- id: liquid-module-products
  statement: 年報產品項目列出液冷模組，包括水冷板／水冷散熱器、水泵／水路分配器／水管快接頭與集成式水冷熱交換機，並把高效率高可靠度水冷系統列為計畫開發的新產品。
  confidence: well-supported
  conditions:
  - 產品清單不揭露出貨、客戶或液冷收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 79–80 頁（PDF 第 83–84 頁）公司目前產品項目、計劃開發之新產品
    read-scope: 已讀產品項目與新產品清單
    stance: supporting
    applicable-period: 114 年度年報
- id: server-share-and-named-customers
  statement: 年報自述在伺服器散熱應用約占全球 20% 市占、排名前三，並稱公司是 DELL、HPE、亞馬遜 AWS、Meta 與微軟的主要供應商。
  confidence: needs-verification
  conditions:
  - 公司自述，未說明市占計算方法，也未揭露對各客戶的金額或產品
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 84 頁（PDF 第 88 頁）市場佔有率
    read-scope: 已讀市場佔有率段落
    stance: supporting
    applicable-period: 114 年度年報
- id: no-major-customer
  statement: 年報揭露最近二年度沒有任何客戶占銷貨總額 10% 以上，並稱進貨廠商及銷貨客戶分散。
  confidence: well-supported
  conditions:
  - 與自述的大型客戶名單並存；兩者都不揭露個別金額
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 93 頁）主要客戶；第 105 頁（PDF 第 109 頁）進貨或銷貨集中風險
    read-scope: 已讀主要客戶與集中風險段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: materials
  statement: 年報列出主要原料為塑膠原料、IC、被動元件、軸承、漆包線、沖壓與車床類零件，並說明部分 IC 曾缺料或供應週期拉長。
  confidence: well-supported
  conditions:
  - 供應商名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 93 頁）主要原料之供應狀況
    read-scope: 已讀原料供應表
    stance: supporting
    applicable-period: 114 年度
- id: production-sites
  statement: 年報的轉投資資料列出佛山與北海的生產基地，永續治理段落另提到菲律賓生產據點。
  confidence: well-supported
  conditions:
  - 未揭露各據點產能或產品分工
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 101 頁（PDF 第 105 頁）轉投資事業；第 39 頁（PDF 第 43 頁）
    read-scope: 已讀轉投資與據點敘述
    stance: supporting
    applicable-period: 114 年度年報
- id: competitive-claims
  statement: 年報列出的競爭利基包括自有品牌 SUNON、專利數量、與系統廠協同設計，以及液冷技術應用趨於成熟，但沒有列出具名競爭者。
  confidence: well-supported
  conditions:
  - 屬公司自評
  reviewed: '2026-10-18'
  evidence:
  - source-id: sunon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2421&year=115&mtype=F&
    locator: 114 年度年報第 85 頁（PDF 第 89 頁）競爭利基
    read-scope: 已讀競爭利基清單
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未拆分液冷模組營收，也未揭露各客戶金額；自述客戶名單無法量化。
- status: not-public
  reason: 年報未列出具名競爭者。
- status: not-obtained
  reason: 銷售地區表在全文抽取時欄位錯位，本輪未引用地區比重，需以原 PDF 版面另行核對。
---

## 供應角色

建準在[散熱環節](/next?focus=segment-thermal)以[伺服器散熱風扇](/next?focus=product-server-fan)為主，並延伸到液冷模組。舊有環節角色只記錄風扇，本輪依年報產品項目把它加入[晶片端取熱](/next?focus=role-chip-heat-capture)角色。

## 研究界線

本頁以 114 年度股東會年報為依據。市占與大型客戶名單是公司自述，標為待核實；年報沒有任何客戶占銷貨一成以上，也沒有拆出液冷營收。銷售地區表在全文抽取時欄位錯位，本輪不引用其數字。

## 產品與用途

- **風扇**：DC／AC 散熱風扇與鼓風扇、EC 風扇、離心扇、微型與高防護等級風扇（第 79 頁）。
- **散熱模組**：熱管、均溫板（第 79 頁）。
- **液冷模組**：水冷板／水冷散熱器、水泵／水路分配器／水管快接頭、集成式水冷熱交換機（第 79 頁）。
- **其他**：馬達、Fan Tray、綠建築換氣扇與工業大吊扇（第 79 頁）。
- **開發中**：高效率高可靠度水冷系統、超薄型主動液冷模組（第 80 頁）。

## 商業模式

以自有品牌 SUNON 銷售，114 年度營業比重中 DC 散熱風扇、散熱模組、鼓風扇占 77.22%，原物料及零組件占 20.42%（第 79 頁）。年報強調與系統廠協同設計、垂直整合與綿密經銷通路（第 85 頁）。

## 客戶與供應商

最近二年度沒有任何客戶占銷貨 10% 以上（第 89 頁）。年報自述是 DELL、HPE、AWS、Meta 與微軟的主要供應商（第 84 頁），但沒有金額或產品對應，本頁不建立具名供貨關係。

主要原料為塑膠、IC、被動元件、軸承、漆包線與金屬加工零件，部分 IC 曾缺料（第 89 頁）。

## 競爭與替代

年報只列出自身競爭利基，沒有具名競爭者（第 85 頁）。在[伺服器風扇](/next?focus=role-server-fan)角色，液冷普及會改變殘餘氣冷負載；在[晶片端取熱](/next?focus=role-chip-heat-capture)角色，可與[雙鴻](/next?focus=company-auras)、[奇鋐](/next?focus=company-avc)比較，但同角色不代表同一專案競爭。

## 業務曝險

營收以風扇與散熱模組為主。液冷模組已在產品清單與開發計畫中，但年報沒有拆出收入，液冷曝險只能定性判斷。

## 風險

- **技術替代**：液冷滲透率提升可能減少部分伺服器的風扇用量，也可能帶來液冷模組機會，方向需看產品組合。
- **原料**：IC 缺料與鋼、銅、鋁價格波動會影響成本（第 89 頁）。
- **產地**：生產基地在中國大陸（佛山、北海）與菲律賓（第 39、101 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出與現金餘額需由年報合併財報人工補錄。
- 液冷模組營收：年報未公開。
