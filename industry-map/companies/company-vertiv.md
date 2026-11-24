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
reviewed: '2026-11-24'
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
  - id: powerdirect-33kw-shelf-delivery
    statement: "Vertiv PowerDirect PSS5033-21N2 為 50 VDC、33 kW ORv3 電源架，含六槽，電源單元 R50-5500E4 為 5.5 kW。"
    confidence: well-supported
    conditions:
    - "132 kW 是文件的系統擴充配置；實配冗餘、輸入型式、架側 BBU 與相符型號分開。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-powerdirect-ordering-datasheet
      url: https://www.vertiv.com/4994f8/globalassets/products/critical-power/dc-power-systems/vertiv-powerdirect-it-rack/vertiv-powerdirect-it-rack-ds-en-na.pdf
      locator: "Description／Ordering Information"
      read-scope: "查 50 V、33 kW、個別機型與 PSU 訂購資訊。"
      stance: supporting
      applicable-period: "北美資料表"
  - id: powerbar-impb-delivery
    statement: "Vertiv PowerBar iMPB 北美版為 3 相 600 VAC、160–800 A 系統，銅導體上限 600 A、鋁導體上限 800 A。"
    confidence: well-supported
    conditions:
    - "與分接盒、當地認證、故障額定和各分路限制配套。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-powerbar-impb-datasheet
      url: https://www.vertiv.com/492f82/globalassets/shared/vertiv-powerbar-impb-data-sheet-sl-70397.pdf
      locator: "p.1 Overview、Standard features"
      read-scope: "查 AC、額定、可配置 tap-off box。"
      stance: supporting
      applicable-period: "SL-70397，北美版"
  - id: geist-rpdu-delivery
    statement: "Vertiv Geist UU30009L 垂直 rPDU 提供插座切換及監控，型錄列三相星形 230／415 V、16 A 選項及 C13／C19 插座。"
    confidence: well-supported
    conditions:
    - "須配合正確進線纜、地區規格、相別與分路降額。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-geist-universal-rpdu
      url: https://www.vertiv.com/globalassets/products/critical-power/power-distribution/vertiv-geist-rpdu---brochure.pdf
      locator: "Universal Rack PDU Model Chart，UU30009L"
      read-scope: "查接線選項、額定、分路和插座。"
      stance: supporting
      applicable-period: "該型錄料號"
  - id: vertiv-power-rack-bbu-design
    statement: "Vertiv 公布 800 VDC power rack 內建 BBU，設計 hold-up 至少 50 秒。"
    confidence: well-supported
    conditions:
    - "源為整合設計，與機櫃低壓 BBU、同負載實測、銷售及出貨分開。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-800vdc-power-rack-2026
      url: https://www.vertiv.com/en-in/about/news-and-events/news-releases/2026/vertiv-advances-800-vdc-power-architectures-to-support-growing-ai-data-center-demands/
      locator: "800 VDC power rack"
      read-scope: "查整合 BBU、設計 hold-up 時間及機架與 IT 轉換的分離。"
      stance: supporting
      applicable-period: "2026 供應商公告"
  - id: trinergy-ups-delivery
    statement: "Vertiv Trinergy 480 VAC 規格列 1,500／2,000／2,500 kW 標稱及 35°C 最大有功功率。"
    confidence: well-supported
    conditions:
    - "這是指定機型與溫度的功率能力，續航取決於電池配置。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-trinergy-ups-brochure
      url: https://www.vertiv.com/4a095b/globalassets/shared/vertiv-trinergy-ups-brochure-sl-71331.pdf
      locator: "Technical Data，Active power／Output"
      read-scope: "查 35°C、480 VAC 的 1,500／2,000／2,500 kW 配置。"
      stance: supporting
      applicable-period: "SL-71331、該機型表"
  - id: powerboard-switchgear-delivery
    statement: "Vertiv PowerBoard 低壓開關設備可配置 800–6,300 A，含分隔及依案場配置的保護。"
    confidence: well-supported
    conditions:
    - "是低壓產品範圍；額定、預期短路電流及分隔型式須按選型。"
    reviewed: '2026-11-24'
    evidence:
    - source-id: vertiv-powerboard-lv-switchgear
      url: https://www.vertiv.com/en-asia/products-catalog/critical-power/switchgear/vertiv-ei-low-voltage-switchgear-iec/
      locator: "Overview、Features"
      read-scope: "核對低壓額定電流範圍與保護繼電器、箱體。"
      stance: supporting
      applicable-period: "PowerBoard 低壓產品頁"
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

