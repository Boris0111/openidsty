---
schema-version: research-v1
entity-id: company-1504-tw
kind: company
name-zh: 東元電機
aliases: [東元, TECO, TECO Electric & Machinery]
summary: 製造變壓器等機電設備，並以資料中心機電工程與產品交付參與設施供電。
legacy-keys: []
listings:
- ticker: "1504.TW"
  market: TW
  exchange: XTAI
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-datacenter
  description: 供應設施變壓設備與機電工程
  tier: 2
  baseline-path: ai-server/datacenter.md
claims:
- id: tecobar-busway-delivery
  statement: "東元子公司 TECOBAR 的 LB 低壓鑄樹脂銅母線用於 1 kV 以下，部分料號額定最高 6,300 A。"
  confidence: well-supported
  conditions:
  - "另依組件、配置及標準驗收，交付主體為 TECOBAR。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: tecobar-lb-busway
    url: https://www.tecobar.com.tw/en/product-396369/LV-Cast-Resin-Insulated-Busway-Copper-Busway-LB-Series.html
    locator: "LB Series／Technical Data"
    read-scope: "查 1 kV 以下、6,300 A 規格列。"
    stance: supporting
    applicable-period: "查核日 LB 系列"
  - source-id: teco-2026-tecobar-affiliation
    url: https://www.teco.com.tw/en-us/press/news/TECO-Showcases-Integrated-Modular-Data-Center-Solutions-in-Singapore--Targeting-Southeast-Asia-s-AI-Infrastructure-Opportunities?tags=1014
    locator: "Exhibition／its subsidiary TECOBAR"
    read-scope: "確認集團歸屬及子公司展示的母線類型。"
    stance: supporting
    applicable-period: "2026 年公告"
- id: teco-switchgear-delivery
  statement: "東元交付資料中心中低壓開關設備，公開頁列設計、製造、安裝與維護。"
  confidence: well-supported
  conditions:
  - "資料中心解決方案可支持能力，指定案場型號和容量須另驗。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-datacenter-solutions
    url: https://www.teco.com.tw/en-us/solution/data-center/
    locator: "MV & LV Switchgear"
    read-scope: "查製造、安裝、維修與整合責任。"
    stance: supporting
    applicable-period: "東元查核日解決方案頁"
- id: facility-transformer-delivery
  statement: "東元型錄列乾式配電、油浸配電與油浸電力變壓器。乾式配電有 22.8 kV 至 380 V 的具體規格表，油浸大型設備另列 150／161 kV、最高 150 MVA。"
  confidence: well-supported
  conditions:
  - "電壓、容量和試驗須按單一案場與樣機核對；型錄上限不能合併成一個料號保證。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-transformer-catalog
    url: https://www.teco.com.tw/en-us/products/power-transmission/transformer/
    locator: "Product：三類變壓器"
    read-scope: "確認乾式、油浸配電與油浸電力級的額定範圍。"
    stance: supporting
    applicable-period: "查核日產品型錄"
  - source-id: teco-transformer-spec-guide
    url: https://www.teco.com.tw/upload/userfiles/files/%E8%AE%8A%E5%A3%93%E5%99%A8%E5%9E%8B%E9%8C%84%E8%8B%B1%E6%96%87%E7%89%88_251210_final_TECO_Transformers.pdf
    locator: "DRY CAST RESIN–DISTRIBUTION TRANSFORMER 規格表 2,500 kVA 列"
    read-scope: "查一次側／二次側、空載、75°C 負載損耗及阻抗。"
    stance: supporting
    applicable-period: "2025-12 型錄"
  - source-id: teco-datacenter-solutions
    url: https://www.teco.com.tw/en-us/solution/data-center/
    locator: "Transformer／Data Center Engineering"
    read-scope: "核對出廠與型式試驗及場址工程範圍。"
    stance: supporting
    applicable-period: "查核日資料中心方案"
- id: teco-data-center-business
  statement: "東元股東會公告確認 TWSE 1504、FY2025 合併營收新台幣 590.9 億元，以及北美與東南亞 AIDC 整合策略。"
  confidence: well-supported
  conditions:
  - "合併營收包含其他業務，無法直接計算變壓器或資料中心產品占比。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-2026-agm
    url: https://www.teco.com.tw/en-us/press/news/20260528?tags=2260
    locator: "公告首段、2025 consolidated revenue 與 AIDC strategy"
    read-scope: "核對上市主體、合併總收入及區域策略。"
    stance: supporting
    applicable-period: "2026-05-28，FY2025"
gaps:
- status: not-public
  reason: "未見具名合格變壓器場址、產品收入和毛利拆分。"
---

## 供應角色

供應[設施變壓設備](/next?focus=role-facility-transformer)，並提供案場的機電工程施工和系統整合。

## 研究界線

設備型錄證實規格範圍，工程頁證實設計及試驗服務。資料中心專案容量與單顆設備容量分開。

## 產品與用途

資料中心方案另列[中低壓開關櫃](/next?focus=product-datacenter-switchgear)；集團由子公司 TECOBAR 供應[低壓母線槽](/next?focus=product-datacenter-busway)。兩者依設備、現場驗收與法律交付主體分開。

[資料中心變壓器](/next?focus=product-datacenter-transformer)包括 22.8 kV → 380 V 乾式配電型，以及另列的 150／161 kV 油浸電力用設備。按接入條件、一次／二次側、短路阻抗與場址消防選型。

## 商業模式

有設備製造和整合交付：型錄按設備選型，資料中心工程則包括 MEP／ICT，成本與驗收邊界取決於合約。

## 客戶與供應商

東元列出台灣及若干東南亞市場的工程經驗，型錄未列本批特定變壓器下游客戶，也未列繞線、鐵心或絕緣材料的具名採購。

## 競爭與替代

與 Eaton cast coil 的可比範圍是同電壓級、容量與環境的乾式配電交付，測試依標準與案場指定。同案需核對空載、負載損耗、溫度與保養成本。

## 業務曝險

北美、東南亞 AIDC 擴張屬公司策略。推論：接入容量、機電分包及驗收時程有利於合格設備，但其他機電產品與變壓器敞口分開。

## 風險

大型變壓器需求受專案變電站設計、當地接入核准、產線與原料、出廠型式試驗及驗收影響。廠方公布新產線策略，仍需追蹤時程與合格產能。

## 財務可取性

股東會公告提供合併收入新台幣 590.9 億元（FY2025），目前已讀文件沒有可用的變壓器或 AIDC 單項收入、毛利或客戶占比。
