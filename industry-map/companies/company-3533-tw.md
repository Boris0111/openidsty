---
schema-version: research-v1
entity-id: company-3533-tw
kind: company
name-zh: 嘉澤
aliases:
- Lotes
- 嘉澤端子
summary: 連接器與插槽廠，連接器占營收 97%；年報自述為全球前三大 CPU 插槽供應商，前幾大匿名客戶各不到一成。
legacy-keys:
- 3533.TW
listings:
- ticker: 3533.TW
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
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 74 頁（PDF 第 78 頁）主要商品銷售地區，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-interconnect
  description: 處理器插槽與高速連接器
  tier: 1
  baseline-path: ai-server/interconnect.md
claims:
- id: revenue-and-products
  statement: 年報 114 年度營業淨額 33,783,411 仟元，其中連接器（含連接線）占 97.40%、其他電子零組件占 2.60%；產品應用於伺服器、個人電腦、汽車、工業控制與醫療。
  confidence: well-supported
  conditions:
  - 營業比重不拆分伺服器或 CPU 插槽收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 69 頁（PDF 第 73 頁）主要產品及其營業比重、公司目前產品及服務項目
    read-scope: 已讀業務範圍段落
    stance: supporting
    applicable-period: 114 年度
- id: rd-direction
  statement: 年報稱近年研發重點包括高速傳輸連接器與連接線、QD 相關產品，以及 AI 伺服器應用的新型互連方案，並與國際客戶共同開發、認證及量產導入。
  confidence: inference
  conditions:
  - QD 相關產品屬研發方向，不等於已量產供應液路快接頭
  reviewed: '2026-10-18'
  evidence:
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 69 頁（PDF 第 73 頁）計畫開發之新產品及服務
    read-scope: 已讀新產品段落
    stance: supporting
    applicable-period: 114 年度年報
- id: market-position
  statement: 年報引用 Bishop 統計，自述在電腦暨週邊連接器廠商中全球排名第四、不分行業排名第十八，並為全球前三大 CPU 插槽供應商之一。
  confidence: needs-verification
  conditions:
  - 第三方統計經公司轉述，未核對原始排名資料
  reviewed: '2026-10-18'
  evidence:
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 74 頁（PDF 第 78 頁）市場佔有率
    read-scope: 已讀市場佔有率段落
    stance: supporting
    applicable-period: 114 年度年報
- id: anonymous-customers
  statement: 年報主要客戶表以代號揭露，114 年度最大客戶約占 8.31%，前幾大客戶各不到一成；公司並稱沒有進貨或銷貨集中風險。
  confidence: well-supported
  conditions:
  - 客戶表依金額與 114 年度合計 33,783,411 仟元逐項核對；客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 76 頁（PDF 第 80 頁）主要客戶；第 83 頁（PDF 第 87 頁）集中風險
    read-scope: 已讀主要客戶表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度
- id: export-and-materials
  statement: 年報 114 年度外銷占 89.45%、內銷 10.55%；主要原料為銅材、塑膠粒與鋼材，供應商合作多年。
  confidence: well-supported
  conditions:
  - 地區只分內外銷
  reviewed: '2026-10-18'
  evidence:
  - source-id: lotes-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3533&year=115&mtype=F&
    locator: 114 年度年報第 74 頁（PDF 第 78 頁）銷售地區；第 76 頁（PDF 第 80 頁）主要原料之供應狀況
    read-scope: 已讀銷售地區與原料段落
    stance: supporting
    applicable-period: 113 至 114 年度
gaps:
- status: not-public
  reason: 年報未拆分伺服器、CPU 插槽或高速連接器收入，也未揭露客戶名稱與具名競爭者。
---

## 供應角色

嘉澤在[互連環節](/next?focus=segment-interconnect)屬[高速與處理器連接器](/next?focus=role-high-speed-connector)，提供處理器插槽、高速連接器與連接線。年報提到 QD 相關研發，但本頁不把它列為液路快接頭供應者。

## 研究界線

本頁以 114 年度股東會年報為依據。市占排名是公司轉述的 Bishop 統計，標為待核實；QD 只是研發方向。客戶表已用金額與合計重新核對。

## 產品與用途

各式連接器、連接線、插槽及相關零組件，應用於伺服器、個人電腦、汽車、工業控制與醫療（第 69 頁）。研發朝小間距、高密度與高速傳輸，回應伺服器與 AI 對高頻高速互連的需求（第 69–70 頁）。

## 商業模式

設計、製造與銷售連接器，114 年度營業淨額 33,783,411 仟元，連接器占 97.40%（第 69 頁）。以外銷為主（89.45%），並與國際客戶共同開發與認證（第 69、74 頁）。

## 客戶與供應商

前幾大客戶以代號揭露，114 年度最大客戶約 8.31%，都不到一成（第 76 頁）。主要原料為銅、塑膠粒與鋼材（第 76 頁）。

## 競爭與替代

年報引述 TE Connectivity 與 Molex 的 224G 方案說明產業方向（第 70 頁），但沒有把它們列為具名競爭者。在[高速與處理器連接器](/next?focus=role-high-speed-connector)角色，可與 [Amphenol](/next?focus=company-aph) 比較；插槽能力不能推定供應液路快接頭。

## 業務曝險

伺服器是主要應用之一，但年報沒有拆出伺服器或 CPU 插槽收入；AI 相關曝險只能由產品方向定性判斷。

## 風險

- **平台世代**：伺服器平台與處理器插槽規格升級，需在新平台持續取得認證。
- **原料價格**：銅、塑膠粒與鋼材價格波動（第 76 頁）。
- **匯率**：外銷占近九成。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 伺服器與 CPU 插槽收入：年報未公開。
