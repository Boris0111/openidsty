# 三方向研究擴充矩陣

對應 [design D2–D5](../openspec/changes/expand-ai-infrastructure-research/design.md) 與 [tasks](../openspec/changes/expand-ai-infrastructure-research/tasks.md)。基準為 a0791ded84fa22fad6efc6224cdd341481aad167，盤點日 2026-11-24；操作及網站閱讀證據見 [驗收紀錄](research-expansion-acceptance.md)。本文件保留必做範圍與證據位置，進度由 OpenSpec 的 task checkbox 判定。

## 填寫與驗收方式

- 下列產品的五面向是**待研究問題**，不是已證實論述。完成時將「待補」替換成本文章節連結、claim ID、來源 locator／read-scope、型號／版本／期間及實際查核日；不能只填來源首頁。
- 狀態逐列分為「分類存在／證據完成／內容審閱／網站走讀」。目前只核對檔案、ID 與 taxonomy；既有 deep、claims 或 offerings 均不表示本次研究已完成。證據、內容與網站三欄的「未」分別指本 change 尚未完成該項審查。
- 缺口依 not-researched／not-public／not-obtained／not-applicable 分開。初始列都是 not-researched；沒有讀原文不能改寫成未公開。核心用途或原理未查核時不得勾選內容 task。
- P1 原理與用途；P2 規格／製程與成本因素（數值附型號、版本、單位與測試條件）；P3 有條件路線比較；P4 公司實際交付；P5 需求傳導與風險。成本未取得同口徑資料時保留限制，不推算排名。
- 公司完成時補九段內容定位：供應角色、研究界線、產品與用途、商業模式、客戶與供應商、競爭與替代、業務曝險、風險、財務可取性。財務可取性只記來源與缺口。
- 新交付範圍先查台股、美股及已發現的其他關鍵市場，紀錄法律主體、既有 ID／aliases／legacy keys、候選納入／排除理由、去重及比較限制；未核對前不預造 product／role ID 或公司關係。

## 範圍核對

| 批次 | 核心產品 | 廣度研究範圍 | 優先公司 | 閱讀與比較交付 |
|---|---|---|---|---|
| A | 8 項 | 光纖連接組件、主機端網路介面 | 7 家 | 光／電互連比較與至少一個條件式需求案例，tasks 3.10–3.11 |
| B | 3 項 | 變壓、開關／配電、UPS、BBU、母線／busway、PDU／供電分配 | 6 家 | 設施／機櫃／板端分層比較與至少一個需求案例，tasks 4.10–4.11 |
| C | 3 項 | 增層介電材料、載板微孔加工、載板線路形成 | 9 家 | 規格 → 製程限制 → 有效產出 → 公司能力案例，tasks 5.10–5.11 |

廣度共 11 列為研究問題的分列，最終是否拆分／沿用 role 與 product 由證據裁決；數量不是新增檔案配額。現有 14 項核心產品的 claims 皆為空，僅為本次基準盤點；不代表相連公司沒有來源。

## A：核心產品五面向

