---
schema-version: research-v1
entity-id: company-3081-two
kind: company
name-zh: 聯亞
aliases:
- LandMark Optoelectronics
- 聯亞光電
summary: III-V 族磊晶片純代工廠，磊晶片及加工品占營收 99%；114 年度營收成長 82%，四家匿名客戶各占一成以上，前三大客戶產品主要用於資料中心與光通訊。
legacy-keys:
- 3081.TWO
listings:
- ticker: 3081.TWO
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
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 75 頁（PDF 第 79 頁）主要商品銷售地區，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-networking
  description: 光通訊磷化銦晶片
  tier: 2
  baseline-path: ai-server/networking.md
claims:
- id: epiwafer-business
  statement: 年報揭露 114 年度營業額 2,202,822 仟元（113 年度 1,208,422 仟元），其中磊晶片及加工品製造銷售占 99.21%；公司以 MOCVD 生產 III-V 族磊晶片，主要產品為 InP 雷射磊晶片（1200–1650nm）、檢光二極體磊晶片與 GaAs 雷射磊晶片。
  confidence: well-supported
  conditions:
  - 營業項目包含晶粒，但營收揭露為磊晶片及加工品，未拆出晶粒
  reviewed: '2026-10-18'
  evidence:
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 69 頁（PDF 第 73 頁）營業比重與商品項目
    read-scope: 已讀業務內容段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: pure-play-model
  statement: 年報稱採純代工商業模式，以彈性 MOCVD 產能配合客戶前期開發與磊晶製程優化；技術涵蓋高速 DFB 雷射、矽光子用連續波雷射（CW Laser）與 PIN／APD 檢光二極體磊晶，並規劃 100G 以上 EML、50G 以上直調 DFB 與 6 吋 VCSEL 磊晶片。
  confidence: well-supported
  conditions:
  - 新產品屬開發計畫，量產程度未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 69 頁（PDF 第 73 頁）計畫開發之新商品；第 76 頁（PDF 第 80 頁）競爭利基
    read-scope: 已讀新商品與競爭利基段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報主要銷貨客戶以代號揭露，114 年度 C06 占 25.76%、C09 占 21.01%（113 年度 0.35%）、C03 占 13.33%、C10 占 10.40%（113 年度 0.02%）；前三大客戶約占 60.10%，產品主要用於資料中心與光通訊磊晶片。
  confidence: well-supported
  conditions:
  - 客戶名稱因保密約定未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 80–81 頁（PDF 第 84–85 頁）主要銷貨客戶；第 93 頁（PDF 第 97 頁）銷貨集中風險
    read-scope: 已讀主要銷貨客戶表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報揭露 114 年度銷售地區為中國 71.40%、美國 21.46%、其他 4.20%、台灣 2.94%（113 年度美國 9.43%）。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，磊晶片多售予晶片廠，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 75 頁（PDF 第 79 頁）主要商品之銷售地區
    read-scope: 已讀銷售地區表並逐欄核對
    stance: supporting
    applicable-period: 113 至 114 年度
- id: supplier-concentration
  statement: 年報揭露 114 年度最大原料供應商 A01 占進貨 40.62%，主要原料為基板、MO 源與設備耗材；供應商因保密約定以代號揭露。
  confidence: well-supported
  conditions:
  - 供應商名稱除凱信 AKZO 外未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: landmark-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3081&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）主要原料與主要供應商；第 93 頁（PDF 第 97 頁）進貨集中風險
    read-scope: 已讀原料與供應商表
    stance: supporting
    applicable-period: 113 至 114 年度
gaps:
- status: not-public
  reason: 年報未揭露客戶名稱、各應用營收與具名競爭者。
---

## 供應角色

聯亞在[網路環節](/next?focus=segment-networking)屬[光通訊磊晶片](/next?focus=role-optical-epiwafer)，為雷射與檢光晶片廠供應 [III-V 族磊晶片](/next?focus=product-optical-epiwafer)。

## 研究界線

**邊界裁決**：聯亞原列於[光通訊雷射與光電晶片](/next?focus=role-optical-chip)。年報顯示 99.21% 營收來自磊晶片及加工品，並自述為純代工；它的客戶是雷射晶片廠，和自有磊晶的晶片廠（如[博通](/next?focus=company-avgo)）不能互相替換，因此改列新的光通訊磊晶片角色。依據為 114 年度年報第 69、76 頁。

## 產品與用途

- **InP 雷射磊晶片**：1200–1650nm，用於光通訊與資料傳輸雷射（第 69 頁）。
- **檢光二極體磊晶片**：650–1600nm，用於光通訊 PD、APD 與監控（第 69 頁）。
- **GaAs 雷射磊晶片**：635–1100nm，用於 VCSEL、3D 感測、LiDAR 與資料中心通訊（第 69 頁）。
- **開發中**：100G 以上 EML、50G 以上直調 DFB、6 吋 VCSEL 磊晶片；矽光子用 CW 雷射磊晶（第 69、76 頁）。

## 商業模式

純代工，以 MOCVD 產能配合客戶開發（第 76 頁）。114 年度營業額 2,202,822 仟元，較 113 年度成長約 82%（第 69 頁）。

## 客戶與供應商

四家匿名客戶各占一成以上，C09 由 0.35% 升到 21.01%、C10 由 0.02% 升到 10.40%，顯示新客戶快速放量（第 80–81 頁）。最大原料供應商占 40.62%（第 80、93 頁）。

## 競爭與替代

年報沒有具名競爭者。磊晶來源更換需晶片廠重新認證；自有磊晶的雷射晶片廠可能不需要外購磊晶片。

## 業務曝險

前三大客戶約六成，產品主要用於資料中心與光通訊；中國客戶占 71.40%，美國由 9.43% 升到 21.46%。AI 光模組需求透過晶片廠間接傳到磊晶片。

## 風險

- **客戶集中**：前三大客戶約 60%，新客戶比重變動大。
- **供應商集中**：最大原料供應商占四成。
- **地緣政治**：中國銷售占七成，受美中科技競爭與貿易政策影響（年報第四章）。

## 財務可取性

- 月營收、損益與負債摘要可由櫃買中心公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 各應用營收與客戶名稱：年報未公開。
