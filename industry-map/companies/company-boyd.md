---
schema-version: research-v1
entity-id: company-boyd
kind: company
name-zh: Boyd
aliases:
- Boyd
- Boyd Corporation
- Boyd Thermal
summary: 未上市；熱管理業務已於 2026 年 3 月以 95 億美元售予 Eaton，留下的 Boyd 以工程材料為主。
legacy-keys:
- PRIVATE:boyd
listings: []
source-identifiers: []
research-depth: deep
reviewed: '2026-10-18'
roles:
- segment-id: segment-thermal
  description: 液冷冷板
  tier: 2
  baseline-path: ai-server/thermal.md
claims:
- id: thermal-sold-to-eaton
  statement: Boyd 官方新聞稿宣布已完成將熱管理（Thermal）業務以 95 億美元出售給 Eaton，交易於 2025 年 11 月 3 日宣布。
  confidence: well-supported
  conditions:
  - 新聞稿未載明確切交割日與產品層級的移轉範圍；Eaton 的報告分部本輪未讀
  reviewed: '2026-10-18'
  evidence:
  - source-id: boyd-thermal-sale-completion
    url: https://www.boydcorp.com/boyd-completes-the-sale-of-its-thermal-business-to-eaton-for-9-5-billion.html
    locator: 完成公告第一段（Boca Raton, FL – March 12, 2026）
    read-scope: 已讀完成公告全文
    stance: supporting
    applicable-period: 2026-03-12 公告
- id: remaining-engineered-materials
  statement: 出售公告說明，Boyd 的工程材料業務在交易後以 Boyd Corporation 品牌獨立營運，由 Goldman Sachs Alternatives 支持；交易原預計 2026 年第二季交割。
  confidence: well-supported
  conditions:
  - 公告未逐項列出哪些產品線隨熱管理業務移轉
  reviewed: '2026-10-18'
  evidence:
  - source-id: boyd-thermal-sale-announcement
    url: https://www.boydcorp.com/about-boyd/resources/news-and-events/boyd-announces-sale-of-its-thermal-business-to-eaton-for-9-5-billion.html
    locator: 出售公告副標與內文（Boca Raton, FL – November 3, 2025）
    read-scope: 已讀出售公告全文
    stance: supporting
    applicable-period: 2025-11-03 公告
- id: chip-to-ambient-positioning
  statement: 出售公告引述 Boyd 執行長，稱結合 Eaton 的 chip-to-grid 供電與 Boyd 的 Chip-to-Ambient 冷卻架構，有助於加速 AI 資料中心部署。
  confidence: inference
  conditions:
  - 屬交易說明中的策略描述，不揭露產品收入、客戶或出貨
  reviewed: '2026-10-18'
  evidence:
  - source-id: boyd-thermal-sale-announcement
    url: https://www.boydcorp.com/about-boyd/resources/news-and-events/boyd-announces-sale-of-its-thermal-business-to-eaton-for-9-5-billion.html
    locator: 出售公告執行長引言
    read-scope: 已讀引言段落
    stance: supporting
    applicable-period: 2025-11-03 公告
- id: engineered-materials-lines
  statement: 官網工程材料頁列出黏著系統、絕緣與屏蔽、防護與密封、墊片與 O 型環、人機介面與圖文、熱介面材料與石墨散熱片等產品線。
  confidence: well-supported
  conditions:
  - 熱介面材料與石墨散熱片和已售出熱管理業務的界線，官網與新聞稿都未說明
  reviewed: '2026-10-18'
  evidence:
  - source-id: boyd-company-pages
    url: https://www.boydcorp.com/about-boyd/locations.html
    locator: https://www.boydcorp.com/engineered-materials.html「What are Engineered Materials?」與產品線清單
    read-scope: 已讀工程材料頁
    stance: supporting
    applicable-period: 2026-10-18 所讀官網
- id: global-footprint
  statement: 官網據點頁列出美洲（含墨西哥華瑞茲）、亞洲（東莞、深圳、無錫、新加坡、泰國春武里、越南北寧等）與歐洲的據點，但未區分熱管理與工程材料。
  confidence: well-supported
  conditions:
  - 據點清單不代表出售後各據點歸屬
  reviewed: '2026-10-18'
  evidence:
  - source-id: boyd-company-pages
    url: https://www.boydcorp.com/about-boyd/locations.html
    locator: https://www.boydcorp.com/about-boyd/locations.html
    read-scope: 已讀據點頁
    stance: supporting
    applicable-period: 2026-10-18 所讀官網
gaps:
- status: not-applicable
  reason: Boyd 未上市，沒有公開財報或 listing；不以收購價推算營收。
- status: not-obtained
  reason: eaton.com 本輪連線逾時，Eaton 對收購範圍、報告分部與營收的官方說明未讀。
- status: not-obtained
  reason: Boyd 官網可達頁面未找到冷板、CDU 或歧管產品頁；出售後的冷板產品應以 Eaton 名義另行核對。
---

## 供應角色

舊地圖把 Boyd 列在[散熱環節](/next?focus=segment-thermal)的液冷冷板角色。依 Boyd 官方新聞稿，熱管理業務已於 2026 年 3 月售予 Eaton，所以這個角色在現況下應理解為「原 Boyd Thermal、現屬 Eaton」的業務；Boyd 公司本身留下的是工程材料。

## 研究界線

本頁只依 Boyd 官方新聞稿與官網。eaton.com 連線逾時，Eaton 的公告與財務分部未讀；官網可達頁面也沒有冷板或 CDU 的產品頁。地圖暫不新增 Eaton 主體，也不把 Eaton 的 listing 套到 Boyd。

## 產品與用途

- **已售出的熱管理業務**：公告以 Chip-to-Ambient 冷卻架構描述，本輪沒有讀到具體產品頁。
- **留下的工程材料**：黏著、絕緣屏蔽、密封、墊片、人機介面與圖文、熱介面材料與石墨散熱片（工程材料頁）。

## 商業模式

出售後，Boyd Corporation 以工程材料業務獨立營運，由 Goldman Sachs Alternatives 支持（出售公告、完成公告）。熱管理業務併入 Eaton，與 Eaton 的供電產品形成「供電加冷卻」的組合。

## 客戶與供應商

官方新聞稿與官網沒有揭露客戶名稱或營收；資料中心頁提到 hyperscale、colocation 等用戶，但內容是工程材料（氣流、密封、標籤），不是液冷客戶名單。

## 競爭與替代

在[晶片端取熱](/next?focus=role-chip-heat-capture)角色，原 Boyd Thermal 與[雙鴻](/next?focus=company-auras)、[奇鋐](/next?focus=company-avc)等可比較；出售後應以 Eaton 的產品資料重新核對。

## 業務曝險

收購價 95 億美元是交易對價，不是營收。Boyd 未公開財報，熱管理業務的規模與 AI 資料中心占比都無法由官方資料得知。

## 風險

- **主體變動**：研究對象的液冷能力已轉到 Eaton，沿用 Boyd 名稱會造成誤讀，需在閱讀時說明。
- **界線不明**：熱介面材料、石墨散熱片等仍列在 Boyd 工程材料下，與已售出熱管理業務的界線未公開。

## 財務可取性

- Boyd 未上市，沒有公開財報，不適用財務比較。
- Eaton 為上市公司，但地圖目前沒有 Eaton 主體；收購後的熱管理營收需由 Eaton 申報另查。
