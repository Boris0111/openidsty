---
schema-version: research-v1
entity-id: company-2059-tw
kind: company
name-zh: 川湖
aliases:
- King Slide
- 川湖科技
summary: 伺服器導軌（rail kit）廠，導軌占營收 98%；114 年度營收成長 72.77%，年報歸因於 AI ASIC 與 GPU 相關產品，前三大客戶是伺服器品牌與 CSP 指定的代工廠。
legacy-keys:
- 2059.TW
listings:
- ticker: 2059.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 90 頁（PDF 第 94 頁）財務績效比較表，113 與 114 年度並列
    read-scope: 已讀財務績效表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-interconnect
  description: 伺服器滑軌與理線機構
  tier: 2
  baseline-path: ai-server/interconnect.md
claims:
- id: rail-revenue-share
  statement: 年報 114 年度營業比重為導軌 98%、鉸鏈 1%、其他 1%、滑軌 0%；導軌商品是 1U–7U 伺服器及其週邊設備用的各式導軌，滑軌與鉸鏈主要用於傢俱、鋼櫃與廚具。
  confidence: well-supported
  conditions:
  - 比重表抽取時欄位錯位，依合計 100% 核對；年報的「導軌」對應本地圖的伺服器滑軌，「滑軌」是傢俱用途
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 66 頁（PDF 第 70 頁）營業比重與目前之商品項目；第 67 頁（PDF 第 71 頁）產業現況
    read-scope: 已讀業務內容與產業現況段落
    stance: supporting
    applicable-period: 114 年度
- id: ai-driven-growth
  statement: 年報 114 年度營業收入淨額 17,500,695 千元，較 113 年度增加 72.77%；營業淨利 12,088,577 千元、本期淨利 9,837,067 千元，年報將成長歸因於 AI 應用使 ASIC 與 GPU 相關產品問市與替換速度加快。
  confidence: well-supported
  conditions:
  - 年報未拆分 AI 伺服器導軌收入
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 90 頁（PDF 第 94 頁）最近二年度營業收入重大變動之主要原因
    read-scope: 已讀財務績效段落
    stance: supporting
    applicable-period: 113 至 114 年度
- id: odm-hub-customers
  statement: 年報主要銷貨客戶以代號揭露，114 年度甲、乙、丙客戶分別占 17.40%、13.87%、12.42%，三者是國際伺服器大廠指定下單的代工廠，因多家 OEM 與 CSP 指定把產品送到客戶全球 HUB 而成為前三大。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露；代工廠是出貨對象，最終指定者是 OEM 與 CSP
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）主要銷貨客戶；第 94 頁（PDF 第 98 頁）銷貨集中風險
    read-scope: 已讀主要銷貨客戶表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度、115 年第 1 季
- id: steel-suppliers
  statement: 年報揭露主要原料為鋼捲，114 年度向中鋼進貨占 33.93%，另一家日本鋼鐵集團子公司（A 公司）占 12.50%。
  confidence: well-supported
  conditions:
  - A 公司名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）主要原料之供應狀況與主要供應商
    read-scope: 已讀原料與供應商表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報 114 年度銷售地區合計為美國 57%、台灣 18%、其他 17%、中國 8%，導軌在各地區都占主要部分。
  confidence: well-supported
  conditions:
  - 地區表抽取時欄位錯位，依各地區合計核對；地區依出貨對象，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 73 頁（PDF 第 77 頁）主要商品之銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 114 年度
- id: rail-roadmap
  statement: 年報稱以整合機架式伺服器安裝、多功能與人性化施工為 rail kit 研發方向，並開發伺服器與儲存櫃用的功能性人工智能導軌，已進入最後驗證階段。
  confidence: inference
  conditions:
  - 功能性導軌仍在驗證階段，不代表量產
  reviewed: '2026-10-18'
  evidence:
  - source-id: kingslide-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2059&year=115&mtype=F&
    locator: 114 年度年報第 66 頁（PDF 第 70 頁）計畫開發之新商品；第 73 頁（PDF 第 77 頁）產品發展方向
    read-scope: 已讀新商品與發展方向段落
    stance: supporting
    applicable-period: 114 年度年報
gaps:
- status: not-public
  reason: 年報稱產品客製化程度高，無法取得市占資料；也未揭露客戶名稱或 AI 伺服器導軌收入。
- status: not-public
  reason: 年報沒有提到理線機構，川湖在理線產品的能力未由此來源確認。
---

## 供應角色

川湖在[互連環節](/next?focus=segment-interconnect)屬[伺服器滑軌與理線](/next?focus=role-server-rail)，供應讓伺服器在機櫃內抽換的[伺服器滑軌](/next?focus=product-server-slide-rail)。年報稱這類產品為「導軌」。

## 研究界線

**邊界裁決**：依「可彼此替換的供應角色」規則，川湖的導軌與其他 rail kit 廠是同一個機構角色；它不在供電路徑上，不能因為英文同樣叫 rail 就配對到 power rail 或 busbar。年報裡的「滑軌」和「鉸鏈」是傢俱用途，合計約 1%，不納入地圖。理線機構未在年報出現，列為未公開。依據為 114 年度年報第 66–67 頁的商品與產業說明。

## 產品與用途

- **導軌**：1U–7U 伺服器及週邊設備用的各式 rail kit，占 98%（第 66 頁）。
- **開發中**：伺服器與儲存櫃用功能性導軌，已進入最後驗證（第 66 頁）。
- **傢俱用途**：多用途滑軌與隱藏式鉸鏈，用於傢俱、鋼櫃與廚具（第 66–67 頁）。

## 商業模式

客製化設計並自行生產，客戶是伺服器品牌與 CSP 指定的代工廠（第 80 頁）。114 年度營收 17,500,695 千元，成長 72.77%；營業毛利 13,308,776 千元，約占營收 76%（第 90 頁）。

## 客戶與供應商

甲、乙、丙三家代工廠在 114 年度分別占 17.40%、13.87%、12.42%，合計約 44%；三者都是因 OEM 與 CSP 指定而下單（第 80、94 頁）。鋼捲向中鋼採購約 34%，另一家日本鋼鐵集團子公司約 12.5%（第 80 頁）。

## 競爭與替代

年報沒有具名伺服器導軌競爭者，也說市占資料難以取得（第 74 頁）。同一伺服器的導軌須依承重、行程與機櫃干涉逐一驗證，換供應商需要重新認證；導軌不能替代供電母排。

## 業務曝險

導軌占營收 98%，年報把 114 年度成長歸因於 AI ASIC 與 GPU 產品，AI 伺服器出貨是主要曝險。美國是最大銷售地區（57%）。

## 風險

- **客戶集中**：前三大代工廠合計約 44%，雖由 OEM／CSP 指定，出貨仍經少數代工廠。
- **產品集中**：營收幾乎全部來自伺服器導軌。
- **原料**：鋼捲價格與中鋼供貨。
- **匯率**：114 年度產生淨外幣兌換損失 440,794 千元（第 90 頁）。

## 財務可取性

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- AI 伺服器導軌收入與市占：年報未公開。
