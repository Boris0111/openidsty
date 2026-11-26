---
schema-version: research-v1
entity-id: product-substrate-laser-microvia-drill
kind: product
name-zh: "載板雷射微孔設備"
aliases: ["ABF laser drill","laser microvia"]
summary: "以雷射在增層介電膜開出微孔，露出目標銅面。"
definition: "以雷射在增層介電膜開出微孔，露出目標銅面。"
purpose: "提供待去膠渣、成種子層與填鍍的層間連接。"
boundary: "機台開孔，填鍍、檢驗與客戶良率屬後段載板流程。"
adoption-conditions: ["對齊材料、孔徑、孔深、孔錐角、對位、底銅損傷與產速。"]
bottlenecks: ["焦高及能量穩定度、膜材差異、板面起伏及孔底殘膠。"]
substitution-limits: ["CO₂、UV、超快雷射須以同材料疊構與合格標準比較。"]
reviewed: '2026-11-24'
claims:
- id: geode-a-abf-microvia-tool
  statement: "MKS 的 ESI Geode A 為 ABF／FCBGA 載板用 CO₂ 雷射設備，原廠列孔徑 30–85 μm、雙頭雙板，適用材料另列 RCC 及非銅箔介電層。"
  confidence: well-supported
  conditions: ["孔徑依膜材、深度、銅面、面板和平整度的實作條件驗證。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: mks-esi-geode-a
    url: https://www.esi.com/f/geode-a-abf-via-drilling-system
    locator: "Specifications、Materials、Processes"
    read-scope: "查 ABF、孔徑範圍及機台架構。"
    stance: supporting
    applicable-period: "Geode A 產品頁"
  - source-id: mks-esi-brand
    url: https://www.mks.com/b/esi
    locator: "ESI brand overview"
    read-scope: "查為 MKS 旗下品牌。"
    stance: supporting
    applicable-period: "查核日原廠頁"
- id: microvia-tooling-and-stage
  statement: "東捷展示機規格列 10–50 μm。三菱電機公開展示用於封裝基板的 ML605GTF5-UVP；工研院技轉規格另列 ≤5 μm。"
  confidence: well-supported
  conditions: ["不同膜、孔深、產速及研發或設備展示階段應分開。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: contrel-smart-machinery-abf-microvia
    url: https://industry.meettaiwan.com/smartmachinery/zh-tw/product/detail/ABF-Laser-Microvia-Drilling
    locator: "產品簡介、鑽孔大小"
    read-scope: "查材料與孔徑範圍。"
    stance: supporting
    applicable-period: "查核日台灣智慧機械型錄"
  - source-id: mitsubishi-jpca-package-laser
    url: https://www.mitsubishielectric.co.jp/fa/events-seminars/exhibitions/2024/jpca2024/index.html
    locator: "出展製品／ML605GTF5-UVP"
    read-scope: "查 JPCA 實機展示與封裝載板定位。"
    stance: supporting
    applicable-period: "JPCA Show 2024"
  - source-id: itri-abf-microvia-tech
    url: https://www.itri.org.tw/ListStyle.aspx?DisplayStyle=13_content&MmmID=1036233375626243454&SiteID=1&Trt_idx=10714
    locator: "技術簡介／技術規格"
    read-scope: "查技轉開發與孔徑。"
    stance: supporting
    applicable-period: "工研院原型／技轉規格"
- id: qualified-microvia-demand
  statement: "合格微孔變小或每板孔數增加時，若有效速度下降，所需設備時間可能增加。"
  confidence: inference
  conditions: ["光束、機台併行、重佈線減孔、可用率提高可抵銷；須估合格孔／小時而非展示速度。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: mks-esi-geode-a
    url: https://www.esi.com/f/geode-a-abf-via-drilling-system
    locator: "Features／Specifications"
    read-scope: "查雷射對位與雙頭能力。"
    stance: supporting
    applicable-period: "Geode A"
  - source-id: itri-abf-microvia-tech
    url: https://www.itri.org.tw/ListStyle.aspx?DisplayStyle=13_content&MmmID=1036233375626243454&SiteID=1&Trt_idx=10714
    locator: "技術規格"
    read-scope: "查孔錐角、圓度、孔徑條件。"
    stance: supporting
    applicable-period: "技轉頁"
gaps:
- status: not-obtained
  reason: "缺同膜、同孔徑／孔深、同面板的合格速度、耗材、維修與成本。"
- status: not-public
  reason: "未公開個別客戶驗收、穩定良率或設備收入。"
---

## 定義與用途

雷射脈衝在固化膜料去除指定材料，留下盲孔供下段去膠渣、鍍銅導通。盲孔位置與底銅品質須和壓合與填鍍一起驗證。

## 規格與成本

ESI Geode A 型錄列 30–85 μm，雙頭雙板；東捷列 10–50 μm 及展示處理速度。核對面板、膜材、孔底與孔徑分布。合格速度需扣換板、對位、抽檢和維修時間。

## 採用條件與限制

CO₂ 或 UV 比較需固定欲去除材料、是否先開銅窗、孔錐與底損。試片中的 ≤5 μm 技轉結果與大面板穩定產速是不同證據。

## 供應角色與公司

[MKS](/next?focus=company-mksi)由 ESI 提供 Geode A，台灣東捷有雷射微鑽孔設備，日本三菱電機公開 UV 設備展示。各案的材料導入和量產要獨立查。

## 需求如何傳導

推論：縮孔、孔數和層數增加可能拉高設備時間；同一設備若可併行、提高可用率或減孔，也能抵銷。查良孔／小時與客戶驗收。
