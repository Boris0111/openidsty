---
schema-version: research-v1
entity-id: company-mksi
kind: company
name-zh: "MKS"
aliases: ["MKS Inc.","MKS Instruments","ESI"]
summary: "提供先進載板雷射與電子製程設備。"
legacy-keys: []
listings:
- ticker: "MKSI"
  market: US
  exchange: XNAS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-equipment
  description: "提供先進載板雷射與電子製程設備。"
  tier: 2
  baseline-path: semiconductor/equipment.md
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
- id: mks-electronics-packaging-business
  statement: "MKS Inc.（MKSI，Nasdaq）在 FY2025 10-K 列出雷射鑽機、電子化學與電鍍設備。"
  confidence: well-supported
  conditions: ["報表 Electronics and Packaging 為終端市場組合。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: mksi-fy2025-10k
    url: https://www.sec.gov/Archives/edgar/data/1049502/000119312526066820/mksi-20251231.htm
    locator: "封面、Item 1 Markets、Item 7 Net Revenues by End Market"
    read-scope: "查上市身分、業務範疇及報表口徑。"
    stance: supporting
    applicable-period: "FY2025 10-K"
gaps:
- status: not-obtained
  reason: "同規格設備效率和取得成本未公開。"
- status: not-public
  reason: "個別 ABF 設備收入、採用與客戶良率仍待核。"
---

## 供應角色

ESI 品牌屬 MKS，供應[載板雷射微孔設備](/next?focus=product-substrate-laser-microvia-drill)與其他微細電路製程設備。

## 研究界線

產品頁支持機台能力，10-K 只支持公司整體分類與其風險揭露。

## 產品與用途

Geode A 是 CO₂ 成孔設備，支援 30–85 μm 與雙頭雙板，去膠渣和填銅依下游設備配置。

## 商業模式

銷售設備、耗材與售後服務；電子封裝中還有 PCB、載板與 WLP 的其他交付。

## 客戶與供應商

10-K 說明與客戶產業、部件供應及單一來源相關風險。未揭露特定 Geode A 客戶。

## 競爭與替代

同材料和孔深下可與東捷或三菱方案比較；先核對良孔產出、定位和維護。

## 業務曝險

載板製造商升級孔徑和製程可能增加設備時數。仍須扣現有設備與校準改機。

## 風險

資本支出循環、競爭與關鍵零件供應影響交付，另有化學和設備整合風險。

## 財務可取性

可查 SEC FY2025 10-K 的整體及終端市場收入口徑。未提供 Geode A 或單客戶載板業務資料。
