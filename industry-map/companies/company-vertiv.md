---
schema-version: research-v1
entity-id: company-vertiv
kind: company
name-zh: Vertiv
aliases:
- Vertiv
summary: 供電、熱管理與服務涵蓋資料中心基礎設施；CoolChip CDU 的產品能力須按架構及場址條件辨認。
legacy-keys:
- VRT
listings:
- ticker: VRT
  market: US
  exchange: UNKNOWN
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1674101'
research-depth: basic
reviewed: '2026-10-16'
roles:
- segment-id: segment-thermal
  description: 資料中心熱管理與冷卻液分配單元
  tier: 1
  baseline-path: ai-server/thermal.md
claims:
  - id: coolchip-l2l-capability
    statement: Vertiv 的 CoolChip CDU 公開產品表列有液對液型號，也另外列出液對氣型號。
    confidence: well-supported
    conditions: [以本輪讀到的產品家族為準，需按具體型號與測試條件驗證]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-coolchip-product-reading
        url: https://www.vertiv.com/en-us/products-catalog/thermal-management/high-density-solutions/vertiv-coolchip-cdu/
        locator: CoolChip CDU／Product Family 與 Model Specifications Overview
        read-scope: 已讀公開家族說明、型號表與功能，未讀需填表的下載文件
        stance: supporting
        applicable-period: 2026-10-16 所讀產品頁；頁面發布日未提供
  - id: infrastructure-business-scope
    statement: Vertiv 的公開定位涵蓋供電、冷卻與服務，不能把公司整體收入直接當作液冷產品收入。
    confidence: inference
    conditions: [業務範圍可由公司介紹核對；產品收入仍需獨立財務揭露]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-company-scope-reading
        url: https://www.vertiv.com/en-us/about/about-us/
        locator: About Us／end-to-end infrastructure 與 Powering and cooling the AI revolution
        read-scope: 已讀公司公開業務範圍，未以頁面營收摘要推算液冷占比
        stance: supporting
        applicable-period: 2026-10-16 所讀公司介紹；頁面公司資料基準為 2025 年底
gaps:
- status: not-researched
  reason: 本輪未核對液冷產品單獨收入、具名客戶與訂單；產品能力不表示特定交易已成立。
---

## 供應角色

這條流程先核對[液對液 CDU](/next?focus=product-liquid-to-liquid-cdu)。它串接伺服器與設施水路，選型取決於供水及回路條件；同一產品家族仍有不同架構。

公司公開定位同時涵蓋供電、冷卻、IT 基礎設施與服務。研究液冷成長時，需要辨認實際產品交付及服務範圍，不能直接以公司總收入代表這一條產品線。

## 研究界線

本輪證據支持公開產品與業務範圍，未完成具名供應關係或產品收入深研。官方額定換熱量附有條件，不能當作個別場址已驗收的數字。
