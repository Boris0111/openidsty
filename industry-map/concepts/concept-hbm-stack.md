---
schema-version: research-v1
entity-id: concept-hbm-stack
kind: concept
name-zh: HBM 堆疊與伺服器 DRAM
aliases:
- HBM vs DIMM
summary: HBM 疊在加速器旁，伺服器 DRAM 插在主機板上，用途與封裝都不同。
reviewed: '2026-10-18'
definition: 說明 HBM 由多層 DRAM 與 base die 組成並與加速器共同封裝，伺服器 DRAM 則以模組插在主機板供 CPU 使用。
scope: 適用記憶體類型與位置的功能說明，不代表特定世代的層數、容量或供應商份額。
related-ids:
- application-ai-memory
- product-hbm-stack
- product-server-dram-module
- product-2p5d-interposer-package
diagram-assets:
- asset-hbm-stack-desktop
- asset-hbm-stack-mobile
comparisons:
- left: product-hbm-stack
  right: product-server-dram-module
  conditions:
  - 比較在 AI 伺服器中的位置與用途
  limitations:
  - 兩者服務不同處理器與頻寬需求，不能直接互替
claims: []
gaps:
- status: not-researched
  reason: 圖解為功能示意，未核對特定平台的規格、尺寸或良率。
---

## 中文解釋

HBM 把多層 DRAM 疊在一顆邏輯 base die 上，再和加速器一起封裝，換取很高的頻寬。伺服器 DRAM 模組則插在主機板上，提供 CPU 的主記憶體容量。

## 圖解

圖為原創功能示意。左三欄是 HBM 由堆疊到封裝的組成，虛線右側是對照用的主記憶體位置；箭頭表示組成順序，不表示供應交易。

## 適用範圍

HBM 的 stack 與 base die 可能由不同製程與廠商分工；各世代規格與認證需按 JEDEC 條文與客戶平台另查。
