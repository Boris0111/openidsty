# 三方向研究擴充矩陣

對應 [design D2–D5](../openspec/changes/expand-ai-infrastructure-research/design.md) 與 [tasks](../openspec/changes/expand-ai-infrastructure-research/tasks.md)。基準為 a0791ded84fa22fad6efc6224cdd341481aad167，盤點日 2026-11-24；操作及網站閱讀證據見 [驗收紀錄](research-expansion-acceptance.md)。本文件保留必做範圍與證據位置，進度由 OpenSpec 的 task checkbox 判定。

## 填寫與驗收方式

- 下列產品的五面向是**待研究問題**，不是已證實論述。完成時將「待補」替換成本文章節連結、claim ID、來源 locator／read-scope、型號／版本／期間及實際查核日；不能只填來源首頁。
- 狀態逐列分為「分類存在／證據完成／內容審閱／網站走讀」。目前只核對檔案、ID 與 taxonomy；既有 deep、claims 或 offerings 均不表示本次研究已完成。證據、內容與網站三欄的「未」分別指本 change 尚未完成該項審查。
- 缺口依 not-researched／not-public／not-obtained／not-applicable 分開。初始列都是 not-researched；沒有讀原文不能改寫成未公開。核心用途或原理未查核時不得勾選內容 task。
- P1 原理與用途；P2 規格／製程與成本因素（數值附型號、版本、單位與測試條件）；P3 有條件路線比較；P4 公司實際交付；P5 需求傳導與風險。成本未取得同口徑資料時保留限制，不推算排名。
- 公司完成時補九段內容定位：供應角色、研究界線、產品與用途、商業模式、客戶與供應商、競爭與替代、業務曝險、風險、財務可取性。財務可取性只記來源與缺口。
- 新交付範圍先查台股、美股及已發現的其他關鍵市場，紀錄法律主體、既有 ID／aliases／legacy keys、候選納入／排除理由、去重及比較限制；未核對前不預造 product／role ID 或公司關係。

## 公司研究最低驗收標準

Boris 於 2026-11-24 確認沿用既有閱讀模板，華星光樣本的研究深度為最低標準。以下逐家公司核對，適用於本 change 新增及重查的公司，包含既有 `deep` 公司與新增角色的代表公司。每一列公司紀錄都須有對應頁面、證據與缺口，才可勾選所屬 task。

