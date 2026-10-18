---
schema-version: research-v1
entity-id: company-4979-two
kind: company
name-zh: 華星光
aliases:
- Luxnet
- 華星光通
summary: 光通訊元件與模組代工廠，主動元件及模組占營收 86%、晶粒 11%；單一客戶占 86.61%，北美占 86.96%，最大供應商（TOSA）占進貨 73.63%。
legacy-keys:
- 4979.TWO
listings:
- ticker: 4979.TWO
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
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 90 頁）主要商品銷售地區，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-networking
  description: 光收發模組
  tier: 2
  baseline-path: ai-server/networking.md
claims:
- id: product-mix
  statement: 年報揭露 114 年度營業收入 4,384,846 仟元（113 年度 3,451,043 仟元），其中光通訊主動元件及模組 86.35%、晶粒 11.05%、其他 2.60%；商品包括 FP／DFB 雷射與 CW 高功率雷射晶粒、PD／APD 檢光晶粒、TO 與 OSA／BOSA 次模組、資料中心用高速平行光學引擎、相干光收發模組及代工服務。
  confidence: well-supported
  conditions:
  - 營業比重不拆分資料中心與 PON 產品
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 72 頁（PDF 第 73 頁）營業比重與商品項目；第 89 頁（PDF 第 90 頁）市場占有率段落
    read-scope: 已讀業務內容段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: cw-laser-and-engines
  statement: 年報稱自 2019 年與策略夥伴共同開發並量產 CW DFB 雷射晶粒，已獲數家主要客戶採用，並朝 100mW CW DFB 與 100G／200G EML 發展；已完成 800G ZR 模塊與 70mW CW LD，並為雲端資料中心提供 100G–1.6T 光引擎與 CoC 封裝的 OEM／ODM 代工。
  confidence: inference
  conditions:
  - 客戶採用為公司自述，未具名；開發中產品不等於量產
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 72 頁（PDF 第 73 頁）計畫開發之新商品；第 81 頁（PDF 第 82 頁）技術及研發概況
    read-scope: 已讀新商品與研發段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報主要銷貨客戶以代號揭露，114 年度 LC01082 占 86.61%（113 年度 92.08%）、LC20188 占 10.33%；公司說明與最大客戶合作的產品成長迅速而形成銷貨集中。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 93–94 頁（PDF 第 94–95 頁）主要銷貨客戶；第 107 頁（PDF 第 108 頁）銷貨集中風險
    read-scope: 已讀主要銷貨客戶表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度
- id: supplier-concentration
  statement: 年報揭露 114 年度供應商 LV221309 占進貨 73.63%（113 年度 74.20%），該供應商在主要原料表中對應次模組（TOSA）；其他原料為 PCB、上蓋、封蓋、軟板與導熱矽膠片。
  confidence: well-supported
  conditions:
  - 供應商以代號揭露；未說明是否為客戶指定料
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 93 頁（PDF 第 94 頁）主要原料之供應狀況與主要進貨廠商
    read-scope: 已讀原料與進貨表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報揭露 114 年度銷售地區為北美 86.96%、內銷 10.81%、中國大陸 1.49%、其他 0.74%。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 90 頁）主要商品之銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: named-competitors
  statement: 年報列出競爭者：收光二極體為 GCS、中國電子科技集團 13 所與 29 所、光環；10G／25G APD 為 Sifotonics、光環、中國電科 44 所、Macom；10G／25G 雷射為西安源杰、武漢敏芯、Macom、Melco 與 Broadcom；代工業務為聯鈞、眾達-KY 與 Fabrinet。
  confidence: well-supported
  conditions:
  - 競爭者依產品線列出，部分僅針對 10G／25G 世代
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 81 頁（PDF 第 82 頁）競爭情形
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報未揭露客戶名稱、資料中心與 PON 產品的營收拆分，也未說明最大供應商是否為客戶指定料。
---

## 供應角色

華星光在[網路環節](/next?focus=segment-networking)屬[光收發模組](/next?focus=role-optical-module)，以代工方式供應光學次模組、光學引擎與[光收發模組](/next?focus=product-optical-transceiver)；同時自製雷射晶粒，屬[光通訊雷射與光電晶片](/next?focus=role-optical-chip)。

## 研究界線

本頁以 114 年度股東會年報為依據。客戶與供應商以代號揭露；CW 雷射獲客戶採用屬公司自述。模組與晶粒分屬兩個角色，營收也分開揭露（86.35% 與 11.05%），不合併比較。

## 產品與用途

- **雷射與檢光晶粒**：FP、DFB、CW 高功率雷射，PD、EMPD、APD（第 72 頁）。
- **次模組**：TO、OSA、PON 用 BOSA（第 72 頁）。
- **資料中心**：高速平行光學引擎、100G–1.6T 光引擎與 CoC 封裝代工（第 72、81 頁）。
- **相干光模組**：已完成 800G ZR 模塊，用於資料中心互連（第 72 頁）。

## 商業模式

以研發、設計、生產與 ODM／OEM 代工為主（第 72 頁）。114 年度營收 4,384,846 仟元，較 113 年度成長約 27%。

## 客戶與供應商

單一客戶 LC01082 占 86.61%，第二大客戶占 10.33%（第 93–94 頁）。最大供應商占進貨 73.63%，對應 TOSA 次模組（第 93 頁）。客戶與供應商名稱都未揭露。

## 競爭與替代

年報依產品線列出競爭者：雷射晶粒包括 [Broadcom](/next?focus=company-avgo)、Macom、源杰與敏芯；代工業務包括聯鈞、眾達-KY 與 Fabrinet（第 81 頁）。年報也說 2016 年起中國廠商的規模與技術快速提升。

## 業務曝險

北美占 86.96%，單一客戶占 86.61%，產品主要用於 AI 資料中心；曝險集中在單一客戶的資料中心光模組計畫。

## 風險

- **單一客戶**：最大客戶占營收八成以上。
- **單一供應商**：TOSA 供應商占進貨七成以上。
- **中國競爭**：中國光元件廠規模與技術快速提升（第 81 頁）。
- **匯率**：營收與成本多以外幣計價（第 105 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由櫃買中心公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 客戶名稱與資料中心營收拆分：年報未公開。