| 產品／既有 role／task | P1 | P2 | P3 | P4 | P5 | 來源定位／適用範圍／查核日 | 具體缺口 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 光收發模組 [product-optical-transceiver](../industry-map/products/product-optical-transceiver.md)；[role-optical-module](../industry-map/roles/role-optical-module.md)；2.1、2.3 | 待補：電／光轉換、輸入輸出及鏈路位置 | 待補：速率、距離、波長、介面、型號與版本 | 待補：可插拔、LPO／CPO、銅互連的替代前提 | 待補：模組整合與 DSP／光元件分工 | 待補：埠速率改變、光鏈路需求與架構抵銷 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 光通訊 DSP [product-optical-dsp](../industry-map/products/product-optical-dsp.md)；[role-optical-dsp](../industry-map/roles/role-optical-dsp.md)；3.1 | 待補：訊號處理、介面及與雷射的分工 | 待補：調變、通道、速率與訊號限制 | 待補：同介面及同用途方案；無同口徑資料的限制 | 待補：DSP 與完整模組交付區別 | 待補：速率升級與 DSP 需求、架構移除 DSP 的條件 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 磷化銦雷射晶片 [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)；[role-optical-chip](../industry-map/roles/role-optical-chip.md)；3.2 | 待補：雷射晶粒作用及模組內位置 | 待補：材料、製程、測試與可用光源條件 | 待補：有條件的光源／整合路線比較 | 待補：晶粒、磊晶與後段整合不重複計算 | 待補：規格、良率及認證如何限制交付 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| III-V 族光通訊磊晶片 [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)；[role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md)；3.2 | 待補：III-V 磊晶結構與後續晶粒分工 | 待補：磊晶製程、材料及均勻性等原文支持的瓶頸 | 待補：依用途、材料及製程範圍比較 | 待補：磊晶交付不等於模組或客戶採用 | 待補：材料規格傳導與客戶認證／良率限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 重定時與橋接晶片 [product-retimer](../industry-map/products/product-retimer.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 待補：端點、協定、訊號恢復與連接位置 | 待補：速率、距離、介面與實際型號條件 | 待補：同協定光／電方案及不能替代情境 | 待補：重定時／橋接晶片的交付界線 | 待補：通道損耗及規格改變、架構抵銷 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 主動電纜 [product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 待補：端點與主動電纜作用 | 待補：協定、距離、速率、線材及功耗條件 | 待補：同用途光／電互連的比較與限制 | 待補：線纜整合和內部晶片的交付 | 待補：短距離鏈路需求與距離／介面限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 交換器晶片 [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)；[role-switch-silicon](../industry-map/roles/role-switch-silicon.md)；3.4 | 待補：交換功能與晶片／整機界線 | 待補：單埠、總頻寬、封裝及系統依賴 | 待補：scale-up／scale-out／跨機房適用條件 | 待補：晶片能力不等於交換器整機能力 | 待補：埠速率、拓樸與整機設計限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 資料中心交換器 [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)；[role-switch-system](../industry-map/roles/role-switch-system.md)；3.4 | 待補：交換器整機及網路位置 | 待補：埠組態、交換晶片、電熱與管理條件 | 待補：同系統用途比較；不以總頻寬無條件排名 | 待補：整機設計、製造及品牌交付區別 | 待補：拓樸與埠數需求、平台驗證與交付風險 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |

### A：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 光纖連接組件；3.5 | 待補：連接位置與光纖介面 | 待補：接頭、纖芯及適用光路的原文條件 | 待補：同介面可替換交付；既有連接角色去重 | 待補：組件供應與模組整合分工 | 待補：鏈路拓樸、纖芯需求與介面限制 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| 主機端網路介面；3.6 | 待補：主機端功能及與交換系統的分工 | 待補：協定、介面、速率及系統依賴 | 待補：既有互連晶片／網卡角色去重 | 待補：端點元件、卡或整機的交付裁決 | 待補：主機配置、協定及採用限制 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |

### A：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 博通 [company-avgo](../industry-map/companies/company-avgo.md)；3.7 | 本批交換晶片／光元件等實際交付；既有其他能力不代替查核 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 邁威爾 [company-mrvl](../industry-map/companies/company-mrvl.md)；3.7 | 光 DSP、交換或互連的適用產品／期間；新能力逐項支持 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Credo [company-crdo](../industry-map/companies/company-crdo.md)；3.8 | 電互連／DSP 的協定與同角色比較；能力、客戶、量產分開 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Astera Labs [company-alab](../industry-map/companies/company-alab.md)；3.8 | 互連介面與適用協定；不沿用無關競爭名單 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 智邦 [company-2345-tw](../industry-map/companies/company-2345-tw.md)；3.9 | 交換器整機交付、法律主體與採用證據 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 聯亞 [company-3081-two](../industry-map/companies/company-3081-two.md)；3.9 | 磊晶交付與應用；不能上推為完整模組或具名客戶 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 華星光 [company-4979-two](../industry-map/companies/company-4979-two.md)；3.9 | 光元件／模組交付層次，依具體產品文件區分 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |

## B：核心產品五面向

| 產品／既有 role／task | P1 | P2 | P3 | P4 | P5 | 來源定位／適用範圍／查核日 | 具體缺口 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 電源供應器與電源架 [product-power-shelf-psu](../industry-map/products/product-power-shelf-psu.md)；[role-rack-power-supply](../industry-map/roles/role-rack-power-supply.md)；4.1 | 待補：供電轉換位置、輸入輸出及負載 | 待補：效率、熱、額定／負載／測試條件 | 待補：相同負載的冗餘、維修及架構比較 | 待補：PSU、電源架與配電分工 | 待補：負載提升及容量限制、效率改善的抵銷 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 電源管理與電壓調節晶片 [product-pmic-voltage-regulator](../industry-map/products/product-pmic-voltage-regulator.md)；[role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md)；4.2 | 待補：控制、板端轉換及保護分工 | 待補：電壓、電流、熱及適用元件範圍 | 待補：控制晶片與整合方案的替代前提 | 待補：控制、功率元件與模組的交付區別 | 待補：負載規格、整合度與採用認證限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 高密度電源模組 [product-power-module](../industry-map/products/product-power-module.md)；[role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md)；4.2 | 待補：模組內轉換與板端位置 | 待補：電壓、電流、熱、保護及整合限制 | 待補：同負載／位置下分立與模組方案 | 待補：模組供應及系統整合責任 | 待補：功率密度需求與架構／散熱限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |

### B：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 資料中心變壓設備；4.3 | 待補：電網接入與電壓轉換位置 | 待補：容量、額定及交付條件 | 待補：同轉換位置／可靠度條件比較 | 待補：設備及系統整合責任 | 待補：容量需求、交期與接入條件 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| 開關／配電設備；4.4 | 待補：與變壓、UPS、機櫃配電的介面 | 待補：額定、保護及設備交付條件 | 待補：不同配電層級的替代限制 | 待補：可替換設備交付與角色去重 | 待補：接入、保護要求及設備交期 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| UPS；4.5 | 待補：不斷電功能與架構 | 待補：負載、備援時間、維修及可靠性 | 待補：UPS 與 BBU 的有條件比較 | 待補：設施端設備及整合責任 | 待補：備援需求、配置與維護限制 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| BBU；4.6 | 待補：備援、電源架與 UPS 分工 | 待補：介面、備援及維護條件 | 待補：同位置／時間下 UPS 與 BBU 替代限制 | 待補：電池、模組及系統責任 | 待補：機櫃架構、備援策略及採用缺口 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| 母線／busway；4.7 | 待補：設施／機櫃供電位置與介面 | 待補：額定、連接、熱與安裝條件 | 待補：不同層級母線不視為同商品 | 待補：依可替換交付拆分或沿用角色 | 待補：架構與部署需求；不加總跨層額定能力 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| PDU／供電分配；4.7 | 待補：供電分配位置與相連設備 | 待補：額定、插接、監測與整合條件 | 待補：同層級分配設備比較與限制 | 待補：PDU 與母線、電源架的邊界 | 待補：負載配置與備援策略的條件及抵銷 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |

### B：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 台達電 [company-delta-electronics](../industry-map/companies/company-delta-electronics.md)；4.8 | 本批電源與新增設備的型號／公司身分／市場限制 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 光寶科 [company-2301-tw](../industry-map/companies/company-2301-tw.md)；4.8 | PSU／電源架等本批實際型號與能力 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 康舒 [company-6282-tw](../industry-map/companies/company-6282-tw.md)；4.8 | 產品及法律主體；新增設備角色需另有證據 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 芯源系統 [company-mpwr](../industry-map/companies/company-mpwr.md)；4.9 | 板端控制／轉換的本批交付與比較條件 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Vicor [company-vicr](../industry-map/companies/company-vicr.md)；4.9 | 電源模組與架構適用範圍；供應關係需雙方證據 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Vertiv [company-vertiv](../industry-map/companies/company-vertiv.md)；4.9 | 設施供電的產品證據；既有液冷能力不代替新能力 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |

## C：核心產品五面向

| 產品／既有 role／task | P1 | P2 | P3 | P4 | P5 | 來源定位／適用範圍／查核日 | 具體缺口 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 2.5D 中介層封裝 [product-2p5d-interposer-package](../industry-map/products/product-2p5d-interposer-package.md)；[role-interposer-integration](../industry-map/roles/role-interposer-integration.md)；5.1 | 待補：中介層、晶粒與封裝整合分工 | 待補：製程、材料、布線與認證範圍 | 待補：同用途的整合路線；名稱不作角色證據 | 待補：整合服務、材料與中介層交付區別 | 待補：規格變化、良率及認證對有效產出的限制 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| 覆晶與委外封裝服務 [product-flip-chip-package-service](../industry-map/products/product-flip-chip-package-service.md)；[role-osat-assembly](../industry-map/roles/role-osat-assembly.md)；5.1 | 待補：覆晶與封裝服務流程／責任 | 待補：製程、材料、測試及認證範圍 | 待補：同交付服務的比較及適用限制 | 待補：封裝整合、測試與服務交付邊界 | 待補：晶粒／封裝規格傳導及良率／認證風險 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |
| ABF 封裝載板 [product-abf-substrate](../industry-map/products/product-abf-substrate.md)；[role-ic-substrate](../industry-map/roles/role-ic-substrate.md)；5.2 | 待補：堆疊、布線、微孔及封裝內位置 | 待補：線寬距、孔徑、層數、面積、翹曲、可靠度 | 待補：玻璃核心等路線的研究／認證／商業化階段 | 待補：完成載板與材料／設備的不同交付 | 待補：規格 → 製程限制 → 有效產出；不以面積換算收入 | 待查原文／待核型號版本期間／未查核 | not-researched：五面向尚未核讀；成本及同條件數值待查 | 已有／未／未／未 |

### C：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 增層介電材料；5.3 | 待補：增層絕緣與製程介面 | 待補：材料性能、加工與可靠度條件 | 待補：同用途材料路線及既有角色去重 | 待補：材料不等於完成載板 | 待補：布線／堆疊需求與材料認證限制 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| 載板微孔加工；5.4 | 待補：微孔製程步驟與交付位置 | 待補：適用材料、孔徑及加工限制 | 待補：設備／製程替代前提 | 待補：製程步驟與設備供應界線 | 待補：規格與設備需求；能力不推定客戶良率 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |
| 載板線路形成；5.5 | 待補：線路形成步驟與相連材料 | 待補：線寬距、材料及製程／設備限制 | 待補：依工序與適用材料比較 | 待補：材料、製程服務與設備分開裁決 | 待補：規格、有效產出與採用限制 | 未研究；待補 locator、版本期間與查核日 | not-researched：既有分類去重、台股／美股／其他關鍵市場候選、法律主體及納入／排除理由皆待查；沿用／新增 ID 待裁決 | 待裁決／未／未／未 |

### C：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 台積電 [company-tsmc](../industry-map/companies/company-tsmc.md)；5.6 | 封裝整合與服務範圍、認證／商業化階段 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 日月光投控 [company-3711-tw](../industry-map/companies/company-3711-tw.md)；5.6 | 集團／法律主體與實際封裝交付；不推定具名採用 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 艾克爾 [company-amkr](../industry-map/companies/company-amkr.md)；5.7 | 封裝／測試如何支撐本批角色，核對納入／排除 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 力成 [company-6239-tw](../industry-map/companies/company-6239-tw.md)；5.7 | 不因同屬封測建立不受支持的產品關聯 | 頁面存在，deep | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Ibiden [company-4062-t](../industry-map/companies/company-4062-t.md)；5.8 | 載板產品、技術／交付差異；九段內容實質檢閱後才標 deep | 頁面存在，basic | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| Shinko [company-private-shinko](../industry-map/companies/company-private-shinko.md)；5.8 | 身分、載板能力、下市／財務可取性限制；九段檢閱 | 頁面存在，basic | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 欣興 [company-3037-tw](../industry-map/companies/company-3037-tw.md)；5.9 | 產品組合、製程、認證與曝險；不將總營收／面積當產品出貨 | 頁面存在，basic | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 南電 [company-8046-tw](../industry-map/companies/company-8046-tw.md)；5.9 | 產品組合、製程、認證與曝險；九段檢閱後才標 deep | 頁面存在，basic | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |
| 景碩 [company-3189-tw](../industry-map/companies/company-3189-tw.md)；5.9 | 載板能力、同條件比較、合格產出限制；九段檢閱 | 頁面存在，basic | 待逐段檢閱及連回適用產品 P1–P5 | 既有 claims 僅作線索；本批原文、版本期間與查核日待補 | not-researched：本批交付及比較尚未重查；客戶、認證、量產與收入分別待查 | 未／未／未 |

## 既有供應角色逐列核對

以下角色確實存在並經 taxonomy 連到本次核心產品；分類本身不證明公司交付。新角色的證據裁決另見各批廣度表。

| 既有角色 | 本次對應產品與 task | 邊界與來源定位 | 分類／證據／內容／網站 |
|---|---|---|---|
| [role-optical-module](../industry-map/roles/role-optical-module.md) | [product-optical-transceiver](../industry-map/products/product-optical-transceiver.md)（2.1、2.3） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-optical-dsp](../industry-map/roles/role-optical-dsp.md) | [product-optical-dsp](../industry-map/products/product-optical-dsp.md)（3.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-optical-chip](../industry-map/roles/role-optical-chip.md) | [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)（3.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md) | [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)（3.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md) | [product-retimer](../industry-map/products/product-retimer.md)（3.3）、[product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)（3.3） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-switch-silicon](../industry-map/roles/role-switch-silicon.md) | [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)（3.4） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-switch-system](../industry-map/roles/role-switch-system.md) | [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)（3.4） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-rack-power-supply](../industry-map/roles/role-rack-power-supply.md) | [product-power-shelf-psu](../industry-map/products/product-power-shelf-psu.md)（4.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md) | [product-pmic-voltage-regulator](../industry-map/products/product-pmic-voltage-regulator.md)（4.2）、[product-power-module](../industry-map/products/product-power-module.md)（4.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-interposer-integration](../industry-map/roles/role-interposer-integration.md) | [product-2p5d-interposer-package](../industry-map/products/product-2p5d-interposer-package.md)（5.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-osat-assembly](../industry-map/roles/role-osat-assembly.md) | [product-flip-chip-package-service](../industry-map/products/product-flip-chip-package-service.md)（5.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-ic-substrate](../industry-map/roles/role-ic-substrate.md) | [product-abf-substrate](../industry-map/products/product-abf-substrate.md)（5.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |

