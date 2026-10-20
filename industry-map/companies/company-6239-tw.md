---
schema-version: research-v1
entity-id: company-6239-tw
kind: company
name-zh: 力成
aliases:
- Powertech Technology
- 力成科技
- PTI
summary: 記憶體封測龍頭，記憶體與邏輯 IC 約各半；2025 年營收 749.3 億元，IC 封裝占 61.76%、各類測試合計約 22%；面板級扇出型封裝已量產消費性產品，AI 伺服器相關的大尺寸 FCBGA 與 HBM TSV 屬開發完成，FOPLP 大量量產規劃在 2026 年。
legacy-keys:
- 6239.TW
listings:
- ticker: 6239.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-10-19'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-19'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 76 頁（PDF 第 80 頁）主要商品銷售地區，2024 與 2025 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 2024–2025 曆年
roles:
- segment-id: segment-advanced-packaging
  description: 記憶體與邏輯封測
  tier: 2
  baseline-path: ai-server/advanced-packaging.md
claims:
- id: revenue-mix
  statement: 年報揭露 114 年度合併營收 74,929,320 仟元，其中 IC 封裝服務 61.76%、IC 測試服務 13.95%、模組加工服務 10.77%、晶圓級測試服務 8.25%、晶圓級封裝服務 5.24%；記憶體（DRAM、NAND）與邏輯 IC 的封測代工約各占一半。
  confidence: well-supported
  conditions:
  - 營業比重不拆分 AI 或 HBM 相關收入
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 68 頁（PDF 第 72 頁）營業比重；第 95 頁（PDF 第 99 頁）進銷貨集中風險
    read-scope: 已讀營業比重表與集中風險
    stance: supporting
    applicable-period: 114 年度
- id: in-production
  statement: 年報列為持續量產的項目包括無凸塊扇出型（BF2O）面板級封裝，用於行動與穿戴裝置等消費性產品；既有服務涵蓋 TSOP、BGA、MCP、DRAM 晶片堆疊、eMMC／UFS／SSD 等記憶體封測，以及覆晶、銅柱凸塊、晶圓級封裝與測試。
  confidence: well-supported
  conditions:
  - 年報未揭露各封裝型態的營收
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 68–69 頁（PDF 第 72–73 頁）商品項目；第 73 頁（PDF 第 77 頁）開發成功之技術
    read-scope: 已讀商品項目與研發成果
    stance: supporting
    applicable-period: 114 年度年報
- id: developed-for-ai
  statement: 年報把下列項目列為開發成功的技術：用於 AI 伺服器的 85mm×85mm 多晶片 FCBGA、以 TSV 與晶片堆疊製作的 HBM、取代傳統打線 BGA 的資料中心用 via-middle TSV DRAM FCCSP，以及用於 CPO 光學引擎的 via-middle TSV；另有 HBM 測試與 CoWoS 類測試開發。
  confidence: inference
  conditions:
  - 開發成功不等於已量產或已取得 AI 客戶訂單
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 69 頁（PDF 第 73 頁）計畫開發；第 73–74 頁（PDF 第 77–78 頁）開發成功之技術或產品
    read-scope: 已讀研發成果段落
    stance: supporting
    applicable-period: 114 年度年報
- id: foplp-plan
  statement: 年報稱擁有全球最成熟的面板級扇出型封裝生產線，並預計 FOPLP 於 2026 年進入成熟的大規模量產期，用於次世代 AI PC 與低軌衛星晶片；高速運算用超細線寬 RDL 的 FOPLP 仍在開發與驗證。
  confidence: needs-verification
  conditions:
  - 「全球最成熟」為公司自述；2026 年量產是規劃
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 72、76 頁（PDF 第 76、80 頁）產業與競爭利基；第 73 頁（PDF 第 77 頁）
    read-scope: 已讀產業概況與競爭利基段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報主要銷貨客戶以代號揭露，114 年度甲占 21.08%、乙占 19.88%（年報標示為關係人）、丙占 10.04%；最大供應商甲占進貨 10.46%。公司說明記憶體 IC 市場集中度高，使封測產業銷貨與進貨較集中。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露；乙客戶的關係人身分未在此表說明
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 79–80 頁（PDF 第 83–84 頁）主要進銷貨客戶；第 95 頁（PDF 第 99 頁）集中風險
    read-scope: 已讀主要進銷貨表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度
