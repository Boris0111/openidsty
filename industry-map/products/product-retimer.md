---
schema-version: research-v1
entity-id: product-retimer
kind: product
name-zh: "重定時與橋接晶片"
aliases:
- "retimer"
summary: "重新取樣並發送 PCIe／CXL 等高速鏈路訊號的晶片，延伸系統可用通道。"
definition: "主動接收、等化、恢復時脈與資料，再從另一側輸出訊號的晶片。此頁以維持 PCIe／CXL 協定的 retimer 為主。"
purpose: "讓 CPU 至 NIC、GPU、SSD 或 CXL 裝置的高速鏈路跨過較長走線及連接器。"
boundary: "兩側仍使用相同鏈路協定。路由封包、協定轉換與機櫃間 Ethernet AEC 另有交付。"
adoption-conditions:
- "按 PCIe／CXL 世代、lane 寬度與每段插入損耗驗證，核對主機、端點及韌體。"
bottlenecks:
- "兩側的通道損耗、連接器反射、板面和散熱限制，以及 link training 與診斷。"
substitution-limits:
- "低損耗 PCB 或較短走線有機會省掉 retimer。相同接頭的 Ethernet AEC 仍須符合各自協定。"
reviewed: "2026-11-24"
claims:
- id: retimer-physical-link
  statement: "PCIe retimer 可放在 root complex 與 endpoint 之間，用 CDR 恢復時脈與資料並重新發送，將通道分段；redriver 對輸入加補償但沒有此 CDR 功能。"
  confidence: well-supported
  conditions:
  - "兩側預算分開。距離由走線材料、頻率、線材與接頭共同決定。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: astera-aries-retimer-2024
    url: https://www.asteralabs.com/wp-content/uploads/2024/03/2402_Astera_Labs-Aries_Smart_DSP_Retimer_Family-Product_Brief.pdf
    locator: "Benefits and Features、Description、Product Family Table"
    read-scope: "已讀 root complex／endpoint、通道擴充、速率與晶片交付。"
    stance: supporting
    applicable-period: "Aries Portfolio Brief，2024-02"
  - source-id: astera-retimer-technical-faq
    url: https://www.asteralabs.com/resources/faqs/
    locator: "PCIe FAQs：Redriver vs Retimer、Retimer placement"
    read-scope: "已讀 CDR、兩段插入損耗與佈線評估。"
    stance: supporting
    applicable-period: "PCIe 5.0／6.x 相關問答，2026-11-24 查閱"
- id: aries-toucan-application
  statement: "Astera Aries 家族列 PCIe 6.x 64 GT/s、x8 或 x16 版本。Credo 2026-08-31 公告 Toucan Gen6x16 完成 PCI-SIG 6.x 64 GT/s retimer 相容性測試。"
  confidence: well-supported
  conditions:
  - "比較限同世代及相同 lane 數；供應商規格與特定測試的合格、客戶採用分別認定。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: astera-aries-retimer-2024
    url: https://www.asteralabs.com/wp-content/uploads/2024/03/2402_Astera_Labs-Aries_Smart_DSP_Retimer_Family-Product_Brief.pdf
    locator: "Benefits and Features、Description、Product Family Table"
    read-scope: "已讀 root complex／endpoint、通道擴充、速率與晶片交付。"
    stance: supporting
    applicable-period: "Aries Portfolio Brief，2024-02"
  - source-id: credo-toucan-gen6x16-pcisig-announcement
    url: https://investors.credosemi.com/news-events/news/news-details/2026/Credos-Toucan-PCIe-Retimer-Achieves-PCI-Express-Compliance-and-Joins-PCI-Express-6-x-Integrators-List/default.aspx
    locator: "Key points、Purpose-Built for Next-Gen Platforms"
    read-scope: "已讀 x16、64 GT/s 測試與 PILOT 診斷。"
    stance: supporting
    applicable-period: "2026-08-31，Toucan Gen6x16"