| 驗收項目 | 最低交付 |
|---|---|
| 研究本文 | 檢閱既有九個段落。用具體產品、料號或產品家族交代供應角色、產品用途、交付層次與相鄰角色分工。 |
| 一手證據 | 用年報、官方產品資料或其他適用原始文件支持核心主張。記錄來源、頁碼或段落、讀取範圍、適用型號／期間、查核日與信心標籤。 |
| 能力與追溯 | 讓讀者可從產品找到公司，從公司回到產品與來源。`offerings` 引用直接支持該交付的主張。分別查核能力、認證、採用、量產、出貨與收入。 |
| 比較、曝險與風險 | 交代比較適用的交付角色、場景與條件。區分已揭露的營收口徑、客戶集中或應用事實，以及依賴前提的曝險推論。 |
| 具體缺口 | 指明未公開或未取得的客戶、終端用途、出貨、產品收入或比較資料，並記錄原文支持到哪裡。核心交付與用途缺少支持時保留未完成。 |

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
| 光收發模組 [product-optical-transceiver](../industry-map/products/product-optical-transceiver.md)；[role-optical-module](../industry-map/roles/role-optical-module.md)；2.1、2.3 | 電介面 ↔ 光路雙向轉換；DSP 重定時與 FEC 責任依介面分工（P1，claim `electrical-optical-boundary`） | Cisco QDD-800G-VR8：OM3 30 m／OM4–5 50 m、15 W；QDD-8X100G-FR：SMF 2 km、17 W；QDD-2X400G-FR4：SMF 2 km、17 W（P2，Cisco 2026-09-21 版） | DSP 可插拔、100G/lane LPO、TH6-Davisson CPO 及指定 1–3 m AEC；各自限於來源平台與互通條件（P3） | Cisco 可訂購成品模組；Marvell MV-CD822 是 8×100G DSP 元件，不推定供應 Cisco 料號；華星光以年報支持模組／光引擎代工範圍（P4） | 伺服器／交換器埠與合格鏈路增加可能帶動模組需求；埠數、breakout、AEC、LPO、CPO 可抵銷模組或 DSP 數量（P5，inference） | Cisco QSFP-DD800 表 2–5／產品段落；LPO MSA Rev 1.0 §§6–7；Arista FAQ p.3；Broadcom TH6 公告；Marvell Spica Gen2 Features／Description；適用型號／版本見產品 claims；查核 2026-11-24 | not-obtained：無同條件整體成本／雙端功耗／維修數據；not-public：供應關係、終端客戶及產品收入未揭露。Cisco 表 5 VR8 距離與表 3–4／產品段落矛盾，採購前需核對平台 | 已有／已／已／樣本驗收完成 |
| 光通訊 DSP [product-optical-dsp](../industry-map/products/product-optical-dsp.md)；[role-optical-dsp](../industry-map/roles/role-optical-dsp.md)；3.1 | 「定義與用途」：PAM4 等化、重定時與 gearbox，區分 SerDes／交換 ASIC、driver、雷射與接收前端 | 「先對齊雙側 lane 與光元件」：MV-CD822 8×100G；MV-CD432 16×100G ↔ 8×200G；Dove 800 8:8，driver 與診斷依型號 | 「LPO 如何改變分工」：100G/lane、0.5–500 m 單模設計範圍，16 dB＠26.56 GHz 電通道與主機 RS-FEC；同介面才比較 retimer | 「供應角色與公司」：Marvell Spica／Nova、Credo Dove 80X 的晶片交付及 driver 分工 | 「需求如何傳到 DSP」：埠速率／數量、兩側 lane、LPO 導入及合格料號，標為 inference | Spica Gen2 2022-12 Applications／Features／Description；Nova 2023-03 Applications／Features／Description；Dove 800 產品說明與規格表；LPO MSA Rev 1.0 §§5–8；查核 2026-11-24 | not-obtained：無同條件功耗、BER 或成本；not-public：公開產品文件未揭露具名採用與料號收入 | 已有／已／已／待 A 批預覽 |
| 磷化銦雷射晶片 [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)；[role-optical-chip](../industry-map/roles/role-optical-chip.md)；3.2 | 定義與用途／inp-eml-transmit-path：DFB 光源經同片 EAM 調變，與 DSP、模組的分工 | 晶粒規格、製程與成本／inp-die-processing：晶粒波長、符號率、劈裂與端面篩測 | EML、DML 與 CW 的替代條件／inp-source-architecture：依光路、耦合、chirp 及調變位置 | 供應角色與公司／inp-laser-delivery：Lumentum、Coherent 晶粒；博通內製；華星光 CW DFB 自述與 EML 研發 | 需求如何傳到晶粒／inp-architecture-demand：採用架構與 lane 數、良率和認證 | Lumentum HL13B5CP00-Ln Overview；Coherent EML Specifications；Lumentum 2020-12 送樣公告；Coherent 2024-08 CW 公告；IPSR-I §2.2.5；博通 FY2025 10-K Manufacturing、華星光 114 年度年報第 72／81 頁；查核 2026-11-24 | not-obtained：同 BER、溫度、鏈路預算的成本與功耗；not-public：已讀資料無特定模組客戶、料號別收入 | 已有／已／已／待 A 批預覽 |
| III-V 族光通訊磊晶片 [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)；[role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md)；3.2 | 定義與用途／iii-v-epi-stack：層堆疊與 MOCVD，晶圓後段另做晶粒 | 先看晶圓上的可用面積／epi-process-window：PL、厚度、邊緣排除、跨批重現性 | 同用途才比較磊晶來源：帶光柵／金屬層的加工界線，依 DFB／EML／VCSEL 用途 | 供應角色與公司／epi-commercial-granularity：聯亞與 IQE 的磊晶家族，區分外購與晶片內製 | 需求如何傳到磊晶／epi-qualified-area-demand：外購率、合格面積及架構抵銷 | IPSR-I §§2.2.1、2.3 及 Epitaxial growth/layer deposition 表；聯亞 Data center 產品頁；IQE Wafer structures offered；查核 2026-11-24 | not-obtained：同片徑、同層結構的公差、良率及價格；not-public：已讀型錄未揭露具名客戶與模組採用 | 已有／已／已／待 A 批預覽 |
| 重定時與橋接晶片 [product-retimer](../industry-map/products/product-retimer.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 定義與用途／retimer-physical-link：root complex 至 endpoint、CDR 與通道分段 | 速率和距離要分開驗證：64 GT/s、lane 數、兩側損耗與板端驗證 | 何時可用較簡單的通道：低損耗 PCB、redriver、PCIe 與 Ethernet 的介面界線 | 供應角色與公司／aries-toucan-application：Astera Aries、Credo Toucan；型錄與合格分列 | 需求如何傳到晶片／retimer-board-demand：以平台拓樸、走線與驗證推導 | Aries 2024-02 brief Benefits／Description；Astera PCIe FAQ；Credo 2026-08-31 公告 Key points；查核 2026-11-24 | not-obtained：同通道的 BER／功耗／延遲／BOM；not-public：料號客戶、用量、收入 | 已有／已／已／待 A 批預覽 |
| 主動電纜 [product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 定義與用途／aec-endpoint-path：NIC 至 ToR、直連或分接、銅纜與主動端 | 線長由料號與端點決定／aec-length-profile：SPAN 3–7 m、SHIFT 1–3 m、Taurus 800G 3 m 30 AWG | 同一對端點再比較光與電／aec-optical-alternative：DAC、AEC 與可插拔光路，對齊協定、模式與距離 | 供應角色與公司：Credo 完整 AEC，Astera Taurus 為整合用 SCM | 需求如何傳到線組／aec-cabling-demand：合格短距埠與實際佈線，DAC／光反向條件 | Credo SPAN REV 100924、SHIFT 2025-09 的 Key Features 與料號表；Taurus brief Product Family Information；Cisco 2026-09 QSFP-DD800 及 Arista FAQ p.3；查核 2026-11-24 | not-obtained：同模式功耗、BER、維修及成本；not-public：料號客戶、出貨與收入 | 已有／已／已／待 A 批預覽 |
| 交換器晶片 [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)；[role-switch-silicon](../industry-map/roles/role-switch-silicon.md)；3.4 | 定義與用途／switch-asic-forwarding：查表、緩衝、QoS 與 SerDes | 看清晶片 lane 與面板埠／switch-asic-lane-and-port：Teralynx 10 51.2T、Tomahawk 6 102.4T | 拓樸決定需要的 ASIC 功能／switch-asic-fabric-boundaries：Tomahawk Ultra、Teralynx 10、Jericho4 依場景 | 供應角色與公司：智邦型錄驗證 Tomahawk 5 設計；Teralynx 10 有原廠量產公告 | 容量升級何時拉動晶片需求／switch-asic-radix-demand：埠數、拓樸整併與驗證 | Teralynx 10 brief Block Diagram／Key Features、2024-07 量產公告；Broadcom Tomahawk 6 2025-06、Ultra 2025-07、Jericho4 2025-08 Availability；Accton AS9817-64O 2023-09；查核 2026-11-24 | not-obtained：同條件延遲、功耗、緩衝及價格；not-public：下游客戶用量與收入 | 已有／已／已／待 A 批預覽 |
| 資料中心交換器 [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)；[role-switch-system](../industry-map/roles/role-switch-system.md)；3.4 | 定義與用途／switch-system-accton-64o：leaf/spine 整機與晶片、NOS、光電埠 | 同一埠數還要對照 NOS 和電熱條件／switch-system-spec-conditions：64×800G、ONIE／EOS、整機環境 | 依用途選整機：機房 scale-out、延遲敏感 scale-up、跨機房與 CPO 維修 | 供應角色與公司：AS9817-64O 的整機與 BCM78900，Arista 7060X6-64PE 的 EOS | 需求如何傳到整機／switch-system-design-demand：可用埠、上行容量、備援及合併 | Accton E092023-AP-R01 Key Features／Specifications；Arista 04-0053-08 Model Overview／EOS／功耗腳註；查核 2026-11-24 | not-obtained：同環境與功能的功耗、延遲及價格；not-public：具名終端用戶、台數、收入 | 已有／已／已／待 A 批預覽 |

### A：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 光纖連接組件；3.5；[product-fiber-cable-assembly](../industry-map/products/product-fiber-cable-assembly.md) | 定義與用途／fiber-passive-interconnect：端面配接、纖芯極性與配線架 | 線組成本取決於安裝和驗收／fiber-budget-and-mechanical：Corning 30 m OS2、彎折與損耗口徑 | 先對照模組，才能換組件：MPO 平行光、LC WDM 及同介面替換條件 | 供應角色與公司／fiber-company-deliveries：安費諾線組、貿聯集團光纜、SENKO 獨立接頭 | 需求如何傳到光纖組件／fiber-port-to-assembly-demand：平行光芯數、WDM／AEC／重用的抵銷 | Cisco QSFP-DD800 表 2 與各料號、Corning AEN163 Rev 1 p.3 及 EDGE8 SKU、APH Features／Specifications、BizLink 2026-01-05 及 MPO 產品頁、SENKO Standard／History；查核 2026-11-24 | 新增 [role-passive-fiber-connectivity](../industry-map/roles/role-passive-fiber-connectivity.md)，既有線束產品按伺服器內電／電力、板端 role 按電接頭；此處按可驗收的光組件。台股納入 3665.TW 集團（XFS 與上市主體分開）；美股沿用 APH，Corning 是同用途型錄參照，無須另建 ID。日本母公司之美國 SENKO 子公司在本原文只證實接頭，未列成組件。缺同規格價格、具名採用與收入。 | 新增／已／已／待 A 批預覽 |
| 主機端網路介面；3.6；[product-datacenter-network-adapter](../industry-map/products/product-datacenter-network-adapter.md) | 定義與用途／nic-host-to-fabric：PCIe、DMA、Ethernet／IB 與交換 | 配好 PCIe、機構與網路埠／nic-port-rate-is-per-protocol：CEM／OCP、單 800 vs 雙 400、FW | 替代條件由資料路徑決定：同網路協定、端點模式、主機和卸載條件 | 供應角色與公司／nic-card-and-chip-scope：博通、輝達成卡，研華 200GbE 成卡使用輝達控制器 | 需求如何傳到主機端／nic-adoption-path：端點埠、單卡密度與驗收 | Broadcom 57708-PB103 Features／Ordering、NVIDIA C8180 硬體與 FW OPN 表、Advantech 2022-10-17 型錄、Senao SX906／Silicom O32CG2B608；查核 2026-11-24 | 新增 [role-host-network-adapter](../industry-map/roles/role-host-network-adapter.md)。既有交換系統、電連接 IC、伺服器整機無法做成卡替換。美股沿用 AVGO／NVDA；台股查研華及神準（卡級交付，所讀均為 200G 級，限其他速率參照）；以色列 Silicom 的 200G OCP 卡是組裝參照。選已有 ID 且有 800G 級資料者進本批。料號收入、終端用戶及同條件效能缺口保留。 | 新增／已／已／待 A 批預覽 |

### A：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 博通 [company-avgo](../industry-map/companies/company-avgo.md)；3.7 | Tomahawk、BCM85822、InP 雷射與 BCM57708 NIC 的交付 | 既有 deep，重查九段 | 供應角色與產品連四項；同角色比較附 51.2T、8:4 與實際 NIC 埠；業務曝險及風險分段 | tomahawk-asic-delivery、bcm85822-optical-dsp-delivery、inp-laser-fabrication-scope、bcm57708-host-adapter-delivery；FY2025 10-K Item 1、2026-03-12 Tomahawk 量產、AS9817-64O 設計、85822-DIE-PB100、57708-PB103；查核 2026-11-24 | not-public：InP 料號、特定客戶及料號收入；not-obtained：同功能效能／成本 | 已／已／待 A 批預覽 |
| 邁威爾 [company-mrvl](../industry-map/companies/company-mrvl.md)；3.7 | Spica／Nova、Teralynx 10、Alaska P／A；線端晶片與成品為不同交付 | 既有 deep，重查九段 | 供應角色與產品段連 DSP、ASIC、retimer、AEC；比較、曝險、風險及財務界線分段 | novaspica-dsp-delivery、teralynx-10-switch-delivery、alaska-p-and-a-delivery、fastlinq-nic-form-factor；FY2026 10-K Item 1／1A、型錄及 2024-07／2025-12 公告；查核 2026-11-24 | not-public：料號收入、特定部署驗收；not-obtained：同條件數據；FastLinQ 僅驗證 25G 歷史型號 | 已／已／待 A 批預覽 |
| Credo [company-crdo](../industry-map/companies/company-crdo.md)；3.8 | SPAN／SHIFT 成品、Toucan 板端、Dove 光 DSP、ZeroFlap 成品各自交付 | 既有 deep，重查九段 | 產品與用途連四產品；競爭依 CPR61664／PT6162、同 8:8 光 DSP 與線端交付；曝險和風險分列 | FY2026 10-K Item 1／1A、SPAN REV 100924、SHIFT 2025-09、Dove 80X；PCI-SIG 2026-07-31、ZeroFlap 2026-03-17 一般供應；查核 2026-11-24 | not-public：個別料號採用、出貨及收入；not-obtained：同板端或線路條件功耗／延遲 | 已／已／待 A 批預覽 |
| Astera Labs [company-alab](../industry-map/companies/company-alab.md)；3.8 | Aries retimer 與 PCIe／CXL SCM；Taurus EM800 Ethernet SCM | 既有 deep，重查九段 | 產品與用途及競爭段連 retimer／AEC；交付、認證及量產有各自條件 | aries-pt6162-compliance、taurus-aries-cable-module-delivery；FY2025 10-K Item 1、PCI-SIG 2026-07-31 PT6162、Taurus Brief Product Family Table、官方工作坊文章；查核 2026-11-24 | not-public：具名採用與各型號營收；not-obtained：同 x16 板卡條件測試及線組數據 | 已／已／待 A 批預覽 |
| 智邦 [company-2345-tw](../industry-map/companies/company-2345-tw.md)；3.9 | 2345.TW，整機對晶片、電熱與 NOS 交付 | 已重查九段 | AS9817-64O → 產品 → BCM78900；Arista 同 64×800G 整機條件比較 | as9817-64o-system-delivery，E092023-AP-R01 Key Components、2025 年報 Letter／DLC；2026-11-24 | 未公開型號客戶、出貨或收入；1.6T 展示、NIC 設計無本批採用資料 | 已／已／待 A 批預覽 |
| 聯亞 [company-3081-two](../industry-map/companies/company-3081-two.md)；3.9 | 3081.TWO，磊晶及部分加工；晶粒與模組另有交付 | 已重查九段 | 資料中心磊晶 → 聯亞 → 年報及產品；IQE 同 InP DFB 選型比較 | datacenter-epiwafer-delivery，114 年報封面及第 69 頁、官網資料中心 DFB／CW／VCSEL／PD；2026-11-24 | 未公開磊晶品類收入、具名下游客戶及認證；同口徑公差與良率未取得 | 已／已／待 A 批預覽 |
| 華星光 [company-4979-two](../industry-map/companies/company-4979-two.md)；2.2、3.9 | 4979.TWO，CW DFB 晶粒、光引擎／CoC 代工與相干模組 | 已重查九段；樣本已驗收 | 產品與用途連光模組、雷射；代工比較按同工序與驗收；客戶、曝險與風險分段 | cw-dfb-die-delivery、optical-engine-and-coherent-boundary、optical-contract-manufacturing-comparison；114 年報第 72、81、83、89 頁、官網民國 112／113 年沿革、Fabrinet 交付；2026-11-24 | 最大客戶僅代碼；未公開 800G ZR、70／100 mW 及各代工分項出貨與收入 | 已／已／樣本完成，待 A 批預覽 |

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
| [role-optical-chip](../industry-map/roles/role-optical-chip.md) | [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)（3.2） | Lumentum HL13B5CP00-Ln、Coherent EML 官方頁和 IPSR-I §2.2.5 支持晶粒交付；磊晶、載體與成品模組按不同節點審查 | 已有／已／已／待 A 批預覽 |
| [role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md) | [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)（3.2） | 聯亞 Data center 與 IQE InP 型錄支持磊晶片交付；光柵或 p-metal 加工可納入約定，但晶粒合格量另核 | 已有／已／已／待 A 批預覽 |
| [role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md) | [product-retimer](../industry-map/products/product-retimer.md)、[product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)（3.3） | Aries、Toucan、SPAN、SHIFT、Taurus 原文核對；應用按 PCIe／CXL 晶片、Ethernet 線組和線端內部模組分開 | 已有／已／已／待 A 批預覽 |
| [role-switch-silicon](../industry-map/roles/role-switch-silicon.md) | [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)（3.4） | Broadcom Tomahawk 與 Marvell Teralynx 支持 ASIC 交付；面板與 NOS 仍取決於整機設計 | 已有／已／已／待 A 批預覽 |
| [role-switch-system](../industry-map/roles/role-switch-system.md) | [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)（3.4） | Accton／Arista 整機資料表支持面板埠、風道及 NOS；限對齊整機條件時比較 | 已有／已／已／待 A 批預覽 |
| [role-rack-power-supply](../industry-map/roles/role-rack-power-supply.md) | [product-power-shelf-psu](../industry-map/products/product-power-shelf-psu.md)（4.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md) | [product-pmic-voltage-regulator](../industry-map/products/product-pmic-voltage-regulator.md)（4.2）、[product-power-module](../industry-map/products/product-power-module.md)（4.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-interposer-integration](../industry-map/roles/role-interposer-integration.md) | [product-2p5d-interposer-package](../industry-map/products/product-2p5d-interposer-package.md)（5.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-osat-assembly](../industry-map/roles/role-osat-assembly.md) | [product-flip-chip-package-service](../industry-map/products/product-flip-chip-package-service.md)（5.1） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |
| [role-ic-substrate](../industry-map/roles/role-ic-substrate.md) | [product-abf-substrate](../industry-map/products/product-abf-substrate.md)（5.2） | 待隨產品核對可替換交付與來源；not-researched | 已有／未／未／未 |