## 閱讀入口、比較與需求案例

| 範圍／task | 應用與既有入口 | 比較／傳導內容的閱讀位置 | 來源、限制與走讀紀錄 |
|---|---|---|---|
| 樣本 2.1–2.3 | [AI networking](../industry-map/applications/application-ai-networking.md) → 光收發模組 → A 代表公司 → 來源 | 代表公司依證據選取後連回 3.7／3.8／3.9；未先指定已供應完整模組 | 尚未建立樣本；桌機與手機待 Boris 確認，見驗收紀錄 |
| A 3.10–3.11 | [AI networking](../industry-map/applications/application-ai-networking.md)、[networking](../industry-map/ai-server/networking.md)、[CPO](../industry-map/themes/cpo-silicon-photonics.md) | 待建立 research 頁；可插拔／LPO／CPO／銅的有條件比較；scale-up／scale-out／跨機房分開 | not-researched；每步 fact／inference、成立與失效條件、追蹤來源待補；網站未走讀 |
| B 4.10–4.11 | [AI rack power](../industry-map/applications/application-ai-rack-power.md)、[power](../industry-map/ai-server/power.md)、[power discrete](../industry-map/semiconductor/power-discrete.md)；供電題材沿用既有 ID，待查適用項 | 待建立 research 頁；設施 → 機櫃 → 板端，分開容量、架構、交期與負載 | not-researched；抵銷情境、原文與追蹤來源待補；不擴至發電／輸電全產業；網站未走讀 |
| C 5.10–5.11 | [chip integration](../industry-map/applications/application-chip-integration.md)、[advanced packaging](../industry-map/ai-server/advanced-packaging.md)、[substrate](../industry-map/ai-server/substrate.md)；材料／設備／測試入口隨交付裁決 | 待建立 research 頁；中介層、載板、PCB 分層；規格 → 製程限制 → 有效產出 → 公司能力 | not-researched；認證／良率假設、反向條件與來源待補；網站未走讀 |
| 共用 6.1–6.6 | 全部上述穩定 ID、跨方向共用公司及研究連結 | 三種影響遍歷及回路、delta specs 對照、同版預覽／發布／公開快照 | 未執行；完整證據欄見驗收紀錄，不把基準驗證當成最終成功 |

## 矩陣建置核對（task 1.2）

2026-11-24 對照 design D3：14 個明列核心 product ID 與 22 個優先 company ID 均有獨立列且檔案存在；12 個既有供應 role 依 taxonomy 展開。A 的 2 個、B 的 6 個、C 的 3 個廣度範圍逐項列入，不因尚未取得證據刪除。三批入口、比較、需求案例與網站驗收各有 task 對照。

這項核對只驗收矩陣覆蓋與欄位，沒有宣稱產品、公司或新增角色的研究完成。後續每個內容 task 必須更新其列中的實際本文、主張、原文定位、期間、查核日及閱讀結果。
