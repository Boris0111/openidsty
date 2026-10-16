---
schema-version: research-v1
entity-id: concept-liquid-cooling-loop
kind: concept
name-zh: 兩個液冷回路
aliases: [二次側回路, facility water, secondary loop]
summary: 熱跨過 CDU 的交換器；兩側液體保持分離。
reviewed: '2026-10-16'
definition: 本圖把晶片側冷卻液及設施側水路分開，說明液對液架構的責任邊界。
scope: 適用冷板加液對液 CDU 的功能說明，並非設備配管或所有平台的工程設計。
related-ids: [application-ai-rack-cooling, product-cold-plate, product-liquid-to-liquid-cdu, company-auras, company-vertiv]
diagram-assets: [asset-cooling-loop-desktop, asset-cooling-loop-mobile]
comparisons:
  - left: product-cold-plate
    right: product-liquid-to-liquid-cdu
    conditions: [比較在同一液對液回路中的功能]
    limitations: [兩者互補而非可替代，冷板表現不能用 CDU 額定容量排名]
claims:
  - id: heat-crosses-liquid-does-not
    statement: NVIDIA 公開參考架構將設施水路與 GPU 冷板的二次側回路分開，CDU 位於兩者之間。
    confidence: well-supported
    conditions: [僅引用參考架構的回路分工]
    reviewed: '2026-10-16'
    evidence:
      - source-id: nvidia-dsx-cooling-overview
        url: https://docs.nvidia.com/dsx/facilities-infra/reference-design-overview
        locator: CDUs - Cooling Distribution Units in the Mechanical Gallery
        read-scope: 已讀公開 overview，未讀 NVOnline 補充文件
        stance: supporting
        applicable-period: overview 引用 2026-08-19 的 DSX 指南 v2.0
gaps: [實際設備的供水條件、流量及水質仍依場址與型號驗證。]
---

## 中文解釋

晶片端的冷卻液帶著熱回到 CDU，再由熱交換器把熱交給設施水路。兩側液體分開，有助於把設備端與場址端的研究問題分開。

## 圖解

圖為原創功能示意。藍色表示較冷的供液，紅色表示帶熱回流；顏色不代表公司股價或證據強度。

## 適用範圍

此圖只畫液對液架構。液對氣 CDU 把熱排到空氣，需另查機房的空氣側容量，不能直接套用本圖的設施水路。
