---
schema-version: research-v1
entity-id: company-2345-tw
kind: company
name-zh: 智邦
aliases:
- Accton
- 智邦科技
- 智邦科技股份有限公司
- Accton Technology Corporation
summary: 網通設備廠；114 年營收成長 124.9%，網路應用設備占 62%、網路交換器占 35%，最大客戶占 52%，美洲占銷售 81%。
legacy-keys:
- 2345.TW
listings:
- ticker: 2345.TW
  market: TW
  exchange: XTAI
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報第 79 頁（PDF 第 83 頁）主要產品銷售地區，113 與 114 年度並列；致股東報告書營收與淨利
    read-scope: 已讀銷售地區表與致股東報告書
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-networking
  description: 資料中心交換器
  tier: 1
  baseline-path: ai-server/networking.md
claims:
- id: product-mix
  statement: 年報揭露 114 年合併營收 2,483.20 億元，較前一年成長約 124.9%，稅後淨利 263.06 億元；營業比重為網路應用設備 62%、網路交換器 35%、網路接取設備 1%、其他 2%。商品項目包括 200G／400G／800G 與 10G–100G 資料中心交換器、模組化光纖交換機、電信路由器與企業無線基地台。
  confidence: well-supported
  conditions:
  - 年報未說明「網路應用設備」包含哪些產品，不能直接等同交換器或 AI 加速器
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報致股東報告書（PDF 第 5 頁）；第 70 頁（PDF 第 74 頁）營業比重與商品項目
    read-scope: 已讀營業比重、商品項目與致股東報告書
    stance: supporting
    applicable-period: 114 年度
- id: ai-product-lines
  statement: 年報稱自 2018 年布局 AI 產品線，由加速器模組與智慧網卡設計起步，擴展至 AI 加速卡與資料處理器，並稱相關產品已導入全球主要 AI 資料中心與雲端平台；另描述以運算托盤與交換托盤組成的機櫃式伺服器設計。
  confidence: needs-verification
  conditions:
  - 公司自述，未揭露客戶、出貨或收入；不能據此把智邦列為加速器或伺服器供應者
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報第 75–76 頁（PDF 第 79–80 頁）技術與研發概況
    read-scope: 已讀研發與產品技術段落
    stance: supporting
    applicable-period: 114 年度年報
- id: switch-roadmap
  statement: 年報列出 51.2T 交換器與 800G 光介面已獲廣泛採用，並發展 102T 交換器與 1.6T 光互連；另在 OCP 2025 展示 1.6T 全水冷交換器平台。
  confidence: inference
  conditions:
  - 展示與研發不等於量產出貨；採用程度為公司自述
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報致股東報告書研發亮點（PDF 第 5 頁）；第 76 頁（PDF 第 80 頁）液冷交換器
    read-scope: 已讀研發亮點與液冷段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報主要銷貨客戶表顯示，114 年客戶甲占銷貨 52%（113 年 32%），113 年客戶乙占 12%；主要供應商 A 占進貨 11%（113 年 17%）。
  confidence: well-supported
  conditions:
  - 客戶與供應商以代號揭露，名稱未公開
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報第 85 頁（PDF 第 89 頁）主要進銷貨客戶
    read-scope: 已讀主要進銷貨表
    stance: supporting
    applicable-period: 113 至 114 年度、115 年第 1 季
- id: sales-regions
  statement: 年報揭露 114 年度銷售地區為美洲 81%、內銷 7%、歐洲 7%、亞太 5%（113 年度美洲 74%）。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報第 79 頁（PDF 第 83 頁）主要產品之銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: market-share-view
  statement: 年報引用 Dell'Oro Group，稱 2025 年資料中心乙太網交換機市場由 Arista 領先，智邦、Celestica 與 NVIDIA 的市占增幅最明顯。
  confidence: needs-verification
  conditions:
  - 第三方研究經公司轉述，未核對原始報告
  reviewed: '2026-10-18'
  evidence:
  - source-id: accton-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=2345&year=115&mtype=F&
    locator: 114 年度年報第 80 頁（PDF 第 84 頁）市場占有率
    read-scope: 已讀市場占有率段落
    stance: supporting
    applicable-period: 2025 年市場資料
- id: as9817-64o-system-delivery
  statement: "智邦 AS9817-64O 整合 Tomahawk 5 BCM78900，列 64×800GbE OSFP800、ONIE、2RU 及備援風扇與電源。公司 2025 年報分別描述 400G／800G 產量擴充及 1.6T 液冷展示。"
  confidence: well-supported
  conditions:
  - "AS9817-64O 型錄支持整機配置；不推定實際出貨客戶或 ASIC 採購量。展出世代不能當作量產機型。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: accton-as9817-64o-datasheet
    url: https://www.accton.com/wp-content/uploads/2023/09/2023-036-AS9817-64O_Accton-R01-20230905-1.pdf
    locator: "Key Features、Specifications"
    read-scope: "已讀埠、系統晶片、機構及軟體安裝環境。"
    stance: supporting
    applicable-period: "E092023-AP-R01"
  - source-id: accton-annual-report-2025-ir
    url: https://www.accton.com/wp-content/uploads/2026/06/2025-Annual-Report.pdf
    locator: "Letter to Shareholders：R&D highlights；DLC 段"
    read-scope: "已讀 51.2T／800G、102T／1.6T 的商業化進度差異。"
    stance: supporting
    applicable-period: "2025 年報、OCP 2025 展示"
