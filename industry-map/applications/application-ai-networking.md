---
schema-version: research-v1
entity-id: application-ai-networking
kind: application
name-zh: AI 叢集網路
aliases:
- AI networking
summary: 連接加速器、伺服器與機房的電訊號與光通訊路徑。
reviewed: '2026-10-18'
definition: 連接加速器、伺服器與機房的電訊號與光通訊路徑。
purpose: 先分 scale-up、scale-out 與跨機房，再拆交換晶片、DSP、連接晶片、光元件、模組與系統。
boundary: 交換晶片、DSP、電訊號連接晶片、光晶片、光模組與交換器系統是不同交付；管理介面、電氣通道與光學傳輸是不同證據範圍。
adoption-conditions:
- 依協議、拓樸、距離、錯誤修正、管理與熱條件驗證整條鏈路
bottlenecks:
- 光／電測試點、雷射與散熱整合及維修流程可能限制採用
substitution-limits:
- 銅、可插拔、LPO 與 CPO 需分別核對端點與系統互通，不能宣稱普遍優勝
claims: []
gaps:
- status: not-researched
  reason: 代表公司依既有環節角色列出；各公司在此應用的產品能力、客戶與收入尚待逐家深研。
---

## 定義與用途

連接加速器、伺服器與機房的電訊號與光通訊路徑。先分 scale-up、scale-out 與跨機房，再拆交換晶片、DSP、連接晶片、光元件、模組與系統。對應既有環節：[網通與光通訊](/next?focus=segment-networking)。

可比較的供應角色：[交換器晶片](/next?focus=role-switch-silicon)、[光通訊 DSP](/next?focus=role-optical-dsp)、[電訊號連接晶片與主動線材](/next?focus=role-electrical-connectivity)、[光通訊雷射與光電晶片](/next?focus=role-optical-chip)、[光收發模組](/next?focus=role-optical-module)、[資料中心交換器系統](/next?focus=role-switch-system)。

## 採用條件與限制

分類依「是否扮演可彼此替換的供應角色」切分；代表公司依既有環節角色列出，不代表已核對產品能力、客戶或收入。
