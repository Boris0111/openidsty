---
schema-version: research-v1
entity-id: product-active-electrical-cable
kind: product
name-zh: "主動電纜"
aliases:
- "AEC"
summary: "兩端有主動電路的短距離銅纜，以整條線組交付給符合介面的乙太網路埠。"
definition: "在一體式銅纜插頭整合主動訊號處理的 Ethernet 線組，依料號支援直連或分接。"
purpose: "在機櫃內或相鄰機櫃的 NIC／交換器之間連接高速電訊號。"
boundary: "線纜、插頭及主動電子組成成品。單獨的 retimer／SCM 與可插拔光模組分開判斷。"
adoption-conditions:
- "核對兩端埠外型、lane 模式、FEC、CMIS 版本、線長與滿載外殼溫度。"
bottlenecks:
- "線徑與線長帶來的損耗、彎折空間、接頭的電熱預算及平台互通。"
substitution-limits:
- "被動 DAC 適用可達同一通道條件的短距離。可插拔光模組配光纖可覆蓋較遠路徑，但需對齊端點速率及管理功能。"
reviewed: "2026-11-24"
claims:
- id: aec-endpoint-path
  statement: "Credo 800G SPAN OSFP AEC 是用於相鄰機櫃之間的主動銅線組。Astera Taurus SCM 裝入主動銅纜組件，可用於伺服器 NIC 至 ToR 或交換器間連線。"
  confidence: well-supported
  conditions:
  - "線組內的 SCM 交付和成品採購分開。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 3–7 m、8 lane、106.25 Gb/s PAM4 與 0–70 °C 外殼溫度。"
    stance: supporting
    applicable-period: "CAC8XXXX1A1B-C1-HW，REV 100924"
  - source-id: astera-taurus-scm-brief
    url: https://www.asteralabs.com/wp-content/uploads/2025/05/PB_Taurus_Ethernet_Smart_Cable_Modules.pdf
    locator: "Applications、Product Family Information、Description"
    read-scope: "已讀 800G 兩款 SCM、3 m 30 AWG、可由多家線材商整合。"
    stance: supporting
    applicable-period: "Taurus EM800-QDX-A／EM800-EPS-A，2026-11-24 查閱"
- id: aec-length-profile
  statement: "Credo SPAN CAC8XXXX1A1B-C1-HW 為 OSFP 至 OSFP-RHS、8×106.25 Gb/s PAM4，列 3–7 m；800G SHIFT DD 至 2×DD 分接線組列 1–3 m，400G 端支援 4 或 8 lane 模式。"
  confidence: well-supported
  conditions:
  - "各自按料號、接頭與速率工作。BER 表數值的測試圖樣是 QPRBS31，不能視為生產環境結果。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 3–7 m、8 lane、106.25 Gb/s PAM4 與 0–70 °C 外殼溫度。"
    stance: supporting
    applicable-period: "CAC8XXXX1A1B-C1-HW，REV 100924"
  - source-id: credo-800g-shift-dd-breakout-brief
    url: https://credosemi.com/wp-content/uploads/Credo_AEC_800G_SHIFT_DD-2xDD_Product_Brief_2025Sept26.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 800G 分接兩支 400G、lane 模式及 1–3 m。"
    stance: supporting
    applicable-period: "SHIFT DD to 2×DD，2025-09 產品簡介"
- id: aec-optical-alternative
  statement: "同是 800G 仍須區分直連、分接和傳輸介質。Arista 列 800G 直連 AEC 為 1–3 m，Cisco QDD-2X400G-FR4 的單模光路為 2 km 並支援 2×400G 分接。"
  confidence: well-supported
  conditions:
  - "僅在兩端埠均可用、指定模式一致的短距情境比較雙端功耗、誤碼率與總成本。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: arista-800g-cables-qa
    url: https://www.arista.com/assets/data/pdf/Datasheets/Arista-800G_Optics_FAQ.pdf
    locator: "p.3"
    read-scope: "參照已讀 800G 直連 AEC 料號與長度。"
    stance: supporting
    applicable-period: "Arista 04-0046-07，2026-09"
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "Optical specifications；QDD-2X400G-FR4 段落"
    read-scope: "參照已讀 2 km 單模光路、分接與模組交付。"
    stance: supporting
    applicable-period: "2026-09-21 版"
