---
schema-version: research-v1
entity-id: concept-test-insertions
kind: concept
name-zh: 晶片測試的插入點
aliases:
- wafer sort
- final test
- SLT
summary: 晶圓測試、成品測試與系統層測試各找不同的失效。
reviewed: '2026-10-18'
definition: 說明晶片在晶圓階段、封裝後與系統環境中分別測試，以及各階段使用的接觸介面與設備。
scope: 適用測試流程分工的說明，不代表特定產品的測試覆蓋率或測試時間。
related-ids:
- application-chip-test
- product-probe-card
- product-test-socket
- product-ate-system
- product-chip-test-service
diagram-assets:
- asset-test-insertions-desktop
- asset-test-insertions-mobile
comparisons:
- left: product-probe-card
  right: product-test-socket
  conditions:
  - 比較不同測試階段的接觸介面
  limitations:
  - 兩者服務晶圓與封裝後不同階段，不能互替
- left: product-ate-system
  right: product-chip-test-service
  conditions:
  - 比較設備銷售與委外服務
  limitations:
  - 收入單位不同，不能互相加總
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

晶圓測試在封裝前篩出不良 die；成品測試確認封裝後功能；系統層測試在接近實際使用的環境補找供電、熱與韌體相關失效。

## 圖解

圖為原創流程示意，由左到右是測試先後；並非每個產品都經過所有階段。

## 適用範圍

SLT 補充系統環境驗證，不能直接替代全部 ATE 或封裝前篩選；chiplet 與 HBM 的測試覆蓋需按產品另查。
