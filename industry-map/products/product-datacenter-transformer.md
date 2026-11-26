---
schema-version: research-v1
entity-id: product-datacenter-transformer
kind: product
name-zh: "資料中心變壓器"
aliases:
- "data center transformer"
- "cast resin transformer"
summary: "藉電磁感應改變設施交流配電的電壓。"
definition: "藉電磁感應改變設施交流配電的電壓。"
purpose: "把適用的電網／場址受電電壓轉到下一段配電並支援隔離與接地設計。"
boundary: "開關設備負責保護與隔離，UPS 負責電源品質／短暫備援。"
adoption-conditions:
- "核對接入責任、一次／二次側、向量組、短路阻抗、頻率、負載和工廠／現場試驗。"
bottlenecks:
- "長交付週期、絕緣散熱、空間和大電流故障承受。"
substitution-limits:
- "同一電壓轉換點和場址條件才比較乾式與液浸。"
reviewed: "2026-11-24"
claims:
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
- id: site-transformer-selection
  statement: "同一次／二次電壓、負載與故障容量下，乾式與液浸可比較絕緣、散熱、空間及維護；設備級距受絕緣、冷卻和案場設計影響。"
  confidence: well-supported
  conditions:
  - "乾式或液浸同屬變壓交付，仍須通過當地接入、消防及試驗要求。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-transformer-spec-guide
    url: https://www.teco.com.tw/upload/userfiles/files/%E8%AE%8A%E5%A3%93%E5%99%A8%E5%9E%8B%E9%8C%84%E8%8B%B1%E6%96%87%E7%89%88_251210_final_TECO_Transformers.pdf
    locator: "DRY CAST RESIN–DISTRIBUTION TRANSFORMER 規格表 2,500 kVA 列"
    read-scope: "查一次側／二次側、空載、75°C 負載損耗及阻抗。"
    stance: supporting
    applicable-period: "2025-12 型錄"
  - source-id: eaton-secondary-substations-guide
    url: https://www.eaton.com/content/dam/eaton/products/design-guides---consultant-audience/eaton-secondary-unit-substation-design-guide-dg022017en.pdf
    locator: "14.1-11 Cast Coil Transformers"
    read-scope: "核對單元變電站用途、環境條件及訂製。"
    stance: supporting
    applicable-period: "DG022017EN，2025-10"
  - source-id: hitachi-energy-hidry
    url: https://www.hitachienergy.com/us/en/products-and-solutions/transformers/distribution-transformers/dry-type-transformers/hidry-dry-type-transformers-40-5-kv
    locator: "Product scope"
    read-scope: "核對 52／72.5 kV 電壓級與最高 63 MVA 尺度、冷卻方式。"
    stance: supporting
    applicable-period: "查核日產品頁"
- id: facility-transformer-demand
  statement: "新增可接入的資料中心容量，可能需要新變壓器或增加既有變電站出線。"
  confidence: inference
  conditions:
  - "須扣除既有可用容量並核實場址方案、交期與冗餘；接入延後會改變出貨時點。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: teco-datacenter-solutions
    url: https://www.teco.com.tw/en-us/solution/data-center/
    locator: "Transformer／Data Center Engineering"
    read-scope: "核對出廠與型式試驗及場址工程範圍。"
    stance: supporting
    applicable-period: "查核日資料中心方案"
  - source-id: eaton-secondary-substations-guide
    url: https://www.eaton.com/content/dam/eaton/products/design-guides---consultant-audience/eaton-secondary-unit-substation-design-guide-dg022017en.pdf
    locator: "14.1-11 Cast Coil Transformers"
    read-scope: "核對單元變電站用途、環境條件及訂製。"
    stance: supporting
    applicable-period: "DG022017EN，2025-10"
gaps:
- status: not-public
  reason: "設備頁與股東會公告未列本產品的合格專案金額、交期、獲利或具名客戶。"
- status: not-obtained
  reason: "逐案報價、同標準及同負載效率資料未取得。"
---

## 定義與用途

電網於何處交付電力由案場與電力公司約定。若以中壓受電，變壓器可能置於設施內，由中壓降到低壓供下游開關、UPS 與配電；大型接入也可在場址先降一級。每個級距的設備分開計算。

## 規格與成本

以東元乾式型錄的 2,500 kVA 列為例，22.8 kV → 380 V，阻抗 6%，空載損耗 3.4 kW，75°C 負載損耗 15 kW。設計同時看功率因數、諧波、溫升及備援配置。能耗估算須按實際負載，另計空間、通風和消防。

## 採用條件與限制

乾式及液浸可在相同一次／二次側、MVA、故障容量和可靠度下比較，還要看通風、絕緣液集液、噪音、安裝位置與試驗。Hitachi Energy HiDry 涵蓋 52／72.5 kV 級且最高 63 MVA；不能由絕緣型式單獨推斷額定。

## 供應角色與公司

[設施變壓設備](/next?focus=role-facility-transformer)的台股代表 [東元電機](/next?focus=company-1504-tw)實際製造上述設備並提供試驗。Eaton 為 NYSE 上市的愛爾蘭主體，乾式單元變電站為可比型錄。Hitachi Energy 為日立集團的設備公司，按產品規格比較，另核對地區接入資格。

## 需求如何傳導

推論：新增受電容量可帶動設備與工程需求。既有站房若有備用容量，或接入時程、發包與機櫃利用率滯後，訂單、出廠、上電與收入可能錯開。追蹤核准 MVA、拓樸、驗收和交期。