- id: aec-cabling-demand
  statement: "同機櫃或相鄰機櫃的 800G 合格短距埠增加，可帶動對應 AEC 線組及其整合元件需求。"
  confidence: inference
  conditions:
  - "追蹤實際鋪線、埠模式與合格長度；保留透過 DAC、光纖或拓樸重排替換的情境。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: credo-800g-shift-dd-breakout-brief
    url: https://credosemi.com/wp-content/uploads/Credo_AEC_800G_SHIFT_DD-2xDD_Product_Brief_2025Sept26.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 800G 分接兩支 400G、lane 模式及 1–3 m。"
    stance: supporting
    applicable-period: "SHIFT DD to 2×DD，2025-09 產品簡介"
  - source-id: credo-800g-span-osfp-brief
    url: https://credosemi.com/wp-content/uploads/2024/10/Credo-HiWire-SPAN-AEC-800G-CAC8XXXX1A1B-C1-Product-Brief.pdf
    locator: "Key Features、Product Selections"
    read-scope: "已讀 3–7 m、8 lane、106.25 Gb/s PAM4 與 0–70 °C 外殼溫度。"
    stance: supporting
    applicable-period: "CAC8XXXX1A1B-C1-HW，REV 100924"
  - source-id: cisco-qsfp-dd800-datasheet
    url: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/qsfp-dd800-transceiver-modules-ds.html
    locator: "Optical specifications；QDD-2X400G-FR4 段落"
    read-scope: "參照已讀 2 km 單模光路、分接與模組交付。"
    stance: supporting
    applicable-period: "2026-09-21 版"
gaps:
- status: not-obtained
  reason: "未取得同埠模式、相同佈線長度／溫度及損耗條件下的兩端功耗、BER、維修與成本。"
- status: not-public
  reason: "已讀型錄未提供各料號的具名客戶、出貨及收入。"
---

## 定義與用途

在伺服器 NIC 接 ToR 或相鄰交換器間，AEC 用銅線傳輸，並在插頭端以主動電路處理高速訊號。直連線的兩端服務同一條鏈路；分接線須與交換器的 breakout 埠模式配合，將高速端接到多個低一級速率的端點。主機板上的[PCIe retimer](/next?focus=product-retimer)與線組內的 Ethernet 主動電路各有適用介面。

## 採用條件與限制

### 線長由料號與端點決定

- **Credo 800G SPAN**。OSFP 至 OSFP-RHS，8×106.25 Gb/s PAM4。3–7 m，外殼 0–70 °C，CMIS 5.1，REV 100924。
- **Credo 800G SHIFT DD 至 2×DD**。QSFP-DD800 Type 2；400G 端依模式用 4 或 8 lane。1–3 m，對照 2025-09 料號表。
- **Taurus EM800-QDX-A／EM800-EPS-A**。可整合至 800G QSFP-DD／OSFP 線組。800G 範例為 3 m、30 AWG，指定 SCM 參考配線。

距離越長，銅通道的插入損耗、線束彎折與線徑更可能限制機櫃佈局。線纜的電路也會用到兩端的供電及散熱預算。以同一端點和環境溫度核對 FEC 前後誤碼率、線材半徑、滿載功耗與裝配工時，再估材料及維護成本。Credo 的 BER 是 QPRBS31 測試條件。

### 同一對端點再比較光與電

被動 DAC 可在損耗合格的近距離省去線端主動電路。AEC 可延伸可用銅距。若佈線超過所選料號、須經配線架或跨不同機房，應評估光纖方案。Cisco 2×400G FR4 的 2 km 是單模光路規格，與 SHIFT 的銅線長度分屬不同介面。即使連線只有 3 m，若兩端無法開出相同的 2×400G 模式，也無法直接替換。

## 供應角色與公司

[邁威爾](/next?focus=company-mrvl) Alaska A MV-CHA180C0C 是 800G AEC 用 8:8 線端 PAM4 DSP，線纜供應者交付完整線組。

屬於[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)。[Credo](/next?focus=company-crdo)交付 SPAN、SHIFT 等完整 AEC 線組。[Astera Labs](/next?focus=company-alab)的 Taurus SCM 型錄描述線纜廠整合用的主動模組及診斷功能；比較整條線組前還須核對實際線纜組件的供應者及平台驗證。

### 需求如何傳到線組

**Inference。** 同一機櫃中的合格 800G NIC／ToR 連線若增加，且實際佈線通過指定 AEC 長度和埠條件，才拉動線組需求。裝置靠近後可能使用 DAC；跨櫃走線變長可能改用[光模組與光纖](/next?focus=product-optical-transceiver)。追蹤連線長度分布、各埠的 breakout 規劃與已通過驗證的線組料號。