- id: retimer-board-demand
  statement: "新平台速度提高、走線延長且無法在原損耗預算內通過，才可能增加設計中的 retimer 用量。"
  confidence: inference
  conditions:
  - "如果端點更靠近或改用低損耗材料，可能維持無 retimer 的通道；觀察拓樸、實測眼圖及可驗證板卡。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: astera-retimer-technical-faq
    url: https://www.asteralabs.com/resources/faqs/
    locator: "PCIe FAQs：Redriver vs Retimer、Retimer placement"
    read-scope: "已讀 CDR、兩段插入損耗與佈線評估。"
    stance: supporting
    applicable-period: "PCIe 5.0／6.x 相關問答，2026-11-24 查閱"
  - source-id: astera-aries-retimer-2024
    url: https://www.asteralabs.com/wp-content/uploads/2024/03/2402_Astera_Labs-Aries_Smart_DSP_Retimer_Family-Product_Brief.pdf
    locator: "Benefits and Features、Description、Product Family Table"
    read-scope: "已讀 root complex／endpoint、通道擴充、速率與晶片交付。"
    stance: supporting
    applicable-period: "Aries Portfolio Brief，2024-02"
gaps:
- status: not-obtained
  reason: "未取得兩家 x16 晶片在同一 Gen6 板卡、同通道、同環境下的 BER、功耗、延遲與 BOM。"
- status: not-public
  reason: "已讀資料未拆分各 retimer 料號的特定客戶、平台用量或收入。"
---

## 定義與用途

CPU 的 PCIe root complex 連到 GPU、NVMe SSD 或網路介面卡時，電訊號可能經過板上走線、riser 或背板。Retimer 在通道中間等化並恢復時脈與資料（CDR），再驅動另一段。接收器與發送器要分別滿足兩個通道的損耗及訓練要求。產品分類中的橋接若涉及協定轉換，要看該橋接料號的功能與驗證；此處列舉的 PCIe retimer 維持 PCIe 鏈路。

## 採用條件與限制

### 速率和距離要分開驗證

Astera Aries 2024-02 簡介列 Gen6 64 GT/s 及 x8／x16 版本，並稱可於 64 GT/s 延伸 36 dB；該值是型錄的損耗描述，不能換算成固定公尺數。走線、過孔、接頭與線纜不同，要在目標頻率逐段量測並留出溫度、量產變異的容限。新增 retimer 也要付出晶片、配電、散熱與平台驗證成本。

### 何時可用較簡單的通道

較短走線或較低損耗 PCB 有機會讓兩端直接連通；redriver 可補償衰減，遇到需重建時序及資料的通道則要評估 retimer。[Ethernet AEC](/next?focus=product-active-electrical-cable)與[Ethernet 光模組](/next?focus=product-optical-transceiver)是 NIC 至交換器的方案，不能直接接替板內 PCIe retimer。若主機側改成光傳輸，應另核同 PCIe 世代的光電端點、實際通道資格與額外功耗；未取得可和此處型號同條件比較的資料。

## 供應角色與公司

PCI-SIG 2026-07-31 清單以 PCIe 6.x 64 GT/s、x16 登錄 Credo CPR61664 與 Astera PT6162。認證限指定料號和速率，兩家的散熱、系統韌體與實際出貨仍各自核對。

[邁威爾](/next?focus=company-mrvl) Alaska P MV-CHP10160 型錄列 PCIe Gen6 x16 64 GT/s 與 CXL 3.x。系列採用公告見公司頁。

屬於[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)。[Astera Labs](/next?focus=company-alab)的 Aries 提供 PCIe／CXL retimer 晶片與 COSMOS 診斷。[Credo](/next?focus=company-crdo)的 Toucan 提供同類晶片及 PILOT 診斷，2026-08-31 公告限 Gen6x16 的 64 GT/s 相容性測試結果。採購比較須固定 lane 寬、通道及軟體需求，再查各料號資格、板卡驗證和出貨。

### 需求如何傳到晶片

**Inference。** 若新 GPU 平台提高 PCIe 世代，又有較長的路徑或更多連接器，通道不足才增加 retimer 設計機會。若重新配置 GPU、NIC 與 switch 位置或升級 PCB，原設計可少用甚至不用 retimer。追蹤 PCIe 速率、拓樸、板卡與料號的合格狀態，再估算每台需求。
