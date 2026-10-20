---
schema-version: research-v1
entity-id: company-avc
kind: company
name-zh: 奇鋐
aliases:
- AVC
- 奇鋐科技
- Asia Vital Components
summary: 散熱、機殼機櫃與系統組裝供應商；年報稱 114 年為液冷元年，但營收只列 3C 電子產品一類。
legacy-keys:
- 3017.TW
listings:
- ticker: 3017.TW
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
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 92 頁）主要產品銷售地區表，113 年與 114 年並列；第 105 頁現金流量分析
    read-scope: 已讀年度銷售與現金流量分析表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-thermal
  description: 均熱板與氣冷散熱模組
  tier: 1
  baseline-path: ai-server/thermal.md
claims:
- id: product-scope
  statement: 年報將主要產品分為散熱產品、機殼與機櫃、系統組裝及轉軸；散熱產品包含風扇、散熱模組、熱管／均熱板、3D VC 與水冷板等水冷方案，應用涵蓋伺服器（含 AI 伺服器）、通訊基地台與電動車等。
  confidence: well-supported
  conditions:
  - 產品範圍不揭露各產品收入或客戶
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 87 頁（PDF 第 90 頁）4.1.1.3 主要產品及服務項目
    read-scope: 已讀主要產品及服務項目與計畫開發新產品段落
    stance: supporting
    applicable-period: 114 年度年報
- id: liquid-cooling-inflection
  statement: 年報稱 114 年被視為公司的「液冷元年」，並把雙相液冷、浸沒式冷卻列為持續開發的前瞻技術。
  confidence: well-supported
  conditions:
  - 這是公司對產業與自身的描述，未提供液冷營收或出貨量
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 87 頁（PDF 第 90 頁）4.1.2.1 產業現況與發展；第 91 頁（PDF 第 94 頁）因應對策
    read-scope: 已讀產業現況與發展趨勢段落
    stance: supporting
    applicable-period: 114 年度年報
- id: revenue-single-category
  statement: 年報主要商品占營業收入淨額比重只列「3C 電子產品」一類，114 年度 139,639,362 千元、占 100%，沒有拆出散熱、機櫃或液冷收入。
  confidence: well-supported
  conditions:
  - 液冷或伺服器收入若見於法說會或新聞，屬不同口徑
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 87 頁（PDF 第 90 頁）4.1.1.2 主要商品佔營業收入淨額比重
    read-scope: 已讀該表
    stance: supporting
    applicable-period: 114 年度
- id: design-partner-claim
  statement: 年報自述為領先 GPU 廠商的參考設計商，也是全球大型雲端服務供應商的主要設計夥伴，但未列出公司名稱。
  confidence: needs-verification
  conditions:
  - 公司自述，未具名，不能據此建立具名客戶或交易關係
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 88 頁（PDF 第 91 頁）4.1.2.3（2）競爭情形
    read-scope: 已讀競爭情形段落
    stance: supporting
    applicable-period: 114 年度年報
- id: anonymous-major-customers
  statement: 114 年度主要銷貨客戶以代號揭露：甲客戶 22.74%、丙客戶 19.73%、乙客戶 9.50%（113 年度分別為 28.61%、10.50%、16.17%）。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露，不能把代號對應到特定公司
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 92 頁（PDF 第 95 頁）4.2.4.1 主要銷貨客戶資料
    read-scope: 已讀 113、114 年度主要客戶表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: largest-supplier
  statement: 年報稱 114 年度最大進貨廠商為代號丁集團，約占總進貨 18.72%，主要原料包括銅、鋁、鋼、塑膠製品及 Sensor、IC、培林等組件。
  confidence: well-supported
  conditions:
  - 供應商名稱未揭露；銅鋁依 LME 價格公式化採購
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 108 頁（PDF 第 111 頁）5.6.9；第 91 頁（PDF 第 94 頁）4.2.3 主要原料之供應狀況
    read-scope: 已讀集中風險與原料供應段落
    stance: supporting
    applicable-period: 114 年度
