---
schema-version: research-v1
entity-id: concept-network-tiers
kind: concept
name-zh: AI 網路的三個距離層
aliases:
- scale-up
- scale-out
summary: 機櫃內、機櫃間與跨機房的連線，選用的介質與元件不同。
reviewed: '2026-10-18'
definition: 把 AI 叢集網路分成 scale-up（機櫃內加速器互連）、scale-out（機櫃間）與跨機房三層。
scope: 適用網路分層的研究分類，不代表任何平台的實際拓樸、埠速或功耗。
related-ids:
- application-ai-networking
- product-ethernet-switch-asic
- product-optical-transceiver
- product-active-electrical-cable
- product-retimer
- product-optical-dsp
diagram-assets:
- asset-network-tiers-desktop
- asset-network-tiers-mobile
comparisons:
- left: product-active-electrical-cable
  right: product-optical-transceiver
  conditions:
  - 在相同距離層、協議與錯誤率要求下比較
  limitations:
  - 取捨需含整條通道的距離、耗電與維修；不能宣稱一方普遍勝出
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

距離越短越常用銅纜與主動電纜，距離拉長後改用光模組。交換晶片、DSP、光元件與模組在不同層分工。

## 圖解

圖為原創分層示意，由左到右距離增加；介質標示是常見選項，不是規定。

## 適用範圍

CPO、LPO 與可插拔模組的取捨要按端點、模組與系統互通另行核對，本圖不代表任何路線已全面取代另一條。
