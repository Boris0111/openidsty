---
schema-version: research-v1
entity-id: concept-package-layers
kind: concept
name-zh: 封裝的四個層次
aliases:
- interposer vs substrate
- 中介層與載板
summary: 晶片、中介層、封裝載板與系統板各負責不同距離的連線。
reviewed: '2026-10-18'
definition: 把 die 與 HBM、矽中介層或 RDL、IC 封裝載板、系統電路板分成四層，說明各層的連線責任。
scope: 適用 2.5D 類先進封裝的功能分層說明，不代表特定平台的尺寸、層數或良率。
related-ids:
- application-chip-integration
- product-2p5d-interposer-package
- product-abf-substrate
- product-server-multilayer-pcb
- product-hbm-stack
diagram-assets:
- asset-package-layers-desktop
- asset-package-layers-mobile
comparisons:
- left: product-2p5d-interposer-package
  right: product-abf-substrate
  conditions:
  - 比較同一封裝中的連線層次
  limitations:
  - 兩者是上下相疊的不同層，不能以產能或單價互相排名
- left: product-abf-substrate
  right: product-server-multilayer-pcb
  conditions:
  - 比較封裝內與系統板的路由責任
  limitations:
  - 載板與系統板材料、線寬與供應商不同，不能互相替代
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

越靠近晶片，連線越密、距離越短。中介層讓晶片與 HBM 之間有大量短距離連線；封裝載板把這些訊號與供電整理後接到系統電路板。

## 圖解

圖為原創功能示意，由左到右是由晶片往外的層次；方塊大小不代表實際尺寸或價值。

## 適用範圍

這張圖只說明分層。CoWoS-S／R／L 等互連結構、玻璃核心或面板化方案各有不同條件，需按指定平台另查。