- id: sales-regions
  statement: 114 年度銷售地區為亞洲 71.76%、美洲 19.05%、歐洲 9.16%；113 年度亞洲占 86.53%。
  confidence: well-supported
  conditions:
  - 地區依出貨或客戶所在地，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 92 頁）4.2.1.1 主要產品銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: production-sites
  statement: 年報提到東莞、越南、深圳及成都廠，並在董事會決議中通過越南子公司建廠與增資。
  confidence: well-supported
  conditions:
  - 年報未提供各廠產能或產品分工
  reviewed: '2026-10-18'
  evidence:
  - source-id: avc-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3017&year=115&mtype=F&
    locator: 114 年度年報第 40 頁（PDF 第 43 頁）能源管理；第 24、26 頁（PDF 第 27、29 頁）審計委員會與董事會決議
    read-scope: 已讀廠區與越南投資相關段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未拆分液冷、伺服器或機櫃營收，也未揭露客戶與供應商名稱；液冷占比不以法說會或新聞數字代替。
- status: not-public
  reason: 年報未列出具名競爭者。
---

## 供應角色

奇鋐在[散熱環節](/next?focus=segment-thermal)同時提供[均熱板與氣冷模組](/next?focus=product-vapor-chamber-air-module)與[液冷冷板](/next?focus=product-cold-plate)，並延伸到機殼與機櫃、系統組裝。舊有環節角色只記錄氣冷，本輪依年報把它加入[晶片端取熱](/next?focus=role-chip-heat-capture)角色。

## 研究界線

本頁以 114 年度股東會年報為依據。年報描述產品範圍與公司自述的設計夥伴地位，但不揭露客戶名稱、各產品收入或液冷占比；「參考設計商」與「主要設計夥伴」屬公司自述，標為待核實。

## 產品與用途

- **散熱產品**：風扇、散熱片、散熱器、散熱模組、熱交換器、熱管／均熱板、3D VC 與水冷板（第 87 頁）。
- **機殼與機櫃、系統組裝、轉軸**：讓公司能從零組件延伸到整櫃結構（第 87 頁）。
- **應用**：伺服器（含 AI 伺服器）、通訊基地台、筆電與桌機、電動車與儲能等（第 87–88 頁）。
- **開發方向**：雙相液冷、浸沒式冷卻與噴流冷卻（第 88、91 頁）。

## 商業模式

奇鋐把自己定位為同時具備散熱、系統整合與機殼／機櫃製造能力的「Total Thermal Solution」供應商（第 88–89 頁）。營收以單一類別「3C 電子產品」揭露，114 年度合併銷貨淨額 139,639,362 千元，約為 113 年度 71,761,296 千元的兩倍（第 87、89 頁）。

## 客戶與供應商

主要客戶以代號揭露：114 年度甲客戶 22.74%、丙客戶 19.73%、乙客戶 9.50%（第 92 頁）。年報自述為領先 GPU 廠商的參考設計商、大型雲端業者的主要設計夥伴，但沒有具名，本頁不建立具名客戶關係。

最大進貨廠商代號丁集團約占總進貨 18.72%；主要原料為銅、鋁、鋼、塑膠與 Sensor、IC、培林，銅鋁依 LME 價格公式化採購（第 91、108 頁）。

## 競爭與替代

年報沒有列出具名競爭者，只以系統級設計能力說明競爭定位（第 88 頁）。研究上可與同一[晶片端取熱](/next?focus=role-chip-heat-capture)角色的[雙鴻](/next?focus=company-auras)、[建準](/next?focus=company-2421-tw)與 Boyd 比較，但同角色不代表爭取同一客戶專案。

## 業務曝險

114 年度銷售地區以亞洲為主（71.76%），美洲升至 19.05%（第 89 頁）。收入只有單一類別，液冷與機櫃的金額無法由年報拆出；液冷曝險只能由產品範圍與公司敘述定性判斷。

## 風險

- **客戶集中**：前三大代號客戶合計約五成二，最大客戶甲集團約 22.74%（第 92、108 頁）。
- **原料價格**：銅、鋁、鋼價格波動，銅鋁採 LME 公式化定價（第 91 頁）。
- **產地**：生產集中在中國大陸（東莞、深圳、成都），並擴充越南（第 24、26、40 頁）。
- **匯率**：114 年度匯兌利益 723,395 千元，占稅後純益 3.45%（第 106 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 年報含現金流量分析：114 年底現金及約當現金 58,529,798 千元（第 105 頁），營業現金流與資本支出需由合併財報人工補錄。
- 液冷、機櫃與伺服器收入：年報未公開。