Vertiv Holdings Co（VRT，NYSE）具備[低壓開關](/next?focus=product-datacenter-switchgear)、[設施 UPS](/next?focus=product-facility-ups)、[busway](/next?focus=product-datacenter-busway)、[rPDU](/next?focus=product-rack-pdu)與機架交付。

Vertiv 在[散熱環節](/next?focus=segment-thermal)以[液對液 CDU](/next?focus=product-liquid-to-liquid-cdu)等熱管理產品參與液冷，同時提供供電、母線、機櫃與服務。它跨足[冷卻液分配](/next?focus=role-coolant-distribution)與機櫃供電等多個角色，研究液冷時要先辨認交付的是哪一段。

## 研究界線

低壓及各地區型錄、備援時間、中壓配置及實配系統依各別來源。已核實產品能力；未據此新增具名採用或關係。

本頁以 FY2025 10-K（簽署日 2026-02-13）與公開產品頁為依據。10-K 沒有 CDU 或 direct-to-chip 的產品線名稱，也沒有液冷收入；產品頁的額定換熱量附有條件，不能當成個別場址已驗收的數字。

## 產品與用途

PowerBoard 低壓 800–6,300 A、Trinergy 480 V 指定機型、PowerBar iMPB 北美版、Geist UU30009L 與 33 kW [電源架](/next?focus=product-power-shelf-psu)各有公開規格；800 VDC power rack 另見[整合 BBU](/next?focus=product-rack-battery-backup)公告。

10-K 把主要提供項目分成兩類：產品，涵蓋 AC／DC 供電、熱管理（含氣冷與液冷）、中低壓開關設備、母線、整合模組、機櫃與儲能；以及服務與備品，涵蓋預防保養、驗收測試、遠端監控與流體管理等。CoolChip CDU 產品頁另列液對液與液對氣型號。

## 商業模式

以直銷為主，約 3,000 名業務人員，並透過通路夥伴、經銷、IT 轉售商與 OEM 銷售。2025 年產品淨銷售 8,390.6 百萬美元、服務與備品 1,839.3 百萬美元。報告分部依地區：美洲、亞太、歐洲中東非洲，2025 年分別占淨銷售 62%、20%、18%。

## 客戶與供應商

終端市場是資料中心（hyperscale／cloud、colocation、neocloud、enterprise）、通訊網路與商工業。10-K 雖列出各類業者的產業例子，但沒有說明它們是 Vertiv 的客戶，也沒有揭露單一客戶占比，只在風險因素指出大型業者占客戶基礎的重要部分、議價力較強。

供應端依賴鋼、銅、鋁與電子元件，通常有多家供應商，部分項目為單一來源；10-K 也提到部分供應商同時是競爭者。

## 競爭與替代

與台達 DPH 或 Schneider Galaxy 比較 UPS，須對齊 kW、溫度、電池／旁路及冗餘。busway 與台股東元旗下 TECOBAR 按安裝級別比較，架內 AC rPDU 又有不同接口。

10-K 列出的利基型競爭者包括[台達電](/next?focus=company-delta-electronics)、Stulz、Johnson Controls 與 Socomec，大型全球競爭者包括 Schneider Electric、Eaton、Legrand 與華為。競爭依產品領域而不同；在液冷分配這一角色，可比較的是同角色的其他 CDU 供應者，如[雙鴻](/next?focus=company-auras)，但同角色不代表互相爭取同一專案。

## 業務曝險

營收分部維持地區口徑。案場接入、設備交期、服務與試驗分屬不同收入時點；33 kW shelf 與 UPS／冷卻不能由地區數字拆出。

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
