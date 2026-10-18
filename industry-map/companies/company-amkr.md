---
schema-version: research-v1
entity-id: company-amkr
kind: company
name-zh: 艾克爾
aliases:
- Amkor Technology
- Amkor
summary: 美國總部最大的委外封測廠；2025 年營收 67.1 億美元、成長 6.2%，運算（含資料中心）占 20%，Apple 與 Qualcomm 分別占 29.8% 與 11.1%；亞利桑那廠預計 2028 年上半年開始生產。
legacy-keys:
- AMKR
listings:
- ticker: AMKR
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1047127'
research-depth: deep
reviewed: '2026-10-19'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-19'
  fiscal-year-end: 12-31
  calendar-valid-from: '2023-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: 10-K Item 7. MD&A（Net sales，2023–2025 年度）；SEC 申報期間 2025-12-31
    read-scope: 已讀營收表
    stance: supporting
    applicable-period: FY2023–FY2025
roles:
- segment-id: segment-advanced-packaging
  description: 委外封測
  tier: 2
  baseline-path: ai-server/advanced-packaging.md
claims:
- id: sales-and-end-markets
  statement: 10-K 揭露 2025 年營收 6,707,981 千美元，較 2024 年成長 6.2%；依終端市場估計為通訊 46%、運算（資料中心、基礎設施、PC、儲存）20%、車用工業及其他 19%、消費 15%，運算比重由 2023 年 16% 逐年上升。
  confidence: well-supported
  conditions:
  - 終端市場比例是依最大客戶抽樣估計的近似值
  reviewed: '2026-10-19'
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: Item 1. Business（End Market Distribution Data）；Item 7. MD&A（Net sales）
    read-scope: 已讀終端市場表與營收段落
    stance: supporting
    applicable-period: FY2023–FY2025
- id: technology-portfolio
  statement: 10-K 說明提供封裝與測試一站式服務（凸塊、晶圓針測、封裝、預燒、系統級與最終測試），技術涵蓋高密度扇出（SWIFT、S-Connect）、2.5D 整合、先進覆晶、細間距凸塊、晶圓級製程與 SiP；研發重點包括含或不含橋接晶片的 2.5D 與 HDFO 多晶片模組。
  confidence: well-supported
  conditions:
  - 10-K 未揭露 2.5D 或 AI 相關營收與量產規模
  reviewed: '2026-10-19'
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: Item 1. Business（Overview；Strategy；Research and Development）
    read-scope: 已讀業務與研發段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: customer-concentration
  statement: 10-K 揭露 2025 年前十大客戶占營收 72%，直接銷售給 Apple 與 Qualcomm 分別占 29.8% 與 11.1%。
  confidence: well-supported
  conditions:
  - 直接銷售口徑，不含透過其他通路的間接銷售
  reviewed: '2026-10-19'
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: Item 1. Business（Customers）；Item 1A 客戶集中風險
    read-scope: 已讀客戶段落
    stance: supporting
    applicable-period: FY2025
- id: named-competitors
  statement: 10-K 說明競爭來自主要位於亞洲的封測廠，具名 ASE Technology、JCET Group 與 Powertech Technology，另有提供部分先進封裝的晶圓代工與 EMS 廠，以及 IDM 自有產能；地緣政治也增加了支援中國本地供應鏈的中國廠商競爭。
  confidence: well-supported
  conditions:
  - 競爭依封裝類型而異
  reviewed: '2026-10-19'
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: Item 1. Business（Competition）
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: FY2025 10-K
- id: arizona-plan
  statement: 10-K 揭露 2025 年開始興建亞利桑那廠第一期，約 180 萬平方英尺，預計 2028 年上半年開始生產；CHIPS Act 獎助最高 4.07 億美元，截至 2025 年底尚未收到撥款。2025 年資本支出 904.6 百萬美元（營收的 13.5%），主要投入先進封裝與測試設備及亞利桑那廠。
  confidence: well-supported
  conditions:
  - 生產時程與獎助取決於里程碑達成
  reviewed: '2026-10-19'
  evidence:
  - source-id: amkr-10k-2025
    url: https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm
    locator: Item 1A（CHIPS Act 風險）；Item 2／Item 7（Arizona Facility；capital expenditures）
    read-scope: 已讀亞利桑那與資本支出段落
    stance: supporting
    applicable-period: FY2025 10-K
gaps:
- status: not-public
  reason: 10-K 未揭露 2.5D、HDFO 或 AI 相關營收與客戶專案。
---

## 供應角色

Amkor 在[先進封裝環節](/next?focus=segment-advanced-packaging)屬[委外封裝](/next?focus=role-osat-assembly)與[晶圓與成品測試服務](/next?focus=role-test-service)，並以 2.5D 整合能力列入[中介層與 2.5D／3D 整合](/next?focus=role-interposer-integration)。

## 研究界線

本頁以 FY2025 10-K 為依據，並分開三種狀態：**已營運**的封裝與測試服務；**技術能力**（2.5D、HDFO），10-K 未揭露量產規模；**規劃**中的亞利桑那廠，預計 2028 年上半年開始生產。客戶比例是直接銷售口徑。

## 產品與用途

- **封裝**：先進覆晶、高密度扇出（SWIFT、S-Connect）、2.5D、晶圓級與 SiP（Item 1）。
- **測試**：晶圓針測、預燒、系統級與最終測試（Item 1）。
- **研發**：含橋接晶片的 2.5D 與 HDFO 多晶片模組、晶圓級與面板級封裝（Item 1）。

## 商業模式

為 IDM、fabless、OEM 與代工廠提供封測，據點在韓國、台灣、中國、日本、馬來西亞、菲律賓、越南、葡萄牙等地（Item 1A）。2025 年營收 67.1 億美元，資本支出 9.05 億美元（Item 7）。

## 客戶與供應商

前十大客戶 72%，Apple 29.8%、Qualcomm 11.1%（Item 1）。兩家客戶目前不在地圖中，未建立關係。客戶端 10-K 具名 Amkor 為封測廠的包括 [Broadcom](/next?focus=company-avgo)、[Credo](/next?focus=company-crdo) 與 [Astera Labs](/next?focus=company-alab)（見關係）。

## 競爭與替代

10-K 具名 [日月光投控](/next?focus=company-3711-tw)、JCET 與[力成](/next?focus=company-6239-tw)，並指出[台積電](/next?focus=company-tsmc)等代工廠也提供部分先進封裝（Item 1）。

## 業務曝險

運算占比由 16% 升到 20%，但通訊（智慧型手機）仍占近一半，且 Apple 占近三成；AI 曝險低於以 AI 為主的封裝供應者。

## 風險

- **客戶集中**：Apple 單一客戶約三成。
- **亞利桑那廠**：建廠成本、時程與 CHIPS 獎助里程碑（Item 1A）。
- **中國競爭**：地緣政治推動中國本地封測廠擴張（Item 1）。
- **原料價格**：金、銅與載板價格波動（Item 1A）。

## 財務可取性

- SEC companyfacts 可自動取得標準科目；主要申報來源設為 SEC，會計年度為曆年。
- 終端市場比重可由 10-K 核對。
- 2.5D 與 AI 相關營收：10-K 未公開。
