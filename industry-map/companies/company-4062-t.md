---
schema-version: research-v1
entity-id: company-4062-t
kind: company
name-zh: Ibiden
aliases: ["IBIDEN CO., LTD.", "揖斐電"]
summary: "日本高性能覆晶 IC 載板廠，公開 SAP、微孔與高層數大尺寸技術資料。"
legacy-keys:
- 4062.T
listings:
- ticker: 4062.T
  market: JP
  exchange: XTKS
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-substrate
  description: 高階 ABF 載板主要供應者
  tier: 1
  baseline-path: ai-server/substrate.md
claims:
- id: ibiden-flip-chip-sap-and-microvia
  statement: "IBIDEN 提供高性能覆晶載板，官網列 SAP 細線與 laser／填鍍微孔，服務資料中心 MPU 與 AI GPU。整合報告列 CY2025 約 80×80 mm／18 層的尺度。"
  confidence: well-supported
  conditions: ["載板家族與尺度趨勢可追溯；未公開同一合格客戶產品的組合、良率或膜牌號。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-flip-chip-pkg-sap
    url: https://www.ibiden.com/product/electronics/merchandise/fliptippkg/
    locator: "Feature／Applications"
    read-scope: "查 SAP、微孔及應用。"
    stance: supporting
    applicable-period: "原廠產品頁"
  - source-id: ibiden-integrated-report-2026
    url: https://www.ibiden.com/ir/items/IntegratedReport2026_en.pdf
    locator: "Special Feature 1 pp.8–10"
    read-scope: "查大型多層與翹曲、尺度圖。"
    stance: supporting
    applicable-period: "Integrated Report 2026"
- id: ibiden-identity-and-gama-development
  statement: "IBIDEN CO., LTD. 的股票為 4062，於東京與名古屋交易。Gama Cell6 計畫由 FY2027 起依序投產並規劃量產。"
  confidence: well-supported
  conditions: ["規劃與完成建物不等於可交付客戶的合格產出。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: ibiden-4062-stock-fy2025
    url: https://www.ibiden.com/ir/items/cashdividendofsurplus.pdf
    locator: "封面"
    read-scope: "確認設立名稱與股票掛牌。"
    stance: supporting
    applicable-period: "2026-05-19"
  - source-id: ibiden-gama-substrate-capex
    url: https://www.ibiden.com/company/2026/02/notice-regarding-capital-investment-plan-for-high-performance-ic-package-substrates.html
    locator: "5. Details of Capital Investment Plan"
    read-scope: "查 Gama Cell6 與量產時程。"
    stance: supporting
    applicable-period: "2026-02 計畫"
gaps:
- status: not-obtained
  reason: "同面積、厚度、熱循環、孔徑的實測良率、價格未取得。"
- status: not-public
  reason: "大尺寸具名客戶及指定規格出貨未公開。"
---

## 供應角色

IBIDEN CO., LTD.（4062.T）提供[封裝載板](/next?focus=product-abf-substrate)成品，主板和封裝工序另計。

## 研究界線

技術報告的 roadmap 從材料／尺寸趨勢讀取。未有客戶指定堆疊的資格和實際出貨。

## 產品與用途

Flip Chip PKG 使用 SAP 細線；雷射微孔與鍍銅連接層間。CY2025 約 80×80 mm／18 層是公司示意；尺寸與層數增加，需控制整板翹曲。

## 商業模式

製造及銷售成品，透過設計協作和客戶驗證導入。Gama Cell6 直到計畫中的 FY2027 才安排投產，不拿建廠面積估收入。

## 客戶與供應商

集團揭露 AI／一般伺服器等用途及與客戶協作的策略，這些不證實指定模型與載板厚度。已讀資料未識別膜或設備的指定合格來源。

## 競爭與替代

與 Shinko DLL 或南電同有芯載板比較，按相同尺寸、增層、翹曲及溫循；coreless 與 glass core 另外驗證。

## 業務曝險

資料中心 MPU、AI GPU、車用均為公開用途。推論：更大外形和多層轉為可交付的量取決於同板缺陷、填孔與有效設備時間。

## 風險

面積與層數增加會加重翹曲及套位；Gama／Ono 產線擴建、驗證或需求時程變動可延後有收入產出。

## 財務可取性

日本 IR 有合併財務與 Electronics 分部。報告年度截至三月底，未取得單一產品、ABF 膜料別或具名案場的業績。
