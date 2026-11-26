---
schema-version: research-v1
entity-id: company-3037-tw
kind: company
name-zh: 欣興
aliases: ["欣興電子", "Unimicron"]
summary: "欣興電子提供 IC 載板與各類 PCB，台灣 KF 擴建另有具名產能承諾。"
legacy-keys:
- 3037.TW
listings:
- ticker: 3037.TW
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
  tier: 1
  baseline-path: ai-server/substrate.md
claims:
- id: unimicron-substrate-capability
  statement: "欣興（3037.TW）列 IC 載板、PCB、HDI、FPC 等產品。其子公司上市文件草稿描述 CPU／GPU／伺服器用 FCBGA 製程歷史；NVIDIA 另公布台灣 KF 載板擴建產能預留。"
  confidence: well-supported
  conditions: ["集團子公司草稿範圍、台灣 KF 線及客戶個別規格不可混用。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: twse-unimicron-company-3037
    url: https://wwwc.twse.com.tw/pdf/en/3037_en.pdf
    locator: "Company Information"
    read-scope: "查股票代碼及公司主要產品。"
    stance: supporting
    applicable-period: "TWSE 公司資訊"
  - source-id: unimicron-fy2025-mops-report
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=3037&year=115&mtype=F&
    locator: "封面／營運概況"
    read-scope: "核對 IC Carrier、PCB 與主要金額口徑。"
    stance: supporting
    applicable-period: "114 年股東會年報"
  - source-id: unimicron-hkex-subsidiary-substrate-draft
    url: https://www1.hkexnews.hk/app/sehk/2026/108620/a133776/sehk26060800915_c.pdf
    locator: "歷史、發展及公司架構"
    read-scope: "查 FCBGA 工藝及集團法體；僅草稿資料。"
    stance: supporting
    applicable-period: "2026-06 申請資料"
  - source-id: nvidia-oct2026-substrate-capacity
    url: https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout
    locator: "Increasing Substrate Capacity"
    read-scope: "查欣興 KF、產能預留及目標時間。"
    stance: supporting
    applicable-period: "2026-10-21"
gaps:
- status: not-obtained
  reason: "未公開同規格、同介質、同尺寸的良率與出貨。"
- status: not-public
  reason: "沒有合格 ABF 產品分項營收與客戶分布。"
---

## 供應角色

欣興電子股份有限公司（Unimicron，3037.TW）供應[ABF／覆晶載板](/next?focus=product-abf-substrate)及系統 PCB。

## 研究界線

股東會年報描述集團組合。HKEX 子公司草稿的製程里程碑限該法律主體，台灣 KF 的產能預留另有公告。

## 產品與用途

IC Carrier 與 PCB／HDI／FPC 各自交付。集團子公司歷史列 CPU、GPU、伺服器 FCBGA；實際台灣料號的 L/S、堆疊與可靠度按案核對。

## 商業模式

製造及銷售載板、PCB 和相關產品，依客戶設計與驗證導入。KF 產能預留與收入確認發生在不同階段。

## 客戶與供應商

NVIDIA 公告具名支持 KF 計畫，新增產能預期自 2027 Q2 起，2028 年中達完整配置。公告未列膜供應或合格型號。

## 競爭與替代

與 Ibiden、南電在相同外形、孔徑、L/S、翹曲與品質下比較。對照核心、基板和組裝資格。

## 業務曝險

推論：伺服器與 AI 專案可能增加同規格合格產出需求，尚受路線、設備時數與客戶驗收影響。

## 風險

廠區及子公司分工、擴產驗證、材料工序和交期都會影響出貨。

## 財務可取性

114 年度年報與 MOPS 有集團財務，未拆分所有 ABF 料號與個別新增量。
