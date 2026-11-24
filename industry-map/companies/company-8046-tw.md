---
schema-version: research-v1
entity-id: company-8046-tw
kind: company
name-zh: 南電
aliases: ["南亞電路板", "Nan Ya PCB"]
summary: "南亞電路板提供 ABF、PP 等封裝載板與 PCB，原廠列有 ABF 製程路線圖。"
legacy-keys:
- 8046.TW
listings:
- ticker: 8046.TW
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
- id: nan-ya-pcb-abf-and-spec-roadmap
  statement: "南電（8046.TW）供應 ABF、PP 載板及 PCB 等產品。ABF 頁現行欄列 9/12 μm L/S 與 50/75 μm 盲孔／pad，2027 H1 有另列目標。"
  confidence: well-supported
  conditions: ["各欄能力是產品族頁面，極值不能拼成一個合格料號。合併收入不等於 ABF 收入。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: nan-ya-pcb-company-8046
    url: https://www.nanyapcb.com.tw/nypcb/english/AboutNanYaPCB/CompanyProfile/Company
    locator: "Major Business Lines"
    read-scope: "核對公司主體、產品族。"
    stance: supporting
    applicable-period: "公司簡介查核日"
  - source-id: nan-ya-pcb-abf-technology-roadmap
    url: https://www.nanyapcb.com.tw/nypcb/english/Technology/ABFSRoadmap
    locator: "Routing Density／Blind via／Green Material Set"
    read-scope: "查現況與開發時間，以及所列材料名稱。"
    stance: supporting
    applicable-period: "ABF 路線圖查核日"
  - source-id: nan-ya-pcb-2025-consolidated
    url: https://www.nanyapcb.com.tw/nypcb/images/InvestorRelations/FinancialReport/114Q4ENG%28Consolidated%29.pdf
    locator: "封面與公司沿革、附註產品及部門"
    read-scope: "查 8046 及 FY2025 來源。"
    stance: supporting
    applicable-period: "FY2025 合併財報"
gaps:
- status: not-obtained
  reason: "缺同材料、面積、層數及熱條件的良率、報價。"
- status: not-public
  reason: "已讀資料未提供個別載板合格量及型號收入。"
---

## 供應角色

南亞電路板股份有限公司（8046.TW）提供[ABF／覆晶載板](/next?focus=product-abf-substrate)與 PP 載板，並製造傳統、HDI、軟硬複合 PCB。

## 研究界線

ABF 技術路線圖的 Current Capability 與未來年份分欄；同一個產品的可交付組合需另查。

## 產品與用途

路線圖現行例為 9/12 μm L/S、50/75 μm 盲孔／pad；指定線寬、表面與材料須按平台測試。

## 商業模式

按分組製造、加工及銷售，經營錦興、樹林及昆山等據點。設計或驗證所需時間與最終銷貨分開。

## 客戶與供應商

公司列 GX-T31、GL102、NX04H 等材料於路線圖；此清單未提供各廠別指定料號、交付比例或客戶身份。

## 競爭與替代

與欣興／Ibiden 以相同厚度、外形、多層套位、孔徑與翹曲互比。PP 載板及 PCB 應按其他應用。

## 業務曝險

路線圖有加大外形、縮小線距與孔距的方向。需求效果取決於有效良率、稼動及資格。

## 風險

面積、工序、料號與膜料替換改變排產；技術路線圖目標需與量產驗收分開。

## 財務可取性

114 年合併財報可取得公司、財務與報表口徑。缺 ABF 料號、客戶合格量、獨立收入與毛利。
