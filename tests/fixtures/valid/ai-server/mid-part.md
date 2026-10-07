---
segment: mid-part
name_zh: 中段環節
layer: ai-server
position: 2
market_coverage:
  tw: present
  us: present
companies:
  - ticker: "2330.TW"
    name_zh: 台積電
    role: 核心製造
    tier: 1
  - ticker: "NVDA"
    name_zh: 輝達
    role: 規格定義者
    tier: 1
  - ticker: "PRIVATE:example-co"
    name_zh: 範例未上市公司
    role: 利基供應
    tier: 3
upstream: [upstream-part, support-part]
downstream: [end-part]
themes: [sample-theme]
kpis:
  - 出貨量
  - 毛利率
signals:
  - 客戶認證通過
---

## 環節定義

測試用的中段環節，連接上游與下游。

## 技術變數

兩條技術路線並行。

## 玩家格局

台積電與輝達為主要玩家，另有未上市的利基供應商。

## 傳導鏈

上游漲價會壓縮本環節毛利，並往 end-part 轉嫁。

## 監測指標

月營收與出貨量。

## 風險

客戶集中度偏高。