## 閱讀入口、比較與需求案例

| 範圍／task | 應用與既有入口 | 比較／傳導內容的閱讀位置 | 來源、限制與走讀紀錄 |
|---|---|---|---|
| 樣本 2.1–2.3 | [AI networking](../industry-map/applications/application-ai-networking.md) → 光收發模組 → A 代表公司 → 來源 | 代表公司依證據選取後連回 3.7／3.8／3.9；未先指定已供應完整模組 | 尚未建立樣本；桌機與手機待 Boris 確認，見驗收紀錄 |
| A 3.10–3.11 | [AI networking](../industry-map/applications/application-ai-networking.md)、[networking](../industry-map/ai-server/networking.md)、[CPO](../industry-map/themes/cpo-silicon-photonics.md) | [research-ai-networking-optical-electrical](../industry-map/research/research-ai-networking-optical-electrical.md)：「先固定通訊域與線組」對照 DAC／AEC、DSP 可插拔、LPO、CPO；「案例」列端點、介質、晶片與公司 | 四步分列事實、inference、反向條件與追蹤證據；Accton AS9817-64O、Cisco QSFP-DD800、Credo SPAN、LPO §§5–8、Davisson Availability、OIF 800ZR §1，2026-11-24 已審；待 A 批草稿預覽 |
| B 4.10–4.11 | [AI rack power](../industry-map/applications/application-ai-rack-power.md)、[power](../industry-map/ai-server/power.md)、[power discrete](../industry-map/semiconductor/power-discrete.md)；供電題材沿用既有 ID，待查適用項 | 待建立 research 頁；設施 → 機櫃 → 板端，分開容量、架構、交期與負載 | not-researched；抵銷情境、原文與追蹤來源待補；不擴至發電／輸電全產業；網站未走讀 |
| C 5.10–5.11 | [chip integration](../industry-map/applications/application-chip-integration.md)、[advanced packaging](../industry-map/ai-server/advanced-packaging.md)、[substrate](../industry-map/ai-server/substrate.md)；材料／設備／測試入口隨交付裁決 | 待建立 research 頁；中介層、載板、PCB 分層；規格 → 製程限制 → 有效產出 → 公司能力 | not-researched；認證／良率假設、反向條件與來源待補；網站未走讀 |
| 共用 6.1–6.6 | 全部上述穩定 ID、跨方向共用公司及研究連結 | 三種影響遍歷及回路、delta specs 對照、同版預覽／發布／公開快照 | 未執行；完整證據欄見驗收紀錄，不把基準驗證當成最終成功 |

