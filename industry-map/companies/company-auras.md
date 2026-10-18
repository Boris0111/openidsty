---
schema-version: research-v1
entity-id: company-auras
kind: company
name-zh: 雙鴻
aliases: [Auras, 雙鴻科技]
summary: 從晶片端散熱模組延伸到冷板、歧管與液冷系統；產品範圍與量產證據須分開看。
legacy-keys:
- 3324.TW
listings:
- ticker: 3324.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: basic
reviewed: '2026-10-16'
roles:
- segment-id: segment-thermal
  description: 液冷冷板、歧管與冷卻液分配單元
  tier: 1
  baseline-path: ai-server/thermal.md
claims:
  - id: cold-plate-portfolio
    statement: 雙鴻 2025 展會新聞明列冷板、歧管與 CDU，並介紹直接液冷的客製化設計。
    confidence: well-supported
    conditions: [此證據支持公司公開產品範圍，不指認客戶與訂單]
    reviewed: '2026-10-16'
    evidence:
      - source-id: auras-ocp-2025-reading
        url: https://www.auras.com.tw/News/NewsContent/14-10/en
        locator: OCP Global Summit 2025／液冷產品及直接液冷段落
        read-scope: 以瀏覽器讀取公開新聞內文，非僅 HTTP 200 的 JavaScript 外殼
        stance: supporting
        applicable-period: '2025-10-15 展會新聞；不是 2026 出貨資料'
  - id: development-is-not-shipment
    statement: 該新聞對液對液 CDU 使用研發措辭，不能據此判定已量產或帶來多少收入。
    confidence: inference
    conditions: [限於這篇 2025 新聞的證據範圍，不推定後續沒有商業進展]
    reviewed: '2026-10-16'
    evidence:
      - source-id: auras-ocp-2025-reading
        url: https://www.auras.com.tw/News/NewsContent/14-10/en
        locator: OCP Global Summit 2025／In-Row L2L CDU 段落
        read-scope: 已讀研發描述，未取得本輪後續出貨與收入查核
        stance: supporting
        applicable-period: '2025-10-15 新聞的產品規劃'
gaps:
- status: not-researched
  reason: 本輪已讀產品新聞；具名客戶、訂單與液冷收入占比尚未完成財務文件核讀。
---

## 供應角色

雙鴻以散熱設計與模組製造銷售起家，官方介紹將應用延伸到伺服器等領域。這條流程先核對[液冷冷板](/next?focus=product-cold-plate)，保留其歧管與 CDU 產品範圍的公開說明。

評估商業機會的下一步是平台驗證、實際交付與收入，而非只因出現在液冷清單就判斷曝險相同。

## 研究界線

2025 展會新聞不是 2026 訂單追蹤。液對液型號的研發描述與冷板產品範圍分開處理，本輪不建立雙鴻與 Vertiv 的具名供貨關係，也不估算液冷營收占比。完整客戶、競爭與財務深研仍待後續核對。
