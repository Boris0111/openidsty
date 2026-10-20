---
schema-version: research-v1
entity-id: product-cold-plate
kind: product
name-zh: 液冷冷板
aliases: [冷板, cold plate, direct-to-chip]
summary: 貼近晶片吸收熱量的零件；價值在接觸、流道與封裝適配，並不包辦整座機房散熱。
reviewed: '2026-10-20'
definition: 將晶片熱量傳入循環冷卻液的接觸式散熱元件。
purpose: 在高熱密度元件附近取熱，再把熱交給後續水路。
boundary: 冷板負責晶片端取熱；CDU 的循環控制、換熱與設施散熱屬於不同交付角色。
adoption-conditions: [晶片接觸面與安裝機構相容, 流量與壓降須和整個二次側回路一起驗證]
bottlenecks: [局部散熱能力與水路阻力需同時考慮, 漏液與材料相容會影響系統可靠度]
substitution-limits: [不能用 CDU 的額定換熱量比較冷板的晶片端表現, 更換冷板仍需重新確認平台及水路介面]
claims:
  - id: chip-heat-capture
    statement: 直接晶片液冷以冷板在發熱元件附近取熱，功能不同於 CDU 的流量與溫度控制。
    confidence: well-supported
    conditions: [本頁討論冷板式直接晶片液冷，不涵蓋浸沒式架構]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-liquid-cooling-reading
        url: https://www.vertiv.com/en-us/solutions/learn-about/liquid-cooling-options-for-data-centers/
        locator: Direct-to-chip liquid cooling；Distribution
        read-scope: 已讀冷板取熱及 CDU 控制的公開說明，未採用文中市場預測與通用節能比例
        stance: supporting
        applicable-period: 公開原理說明；頁面未提供獨立發布日
gaps:
- status: not-researched
  reason: 各平台的冷板性能、驗證及售價需另查產品規格，不能由通用原理推估。
---

## 定義與用途

冷板處理的是「熱如何離開晶片」。研究供應商時，先辨認交付的是冷板、歧管還是完整水路，才能比較實際可替換的角色。

## 採用條件與限制

本頁的介面與替代判斷是研究推論，須以特定平台驗證。冷板、配管及泵浦共同決定工作點；元件單獨性能較好，不保證整個回路更好。

## 供應角色與公司

[雙鴻](/next?focus=company-auras)、[奇鋐](/next?focus=company-avc)與[建準](/next?focus=company-2421-tw)的官方資料可支持冷板產品範圍：雙鴻依 2025 展會新聞，奇鋐與建準依年報產品項目。這不等於已確認某一客戶、訂單或液冷收入。[Boyd](/next?focus=company-boyd)依既有環節角色列入，尚未核對其冷板產品證據。
