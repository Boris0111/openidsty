---
segment: power-discrete
name_zh: 功率與分離式元件
layer: semiconductor
position: 2
market_coverage:
  tw: present
  us: present
  led_by: [DE]
companies:
  - ticker: "IFX.DE"
    name_zh: 英飛凌
    role: 功率半導體主要供應者
    tier: 1
  - ticker: "ON"
    name_zh: 安森美
    role: 功率半導體與碳化矽
    tier: 1
  - ticker: "WOLF"
    name_zh: Wolfspeed
    role: 碳化矽基板與元件
    tier: 2
  - ticker: "4919.TW"
    name_zh: 新唐
    role: 微控制器與電源管理
    tier: 2
  - ticker: "2481.TW"
    name_zh: 強茂
    role: 分離式元件
    tier: 2
  - ticker: "3016.TW"
    name_zh: 嘉晶
    role: 磊晶片
    tier: 3
  - ticker: "3707.TWO"
    name_zh: 漢磊
    role: 碳化矽與氮化鎵代工
    tier: 3
upstream: [foundry]
downstream: [power]
themes: []
kpis:
  - 寬能隙元件營收佔比
  - 伺服器電源應用營收比重
  - 產能利用率
signals:
  - 高壓直流架構對元件規格的要求變動
  - 碳化矽與氮化鎵在伺服器供電的導入進度
downstream-relations:
  power:
    kind: supply
    summary: 功率與分離式元件至電源與供電架構：功率開關、控制及電力轉換所需元件子角色。
    items:
    - 功率開關、控制及電力轉換所需元件子角色
    dependencies:
    - 額定電壓電流、損耗、散熱及保護控制
    conditions:
    - 元件在實際拓樸、溫度與安全條件完成設計驗證
    confidence: inference
    evidence: []
    gaps:
    - 缺少指定 PSU／DC-DC／高壓架構的元件 BOM 與認證；Si、SiC、GaN 不能僅憑材料名互替。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 功率切換、整流、保護及控制元件、磊晶與特殊製程分工；整體 PSU／DC-DC 模組在電源環節。
  adoption-conditions:
  - 按拓樸、實際工作電壓／電流、頻率、損耗、驅動、熱與可靠度設計選型。
  bottlenecks:
  - 材料缺陷、封裝、驅動保護與設計資格都可能限制採用，不只看晶圓面積或材料名。
  substitution-limits:
  - Si、SiC、GaN 有不同適用條件；800VDC 架構不是每顆元件的額定電壓，也不是單一材料必勝證據。
  claims:
  - id: multiple-materials
    statement: Infineon 公開 AI 供電說明將 Si、SiC、GaN 分工並列，支持按轉換位置與性能條件選型；不代表每種材料都有具名訂單。
    confidence: well-supported
    evidence:
    - source-id: infineon-power-technical
      url: https://www.infineon.com/technology/ai/we-power-ai
      locator: 'Si, SiC and GaN: a hybrid approach'
      read-scope: 已讀指定公開說明；沒有取得客戶完整設計、測試或認證檔
  evidence-gaps:
  - 缺少各候選公司的 AI 電源指定料號、實際拓樸 BOM、認證與收入拆分；不以汽車或工業收入填題材收入。
  reviewed: '2026-10-16'
---

## 環節定義

提供電力切換、整流、保護與控制所需的功率半導體、分離式元件、磊晶及特殊製程，收入角色包括材料、代工與成品元件。此處承載底層元件與製造能力；整體伺服器供電、板端電源方案與模組歸 `power`。類比控制與 MCU 是否受 AI 電源需求影響，要以實際料號用途判斷，不能把所有類比產品都列為 AI 供電。

## 技術變數

Si、SiC、GaN 依耐壓、頻率、導通／切換損耗、熱管理及總成本分工；寬能隙並非所有電壓區間都取代矽。800VDC 也不是每顆元件的額定電壓，需依轉換級、拓樸及設計餘裕選型。**well-supported**：英飛凌的 AI 供電方案同時涵蓋 Si、SiC 與 GaN，支持多材料分工；展示不代表所有材料商已有 AI 訂單。[英飛凌供電技術](https://www.infineon.com/technology/ai/we-power-ai)。

## 玩家格局

英飛凌（IFX.DE）供應多類功率半導體；安森美（ON）涵蓋功率元件與 SiC；Wolfspeed（WOLF）涵蓋 SiC 材料與元件。台股新唐（4919.TW）偏向 MCU 與控制相關產品，強茂（2481.TW）提供分離式元件，嘉晶（3016.TW）提供磊晶，漢磊（3707.TWO）提供 SiC／GaN 等特殊製程能力。這些公司分屬材料、製造及成品角色，不能以總營收直接比較 AI 電源份額。嘉晶的上市身分以交易所資料核對，修正為 `.TW`。[嘉晶公司與磊晶業務](https://www.epi.episil.com/Default/Company_Profile)、[交易所公司資訊](https://www.twse.com.tw/pdf/ch/3016_ch.pdf)。

## 傳導鏈

`foundry → power-discrete → power → odm / datacenter`：特殊製程與元件良率影響 PSU/DC/DC 的效率及可靠度，再影響整櫃功率與設施部署。本檔沒有直接題材連結，800VDC 需求可經下游 `power.themes` 到達。**inference**：更高機櫃功率帶來元件升級機會，但哪一材料或哪一供應商受惠，須由採用拓樸、認證與客戶設計確認，不能只以「高壓」推定 SiC 或 GaN 單方勝出。

## 監測指標

追蹤寬能隙及伺服器電源應用收入組合、認證轉量產、磊晶／晶圓良率、產能利用率及價格。優先使用各公司 IR、公開申報與實際 reference design 的料號；汽車、工業及資料中心收入須分開。**needs verification**：未揭露 AI 訂單時只標為潛在供應角色，並查財務重整、資金與產能承諾是否影響交貨，不使用歷史持股或股數作現況。

## 風險

SiC／GaN 擴產與非 AI 終端需求下滑可能同時發生，AI 成長未必抵銷價格與利用率壓力。新材料缺陷、封裝、驅動及可靠度驗證限制採用；客戶可能選回成熟矽方案。資本密集的材料與製造商承擔融資和長約風險，代工能力或展示板也不等於取得最終電源設計訂單。
