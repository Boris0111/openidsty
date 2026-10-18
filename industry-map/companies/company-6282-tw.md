---
schema-version: research-v1
entity-id: company-6282-tw
kind: company
name-zh: 康舒
aliases:
- AcBel
- 康舒科技
- ACBEL
summary: 電源供應器廠，電源及零組件占營收九成四；伺服器電源發展 54V 輸出與資料中心機櫃級電源，沒有客戶超過一成。
legacy-keys:
- 6282.TW
listings:
- ticker: 6282.TW
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
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）主要產品銷售地區表，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-power
  description: 電源供應器
  tier: 2
  baseline-path: ai-server/power.md
claims:
- id: revenue-mix
  statement: 年報 114 年度營業金額 31,726,761 千元，其中電源及零組件占 93.92%、五金零件及其他占 6.08%。
  confidence: well-supported
  conditions:
  - 電源類未再拆分伺服器、消費性與電動車電源
  reviewed: '2026-10-18'
  evidence:
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 71 頁（PDF 第 75 頁）主要產(商)品之營業比重
    read-scope: 已讀營業比重表
    stance: supporting
    applicable-period: 114 年度
- id: server-power-products
  statement: 年報列出 500W–5500W 伺服器電源，因應 AI／GPU 高功率趨勢發展 54V 輸出電源，並提供資料中心機櫃級電源系統、儲存與網通電源。
  confidence: well-supported
  conditions:
  - 產品說明不揭露客戶、出貨或收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 71–72 頁（PDF 第 75–76 頁）公司目前之商品項目（企業用雲端電源供應器）
    read-scope: 已讀企業用雲端與資料中心電源段落
    stance: supporting
    applicable-period: 114 年度年報
- id: no-concentration
  statement: 年報揭露最近二年度沒有任何客戶占銷貨 10% 以上，也沒有供應商占進貨 10% 以上；主要原料為半導體、變壓器、風扇、排線、外殼及電路板，每項至少兩家供應商。
  confidence: well-supported
  conditions:
  - 客戶與供應商名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 85 頁（PDF 第 89 頁）主要原料之供應狀況與主要進銷貨客戶名單
    read-scope: 已讀原料與進銷貨段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報 114 年度銷售地區為美洲 51.27%、亞洲 18.91%、內銷 12.92%、歐洲 4.01%、其他 12.89%，外銷合計 87.08%。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）主要產品銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: hyperscaler-demand-view
  statement: 年報引述北美主要雲端業者自 114 年起增加資料中心資本支出，帶動伺服器與資料中心設備需求，並指出資料中心電力朝高功率密度、高轉換效率與液冷散熱發展。
  confidence: inference
  conditions:
  - 屬產業描述，不代表康舒已取得特定雲端業者訂單
  reviewed: '2026-10-18'
  evidence:
  - source-id: acbel-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6282&year=115&mtype=F&
    locator: 114 年度年報第 74 頁（PDF 第 78 頁）企業雲端與資料中心市場
    read-scope: 已讀市場說明段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未拆分伺服器電源營收，也未揭露客戶名稱與具名競爭者。
---

## 供應角色

康舒在[電源環節](/next?focus=segment-power)提供伺服器[電源供應器與機櫃級電源](/next?focus=product-power-shelf-psu)，同時保有個人電腦、消費性、電信與電動車等電源產品。

## 研究界線

本頁以 114 年度股東會年報為依據。年報說明伺服器電源規格方向，但不拆出伺服器電源營收，也沒有客戶名稱；雲端業者資本支出是產業描述，不代表訂單。

## 產品與用途

- **企業用雲端電源**：500W–5500W 伺服器電源，因應 AI／GPU 發展 54V 輸出；資料中心機櫃級電源系統、儲存與網通電源（第 71–72 頁）。
- **消費性電源**：個人電腦、電競主機、AIO、機上盒、印表機電源與充電器（第 71 頁）。
- **電信與其他**：5G 基站與電信數據中心電源、新能源與電動車相關產品（第 71–72 頁）。

## 商業模式

以 AC/DC、DC/DC 電源供應器製造銷售為主，114 年度營業金額 31,726,761 千元，電源及零組件占 93.92%（第 71 頁）。外銷占 87.08%，美洲是最大市場（第 80 頁）。

## 客戶與供應商

沒有任何客戶或供應商占比達一成，公司自評無集中風險（第 85、97 頁）。主要原料為半導體、變壓器、風扇、排線、外殼與電路板，每項至少兩家供應商（第 85 頁）。

## 競爭與替代

年報沒有具名競爭者。在[機櫃與系統電源](/next?focus=role-rack-power-supply)角色，可與[台達電](/next?focus=company-delta-electronics)、[光寶科](/next?focus=company-2301-tw)比較；54V 與更高電壓架構的轉換，會改變伺服器電源的規格與供應位置。

## 業務曝險

電源類占營收九成四，但伺服器電源只是其中一部分，年報沒有拆出金額。美洲營收占比由 113 年度 42.58% 升到 114 年度 51.27%（第 80 頁），反映北美客戶比重上升，但無法對應到特定產品。

## 風險

- **產品組合**：消費性電源與伺服器電源的需求循環不同，年報沒有分開揭露。
- **架構轉換**：AI 伺服器電源走向 54V 與更高電壓，產品開發與認證時程需逐案核對。

## 財務可取性

- 月營收、損益與負債摘要可由公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 伺服器電源營收：年報未公開。
