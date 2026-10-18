---
schema-version: research-v1
entity-id: company-vertiv
kind: company
name-zh: Vertiv
aliases: [Vertiv, Vertiv Holdings]
summary: 資料中心供電、熱管理與服務的基礎設施供應商；10-K 以地區分部，未單獨揭露液冷收入。
legacy-keys:
- VRT
listings:
- ticker: VRT
  market: US
  exchange: XNYS
  share-class: Class A common stock
  valid-from: null
  valid-to: null
source-identifiers:
- provider: sec-cik
  value: '1674101'
research-depth: deep
reviewed: '2026-10-18'
financial-reporting:
  primary-source-family: sec
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2025-01-01'
  calendar-valid-to: null
  evidence:
    - source-id: vertiv-10k-2025
      url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
      locator: 10-K 封面 "For the fiscal year ended December 31, 2025"；Section 12(b) 列 Class A common stock、VRT、New York Stock Exchange
      read-scope: 已讀封面、Item 1–15 與主要財務報表
      stance: supporting
      applicable-period: FY2025（2025 曆年）
roles:
- segment-id: segment-thermal
  description: 資料中心熱管理與冷卻液分配單元
  tier: 1
  baseline-path: ai-server/thermal.md
claims:
  - id: coolchip-l2l-capability
    statement: Vertiv 的 CoolChip CDU 公開產品表列有液對液型號，也另外列出液對氣型號。
    confidence: well-supported
    conditions: [以本輪讀到的產品家族為準，需按具體型號與測試條件驗證]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-coolchip-product-reading
        url: https://www.vertiv.com/en-us/products-catalog/thermal-management/high-density-solutions/vertiv-coolchip-cdu/
        locator: CoolChip CDU／Product Family 與 Model Specifications Overview
        read-scope: 已讀公開家族說明、型號表與功能，未讀需填表的下載文件
        stance: supporting
        applicable-period: 2026-10-16 所讀產品頁；頁面發布日未提供
  - id: infrastructure-business-scope
    statement: Vertiv 的公開定位涵蓋供電、冷卻與服務，不能把公司整體收入直接當作液冷產品收入。
    confidence: inference
    conditions: [業務範圍可由公司介紹核對；產品收入仍需獨立財務揭露]
    reviewed: '2026-10-16'
    evidence:
      - source-id: vertiv-company-scope-reading
        url: https://www.vertiv.com/en-us/about/about-us/
        locator: About Us／end-to-end infrastructure 與 Powering and cooling the AI revolution
        read-scope: 已讀公司公開業務範圍，未以頁面營收摘要推算液冷占比
        stance: supporting
        applicable-period: 2026-10-16 所讀公司介紹；頁面公司資料基準為 2025 年底
  - id: offering-categories
    statement: 10-K 將主要產品分為 products 與 services & spares；產品包含 AC／DC 供電管理、熱管理、中低壓開關設備、母線、氣冷與液冷熱管理產品、機櫃與儲能等。
    confidence: well-supported
    conditions: [產品清單是業務範圍，不揭露各產品收入]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1. Business／Our Offerings（Products；Services & spares）
        read-scope: 已讀 Our Offerings 全段
        stance: supporting
        applicable-period: FY2025 10-K
  - id: geographic-segments
    statement: 10-K 以美洲、亞太與歐洲中東非洲三個地區作為報告分部；2025 年淨銷售額 10,229.9 百萬美元，62% 在美洲、20% 在亞太、18% 在歐洲中東非洲。
    confidence: well-supported
    conditions: [分部依地區而非產品線，無法由分部資料拆出熱管理或液冷]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1. Business／Our Business；Item 7. MD&A／Business Segments
        read-scope: 已讀分部說明與 MD&A 分部表
        stance: supporting
        applicable-period: FY2025
  - id: end-markets-and-channels
    statement: 10-K 列出三個終端市場：資料中心（含 hyperscale／cloud、colocation、neocloud、enterprise）、通訊網路與商工業；以直銷為主，約 3,000 名業務人員，另有通路夥伴、經銷與 OEM。
    confidence: well-supported
    conditions: [10-K 舉例的雲端與託管業者是產業例子，文件未說明它們是 Vertiv 的客戶]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1. Business／Our Customers；Sales and Marketing
        read-scope: 已讀客戶市場、舉例與銷售通路段落
        stance: supporting
        applicable-period: FY2025 10-K
  - id: large-customer-leverage
    statement: 10-K 風險因素指出，大型通訊網路、雲端／hyperscale、neocloud 與託管業者占客戶基礎的重要部分且議價力較強，但未揭露單一客戶占比。
    confidence: well-supported
    conditions: [未揭露客戶集中百分比，不能推算單一客戶依賴度]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1A. Risk Factors／Risks Related to Our Customers and Our Industry
        read-scope: 已讀大型客戶議價與客戶整併風險段落
        stance: supporting
        applicable-period: FY2025 10-K
  - id: named-competitors
    statement: 10-K 將競爭者分為利基型（台達電、Stulz、Johnson Controls、Socomec）與大型全球型（Schneider Electric、Eaton、Legrand、華為）。
    confidence: well-supported
    conditions: [競爭範圍依產品領域而異，名單不代表各領域都直接競爭]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1. Business／Competition
        read-scope: 已讀競爭段落與 Item 1A 的重複名單
        stance: supporting
        applicable-period: FY2025 10-K
  - id: liquid-cooling-strategy
    statement: 10-K 的 MD&A 說明 AI 工作負載帶來混合氣冷與液冷的需求，公司持續擴充熱管理產品；2025 年 12 月收購 PurgeRite，以擴充液冷與混合冷卻應用的熱管理服務。
    confidence: well-supported
    conditions: [策略與收購說明不等於液冷收入；10-K 未提 CDU 或 direct-to-chip 產品線名稱]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 7. MD&A／Outlook and Trends（Thermal Management Portfolio Expansion；Strengthened Services Capabilities）
        read-scope: 已讀熱管理與服務擴充段落
        stance: supporting
        applicable-period: FY2025 10-K
  - id: supply-and-materials
    statement: 10-K 稱產品依賴鋼、銅、鋁與各種電子元件，原物料通常來自多家供應商，但部分材料或元件因技術、供應或價格因素採單一來源。
    confidence: well-supported
    conditions: [未揭露具名供應商或採購占比]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1. Business／Raw Materials and Supply Chain；Item 1A／Risks Related to Our Business Operations
        read-scope: 已讀供應鏈與單一來源風險段落
        stance: supporting
        applicable-period: FY2025 10-K
  - id: backlog-and-mix
    statement: 10-K 揭露 2025 年底估計訂單積壓約 150 億美元（2024 年底約 72 億美元）；損益表中 2025 年產品淨銷售 8,390.6 百萬美元、服務 1,839.3 百萬美元。
    confidence: well-supported
    conditions: [風險因素同時提醒積壓訂單未必全數實現；產品與服務拆分不等於熱管理或液冷拆分]
    reviewed: '2026-10-18'
    evidence:
      - source-id: vertiv-10k-2025
        url: https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm
        locator: Item 1A／"We may not realize all of the sales expected from our backlog"；Item 8／Consolidated Statements of Earnings
        read-scope: 已讀積壓訂單風險段與損益表
        stance: supporting
        applicable-period: FY2025 與 FY2024
