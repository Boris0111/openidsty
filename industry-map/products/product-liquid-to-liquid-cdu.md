---
schema-version: research-v1
entity-id: product-liquid-to-liquid-cdu
kind: product
name-zh: 液對液 CDU
aliases: [液對液冷卻液分配單元, L2L CDU, coolant distribution unit]
summary: 讓伺服器側冷卻液循環、受控，並透過熱交換器把熱交給設施水路；兩側液體維持分離。
reviewed: '2026-10-20'
definition: 具液對液換熱及冷卻液分配功能的設備。
purpose: 串接伺服器二次側回路與設施側散熱能力。
boundary: 本類限定液對液型；液對氣 CDU 把熱排回空氣，是不同場址條件下的選擇。
adoption-conditions: [場址有相容且足量的設施水路, 選型要核對供水溫度、溫差、流量與冗餘條件]
bottlenecks: [CDU 與設施端散熱容量都可能成為限制, 材料、水質、過濾與維護責任需在回路整合時確認]
substitution-limits: [沒有設施水路時不能直接以液對液型取代液對氣型, 不同測試溫差下的額定容量不能直接排名]
claims:
  - id: separate-circuits
    statement: NVIDIA 的 DSX 公開架構以 CDU 連接設施水路及服務 GPU 冷板的獨立二次側回路。
    confidence: well-supported
    conditions: [只引用該參考架構的回路分工，不泛用其場址容量或流量數字]
    reviewed: '2026-10-16'
    evidence:
      - source-id: nvidia-dsx-cooling-overview
        url: https://docs.nvidia.com/dsx/facilities-infra/reference-design-overview
        locator: CDUs - Cooling Distribution Units in the Mechanical Gallery
        read-scope: 已讀公開 overview 的 CDU 分工，未取得 NVOnline 補充設計文件
        stance: supporting
        applicable-period: overview 引用 2026-08-19 的 DSX 設施設計指南 v2.0
  - id: model-conditions
    statement: Vertiv CoolChip CDU 家族同時有液對液及液對氣型號，額定能力附有溫差條件。
    confidence: well-supported
    conditions: [必須按具體型號及測試條件選型，產品家族不是單一可互換規格]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-coolchip-product-reading
        url: https://www.vertiv.com/en-us/products-catalog/thermal-management/high-density-solutions/vertiv-coolchip-cdu/
        locator: Product Family；Model Specifications Overview
        read-scope: 已讀家族架構及型號表，未讀登入或留資料才能下載的文件
        stance: supporting
        applicable-period: 2026-10-16 所讀公開產品頁；頁面未提供獨立發布日
gaps:
- status: not-public
  reason: 官方額定能力不等於個別場址驗收，也不能證明客戶採用或出貨收入；場址驗收與客戶採用資料未公開。
---

## 定義與用途

CDU 回答的是「冷卻液怎麼穩定循環、熱要交給誰」。液對液設計需要另一側設施水路接走熱量，不能只看 CDU 本身的容量。

## 採用條件與限制

本頁的選型與替代限制是有條件推論。比較時須使用同一水溫、溫差、流量及冗餘基準；用一個最大 kW 數字判斷優劣會省略關鍵條件。

## 供應角色與公司

[Vertiv](/next?focus=company-vertiv)的 CoolChip 公開產品頁支持本類能力。[雙鴻](/next?focus=company-auras)的 114 年度年報列出水對水 CDU 方案（機櫃型 In-rack 與一對多 In-Row）；2025 展會新聞曾以研發措辭描述，年報也未揭露出貨量、客戶或收入，因此只代表可提供的產品方案。
