---
schema-version: research-v1
entity-id: company-onto
kind: company
name-zh: "Onto Innovation"
aliases: ["Onto Innovation Inc.","Onto"]
summary: "供應高階載板面板曝光與封裝量測設備。"
legacy-keys: ["ONTO"]
listings:
- ticker: "ONTO"
  market: US
  exchange: XNYS
  share-class: common stock
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-equipment
  description: "供應高階載板面板曝光與封裝量測設備。"
  tier: 2
  baseline-path: semiconductor/equipment.md
claims:
- id: jetstep-x500-substrate-exposure
  statement: "Onto 的 JetStep X500 面板曝光設備適用於先進 IC 載板及有機 laminate 面板，支援板變形補償。"
  confidence: well-supported
  conditions: ["該產品交付為曝光設備。解像、焦深、套位及吞吐量以實配基板與光阻驗證。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: onto-jetstep-x500
    url: https://ontoinnovation.com/products/jetstep-x500/
    locator: "Overview、Key Features"
    read-scope: "查 AICS 適用範圍及面板尺寸／厚度／翹曲考量。"
    stance: supporting
    applicable-period: "X500 產品頁"
  - source-id: onto-fy2025-10k
    url: https://www.sec.gov/Archives/edgar/data/704532/000119312526066937/onto-20260103.htm
    locator: "Item 1 Our Products、封面"
    read-scope: "核對封裝光刻與股票身分。"
    stance: supporting
    applicable-period: "FY2025 10-K（截至 2026-01-03）"
gaps:
- status: not-obtained
  reason: "同材料及曝光條件的成本、有效產速未取得。"
- status: not-public
  reason: "FY2025 10-K 未單列 X500 收入、指定客戶合格出貨。"
---

## 供應角色

Onto Innovation Inc.（NYSE: ONTO）提供[載板線路曝光設備](/next?focus=product-substrate-patterning-lithography)和量測設備。

## 研究界線

以 X500 原廠規格與 FY2025 10-K 為準，量測、曝光與整線資格分開。

## 產品與用途

JetStep X500 針對先進封裝與高階 IC 載板面板，處理有機 laminate 及板變形。

## 商業模式

銷售與維護系統，另交付量測、檢測與軟體。設備價值與光阻耗材及成品載板不同。

## 客戶與供應商

面向半導體製造及先進封裝製造業者，本批資料沒有 X500 的客戶採用或供應份額。

## 競爭與替代

與 SCREEN PE 同後段圖形用途可比較；選型需確認投影或直寫、板形、焦穩定、對位及鍍後制程窗口。

## 業務曝險

面板與載板微縮可增加檢測及曝光需求，惟設備訂單和通過量產相隔。

## 風險

資本支出循環、機台資格及技術替換影響交付，曝光上游光阻和下游填鍍須同版驗證。

## 財務可取性

SEC 年報可查 consolidated 科目與市場口徑，欠缺單機台客戶、價格、收入及良率。