gaps:
- status: not-public
  reason: 10-K 以地區分部，未單獨揭露液冷、CDU 或熱管理收入，也未揭露客戶名稱與單一客戶占比。
- status: not-obtained
  reason: 10-K 附註（含收入拆分 Note 3 與分部 Note 13）本輪未取得全文，相關口徑待補讀。
---

## 供應角色

Vertiv 在[散熱環節](/next?focus=segment-thermal)以[液對液 CDU](/next?focus=product-liquid-to-liquid-cdu)等熱管理產品參與液冷，同時提供供電、母線、機櫃與服務。它跨足[冷卻液分配](/next?focus=role-coolant-distribution)與機櫃供電等多個角色，研究液冷時要先辨認交付的是哪一段。

## 研究界線

本頁以 FY2025 10-K（簽署日 2026-02-13）與公開產品頁為依據。10-K 沒有 CDU 或 direct-to-chip 的產品線名稱，也沒有液冷收入；產品頁的額定換熱量附有條件，不能當成個別場址已驗收的數字。

## 產品與用途

10-K 把主要提供項目分成兩類：產品，涵蓋 AC／DC 供電、熱管理（含氣冷與液冷）、中低壓開關設備、母線、整合模組、機櫃與儲能；以及服務與備品，涵蓋預防保養、驗收測試、遠端監控與流體管理等。CoolChip CDU 產品頁另列液對液與液對氣型號。

## 商業模式

以直銷為主，約 3,000 名業務人員，並透過通路夥伴、經銷、IT 轉售商與 OEM 銷售。2025 年產品淨銷售 8,390.6 百萬美元、服務與備品 1,839.3 百萬美元。報告分部依地區：美洲、亞太、歐洲中東非洲，2025 年分別占淨銷售 62%、20%、18%。

## 客戶與供應商

終端市場是資料中心（hyperscale／cloud、colocation、neocloud、enterprise）、通訊網路與商工業。10-K 雖列出各類業者的產業例子，但沒有說明它們是 Vertiv 的客戶，也沒有揭露單一客戶占比，只在風險因素指出大型業者占客戶基礎的重要部分、議價力較強。

供應端依賴鋼、銅、鋁與電子元件，通常有多家供應商，部分項目為單一來源；10-K 也提到部分供應商同時是競爭者。

## 競爭與替代

10-K 列出的利基型競爭者包括[台達電](/next?focus=company-delta-electronics)、Stulz、Johnson Controls 與 Socomec，大型全球競爭者包括 Schneider Electric、Eaton、Legrand 與華為。競爭依產品領域而不同；在液冷分配這一角色，可比較的是同角色的其他 CDU 供應者，如[雙鴻](/next?focus=company-auras)，但同角色不代表互相爭取同一專案。

## 業務曝險

公司整體受資料中心與 AI 需求帶動：2025 年底估計訂單積壓約 150 億美元，2024 年底約 72 億美元。液冷只是熱管理的一部分，10-K 沒有單獨揭露；PurgeRite 收購擴充的是液冷與混合冷卻的服務能力，不等於產品收入。

## 風險

- **需求循環**：成長仰賴資料中心與通訊基礎設施的持續擴張，需求下降會直接影響產品需求。
- **大型客戶議價**：大型業者占比高，可能壓低價格條件。
- **積壓訂單不一定實現**：訂單可能延後或取消。
- **原物料與供應鏈**：鋼、銅、鋁與電子元件價格波動，部分元件單一來源。
- **貿易政策**：關稅或貿易衝突可能提高成本並削弱價格競爭力。

## 財務可取性

- SEC 公開財務資料 已自動取得標準科目（本機 393 個財務序列）；主要申報來源設為 SEC、會計年度為曆年。
- 產品與服務淨銷售、地區分部營收與營業利益可由 10-K 損益表與 MD&A 核對。
- 液冷、CDU 與熱管理收入：10-K 未公開。
- 附註中的收入拆分口徑本輪未取得全文。
