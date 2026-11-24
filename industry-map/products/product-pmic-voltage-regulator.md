---
schema-version: research-v1
entity-id: product-pmic-voltage-regulator
kind: product
name-zh: "電源管理與電壓調節晶片"
aliases:
- "PMIC"
- "VRM"
- "PWM controller"
summary: "板端監控電壓並控制一相或多相功率級的晶片。"
definition: "板端監控電壓並控制一相或多相功率級的晶片。"
purpose: "將處理器要求的供電狀態轉為相位控制、回授與保護。"
boundary: "功率級開關與電感承受和轉換負載電力；整合模組包含更多器件。"
adoption-conditions:
- "確認 VID／AVS、PMBus、電流回授、啟停時序與保護。"
bottlenecks:
- "瞬態掉壓、相間分攤與熱。"
substitution-limits:
- "更換 controller 或 power stage 需重新驗證 PWM、電氣與韌體。"
reviewed: "2026-11-24"
claims:
- id: board-controller-versus-stage
  statement: "MP2965 是雙迴路數位 PWM controller。典型 6+1 電路有外接功率級、每相電感和回授。"
  confidence: well-supported
  conditions:
  - "12 V 為典型功率端應用。控制器偏壓、功率級輸入與核心電壓須分別核對。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: mps-mp2965-datasheet
    url: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/EN/sku/MP2965
    locator: "Description、Figure 2: PVID 6+1 Application、Protection"
    read-scope: "查兩路多相控制，PWM、電流回授、外接功率級及電感位置。"
    stance: supporting
    applicable-period: "MP2965 datasheet"
- id: controller-compatibility
  statement: "Renesas RAA228228 圖示以 12 V 供外部智慧功率級，展示 16+4 相設定。兩家控制器須對齊負載介面、相數和保護需求才可比較。"
  confidence: well-supported
  conditions:
  - "相數示意不代表在同一熱邊界下有相同總電流。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: renesas-raa228228-datasheet
    url: https://www.renesas.com/en/document/sds/raa228228-short-form-datasheet
    locator: "p.3 Figure 2 16+4 Smart Power Stage"
    read-scope: "核對 12 V 功率端、雙路 PWM 與分離功率級。"
    stance: supporting
    applicable-period: "Rev.2.0，2021-05-17"
  - source-id: mps-mp2965-datasheet
    url: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/EN/sku/MP2965
    locator: "Description、Figure 2: PVID 6+1 Application、Protection"
    read-scope: "查兩路多相控制，PWM、電流回授、外接功率級及電感位置。"
    stance: supporting
    applicable-period: "MP2965 datasheet"
- id: board-controller-demand
  statement: "如果同一架構的處理器功耗與瞬態需求提高，可能增加每路相數、每相功率級電流或輸出電容。"
  confidence: inference
  conditions:
  - "既有 controller 還有可用相數、電壓提高或改成整合模組時，控制晶片數量可維持或下降。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: mps-mp2965-datasheet
    url: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/EN/sku/MP2965
    locator: "Description、Figure 2: PVID 6+1 Application、Protection"
    read-scope: "查兩路多相控制，PWM、電流回授、外接功率級及電感位置。"
    stance: supporting
    applicable-period: "MP2965 datasheet"
  - source-id: renesas-raa228228-datasheet
    url: https://www.renesas.com/en/document/sds/raa228228-short-form-datasheet
    locator: "p.3 Figure 2 16+4 Smart Power Stage"
    read-scope: "核對 12 V 功率端、雙路 PWM 與分離功率級。"
    stance: supporting
    applicable-period: "Rev.2.0，2021-05-17"
gaps:
- status: not-obtained
  reason: "未取得跨廠同核心、同相數、同電流步階的瞬態、效率、板面積及成本。"
- status: not-public
  reason: "來源未揭露指定加速器採用、客戶、料號出貨或收入。"
---

## 定義與用途

多相 buck controller 讀取輸出電壓和各相電流，據以控制 PWM。外接 power stage 承受開關電流，輸出電感與電容負責平滑波形。典型位置是 12 V 中間匯流排之後、CPU／GPU／ASIC 負載之前。

## 規格與成本

MP2965 的 6+1 圖例以一顆 controller 掌管兩路輸出，各相另接 Intelli-Phase 與電感。比較控制器時先問各相能帶多少、輸出允許多少壓降、負載上升多快、溫度多高；PCB 銅損、磁件和電容也納入總成本。

## 採用條件與限制

相容的 PWM／VID、感測方式、故障反應及上電時序是替換前提。必要時重測 OCP／OVP、熱感測與負載步階。若選用[整合 power module](/next?focus=product-power-module)，板上仍要確認溫升、外接元件及控制介面。

## 供應角色與公司

[板端電源轉換](/next?focus=role-board-power-conversion)下，[芯源系統](/next?focus=company-mpwr)交付 MP2965 控制晶片與可搭配的功率級；Renesas RAA228228 與 ISL99390 系列也是控制與功率級分離的比較例。[Vicor](/next?focus=company-vicr)的 PRM／VTM 另列整合模組。

## 需求如何傳導

推論：負載變大可能增加每路相數或功率級規格，應追蹤核心 rail 的瞬態驗證、每相電流與架構。若原控制器留有餘裕，或系統改用內建 controller 的模組，分立 controller 用量可能不變或下降。
