---
schema-version: research-v1
entity-id: company-2301-tw
kind: company
name-zh: 光寶科
aliases:
- Lite-On
- 光寶
- 光寶科技
- LITEON
summary: 電源、光電與資訊產品供應商；雲端及物聯網部門占營收 45%，含伺服器電源與儲能，一家匿名客戶約占一成一。
legacy-keys:
- 2301.TW
listings:
- ticker: 2301.TW
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
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 120 頁（PDF 第 125 頁）主要銷貨客戶資料，114 年與 113 年銷貨淨額並列
    read-scope: 已讀銷貨客戶表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-power
  description: 伺服器電源
  tier: 1
  baseline-path: ai-server/power.md
claims:
- id: segment-mix
  statement: 年報 114 年度營業比重為光電部門 17%、雲端及物聯網部門 45%、資訊及消費性電子部門 38%；雲端及物聯網部門產品包括伺服器電源及儲能系統解決方案、網通設備零組件與智慧影像裝置。
  confidence: well-supported
  conditions:
  - 比重表在全文抽取時欄位錯位，依部門順序對應；部門比重不拆出伺服器電源收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 105 頁（PDF 第 110 頁）業務內容及營業比重
    read-scope: 已讀業務內容與營業比重表
    stance: supporting
    applicable-period: 114 年度
- id: ai-infrastructure-showcase
  statement: 年報致股東報告書稱光寶在 114 年 Supercomputing 展示符合 ORV3 標準與 NVIDIA 架構的方案，整合電源、機櫃與液冷系統，以及 800 VDC Power Rack，並擴大在台灣、美國與越南的投入。
  confidence: inference
  conditions:
  - 展示與投入計畫不等於量產出貨或客戶訂單
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報致股東報告書（PDF 第 9、12 頁）
    read-scope: 已讀致股東報告書
    stance: supporting
    applicable-period: 114 年度年報
- id: major-customer
  statement: 年報揭露 114 年度唯一占銷貨 10% 以上的客戶以代號「甲」表示，金額 18,783,299 仟元、占 11.31%（113 年度占 12.02%）；114 年度銷貨淨額 166,084,859 仟元。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 120 頁（PDF 第 125 頁）主要銷貨客戶資料
    read-scope: 已讀主要銷貨客戶表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: no-major-supplier
  statement: 年報稱最近二年度沒有占進貨總額 10% 以上的供應商。
  confidence: well-supported
  conditions:
  - 供應商名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 119 頁（PDF 第 124 頁）主要供應商資料
    read-scope: 已讀該段
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報 114 年度銷售地區依表列順序為亞洲約 52.18%、美洲約 36.50%、歐洲約 10.62%，內銷不到 1%。
  confidence: well-supported
  conditions:
  - 地區表抽取時欄位錯位，依金額與合計重新核對比率
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 117 頁（PDF 第 122 頁）主要商品之銷貨地區
    read-scope: 已讀銷貨地區表並以合計 166,084,859 仟元核對
    stance: supporting
    applicable-period: 114 年度
- id: psu-market-position
  statement: 年報自述電源供應器廣泛用於資通訊產品、雲端資料中心與伺服器，為全球前兩大電源供應器廠商。
  confidence: needs-verification
  conditions:
  - 公司自述，未說明排名口徑與資料來源
  reviewed: '2026-10-18'
  evidence:
  - source-id: liteon-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2301&year=115&mtype=F&
    locator: 114 年度年報第 117 頁（PDF 第 122 頁）市場占有率
    read-scope: 已讀市場占有率段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未拆分伺服器電源、儲能或 800VDC 產品營收，也未揭露客戶名稱。
- status: not-public
  reason: 年報未列出具名競爭者。
---

## 供應角色

光寶科在[電源環節](/next?focus=segment-power)提供伺服器[電源供應器與電源架](/next?focus=product-power-shelf-psu)，雲端及物聯網部門同時包含儲能與網通零組件。它也有光電與消費性電源業務，研究 AI 供電時要先分開部門。

## 研究界線

本頁以 114 年度股東會年報為依據。部門比重與銷售地區表在全文抽取時欄位錯位，已用表列順序與合計重新核對。展會展示與「全球前兩大」屬公司自述，分別標為推論與待核實。

## 產品與用途

- **雲端及物聯網（45%）**：伺服器電源及儲能系統、網通設備零組件、智慧影像與物聯網裝置（第 105 頁）。
- **資訊及消費性電子（38%）**：電源供應器、智慧輸入裝置（第 105 頁）。
- **光電（17%）**：LED 光電半導體封裝、車用電子與相機模組、電動車充電模組（第 105 頁）。
- **AI 基礎設施方向**：ORV3 與 NVIDIA 架構方案、800 VDC Power Rack、液冷系統整合展示（致股東報告書）。

## 商業模式

114 年度銷貨淨額 166,084,859 仟元，較 113 年度 137,133,894 仟元成長（第 120 頁）。以外銷為主，亞洲約五成二、美洲約三成六（第 117 頁）。

## 客戶與供應商

一家代號「甲」的客戶占 114 年度銷貨 11.31%，其餘客戶都低於一成（第 120 頁）；沒有供應商占進貨一成以上（第 119 頁）。年報未揭露客戶名稱。

## 競爭與替代

年報沒有具名競爭者。在[機櫃與系統電源](/next?focus=role-rack-power-supply)角色，可與[台達電](/next?focus=company-delta-electronics)、[康舒](/next?focus=company-6282-tw)比較；800VDC 架構會改變電源轉換位置，需逐案看產品是否進入量產。

## 業務曝險

伺服器電源與儲能落在雲端及物聯網部門（45%），但年報沒有拆出伺服器電源的金額。AI 相關曝險只能由部門比重與產品方向定性判斷。

## 風險

- **客戶集中**：一家匿名客戶約占一成一，公司自評無集中風險（第 141 頁）。
- **架構轉換**：800VDC 等新架構導入時程與規格仍需逐案核對。
- **產能布局**：年報提到擴大台灣、美國與越南投入，實際產能與時程未在本輪核對。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 部門比重可由年報核對；營業現金流、資本支出需由合併財報人工補錄。
- 伺服器電源與 800VDC 產品營收：年報未公開。
