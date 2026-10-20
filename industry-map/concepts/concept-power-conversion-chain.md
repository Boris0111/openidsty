---
schema-version: research-v1
entity-id: concept-power-conversion-chain
kind: concept
name-zh: 機櫃供電轉換鏈
aliases:
- power conversion chain
- 800VDC
summary: 電力從設施到晶片要經過多次轉換，每一級由不同產品負責。
reviewed: '2026-10-18'
definition: 說明設施電力經 AC/DC 轉換成機櫃母線，再由板端 DC/DC 轉成晶片電壓的轉換鏈。
scope: 適用供電轉換位置的功能說明，不代表特定架構的電壓、效率或保護設計。
related-ids:
- application-ai-rack-power
- product-power-shelf-psu
- product-pmic-voltage-regulator
- product-power-module
- product-power-transistor
diagram-assets:
- asset-power-conversion-chain-desktop
- asset-power-conversion-chain-mobile
comparisons:
- left: product-power-shelf-psu
  right: product-pmic-voltage-regulator
  conditions:
  - 比較在同一供電鏈中的轉換位置
  limitations:
  - 兩者位於不同轉換級，互補而非替代
- left: product-power-module
  right: product-pmic-voltage-regulator
  conditions:
  - 在相同板端電流與空間條件下比較
  limitations:
  - 模組化與分立方案依設計取捨，不能由單一效率數字排名
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

每一級轉換把電壓換到下一段需要的範圍。電源架或 PSU 處理系統供電，板端電壓調節把母線電壓降到晶片可用的低電壓高電流。

## 圖解

圖為原創功能示意；功率元件存在於每一級轉換中，圖中未逐一標出。

## 適用範圍

800VDC 是架構，不是 GPU 工作電壓；BBU、UPS 與設施儲能依位置與時間尺度分工，需按場址另查。