- id: named-materials
  statement: 年報列出主要原料供應商：基板為景碩、Shinko Electric、SIMMTECH、Samsung Electro-Mechanics、禮鼎、恆勁與 GTS；導線架為 Shinko Electric、長華電材與 NICHIDEN SEIMITU；金線為 Nippon 與 Tanaka。
  confidence: well-supported
  conditions:
  - 未揭露各供應商採購金額
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 79 頁（PDF 第 83 頁）主要原料之供應狀況
    read-scope: 已讀原料供應表
    stance: supporting
    applicable-period: 114 年度年報
- id: sales-regions
  statement: 年報揭露 2025 年度內銷占 41.01%（2024 年 19.19%）、外銷 58.99%；外銷以日本 20,693,320 仟元與美洲 13,445,864 仟元為主，新加坡由 18,360,461 仟元降至 2,763,950 仟元。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，年報未說明新加坡下降原因
  reviewed: '2026-10-19'
  evidence:
  - source-id: pti-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=6239&year=115&mtype=F&
    locator: 114 年度年報第 76 頁（PDF 第 80 頁）主要商品之銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 2024–2025
gaps:
- status: not-public
  reason: 年報未揭露客戶名稱、HBM 或 AI 相關營收，也未說明 FOPLP 在高速運算的客戶。
---

## 供應角色

力成在[先進封裝環節](/next?focus=segment-advanced-packaging)屬[委外封裝](/next?focus=role-osat-assembly)與[晶圓與成品測試服務](/next?focus=role-test-service)，以記憶體封測為主、邏輯 IC 約占一半。

## 研究界線

本頁以 114 年度股東會年報為依據，並把技術分成三種狀態：**已量產**（記憶體封測、BF2O 面板級扇出用於消費性產品）、**開發完成**（AI 伺服器用大尺寸 FCBGA、HBM TSV、CPO 用 TSV）、**規劃**（FOPLP 2026 年大規模量產）。後兩者不能當成已取得 AI 訂單的證據。

## 產品與用途

- **記憶體封測**：TSOP、BGA、MCP、DRAM 堆疊、記憶卡、eMMC／UFS／SSD（第 68–69 頁）。
- **邏輯封測**：覆晶、銅柱凸塊、晶圓級封裝、扇出型封裝與 SiP（第 69、77 頁）。
- **面板級扇出型封裝**：BF2O 持續量產；高速運算用細線寬 RDL 版本仍在驗證（第 73 頁）。
- **開發完成**：85mm FCBGA（AI 伺服器）、HBM TSV、資料中心 DRAM FCCSP、CPO 光學引擎 TSV（第 73–74 頁）。

## 商業模式

一站式提供晶圓針測、封裝與最終測試（第 76 頁）。114 年度營收 74,929,320 仟元，與 113 年度相近（第 68、76 頁）。

## 客戶與供應商

三家匿名客戶各占一成以上，其中乙客戶為關係人（第 80 頁）。原料供應商包括[景碩](/next?focus=company-3189-tw)、Shinko、SIMMTECH 與 Samsung Electro-Mechanics 等（第 79 頁）。台灣鎧俠先進半導體為法人董事（PDF 第 11 頁）。

## 競爭與替代

年報未具名競爭者。[Amkor](/next?focus=company-amkr) 的 10-K 把力成列為主要競爭者之一。在[委外封裝](/next?focus=role-osat-assembly)可與 Amkor、[日月光投控](/next?focus=company-3711-tw)比較；FOPLP 是否取代晶圓級封裝，要看 AI 晶片的尺寸、成本與良率。

## 業務曝險

記憶體約占一半，受記憶體廠資本支出與庫存循環影響；AI 曝險主要透過 HBM 與大尺寸封裝的開發計畫，年報沒有收入數字。

## 風險

- **客戶集中**：三大客戶合計約 51%，記憶體客戶集中度高（第 95 頁）。
- **技術轉換**：FOPLP 與 HBM 需持續投資，量產時程可能延後。
- **景氣循環**：記憶體封測隨記憶體市況波動（第 77 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- HBM 與 AI 相關營收：年報未公開。
