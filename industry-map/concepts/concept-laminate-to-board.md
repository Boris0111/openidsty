---
schema-version: research-v1
entity-id: concept-laminate-to-board
kind: concept
name-zh: 從板材到電路板
aliases:
- CCL vs PCB
summary: 銅箔基板是材料，電路板是加工後的成品，供應商與驗證項目不同。
reviewed: '2026-10-18'
definition: 說明銅箔基板（CCL）經層疊、鑽孔與電鍍等加工成為高多層伺服器電路板。
scope: 適用材料與成板分工的說明，不代表特定平台的層數、損耗值或材料等級。
related-ids:
- application-server-assembly
- product-high-speed-ccl
- product-server-multilayer-pcb
diagram-assets:
- asset-laminate-to-board-desktop
- asset-laminate-to-board-mobile
comparisons:
- left: product-high-speed-ccl
  right: product-server-multilayer-pcb
  conditions:
  - 比較同一塊板的材料與加工責任
  limitations:
  - 板材性能需經成板加工驗證，不能只看材料等級判斷成板良率
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

高速訊號的損耗同時受板材與加工影響。CCL 廠提供材料，PCB 廠負責層疊、對位與鑽孔，兩者需共同符合阻抗與可靠度要求。

## 圖解

圖為原創製程分工示意，由左到右是材料到成品；不表示所有板都經相同步驟。

## 適用範圍

flyover 線纜或光互連可能改變板上走線，但不能由新技術發表推定板材或成板需求消失。
