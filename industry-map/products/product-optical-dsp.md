---
schema-version: research-v1
entity-id: product-optical-dsp
kind: product
name-zh: 光通訊 DSP
aliases:
- PAM4 DSP
summary: 在可插拔光模組中整合等化、重定時或 lane 映射，銜接主機 SerDes 與光收發電路。
reviewed: '2026-11-24'
definition: 光模組中處理高速電訊號的 DSP，可依型號重定時、等化、改變 lane 配置或整合 driver。
purpose: 讓主機電介面與光收發電路對接，並以訊號診斷協助模組驗證。
boundary: 本頁以機房內的 PAM4 光模組 DSP 為主。DSP 處理電訊號，雷射或調變器形成光訊號，交換 ASIC 決定封包轉送。
adoption-conditions:
- 核對主機與線側的 lane 數、lane 速率、FEC 分工、模組外型及埠模式。
- 依光元件核對 driver 與 TIA 介面、訊號容限、模組滿載功耗及診斷測試。
bottlenecks:
- 當 lane 速率提高，需共同驗證電通道損耗、光元件、誤碼率與熱設計。
- 整合 driver 可減少外部元件，配套光元件與測試流程須重新核對。
substitution-limits:
- 同速率 retimer 與不同 lane 速率的 gearbox 須各自匹配主機與線側介面。
- 100G-DR-LPO 的 DSP SerDes 與 RS-FEC 在主機端，須符合該規格電通道與光路條件。
claims:
- id: optical-dsp-signal-path
  statement: 資料中心用光模組 DSP 可對 PAM4 電訊號做等化或重定時。模組發送端仍須藉由雷射或調變器輸出光訊號，接收端由檢光器與接收前端提供電訊號。
  confidence: well-supported
  conditions:
  - 是否內建 driver、FEC 或改變 lane 配置依料號核對。
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-spica-gen2-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-spica-gen2-product-brief.pdf
    locator: Features、Description
    read-scope: 已讀 8×100G retimer、driver 整合及適用光元件。
    stance: supporting
    applicable-period: MV-CD822，2022-12 版
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: §§5.1–5.2、§§6.1–6.2
    read-scope: 已讀主機與模組的位置及線性模組的光收發分工。
    stance: supporting
    applicable-period: 100G-DR-LPO Revision 1.0
- id: eight-lane-retimer-vs-gearbox
  statement: Spica Gen2 MV-CD822 為 8×100 Gb/s PAM4 retimer，用於 800G 模組。Nova MV-CD432 以 16×100 Gb/s 主機電介面對應 8×200 Gb/s 線側，並整合調變器 driver，對應 1.6T OSFP-XD 單模模組。
  confidence: well-supported
  conditions:
  - 固定於兩款 product brief 的介面與外型。不同 lane 配置須另驗證主機及光路。
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-spica-gen2-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-spica-gen2-product-brief.pdf
    locator: Applications、Features
    read-scope: 已讀 800G 應用、lane 規格與分接。
    stance: supporting
    applicable-period: MV-CD822，2022-12 版
  - source-id: marvell-nova-mv-cd432-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-nova-1.6t-pam4-dsp-for-optical-transceiver-applications-product-brief.pdf
    locator: Applications、Features、Description
    read-scope: 已讀雙側 lane 映射、線側 driver、診斷與 FEC。
    stance: supporting
    applicable-period: MV-CD432，2023-03 版
- id: dove-driver-integration
  statement: Credo Dove 80X 家族涵蓋 800G 光模組 DSP。Dove 800 可搭配外接 driver，Dove 801 整合薄膜鈮酸鋰與 EML 調變器 driver，Dove 802 整合矽光子 driver。
  confidence: well-supported
  conditions:
  - 依各料號及光元件比較，產品頁供應能力不延伸到具名模組認證或出貨。
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-dove-800-product
    url: https://credosemi.com/products/optical-dsp/dove-800/
    locator: Dove 800 產品說明、About this product
    read-scope: 已讀 driver 分工、8:8 配置、主機及線側標示速率、封裝與測試功能。
    stance: supporting
    applicable-period: Dove 80X 頁面，2026-11-24 查閱