gaps:
- status: not-public
  reason: 年報未說明「網路應用設備」的產品組成，也未揭露客戶名稱與 AI 相關收入。
- status: not-obtained
  reason: Dell'Oro 原始市占報告為付費資料，未取得。
---

## 供應角色

智邦科技股份有限公司（Accton Technology Corporation，2345.TW）以 AS9817-64O 為[資料中心交換器](/next?focus=product-datacenter-switch)整機例，整合博通晶片、前面板、PSU、散熱與 NOS 安裝環境。

智邦在[網路環節](/next?focus=segment-networking)屬[資料中心交換器系統](/next?focus=role-switch-system)，供應[資料中心交換器](/next?focus=product-datacenter-switch)。年報也描述 AI 加速卡、智慧網卡與機櫃式伺服器設計，但沒有收入或客戶證據，本頁不把它列為加速器或伺服器供應者。

## 研究界線

重讀 2025 年報與 AS9817-64O 資料表。機型的硬體規格、2025 年報中的產品家族進度、OCP 會場展示與實際商用採用分別記錄。

本頁以 114 年度股東會年報為依據。最大的營業類別「網路應用設備」（62%）在年報中沒有定義，不能直接當成交換器或 AI 加速器收入；AI 產品導入與市占增長屬公司自述或轉述，標為待核實。

## 產品與用途

AS9817-64O 以 BCM78900 做 64×800GbE OSFP800；在相同埠下比對 2×400／4×200／8×100 的 breakout、ONIE 及風道。年報稱 2025 年擴充高速交換器產量，1.6T 水冷機型列為展示。智慧網卡或 DPU 目前只有年報描述，尚缺本批可核成卡料號。

- **資料中心交換器**：200G／400G／800G 與 10G–100G 機型，51.2T 已採用、102T 開發中（第 70 頁、致股東報告書）。
- **網路應用設備**：占 62%，年報未說明組成。
- **電信與企業網路**：路由器、接取設備、企業與電信級無線基地台（第 70 頁）。
- **開發中**：1.6T 全水冷交換器、CXL 交換器與 Smart Appliance（第 76 頁、致股東報告書）。

## 商業模式

交付可涵蓋機箱、PCB、軟體安裝環境與共同設計。ASIC、NOS 支援與終端現場部署各有來源，定義 ODM／JDM 的比較範圍。

為國際大廠設計製造網通設備，並提供開放式網路軟體；生產據點在台灣、越南與美國，規劃擴展墨西哥與馬來西亞（第 77 頁）。114 年營收 2,483.20 億元、稅後淨利 263.06 億元（致股東報告書）。

## 客戶與供應商

AS9817-64O 型錄支持 BCM78900 設計，但未揭露該機型的下游買方、數量或現場資格。年報最大客戶以代號揭露，不能反推型號客群。

客戶甲占 114 年銷貨 52%，前一年是 32%；供應商 A 占進貨 11%（第 85 頁）。主要零組件至少維持兩家供應商，並提供 12–18 個月需求預測給主要晶片與零件商（第 84 頁）。

## 競爭與替代

與 Arista 7060X6-64PE 比較同為 64×800G 2RU 整機時，智邦附 ONIE，Arista 含 EOS；要固定 NOS 功能、可用埠、互通及風道再比價格和功耗。

年報引用 Dell'Oro，把 Arista、Celestica 與 NVIDIA 列為資料中心交換機市場的主要參與者（第 80 頁）。同一角色的白牌交換器廠，可依交換晶片、埠速與散熱方案比較；交換器系統不能替代交換晶片。

## 業務曝險

交換器業務會隨網路架構、有效埠和箱數變動。全年交換器營收比重含其他規格，未單列 800G 或 1.6T。

營收倍增、最大客戶占比由 32% 升到 52%、美洲占 81%，曝險集中在北美雲端客戶的資料中心建置；但年報沒有拆出 AI 相關收入。

## 風險

電熱設計、NOS、光模組互通與樣品轉量產是不同關卡。對已量產的產品家族，也要確認場址、出貨與客戶的集中風險。

- **客戶集中**：單一客戶占五成以上。
- **地緣政治與關稅**：美國關稅政策促使擴充台灣與越南產能（第 84 頁）。
- **零組件供應**：關鍵零組件可能短缺（第 84 頁）。

## 財務可取性

從公開資訊觀測站或公司年報核對產品分類與主要銷貨資料，未拆個別機型、800G 或展示平台收入。

- 月營收、損益與負債摘要可由證交所公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 網路應用設備組成與 AI 收入：年報未公開。
