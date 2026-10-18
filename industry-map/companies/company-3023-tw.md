---
schema-version: research-v1
entity-id: company-3023-tw
kind: company
name-zh: 信邦
aliases:
- SINBON
- 信邦電子
summary: 客製化連接線組與連接器廠，主力在醫療、汽車、綠能、工業與通訊；年報未把 AI 伺服器列為自身主要應用，資料中心曝險未揭露。
legacy-keys:
- 3023.TW
listings:
- ticker: 3023.TW
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
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 113 頁銷售地區表，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-interconnect
  description: 線材與連接組件
  tier: 2
  baseline-path: ai-server/interconnect.md
claims:
- id: custom-cable-business
  statement: 年報稱公司提供各式客製化強固、防水及惡劣環境用的連接線材與連接器，並延伸至機構設計、PCBA 與 Smart Cable 等整合工程服務；產品應用於綠能、電動車充電、高精密設備、半導體設備機櫃與醫療檢測設備，並經營電子零組件代理。
  confidence: well-supported
  conditions:
  - 年報未把 AI 伺服器或資料中心列為公司主要應用
  reviewed: '2026-10-18'
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 111 頁近期經營方針；第 112 頁深耕 iMAGIC 產業
    read-scope: 已讀業務發展計畫段落
    stance: supporting
    applicable-period: 114 年度年報
- id: revenue-and-regions
  statement: 年報 114 年度銷貨淨額 31,023,871 仟元（113 年度 33,087,505 仟元）；銷售地區為中國大陸 53.01%、美國 19.39%、內銷 10.93%、歐洲 8.26%、其他 8.41%。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，不等於終端使用地；年報無產品營業比重
  reviewed: '2026-10-18'
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 113 頁市場分析（銷售地區）
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: customer-supplier-concentration
  statement: 年報主要進銷貨表顯示，113 年度客戶 A 占銷貨 13.95%，114 年度已無客戶達一成；114 年度供應商 A 占進貨 21.54%（113 年度 27.89%）。
  confidence: well-supported
  conditions:
  - 客戶與供應商以代號揭露，名稱未公開
  reviewed: '2026-10-18'
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 114 頁最近二年度主要進銷貨客戶
    read-scope: 已讀主要進銷貨表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: named-materials-suppliers
  statement: 年報列出主要原料供應商：連接器來自 Hirose 與光福廣鑫，線材來自 STANDARD Mexico 與斯達半導體，供應情形均列為良好穩定。
  confidence: well-supported
  conditions:
  - 只列原料來源，不代表供應比重
  reviewed: '2026-10-18'
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 114 頁主要原料之供應狀況
    read-scope: 已讀原料供應表
    stance: supporting
    applicable-period: 114 年度年報
- id: named-peers
  statement: 年報引用券商報告，列出業務相似的上市櫃公司為正崴（2392）、佳必琪（6197）、貿聯-KY（3665）與廣宇（2328），並說明同業多轉向 AI 資料中心、半導體設備與電動車高壓傳輸。
  confidence: inference
  conditions:
  - 同業表的資料來源是券商報告，不是公司自行比較；同業轉向 AI 不代表信邦自身產品已用於 AI 伺服器
  reviewed: '2026-10-18'
  evidence:
  - source-id: sinbon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3023&year=115&mtype=F&
    locator: 114 年度年報第 108 頁主要產品之主要競爭情形
    read-scope: 已讀競爭情形段落
    stance: supporting
    applicable-period: 114 年度年報（引用 2026 年第 1 季券商報告）
gaps:
- status: not-public
  reason: 年報沒有主要產品營業比重，也未揭露資料中心或 AI 伺服器相關收入與客戶。
- status: not-researched
  reason: 尚未取得能證明信邦線組用於 AI 伺服器機櫃的公司產品頁或客戶文件；在高速線材角色中的列名仍是既有環節分類。
---

## 供應角色

信邦在[互連環節](/next?focus=segment-interconnect)列於[高速線材與線束](/next?focus=role-cable-harness)，提供客製化[連接線組](/next?focus=product-cable-assembly)與連接器。年報的主要應用是醫療、汽車、綠能、工業與通訊，AI 伺服器不在自述的主要應用中，所以這個列名只代表產品類型相同。

## 研究界線

本頁以 114 年度股東會年報為依據。年報沒有產品營業比重表，也沒有資料中心收入；同業名單引自券商報告。要確認信邦是否供應 AI 伺服器線組，需要另外取得產品或客戶文件。

## 產品與用途

- **客製化連接線組與連接器**：強固、防水、惡劣環境用途（第 111 頁）。
- **整合工程服務**：機構設計、PCBA 與 Smart Cable（第 111 頁）。
- **應用產業**：醫療、汽車、綠能、工業與通訊，並開發半導體設備機櫃、電動車充電與機器人相關產品（第 112 頁）。
- **零組件代理**：電子零組件代理與技術支援（第 111 頁）。

## 商業模式

以客製化設計與早期參與客戶開發為主，搭配零組件代理。114 年度銷貨淨額 31,023,871 仟元，較 113 年度減少；中國大陸是最大銷售地區（53.01%）（第 113 頁）。

## 客戶與供應商

113 年度一家客戶占 13.95%，114 年度沒有客戶達一成；114 年度一家供應商占進貨 21.54%（第 114 頁）。主要原料來源包括 Hirose、光福廣鑫、STANDARD Mexico 與斯達半導體（第 114 頁）。

## 競爭與替代

年報引用券商報告，列出正崴、佳必琪、[貿聯](/next?focus=company-3665-tw)與廣宇為業務相似公司（第 108 頁）。佳必琪與貿聯在表中被描述為有 AI 伺服器產品，信邦本身沒有；同角色比較時要先確認應用場景相同。

## 業務曝險

AI 資料中心不是年報揭露的主要應用。信邦的曝險集中在醫療、汽車、綠能與工業設備，與 AI 伺服器需求的連動性目前沒有公開證據。

## 風險

- **供應商集中**：最大供應商占進貨兩成以上。
- **地區集中**：中國大陸銷售過半。
- **終端市場**：電動車與綠能需求放緩會直接影響營收（第 104–105 頁產業描述）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 產品別與資料中心相關收入：年報未公開。