- id: port-speed-and-dsp-demand
  statement: 埠速率升級會改變 lane 速率或映射需求。DSP 光模組出貨增加時可能拉動模組內 DSP 用量，採用由主機承擔 DSP 與 FEC 的 LPO 則可能降低每條光鏈路的模組內 DSP 用量。
  confidence: inference
  conditions:
  - 追蹤實際埠數、兩側 lane 配置、模組架構與平台認證。總頻寬不能直接換算晶片顆數。
  reviewed: '2026-11-24'
  evidence:
  - source-id: marvell-nova-mv-cd432-brief
    url: https://www.marvell.com/content/dam/marvell/en/public-collateral/dsp/marvell-nova-1.6t-pam4-dsp-for-optical-transceiver-applications-product-brief.pdf
    locator: Features、Description
    read-scope: 已讀 1.6T 模組的 lane 映射與 DSP 晶片交付。
    stance: supporting
    applicable-period: MV-CD432，2023-03 版
  - source-id: lpo-msa-100g-dr
    url: https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf
    locator: 摘要、§5.6、§7.2
    read-scope: 已讀主機 DSP SerDes、RS-FEC 與電通道。
    stance: counter
    applicable-period: 100G-DR-LPO Revision 1.0
gaps:
- status: not-obtained
  reason: 未取得同一光路、相同負載與溫度下的晶片功耗、雙端連線功耗、BER 與成本，無法給出跨廠牌排名。
- status: not-public
  reason: 所讀產品資料未揭露具名客戶、指定模組的實際採用或料號分項收入。
---

## 定義與用途

在[資料中心交換器](/next?focus=product-datacenter-switch)或網卡的可插拔光埠，主機 SerDes 先把資料送進[光收發模組](/next?focus=product-optical-transceiver)。發送方向由模組 DSP 處理高速電訊號，再經 driver 驅動調變器或雷射。接收方向則由檢光器把光轉成電，跨阻放大器（TIA）把微小電流轉成電壓，再交由 DSP 補償失真並重定時。交換 ASIC 負責封包轉送與主機端介面。模組 DSP 的工作範圍取決於光鏈路的介面與晶片設計。

等化補償通道對訊號的影響，重定時恢復取樣時序，gearbox 進一步在不同 lane 速率和數量間映射資料。FEC 的位置要另外核對。Nova 可做串接 FEC，100G-DR-LPO 則要求主機端提供 RS-FEC。來源見下方產品主張與規格。

## 採用條件與限制

### 先對齊雙側 lane 與光元件

- **Marvell Spica Gen2 MV-CD822**（2022-12）。8×100 Gb/s PAM4 retimer，面向 800G QSFP-DD／OSFP，可對應 1×800G、2×400G 或 8×100G Ethernet 分接。產品簡介列出 EML、矽光子與 VCSEL 應用。
- **Marvell Nova MV-CD432**（2023-03）。主機端 16×100 Gb/s，線側 8×200 Gb/s，面向 1.6T OSFP-XD 單模模組。可用的分接仍須核對主機埠模式、模組與遠端光介面。
- **Credo Dove 800**（2026-11-24 查閱）。主機與線側各 8 lane，規格表每 lane 標示 100G。Dove 800 與 Spica Gen2 都是 800G 模組的候選，仍需對齊主機、光路規格及 driver 配置。型錄未提供同條件功耗、誤碼率或成本。

整合調變器 driver 可影響外部 IC 數量、PCB 走線與模組裝配，選型還需核對光元件與接收端 TIA。診斷與分接也是驗證成本來源。例如 Nova 支援測試序列與 loopback，可協助將主機側或線側分開驗證。選型時把 IC 功耗、整顆模組功耗和兩端連線功耗分開，並核對目標誤碼率及測試條件。

### LPO 如何改變分工

100G-DR-LPO Rev 1.0 表 12 定義 0.5–500 m 的單模光路範圍。主機須提供符合規範的 DSP SerDes 與 RS-FEC，§7.2 的電通道在 26.56 GHz 上限為 16 dB。是否能用線性模組取代既有 DSP 模組，要看兩端主機及模組能否在指定走線和光路條件下通過互通驗證。這個規格的 100 Gb/s 每 lane 條件不可直接套到 200 Gb/s 每 lane。

## 供應角色與公司

[博通](/next?focus=company-avgo) BCM85822 的 800GbE 模式為 8×106 至 4×226 Gb/s，須按 8:4 gearbox 配置查光元件與 FEC。

屬於[光通訊 DSP](/next?focus=role-optical-dsp)。[邁威爾](/next?focus=company-mrvl)的 Spica／Nova 與 [Credo](/next?focus=company-crdo) 的 Dove 都有公開產品證據。上述交付是 DSP 晶片，後段仍需由模組供應商整合光元件、接頭與散熱，並完成整顆模組驗證。

### 需求如何傳到 DSP

**Inference。** 當 800G 或 1.6T 的上線埠數增加，且採用模組內 DSP 的可插拔方案，會增加 DSP 型光模組的交付需求。若只是用更快的單埠整併連線，或新增埠轉用 LPO，DSP 出貨可能低於依頻寬增幅推估的數量。追蹤實際交換器與網卡埠數、lane 速率、合格料號與主機驗證結果，再判斷影響哪一代產品。公司產品頁可確認設計能力，客戶採用與出貨仍要另找證據。