## 矩陣建置核對（task 1.2）

2026-11-24 對照 design D3：14 個明列核心 product ID 與 22 個優先 company ID 均有獨立列且檔案存在；12 個既有供應 role 依 taxonomy 展開。A 的 2 個、B 的 6 個、C 的 3 個廣度範圍逐項列入，不因尚未取得證據刪除。三批入口、比較、需求案例與網站驗收各有 task 對照。

這項核對只驗收矩陣覆蓋與欄位，沒有宣稱產品、公司或新增角色的研究完成。後續每個內容 task 必須更新其列中的實際本文、主張、原文定位、期間、查核日及閱讀結果。


### 光纖組件新增角色公司審閱（3.5）

| 公司 | 九段閱讀位置與已讀原文 | 交付與限制 | 狀態 |
|---|---|---|---|
| [安費諾 APH](../industry-map/companies/company-aph.md) | 逐段核對供應角色至財務可取性。MPO Cable Assemblies 的 Features／Specifications、既有 FY2025 10-K Item 1 Markets／Customers、MD&A；2026-11-24 補查產品。 | offering 回到 mpo-fiber-assembly-capability。同 APC 介面及芯數時與貿聯比對，尚缺同條件數據。個別終端認證、客戶、出貨及營收未揭露。 | 內容已審閱，待 A 批預覽 |
| [貿聯 3665.TW](../industry-map/companies/company-3665-tw.md) | 逐段核對九個公司段落；BizLink 2026-01-05 公告、MPO Connectors All Products 與既有 114 年年報交付及集中度。2026-11-24 補查產品及集團歸屬。 | offering 回到 xfs-optical-assembly-capability。既有 3665.TW／BizLink 識別沿用。XFS 是集團子公司；官網尚缺指定光組件的合格客戶、料號損耗及收入。 | 內容已審閱，待 A 批預覽 |


### 主機介面卡新增角色公司審閱（3.6）

- [博通 AVGO](../industry-map/companies/company-avgo.md) 的 NIC 角色、交付與同用途比較已核對 57708-PB103；既有製造、客戶、曝險與申報邊界依 FY2025 Form 10-K 逐段閱讀，下一步依 3.7 完成交換、光與網路產品合併審閱。offering 指向 bcm57708-host-adapter-delivery，卡別採用及出貨未核實。
- [輝達 NVDA](../industry-map/companies/company-nvda.md) 九段已按該角色逐項審閱。C8180 OPN／FW、硬體規格與 FY2026 Form 10-K Item 1／1A／7；沿用 NVDA 與 CIK，按封面確認 Nasdaq。offering 指向 connectx8-host-adapter-delivery；指定料號收入、套件客戶與同條件對照未揭露或未取得。研究深度限主機介面卡，其餘產品線缺口留在公司頁。兩家均待 A 批網站預覽。
