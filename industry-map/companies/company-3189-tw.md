---
schema-version: research-v1
entity-id: company-3189-tw
kind: company
name-zh: 景碩
aliases: ["景碩科技", "Kinsus"]
summary: "景碩提供 FCBGA、ABF 與 SiP 載板，幼獅擴建具有雙方具名公告。"
legacy-keys:
- 3189.TW
listings:
- ticker: 3189.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-substrate
  description: ABF 載板
  tier: 2
  baseline-path: ai-server/substrate.md
claims:
- id: kinsus-fcbga-abf-substrate-delivery
  statement: "景碩（3189.TW）列 FCBGA、SiP、PBGA 產品；公司對大型高層 ABF 說明良率與資格取得進展。"
  confidence: well-supported
  conditions: ["屬公司自述，不支持未具名的料號驗收或採用。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: kinsus-fcbga-substrates-product
    url: https://www.kinsus.com.tw/en/product/products/products_overview
    locator: "FCBGA／PBGA／SiP"
    read-scope: "查各交付用途。"
    stance: supporting
    applicable-period: "產品頁查核日"
  - source-id: kinsus-chairman-capability
    url: https://www.kinsus.com.tw/en/html/message_from_the_chairman/index
    locator: "FCBGA and SiP／Xing-Feng and Youth"
    read-scope: "查布局、良率及未具名認證。"
    stance: supporting
    applicable-period: "董事長致詞現行版"
  - source-id: twse-kinsus-company-3189
    url: https://www.twse.com.tw/pdf/ch/3189_ch.pdf
    locator: "公司基本資料"
    read-scope: "查 3189 以及上市主體。"
    stance: supporting
    applicable-period: "TWSE 公司頁"
- id: kinsus-nvidia-youth-substrate-supply
  statement: "景碩及 NVIDIA 公布既有先進載板供應與幼獅廠擴建協議。NVIDIA 指協議目標是將專屬先進 ABF 載板產能擴到目前的 3.5 倍以上，預期 2027 下半年開始投產、2028 Q3 達額外產能。"
  confidence: well-supported
  conditions: ["供應意圖與既有合作有雙方說法，預計產能與未來投產、驗收、實際出貨分開。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: kinsus-youth-nvidia-expansion
    url: https://www.kinsus.com.tw/zh-tw/news/newsroom/detail/news_category1/news_20261118
    locator: "幼獅設備投入與產能供應"
    read-scope: "查雙方、機台投資與時間。"
    stance: supporting
    applicable-period: "2026-11-17 公告"
  - source-id: nvidia-nov2026-substrate-capacity
    url: https://nvidianews.nvidia.com/news/nvidia-expands-commitments-with-supply-chain-partners-to-support-ai-infrastructure-buildout
    locator: "Increasing Substrate Capacity and Production Capabilities"
    read-scope: "查雙方、多年協議、進度及既有供應。"
    stance: supporting
    applicable-period: "2026-11-17 公告"
gaps:
- status: not-obtained
  reason: "缺同規格、同客戶、合格率及單位定價。"
- status: not-public
  reason: "各型號獨立收入及供應量未公開。"
---

## 供應角色

景碩科技股份有限公司（3189.TW）供應[ABF／覆晶載板](/next?focus=product-abf-substrate)、SiP 與 PBGA 等載板。

## 研究界線

原廠列產品家族與用途，董事長致詞的未具名資格與雙方幼獅 ABF 公告分開。

## 產品與用途

FCBGA 用於高腳數 CPU／GPU 等，SiP、PBGA 按封裝及材料需求分別賣。大型高層料號、熱循環與良率由個案核對。

## 商業模式

產品以可供交付的載板為單位，從設計與製造整合到電性驗證。設備投資、擴產協議與認列出貨分期。

## 客戶與供應商

NVIDIA 和景碩互證既有協作及幼獅專屬 ABF 擴建。2027、2028 是目標時點；未確認個別平台膜種、收入占比與實際用量。

## 競爭與替代

與南電或欣興在相同 FCBGA 外框、L/S、孔徑、翹曲與合格條件比較，SiP 與 PBGA 要選不同同類產品。

## 業務曝險

推論：大型高層數 ABF 規格變重可能增加工序時間；幼獅協議支持需求能見度，實際出貨仍取決於驗收。

## 風險

良率爬坡、設備、客戶需求推遲及核心或膜料變動可影響規劃。預期產能倍數有其專屬基準。

## 財務可取性

TWSE／MOPS 有公司及公開財務，合作公告有擴產計畫；缺指定 ABF 型號收入、獲利及已驗收出貨。
