---
schema-version: research-v1
entity-id: company-2802-t
kind: company
name-zh: "味之素"
aliases: ["Ajinomoto","Ajinomoto Co., Inc."]
summary: "透過精細化學子公司 AFT 供應載板增層介電膜。"
legacy-keys: ["2802.T"]
listings:
- ticker: "2802.T"
  market: JP
  exchange: XTKS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-materials
  description: "透過精細化學子公司 AFT 供應載板增層介電膜。"
  tier: 2
  baseline-path: semiconductor/materials.md
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
- id: ajinomoto-listing-and-manufacture
  statement: "味之素母公司於東京證交所上市（2802），AFT 設計與供應電子材料，集團公開文件分列 ABF 原液與塗膜等流程。"
  confidence: well-supported
  conditions: ["上市主體、設備及膜料交付法律主體分開。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: ajinomoto-stock-data
    url: https://www.ajinomoto.co.jp/company/en/ir/faq.html
    locator: "Questions about stock"
    read-scope: "查 2802 與東京掛牌。"
    stance: supporting
    applicable-period: "公司 IR 查核日"
  - source-id: ajinomoto-aft-company-and-abf
    url: https://www.ajinomoto.co.jp/company/en/presscenter/press/detail/g2016_04_13.html
    locator: "Equity ownership／About ABF"
    read-scope: "核對 AFT 由味之素持有及 varnish／膜生產分工。"
    stance: supporting
    applicable-period: "2016 年公告"
  - source-id: ajinomoto-ict-abf-briefing
    url: https://www.ajinomoto.co.jp/company/en/ir/event/business_briefing/main/01113/teaserItems1/01/linkList/00/link/3_ICT_E.pdf
    locator: "ABF production process／growth strategy"
    read-scope: "讀原液塗佈與供應產能／AI 應用規劃。"
    stance: supporting
    applicable-period: "2023 ICT brief"
gaps:
- status: not-obtained
  reason: "同條件膜料及製程成本未取得。"
- status: not-public
  reason: "公開資料未逐料號拆出客戶、認證、出貨及營收。"
---

## 供應角色

Ajinomoto Co., Inc.（2802.T）的 AFT 交付[載板增層介電膜](/next?focus=product-substrate-build-up-dielectric)，載板商承擔後續成形與驗收。

## 研究界線

原廠技術目錄證實牌號與材料；集團法說描述產能及供應規劃，客戶驗收要以具體產品核對。

## 產品與用途

GX-92 為基準，GX-T31、GZ-41 與 GL-102 各有粗度、CTE、Tg 及 Df 的組合。採用要核對銅附著、翹曲與溫循。

## 商業模式

透過精細化學部門投入樹脂原液與膜材料生產，部分塗膜與物流等工序依供應體系分工，與成品載板成本不同。

## 客戶與供應商

用途涵蓋 CPU 及 HPC。原廠頁未列各載板客戶的合格牌號、供應數量或塗布來源份額。

## 競爭與替代

與積水 NX04H 或晶化 TBF 比較時先對齊固化、膜厚、電性測試和 SAP 相容性。

## 業務曝險

推論：高層數載板大幅拉高增層實作時間，膜料面積可能增加，仍受尺寸、產品組合及合格率影響。

## 風險

原液／膜批次一致性、塗佈產能、配方與認證時程均會影響交貨和替代速度。

## 財務可取性

可讀日文／英文 IR Data Book、集團合併報告與 ICT 事業簡報。缺 ABF 逐牌號獨立收入、毛利、合格出貨與客戶占比。
