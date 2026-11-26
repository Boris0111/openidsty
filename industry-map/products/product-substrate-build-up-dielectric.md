---
schema-version: research-v1
entity-id: product-substrate-build-up-dielectric
kind: product
name-zh: "載板增層介電膜"
aliases: ["build-up dielectric film","ABF","BUF"]
summary: "在封裝載板銅層間形成隔離絕緣的增層膜。"
definition: "在封裝載板銅層間形成隔離絕緣的增層膜。"
purpose: "支援雷射微孔、填鍍及細線多層互連。"
boundary: "交付為膜料，銅佈線、微孔與驗收依載板商製程。"
adoption-conditions: ["同膜厚和熱條件驗證壓合、去膠渣、銅附著和可靠度。"]
bottlenecks: ["粗糙度、厚度、CTE、Df、Tg 與鍍銅黏著的交互限制。"]
substitution-limits: ["替換膜料需以同規格重做完整載板資格。"]
reviewed: '2026-11-24'
claims:
- id: aft-abf-grade-delivery
  statement: "味之素集團由 Ajinomoto Fine-Techno 供應 ABF 增層膜，型錄區分 GX-T31 低 CTE／粗度、GZ-41 高 Tg 與 GL-102 低 Df 等。"
  confidence: well-supported
  conditions: ["產品為覆於載板導體間的介電材料；型錄性質以牌號為準。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: aft-abf-grade-catalog
    url: https://www.aft-website.com/en/products/insulating_film-abf/
    locator: "Variety/grade、Composition、Instructions for use"
    read-scope: "讀 GX-T31、GZ-41、GL-102、壓合後加工位置。"
    stance: supporting
    applicable-period: "產品型錄，查核日"
  - source-id: ajinomoto-aft-company-and-abf
    url: https://www.ajinomoto.co.jp/company/en/presscenter/press/detail/g2016_04_13.html
    locator: "Equity ownership／About ABF"
    read-scope: "核對 AFT 由味之素持有及 varnish／膜生產分工。"
    stance: supporting
    applicable-period: "2016 年公告"
- id: build-up-film-comparison
  statement: "積水 NX04H 型錄標 HVM，列 25–150°C CTE 24.5 ppm/°C 及 5.8 GHz Dk 3.3。台灣晶化科技則公開 10–150 μm TBF 產品厚度範圍。"
  confidence: well-supported
  conditions: ["不同試驗與指標不可直接排名；各企業自述未證實同平台可替換。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: sekisui-taiwan-build-up-film
    url: https://www.sekisui.com.tw/product/21/17
    locator: "Current Product Lineup／Semi-Additive Process"
    read-scope: "對照 NX04H 與 NQ07XP 各自量產狀態、CTE 溫區及 Dk 頻率。"
    stance: supporting
    applicable-period: "查核日台灣網站"
  - source-id: waferchem-tbf-material
    url: https://www.waferchem.com.tw/taiwan-build-up-film-en.html
    locator: "Product Structure／Product Lineup／Thickness"
    read-scope: "查 TBF 膜厚與應用，限制為廠商資料。"
    stance: supporting
    applicable-period: "查核日產品頁"
- id: dielectric-film-demand
  statement: "若同一平台的合格載板增層變多且膜種不變，可能增加有效膜面積及經認證的供給需求。"
  confidence: inference
  conditions: ["尺寸、層數、裁切效率、材料轉換與不同良率可抵銷，需要實際採購與 qualified stackup。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: aft-abf-grade-catalog
    url: https://www.aft-website.com/en/products/insulating_film-abf/
    locator: "Variety/grade、Composition、Instructions for use"
    read-scope: "讀 GX-T31、GZ-41、GL-102、壓合後加工位置。"
    stance: supporting
    applicable-period: "產品型錄，查核日"
  - source-id: ajinomoto-ict-abf-briefing
    url: https://www.ajinomoto.co.jp/company/en/ir/event/business_briefing/main/01113/teaserItems1/01/linkList/00/link/3_ICT_E.pdf
    locator: "ABF production process／growth strategy"
    read-scope: "讀原液塗佈與供應產能／AI 應用規劃。"
    stance: supporting
    applicable-period: "2023 ICT brief"
gaps:
- status: not-obtained
  reason: "同試驗頻率、溫區及膜厚的價格、附著力或良率未取得。"
- status: not-public
  reason: "公開型錄未揭露逐型號的合格用量與收入。"
---

## 定義與用途

增層膜經壓合與硬化覆於既有導線，使銅層間絕緣。由雷射開孔後清除膠渣，進入初始化鍍銅與後續線路形成。AFT 的 ABF 是帶 PET 支撐及保護膜的熱固性樹脂材料。

## 規格與成本

GX-T31 強調低粗度／CTE，GZ-41 再提高 Tg，GL-102 另列低 Df。積水 NX04H 列 25–150°C CTE 24.5 ppm/°C、5.8 GHz Dk 3.3；不同條件的數字不能直接比較。查膜厚、固化、下游銅附著與熱循環後失效。

## 採用條件與限制

同一層堆疊可評估其他樹脂膜、RCC 或感光性絕緣材料，路徑會改變開孔、種子層或銅粗化。驗證同頻率電性、吸濕、溫區及加工良率後才能認定替換。

## 供應角色與公司

[味之素](/next?focus=company-2802-t)透過 AFT 供應 ABF；積水熱固膜與晶化 TBF 為同一交付功能的公開比較。Qnity 的光阻及鍍銅化學為後段耗材。個別材料以及載板採用依成品規格驗證。

## 需求如何傳導

推論：放大有效載板面積或增加重複增層可提高膜料需求；換芯、削減增層、改牌號或改善裁切良率會改變用量。追蹤客戶合格堆疊、材料採購和可用面積。
