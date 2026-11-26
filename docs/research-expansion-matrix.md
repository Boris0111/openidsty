# 三方向研究擴充矩陣

對應 [design D2–D5](../openspec/changes/archive/2026-11-25-expand-ai-infrastructure-research/design.md) 與 [tasks](../openspec/changes/archive/2026-11-25-expand-ai-infrastructure-research/tasks.md)。基準為 a0791ded84fa22fad6efc6224cdd341481aad167，盤點日 2026-11-24；操作及網站閱讀證據見 [驗收紀錄](research-expansion-acceptance.md)。本文件保留必做範圍與證據位置，進度由 OpenSpec 的 task checkbox 判定。

## 填寫與驗收方式

- 五面向以本文的章節、claim ID 與來源 locator／read-scope 核對；依型號、版本、期間及實際查核日解讀。
- 狀態逐列分為「分類存在／證據完成／內容審閱／網站走讀」。目前只核對檔案、ID 與 taxonomy；既有 deep、claims 或 offerings 均不表示本次研究已完成。證據、內容與網站三欄的「未」分別指本 change 尚未完成該項審查。
- 缺口依 not-researched／not-public／not-obtained／not-applicable 分開。新研究起始時為 not-researched，已讀證據及實際限制在各列更新。核心用途或原理未查核時不得勾選內容 task。
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
| 光通訊 DSP [product-optical-dsp](../industry-map/products/product-optical-dsp.md)；[role-optical-dsp](../industry-map/roles/role-optical-dsp.md)；3.1 | 「定義與用途」：PAM4 等化、重定時與 gearbox，區分 SerDes／交換 ASIC、driver、雷射與接收前端 | 「先對齊雙側 lane 與光元件」：MV-CD822 8×100G；MV-CD432 16×100G ↔ 8×200G；Dove 800 8:8，driver 與診斷依型號 | 「LPO 如何改變分工」：100G/lane、0.5–500 m 單模設計範圍，16 dB＠26.56 GHz 電通道與主機 RS-FEC；同介面才比較 retimer | 「供應角色與公司」：Marvell Spica／Nova、Credo Dove 80X 的晶片交付及 driver 分工 | 「需求如何傳到 DSP」：埠速率／數量、兩側 lane、LPO 導入及合格料號，標為 inference | Spica Gen2 2022-12 Applications／Features／Description；Nova 2023-03 Applications／Features／Description；Dove 800 產品說明與規格表；LPO MSA Rev 1.0 §§5–8；查核 2026-11-24 | not-obtained：無同條件功耗、BER 或成本；not-public：公開產品文件未揭露具名採用與料號收入 | 已有／已／已／A 批 revision 3 預覽通過 |
| 磷化銦雷射晶片 [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)；[role-optical-chip](../industry-map/roles/role-optical-chip.md)；3.2 | 定義與用途／inp-eml-transmit-path：DFB 光源經同片 EAM 調變，與 DSP、模組的分工 | 晶粒規格、製程與成本／inp-die-processing：晶粒波長、符號率、劈裂與端面篩測 | EML、DML 與 CW 的替代條件／inp-source-architecture：依光路、耦合、chirp 及調變位置 | 供應角色與公司／inp-laser-delivery：Lumentum、Coherent 晶粒；博通內製；華星光 CW DFB 自述與 EML 研發 | 需求如何傳到晶粒／inp-architecture-demand：採用架構與 lane 數、良率和認證 | Lumentum HL13B5CP00-Ln Overview；Coherent EML Specifications；Lumentum 2020-12 送樣公告；Coherent 2024-08 CW 公告；IPSR-I §2.2.5；博通 FY2025 10-K Manufacturing、華星光 114 年度年報第 72／81 頁；查核 2026-11-24 | not-obtained：同 BER、溫度、鏈路預算的成本與功耗；not-public：已讀資料無特定模組客戶、料號別收入 | 已有／已／已／A 批 revision 3 預覽通過 |
| III-V 族光通訊磊晶片 [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)；[role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md)；3.2 | 定義與用途／iii-v-epi-stack：層堆疊與 MOCVD，晶圓後段另做晶粒 | 先看晶圓上的可用面積／epi-process-window：PL、厚度、邊緣排除、跨批重現性 | 同用途才比較磊晶來源：帶光柵／金屬層的加工界線，依 DFB／EML／VCSEL 用途 | 供應角色與公司／epi-commercial-granularity：聯亞與 IQE 的磊晶家族，區分外購與晶片內製 | 需求如何傳到磊晶／epi-qualified-area-demand：外購率、合格面積及架構抵銷 | IPSR-I §§2.2.1、2.3 及 Epitaxial growth/layer deposition 表；聯亞 Data center 產品頁；IQE Wafer structures offered；查核 2026-11-24 | not-obtained：同片徑、同層結構的公差、良率及價格；not-public：已讀型錄未揭露具名客戶與模組採用 | 已有／已／已／A 批 revision 3 預覽通過 |
| 重定時與橋接晶片 [product-retimer](../industry-map/products/product-retimer.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 定義與用途／retimer-physical-link：root complex 至 endpoint、CDR 與通道分段 | 速率和距離要分開驗證：64 GT/s、lane 數、兩側損耗與板端驗證 | 何時可用較簡單的通道：低損耗 PCB、redriver、PCIe 與 Ethernet 的介面界線 | 供應角色與公司／aries-toucan-application：Astera Aries、Credo Toucan；型錄與合格分列 | 需求如何傳到晶片／retimer-board-demand：以平台拓樸、走線與驗證推導 | Aries 2024-02 brief Benefits／Description；Astera PCIe FAQ；Credo 2026-08-31 公告 Key points；查核 2026-11-24 | not-obtained：同通道的 BER／功耗／延遲／BOM；not-public：料號客戶、用量、收入 | 已有／已／已／A 批 revision 3 預覽通過 |
| 主動電纜 [product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)；[role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md)；3.3 | 定義與用途／aec-endpoint-path：NIC 至 ToR、直連或分接、銅纜與主動端 | 線長由料號與端點決定／aec-length-profile：SPAN 3–7 m、SHIFT 1–3 m、Taurus 800G 3 m 30 AWG | 同一對端點再比較光與電／aec-optical-alternative：DAC、AEC 與可插拔光路，對齊協定、模式與距離 | 供應角色與公司：Credo 完整 AEC，Astera Taurus 為整合用 SCM | 需求如何傳到線組／aec-cabling-demand：合格短距埠與實際佈線，DAC／光反向條件 | Credo SPAN REV 100924、SHIFT 2025-09 的 Key Features 與料號表；Taurus brief Product Family Information；Cisco 2026-09 QSFP-DD800 及 Arista FAQ p.3；查核 2026-11-24 | not-obtained：同模式功耗、BER、維修及成本；not-public：料號客戶、出貨與收入 | 已有／已／已／A 批 revision 3 預覽通過 |
| 交換器晶片 [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)；[role-switch-silicon](../industry-map/roles/role-switch-silicon.md)；3.4 | 定義與用途／switch-asic-forwarding：查表、緩衝、QoS 與 SerDes | 看清晶片 lane 與面板埠／switch-asic-lane-and-port：Teralynx 10 51.2T、Tomahawk 6 102.4T | 拓樸決定需要的 ASIC 功能／switch-asic-fabric-boundaries：Tomahawk Ultra、Teralynx 10、Jericho4 依場景 | 供應角色與公司：智邦型錄驗證 Tomahawk 5 設計；Teralynx 10 有原廠量產公告 | 容量升級何時拉動晶片需求／switch-asic-radix-demand：埠數、拓樸整併與驗證 | Teralynx 10 brief Block Diagram／Key Features、2024-07 量產公告；Broadcom Tomahawk 6 2025-06、Ultra 2025-07、Jericho4 2025-08 Availability；Accton AS9817-64O 2023-09；查核 2026-11-24 | not-obtained：同條件延遲、功耗、緩衝及價格；not-public：下游客戶用量與收入 | 已有／已／已／A 批 revision 3 預覽通過 |
| 資料中心交換器 [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)；[role-switch-system](../industry-map/roles/role-switch-system.md)；3.4 | 定義與用途／switch-system-accton-64o：leaf/spine 整機與晶片、NOS、光電埠 | 同一埠數還要對照 NOS 和電熱條件／switch-system-spec-conditions：64×800G、ONIE／EOS、整機環境 | 依用途選整機：機房 scale-out、延遲敏感 scale-up、跨機房與 CPO 維修 | 供應角色與公司：AS9817-64O 的整機與 BCM78900，Arista 7060X6-64PE 的 EOS | 需求如何傳到整機／switch-system-design-demand：可用埠、上行容量、備援及合併 | Accton E092023-AP-R01 Key Features／Specifications；Arista 04-0053-08 Model Overview／EOS／功耗腳註；查核 2026-11-24 | not-obtained：同環境與功能的功耗、延遲及價格；not-public：具名終端用戶、台數、收入 | 已有／已／已／A 批 revision 3 預覽通過 |

### A：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 光纖連接組件；3.5；[product-fiber-cable-assembly](../industry-map/products/product-fiber-cable-assembly.md) | 定義與用途／fiber-passive-interconnect：端面配接、纖芯極性與配線架 | 線組成本取決於安裝和驗收／fiber-budget-and-mechanical：Corning 30 m OS2、彎折與損耗口徑 | 先對照模組，才能換組件：MPO 平行光、LC WDM 及同介面替換條件 | 供應角色與公司／fiber-company-deliveries：安費諾線組、貿聯集團光纜、SENKO 獨立接頭 | 需求如何傳到光纖組件／fiber-port-to-assembly-demand：平行光芯數、WDM／AEC／重用的抵銷 | Cisco QSFP-DD800 表 2 與各料號、Corning AEN163 Rev 1 p.3 及 EDGE8 SKU、APH Features／Specifications、BizLink 2026-01-05 及 MPO 產品頁、SENKO Standard／History；查核 2026-11-24 | 新增 [role-passive-fiber-connectivity](../industry-map/roles/role-passive-fiber-connectivity.md)，既有線束產品按伺服器內電／電力、板端 role 按電接頭；此處按可驗收的光組件。台股納入 3665.TW 集團（XFS 與上市主體分開）；美股沿用 APH，Corning 是同用途型錄參照，無須另建 ID。日本母公司之美國 SENKO 子公司在本原文只證實接頭，未列成組件。缺同規格價格、具名採用與收入。 | 新增／已／已／A 批 revision 3 預覽通過 |
| 主機端網路介面；3.6；[product-datacenter-network-adapter](../industry-map/products/product-datacenter-network-adapter.md) | 定義與用途／nic-host-to-fabric：PCIe、DMA、Ethernet／IB 與交換 | 配好 PCIe、機構與網路埠／nic-port-rate-is-per-protocol：CEM／OCP、單 800 vs 雙 400、FW | 替代條件由資料路徑決定：同網路協定、端點模式、主機和卸載條件 | 供應角色與公司／nic-card-and-chip-scope：博通、輝達成卡，研華 200GbE 成卡使用輝達控制器 | 需求如何傳到主機端／nic-adoption-path：端點埠、單卡密度與驗收 | Broadcom 57708-PB103 Features／Ordering、NVIDIA C8180 硬體與 FW OPN 表、Advantech 2022-10-17 型錄、Senao SX906／Silicom O32CG2B608；查核 2026-11-24 | 新增 [role-host-network-adapter](../industry-map/roles/role-host-network-adapter.md)。既有交換系統、電連接 IC、伺服器整機無法做成卡替換。美股沿用 AVGO／NVDA；台股查研華及神準（卡級交付，所讀均為 200G 級，限其他速率參照）；以色列 Silicom 的 200G OCP 卡是組裝參照。選已有 ID 且有 800G 級資料者進本批。料號收入、終端用戶及同條件效能缺口保留。 | 新增／已／已／A 批 revision 3 預覽通過 |

### A：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 博通 [company-avgo](../industry-map/companies/company-avgo.md)；3.7 | Tomahawk、BCM85822、InP 雷射與 BCM57708 NIC 的交付 | 既有 deep，重查九段 | 供應角色與產品連四項；同角色比較附 51.2T、8:4 與實際 NIC 埠；業務曝險及風險分段 | tomahawk-asic-delivery、bcm85822-optical-dsp-delivery、inp-laser-fabrication-scope、bcm57708-host-adapter-delivery；FY2025 10-K Item 1、2026-03-12 Tomahawk 量產、AS9817-64O 設計、85822-DIE-PB100、57708-PB103；查核 2026-11-24 | not-public：InP 料號、特定客戶及料號收入；not-obtained：同功能效能／成本 | 已／已／A 批 revision 3 預覽通過 |
| 邁威爾 [company-mrvl](../industry-map/companies/company-mrvl.md)；3.7 | Spica／Nova、Teralynx 10、Alaska P／A；線端晶片與成品為不同交付 | 既有 deep，重查九段 | 供應角色與產品段連 DSP、ASIC、retimer、AEC；比較、曝險、風險及財務界線分段 | novaspica-dsp-delivery、teralynx-10-switch-delivery、alaska-p-and-a-delivery、fastlinq-nic-form-factor；FY2026 10-K Item 1／1A、型錄及 2024-07／2025-12 公告；查核 2026-11-24 | not-public：料號收入、特定部署驗收；not-obtained：同條件數據；FastLinQ 僅驗證 25G 歷史型號 | 已／已／A 批 revision 3 預覽通過 |
| Credo [company-crdo](../industry-map/companies/company-crdo.md)；3.8 | SPAN／SHIFT 成品、Toucan 板端、Dove 光 DSP、ZeroFlap 成品各自交付 | 既有 deep，重查九段 | 產品與用途連四產品；競爭依 CPR61664／PT6162、同 8:8 光 DSP 與線端交付；曝險和風險分列 | FY2026 10-K Item 1／1A、SPAN REV 100924、SHIFT 2025-09、Dove 80X；PCI-SIG 2026-07-31、ZeroFlap 2026-03-17 一般供應；查核 2026-11-24 | not-public：個別料號採用、出貨及收入；not-obtained：同板端或線路條件功耗／延遲 | 已／已／A 批 revision 3 預覽通過 |
| Astera Labs [company-alab](../industry-map/companies/company-alab.md)；3.8 | Aries retimer 與 PCIe／CXL SCM；Taurus EM800 Ethernet SCM | 既有 deep，重查九段 | 產品與用途及競爭段連 retimer／AEC；交付、認證及量產有各自條件 | aries-pt6162-compliance、taurus-aries-cable-module-delivery；FY2025 10-K Item 1、PCI-SIG 2026-07-31 PT6162、Taurus Brief Product Family Table、官方工作坊文章；查核 2026-11-24 | not-public：具名採用與各型號營收；not-obtained：同 x16 板卡條件測試及線組數據 | 已／已／A 批 revision 3 預覽通過 |
| 智邦 [company-2345-tw](../industry-map/companies/company-2345-tw.md)；3.9 | 2345.TW，整機對晶片、電熱與 NOS 交付 | 已重查九段 | AS9817-64O → 產品 → BCM78900；Arista 同 64×800G 整機條件比較 | as9817-64o-system-delivery，E092023-AP-R01 Key Components、2025 年報 Letter／DLC；2026-11-24 | 未公開型號客戶、出貨或收入；1.6T 展示、NIC 設計無本批採用資料 | 已／已／A 批 revision 3 預覽通過 |
| 聯亞 [company-3081-two](../industry-map/companies/company-3081-two.md)；3.9 | 3081.TWO，磊晶及部分加工；晶粒與模組另有交付 | 已重查九段 | 資料中心磊晶 → 聯亞 → 年報及產品；IQE 同 InP DFB 選型比較 | datacenter-epiwafer-delivery，114 年報封面及第 69 頁、官網資料中心 DFB／CW／VCSEL／PD；2026-11-24 | 未公開磊晶品類收入、具名下游客戶及認證；同口徑公差與良率未取得 | 已／已／A 批 revision 3 預覽通過 |
| 華星光 [company-4979-two](../industry-map/companies/company-4979-two.md)；2.2、3.9 | 4979.TWO，CW DFB 晶粒、光引擎／CoC 代工與相干模組 | 已重查九段；樣本已驗收 | 產品與用途連光模組、雷射；代工比較按同工序與驗收；客戶、曝險與風險分段 | cw-dfb-die-delivery、optical-engine-and-coherent-boundary、optical-contract-manufacturing-comparison；114 年報第 72、81、83、89 頁、官網民國 112／113 年沿革、Fabrinet 交付；2026-11-24 | 最大客戶僅代碼；未公開 800G ZR、70／100 mW 及各代工分項出貨與收入 | 已／已／樣本完成；A 批 revision 3 預覽通過 |

## B：核心產品五面向

| 產品／既有 role／task | P1 | P2 | P3 | P4 | P5 | 來源定位／適用範圍／查核日 | 具體缺口 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 電源供應器與電源架 [product-power-shelf-psu](../industry-map/products/product-power-shelf-psu.md)；[role-rack-power-supply](../industry-map/roles/role-rack-power-supply.md)；4.1 | AC/DC 轉換位置、DC 母線，以及 PSU 與機框分工 | orv3-shelf-capacity、power-shelf-efficiency-conditions：滿配／5+1、峰值和負載點分列 | shelf-topology-and-transient：AC／HVDC、熱插拔、共同故障域及 20 ms 瞬態 | 台達 18／33 kW、康舒 19 吋 33 kW，光寶 ORv3 展示 | shelf-demand-transmission：合格容量、功率密度與轉換位置抵銷 | OCP Marketplace 台達 18 kW／康舒 33 kW；台達 Power Shelf；Diablo 400 v0.7.0 §7.3.4；OCP HVDC Rev 1.0 §§3.1、4.2、5.3；光寶官方 ORv3；2026-11-24 | not-obtained：同測試口徑的效率、價格、換修；not-public：客戶、合格量、料號收入 | 已有／已／已／B 批 revision 4 預覽通過 |
| 電源管理與電壓調節晶片 [product-pmic-voltage-regulator](../industry-map/products/product-pmic-voltage-regulator.md)；[role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md)；4.2 | PWM、回授、外接功率級和電感 | MP2965 6+1 典型電路及 12 V 功率端，相數、電流、電熱分列 | 同 rail、介面、熱、時序與保護再比較；與整合模組分工 | MPS MP2965、Renesas RAA228228 型號交付 | board-controller-demand：相數提高、剩餘相數及整合的抵銷 | MPS MP2965 圖 2／Protection、Renesas Rev.2.0 圖 2；2026-11-24 | 同平台步階／效率／價格、料號出貨與收入未取得 | 已有／已／已／B 批 revision 4 預覽通過 |
| 高密度電源模組 [product-power-module](../industry-map/products/product-power-module.md)；[role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md)；4.2 | 中間端、調節端及負載端功率轉換 | MPM3698 90 A 連續／120 A 峰值；VTM 固定比 95 A 標稱 | 分立、整合及 PRM／VTM，需同位置與電熱條件 | MPS MPM3698、Vicor PRM／VTM、台達 RBC | module-design-demand：面積、近負載損耗與熱／成本抵銷 | MPS MPM3698 Operation／Protection；Vicor Rev.1.5 p.1 NRND；台達 RBC／UBC 2023-10；2026-11-24 | 同平台散熱、連續承載、總成本、具名採用與收入未取得 | 已有／已／已／B 批 revision 4 預覽通過 |

### B：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 資料中心變壓設備；4.3；[product-datacenter-transformer](../industry-map/products/product-datacenter-transformer.md) | 接入後一次／二次電壓轉換；設施責任邊界 | 東元 2,500 kVA 範例、22.8 kV→380 V、空載／75°C 負載損耗 | 同場址比較乾式與液浸、維護與消防 | 東元 1504.TW 有設備與工程來源；ETN、Hitachi Energy 為同角色型錄參照 | facility-transformer-demand：可接入 MVA、冗餘、交期和預留容量 | 東元型錄乾式 2,500 kVA／接入試驗／2026 股東會；Eaton DG022017EN 14.1-11 與 10-K 封面；Hitachi Energy HiDry 及 2022 股權公告；2026-11-24 | 新增 [role-facility-transformer](../industry-map/roles/role-facility-transformer.md)；與 UPS、架端轉換及開關保護分開。台股深研 [東元](../industry-map/companies/company-1504-tw.md)；Eaton 為愛爾蘭 NYSE 主體；Hitachi Energy 為日本日立集團設備公司。後兩者作選型比較，未新增公司。無指定專案價格、交期、合格量與收入。 | 新增／已／已／B 批 revision 4 預覽通過 |
| 開關／配電設備；4.4；[product-datacenter-switchgear](../industry-map/products/product-datacenter-switchgear.md) | 接入、變壓一次／二次側、UPS 饋線與保護 | PowerBoard 連續 A 與 MCSeT 短時 kA 分列 | 同電壓、故障額定、GIS／AIS、維修及保護協調 | 東元 1504.TW 中低壓集成；Vertiv VRT 低壓成套；Schneider MCSeT 作規格參照 | switchgear-demand-by-feeders：按饋線、備援、接入和交期 | 東元 MV & LV Switchgear；Vertiv PowerBoard Features；Schneider MCSeT Cubicle Ratings；2026-11-24 | 新增 [role-facility-switchgear](../industry-map/roles/role-facility-switchgear.md)；既有系統電源與變壓均為轉換交付，架內 PDU 為下游插座。台股沿用東元、美股沿用 Vertiv、法國 Schneider 型錄只作對照。缺個案驗收、報價及收入。 | 新增／已／已／B 批 revision 4 預覽通過 |
| UPS；4.5；[product-facility-ups](../industry-map/products/product-facility-ups.md) | 設施 AC 雙變換、電池、旁路與保護範圍 | 相同負載、功因、溫度、末期續航；600 kW × 5 min 情境 | UPS／BBU 差異、旁路電池不可用與維修故障域 | 台達 Modulon DPH、Vertiv Trinergy；法國 Schneider Galaxy VX 作比較 | ups-demand-capacity-and-runtime：容量、續航與分級供電抵銷 | Vertiv SL-71331 Technical Data、台達 DPH v3.2 規格、Schneider 990-914303 Operation Modes；2026-11-24 | 新增 [role-facility-ups](../industry-map/roles/role-facility-ups.md)；與架側 DC 備援、開關及分配依責任拆分。台股台達、美股 Vertiv 沿用。實際電池配置、可用率、收入未揭露。 | 新增／已／已／B 批 revision 4 預覽通過 |
| BBU；4.6；[product-rack-battery-backup](../industry-map/products/product-rack-battery-backup.md) | 電池組、BMS、充放電；接在架側 DC 母線 | ORv3 3 kW、四分鐘、35°C；SOH 90 秒條件分列 | 與 UPS／CBU 對齊負載、時間窗、故障域與維修 | 光寶 72 kW 展示及 Vertiv 800 VDC 整合設計，電芯與箱體供應另計 | bbu-design-demand：供電架構、續供負載與集中備援抵銷 | OCP ORv3 v1.4 §§4.2.1、4.2.4、4.3、SOH；光寶 2025 Datacloud；Vertiv 2026 800 VDC 公告；2026-11-24 | 新增 [role-rack-battery-backup](../industry-map/roles/role-rack-battery-backup.md)；台股光寶、美股 Vertiv；其他市場原文尚未核實同一介面與配置，保留空白。機櫃 PSU 與設施 UPS 的功能各異。續航、具名驗收與收入仍缺。 | 新增／已／已／B 批 revision 4 預覽通過 |
| 母線／busway；4.7；[product-datacenter-busway](../industry-map/products/product-datacenter-busway.md) | 案場幹線與分接至下游 | 北美 iMPB、TECOBAR LB 的電壓、材料、電流與規範 | 固定線纜、同分路/保護/溫升比較 | 台股東元子公司 TECOBAR、美股 Vertiv；其餘區域型錄需另對規格 | busway-project-demand：分路、幹線長度與備用容量 | TECOBAR Technical Data、東元新加坡展題、Vertiv SL-70397 p.1；2026-11-24 | 新增 [role-facility-busway](../industry-map/roles/role-facility-busway.md)；與架內母線、開關盤與插座分配依交付拆分。缺同案成本、驗收、收入。 | 新增／已／已／B 批 revision 4 預覽通過 |
| PDU／供電分配；4.7；[product-rack-pdu](../industry-map/products/product-rack-pdu.md) | 機櫃內 AC 插座及監測／保護 | 插座、連續電流、相別、接法與 A/B 冗餘 | 同電氣介面比較，中央 DC 可減少 AC 插座 | 台股台達、美股 Vertiv；法國 Schneider 旗下 APC 作型錄參照 | rpdu-rack-design-demand：架構、插座、計量與集中供電 | ViLink §2.1、Geist UU30009L Model Chart、APC APDU10350ME Specifications；2026-11-24 | 新增 [role-rack-power-distribution](../industry-map/roles/role-rack-power-distribution.md)；已與幹線、整流、備援和設施 PDU 區分，不同層級容量不可相加。缺現場系統負載及收入。 | 新增／已／已／B 批 revision 4 預覽通過 |

### B：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 台達電；4.8 [company-delta-electronics](../industry-map/companies/company-delta-electronics.md) | 2308.TW；18／33 kW、DPH UPS、ViLink、RBC 四種交付 | deep；本批重查九段 | 產品頁及 offering 對齊四項；同冗餘容量、機框、架構和 UPS 電池比較 | OCP 18 kW、33 kW Power Shelf、DPH v3.2、ViLink §2.1、RBC 2023-10、既有 114 年報；2026-11-24 | 料號認證、客戶、同條件成本及各產品收入分項缺口 | 已／已／B 批 revision 4 預覽通過 |
| 光寶科；4.8 [company-2301-tw](../industry-map/companies/company-2301-tw.md) | 2301.TW；33 kW、72 kW BBU 供應與展示；後續試產分開 | deep；本批重查九段 | 電源架、BBU 各回產品；合作、集中度及公司自報 AI 營收依口徑 | QCT 2025 OCP、2025 Datacloud、3Q26 Outlook、既有 114 年報；2026-11-24 | 終端採用、72 kW BBU 放電時間、出貨量與料號收入未揭露 | 已／已／B 批 revision 4 預覽通過 |
| 康舒；4.8 [company-6282-tw](../industry-map/companies/company-6282-tw.md) | 6282.TW AcBel；19 吋 1RU 33 kW 與 21 吋型分開 | deep；本批重查九段 | 產品、競爭、財務段回到電源架；本批未確立 UPS／BBU 等不同設備交付 | OCP 19 吋 Product Details、年報封面／第 80 頁；量產及認證限公司自報；2026-11-24 | 缺 33 kW 個別終端採用、料號收入與同口徑實測、Ruby 原始報告 | 已／已／B 批 revision 4 預覽通過 |
| 芯源系統；4.9 [company-mpwr](../industry-map/companies/company-mpwr.md) | MPWR；MP2965 控制、MPM3698 整合模組 | deep；本批重查九段 | 兩交付連回板端產品；與 Renesas 同控制功能、Vicor 對齊整路轉換 | MP2965 Typical Application、MPM3698 Operation、Renesas Figure 2、既有 FY2025 10-K；2026-11-24 | 未取得具名平台、料號收入與同核心條件測試 | 已／已／B 批 revision 4 預覽通過 |
| Vicor；4.9 [company-vicr](../industry-map/companies/company-vicr.md) | VICR；NBM、PRM／VTM、Hydra II 產品分工 | deep；本批重查九段 | 競爭段落按中間端固定比、調節、近負載與封裝區別 | NBM2317S60E1560T0R datasheet、VTM Rev.1.5 NRND、Hydra II、FY2025 10-K；2026-11-24 | 未取得板端 TCO、具名合格、型號收入及權利金拆分 | 已／已／B 批 revision 4 預覽通過 |
| Vertiv；4.9 [company-vertiv](../industry-map/companies/company-vertiv.md) | VRT；開關、UPS、母線、rPDU、電源架、BBU 整合 | deep；本批重查九段 | 各設備回到對應產品；同受保護負載比較，另有液冷既有角色 | PowerBoard Features、Trinergy SL-71331、iMPB SL-70397、Geist、PSS5033 料號表、800 VDC 公告及 FY2025 10-K；2026-11-24 | 各具名案場、設備收入、同口徑成本與配置未揭露 | 已／已／B 批 revision 4 預覽通過 |

## C：核心產品五面向

| 產品／既有 role／task | P1 | P2 | P3 | P4 | P5 | 來源定位／適用範圍／查核日 | 具體缺口 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 2.5D 中介層封裝；5.1 [product-2p5d-interposer-package](../industry-map/products/product-2p5d-interposer-package.md)；[role-interposer-integration](../industry-map/roles/role-interposer-integration.md) | D2D、HBM、中介層與載板分層 | CoWoS-S／R／L、3.5× 量產，5.5× 資格口徑不一 | 全矽、RDL、局部橋，以同 I/O／可靠度比較 | TSMC CoWoS／ASE FOCoS／Amkor MEOL；各自責任 | interposer-yield-demand：良品、面積、組裝與替代 | TSMC 3DFabric CoWoS 及 HPC、2025 年報 R&D；ASE FOCoS test vehicles；Amkor MEOL；2026-11-24 | 5.5× 資格需核，缺同產品良率、成本與具名採用 | 已有／已／已／C 批 revision 5 預覽通過 |
| 覆晶與委外封裝服務；5.1 [product-flip-chip-package-service](../industry-map/products/product-flip-chip-package-service.md)；[role-osat-assembly](../industry-map/roles/role-osat-assembly.md) | 覆晶、底膠、模封或封蓋、上板與測試 | Amkor 封裝尺寸、節距、基板層數及資格狀態 | 同服務比較 FCBGA、fan-out 及 CoW 應用 | ASE 高雄與 Amkor 成品；力成按工序證據 | flip-chip-service-demand：良率、委外邊界與認證 | ASE Flip Chip Package Offerings；Amkor FCBGA Features、Additional Options；2026-11-24 | 同封裝測試、份額、量產與料號收入仍待取得 | 已有／已／已／C 批 revision 5 預覽通過 |
| ABF 封裝載板；5.2 [product-abf-substrate](../industry-map/products/product-abf-substrate.md)；[role-ic-substrate](../industry-map/roles/role-ic-substrate.md) | 核心至增層／SAP／微孔／BGA，在封裝與 PCB 間 | Ibiden 80×80 mm／約 18 層為 CY2025 級距，Shinko CO₂／UV 及層間布線 | 有機、coreless、玻璃的同條件比較，玻璃原型與研發分開 | Ibiden、Shinko 與台股載板廠供應成品；膜料另列 | substrate-yield-and-demand：面積、層數、套位、可靠度及良率 | Ibiden IR 2026 p.9；Shinko DLL／DLL3 與 ECTC TGV；Ajinomoto 材料；Intel 2026 合作；2026-11-24 | 未有同尺寸、層數、線寬與孔徑的成本、良率、具名採用及收入 | 已有／已／已／C 批 revision 5 預覽通過 |

### C：廣度研究與角色裁決

| 交付範圍／task | P1 | P2 | P3 | P4 | P5 | 來源／範圍／查核日 | 角色、候選與市場查核紀錄 | 分類／證據／內容／網站 |
|---|---|---|---|---|---|---|---|---|
| 增層介電材料；5.3；[product-substrate-build-up-dielectric](../industry-map/products/product-substrate-build-up-dielectric.md)；[role-substrate-dielectric-material](../industry-map/roles/role-substrate-dielectric-material.md) | 膜料隔離銅線，壓合後供雷射與 SAP | AFT GX／GZ／GL 與積水 NX04H 的適用試驗 | 按同溫區、頻率、銅附著、粗度和層壓比較 | 日本 AFT／積水、台灣晶化；美股 Qnity 光阻與藥水另計 | 層數與需求；裁切、合格率、換料和認證影響 | AFT Grade Table／所有權、積水 NX04H、晶化 TBF 厚度、Qnity IC Substrates；2026-11-24 | 與 PCB CCL、線路光阻及載板成品去重。納入日本 2802.T 集團 AFT；積水與晶化作同功能比較，上市母公司與地區據點分開。Qnity 來源證實耗材用途不同。規格級距及客戶採用未取得同口徑。 | 新增／已／已／C 批 revision 5 預覽通過 |
| 載板微孔加工；5.4；[product-substrate-laser-microvia-drill](../industry-map/products/product-substrate-laser-microvia-drill.md)；[role-substrate-microvia-equipment](../industry-map/roles/role-substrate-microvia-equipment.md) | 增層成孔、去膠渣與填銅 | ESI 30–85 μm、東捷 10–50 μm、其他研發口徑 | 比較同材料／深度、位置、尾部缺陷與合格速度 | 美股 MKS／ESI；台股東捷、日股三菱設備比較 | 孔數、材料與合格設備時數，存在生產率抵銷 | ESI Geode A、MKS FY25 10-K、台灣智慧機械及東捷公司、三菱 JPCA 2024、工研院；2026-11-24 | 設備供應另建；有機膜微孔與玻璃 TGV、矽 TSV 分開。台灣 8064 東捷、日本三菱作同工序參照，台灣技轉樣件未列為量產。客戶良率與收入未公開。 | 新增／已／已／C 批 revision 5 預覽通過 |
| 載板線路形成；5.5；[product-substrate-patterning-lithography](../industry-map/products/product-substrate-patterning-lithography.md)；[role-substrate-patterning-equipment](../industry-map/roles/role-substrate-patterning-equipment.md) | SAP 種子層、圖形曝光顯影、鍍銅、剝膜與除種子層 | SCREEN Ledia Qs 5/5 μm、X500 對位補償和面板條件 | 直寫／光罩曝光同膜、焦深、合格 L/S 及套位比較 | 美股 ONTO；日本 SCREEN；台股志聖相鄰工序；光阻及濕製程另列 | 面板翹曲、多層套位、成品良率及瓶頸轉移 | Onto X500／FY25 10-K、SCREEN PE 與 2025 IR Day、志聖年報與產發署、Atotech G-Plate、Qnity Riston；2026-11-24 | 新增曝光設備角色，與既有廣義設備、材料、去膠填銅和載板廠加工區別。台灣志聖可驗防焊／軟板與壓膜設備，未查到可比同線寬載板線路驗收。後續光阻／藥液收入及設備驗收仍待。 | 新增／已／已／C 批 revision 5 預覽通過 |

### C：優先公司與交付證據

| 公司／task | 本次必查交付與比較界線 | 既有狀態（不代表本次完成） | 九段閱讀位置／產品五面向連結 | 主張／來源定位／適用範圍／查核日 | 具體缺口 | 證據／內容／網站紀錄 |
|---|---|---|---|---|---|---|
| 台積電；5.6 [company-tsmc](../industry-map/companies/company-tsmc.md) | TSMC 覆蓋 -S／-R／-L 整合，3.5× 量產與 5.5× 資格分開 | deep；本批重查九段 | 對齊覆晶、中介層、基板、已知良品與測試；既有代工關係保留 | CoWoS 平台、FY2025 R&D、HPC Q&R；2026-11-24 | 5.5× 口徑、具名封裝採用、產出與產品收入未查得 | 已／已／C 批 revision 5 預覽通過 |
| 日月光投控；5.6 [company-3711-tw](../industry-map/companies/company-3711-tw.md) | ASE Inc. 持股法體、TSV 整合、FOCoS test vehicle 與覆晶服務 | deep；本批重查九段 | 整合、覆晶和測試連結各自引用；對齊封裝尺寸、熱與交付範圍 | ASE Financials、2.5D/3D、FOCoS、ASE 高雄與既有 20-F；2026-11-24 | 無同規格產出、成本、專案客戶與收入 | 已／已／C 批 revision 5 預覽通過 |
| 艾克爾；5.7 [company-amkr](../industry-map/companies/company-amkr.md) | FCBGA、MEOL、2.5D 組裝與測試各分開 | deep；本批重查九段 | 與 ASE 對齊工序、尺寸、測試關係；保留客戶端既有封測證據 | Amkor FCBGA 型錄、MEOL、Test Services、FY2025 10-K；2026-11-24 | 85 mm／5 nm 階段及客戶資格，2.5D 獨立量產／收入未揭露 | 已／已／C 批 revision 5 預覽通過 |
| 力成；5.7 [company-6239-tw](../industry-map/companies/company-6239-tw.md) | 6239.TW FCBGA／FCCSP、BT／ETS／MIS 及測試；大型 AI 方案仍查證 | deep；本批重查九段 | 覆晶、測試與已開發大型封裝；無 2.5D 中介層 offering | PTI Flip Chips／Tech、114 年報第 73–74 頁；2026-11-24 | 缺具名 HBM／85 mm 採用與量產。本批不以 TSV 開發推定中介層交付 | 已／已／C 批 revision 5 預覽通過 |
| Ibiden；5.8 [company-4062-t](../industry-map/companies/company-4062-t.md) | 4062.T 的 SAP、微孔、大尺寸與多層覆晶載板 | deep；本批重查九段 | 成品與原料交付分開；Gama／Ono 擴建、資格和業務曝險分列 | Flip Chip PKG、IR 2026 pp.8–10、4062 官方及 Gama 計畫；2026-11-24 | 未取得具名驗收、同板良率及產品收入 | 已／已／C 批 revision 5 預覽通過 |
| Shinko；5.8 [company-private-shinko](../industry-map/companies/company-private-shinko.md) | DLL／DLL3；6967 下市、JICC-04 存續更名及歷史財務 | deep；本批重查九段 | 同載板與 Ibiden 對齊；IATF 只限列示範圍，玻璃 prototype 分列 | DLL／DLL3 型錄、JPX、電子公告、IR Archive、IATF；2026-11-24 | 下市後財務資料不足，無產品客戶／收入、詳細驗收 | 已／已／C 批 revision 5 預覽通過 |
| 欣興；5.9 [company-3037-tw](../industry-map/companies/company-3037-tw.md) | 3037.TW；PCB／IC Carrier 與集團 FCBGA；台灣 KF 產能預留 | deep；本批重查九段 | 子公司 HKEX 草稿及台灣產線分開；同條件比較 | TWSE 3037、114 年報、HKEX 歷史、NVIDIA 2026-10-21；2026-11-24 | 無 KF 合格料號、量產與獨立產品收入 | 已／已／C 批 revision 5 預覽通過 |
| 南電；5.9 [company-8046-tw](../industry-map/companies/company-8046-tw.md) | 8046.TW；ABF、PP、HDI、PCB，現行 L/S 9/12 μm | deep；本批重查九段 | 材料、規格、資格與產線分開；與欣興／Ibiden 同角色比較 | 公司簡介、ABF 路線圖、114 合併財報；2026-11-24 | 同條件良率、驗收、ABF 單項收入未公開 | 已／已／C 批 revision 5 預覽通過 |
| 景碩；5.9 [company-3189-tw](../industry-map/companies/company-3189-tw.md) | 3189.TW；FCBGA／ABF、SiP 與 PBGA；NVIDIA 幼獅具名合作 | deep；本批重查九段 | 比較同堆疊與認證；已供應、未來擴建及營收分開 | Products／董事長、TWSE 3189、雙方幼獅 2026-11-17；2026-11-24 | 無個別料號、專屬量的基期及收入；時程為目標 | 已／已／C 批 revision 5 預覽通過 |

## 既有供應角色逐列核對

以下角色確實存在並經 taxonomy 連到本次核心產品；分類本身不證明公司交付。新角色的證據裁決另見各批廣度表。

| 既有角色 | 本次對應產品與 task | 邊界與來源定位 | 分類／證據／內容／網站 |
|---|---|---|---|
| [role-optical-module](../industry-map/roles/role-optical-module.md) | [product-optical-transceiver](../industry-map/products/product-optical-transceiver.md)（2.1、2.3） | Cisco QSFP-DD800 成品型號、華星光年報與 Marvell 元件；以距離、lane 與 FEC 核對成品交付及替代。 | 已有／已／已／樣本驗收完成 |
| [role-optical-dsp](../industry-map/roles/role-optical-dsp.md) | [product-optical-dsp](../industry-map/products/product-optical-dsp.md)（3.1） | Marvell Spica／Nova、Credo Dove 的 lane、driver 與主機側 LPO 分工。 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-optical-chip](../industry-map/roles/role-optical-chip.md) | [product-inp-laser-chip](../industry-map/products/product-inp-laser-chip.md)（3.2） | Lumentum HL13B5CP00-Ln、Coherent EML 官方頁和 IPSR-I §2.2.5 支持晶粒交付；磊晶、載體與成品模組按不同節點審查 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-optical-epiwafer](../industry-map/roles/role-optical-epiwafer.md) | [product-optical-epiwafer](../industry-map/products/product-optical-epiwafer.md)（3.2） | 聯亞 Data center 與 IQE InP 型錄支持磊晶片交付；光柵或 p-metal 加工可納入約定，但晶粒合格量另核 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-electrical-connectivity](../industry-map/roles/role-electrical-connectivity.md) | [product-retimer](../industry-map/products/product-retimer.md)、[product-active-electrical-cable](../industry-map/products/product-active-electrical-cable.md)（3.3） | Aries、Toucan、SPAN、SHIFT、Taurus 原文核對；應用按 PCIe／CXL 晶片、Ethernet 線組和線端內部模組分開 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-switch-silicon](../industry-map/roles/role-switch-silicon.md) | [product-ethernet-switch-asic](../industry-map/products/product-ethernet-switch-asic.md)（3.4） | Broadcom Tomahawk 與 Marvell Teralynx 支持 ASIC 交付；面板與 NOS 仍取決於整機設計 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-switch-system](../industry-map/roles/role-switch-system.md) | [product-datacenter-switch](../industry-map/products/product-datacenter-switch.md)（3.4） | Accton／Arista 整機資料表支持面板埠、風道及 NOS；限對齊整機條件時比較 | 已有／已／已／A 批 revision 3 預覽通過 |
| [role-rack-power-supply](../industry-map/roles/role-rack-power-supply.md) | [product-power-shelf-psu](../industry-map/products/product-power-shelf-psu.md)（4.1） | OCP 台達、康舒列示 AC/DC 成品；機架或伺服器轉換位置與 N+1、電氣及機械介面一致才能互比。 | 已有／已／已／B 批 revision 4 預覽通過 |
| [role-board-power-conversion](../industry-map/roles/role-board-power-conversion.md) | [product-pmic-voltage-regulator](../industry-map/products/product-pmic-voltage-regulator.md)、[product-power-module](../industry-map/products/product-power-module.md)（4.2） | 以 MPS、Renesas、Vicor 與台達原文區分控制晶片、功率級、中間端及近負載模組。 | 已有／已／已／B 批 revision 4 預覽通過 |
| [role-interposer-integration](../industry-map/roles/role-interposer-integration.md) | [product-2p5d-interposer-package](../industry-map/products/product-2p5d-interposer-package.md)（5.1） | 與載板、材料及封裝局部加工依交付拆分；TSMC、ASE 與 Amkor 依各自平台範圍。 | 已有／已／已／C 批 revision 5 預覽通過 |
| [role-osat-assembly](../industry-map/roles/role-osat-assembly.md) | [product-flip-chip-package-service](../industry-map/products/product-flip-chip-package-service.md)（5.1） | ASE／Amkor 同一尺寸與覆晶服務再互比；製造、整合和純測試分開。 | 已有／已／已／C 批 revision 5 預覽通過 |
| [role-ic-substrate](../industry-map/roles/role-ic-substrate.md) | [product-abf-substrate](../industry-map/products/product-abf-substrate.md)（5.2） | Ibiden／Shinko 等成品並依核心、層數、用途區分，材料與設備各自交付。 | 已有／已／已／C 批 revision 5 預覽通過 |

## 閱讀入口、比較與需求案例

| 範圍／task | 應用與既有入口 | 比較／傳導內容的閱讀位置 | 來源、限制與走讀紀錄 |
|---|---|---|---|
| 樣本 2.1–2.3 | [AI networking](../industry-map/applications/application-ai-networking.md) → [光收發模組](../industry-map/products/product-optical-transceiver.md) → [華星光](../industry-map/companies/company-4979-two.md) → 來源 | Cisco 成品、DSP、AEC、LPO、CPO 與華星光代工交付界線；見上列 P1–P5 | 樣本 revision 3 已匯入並驗證，Boris 完成樣本驗收。最終 release 的桌機與手機另查 6.5。 |
| A 3.10–3.11 | [AI networking](../industry-map/applications/application-ai-networking.md)、[networking](../industry-map/ai-server/networking.md)、[CPO](../industry-map/themes/cpo-silicon-photonics.md) | [research-ai-networking-optical-electrical](../industry-map/research/research-ai-networking-optical-electrical.md)：「先固定通訊域與線組」對照 DAC／AEC、DSP 可插拔、LPO、CPO；「案例」列端點、介質、晶片與公司 | 四步分列事實、inference、反向條件與追蹤證據；Accton AS9817-64O、Cisco QSFP-DD800、Credo SPAN、LPO §§5–8、Davisson Availability、OIF 800ZR §1，2026-11-24 已審；Revision 3 已通過預覽 |
| B 4.10–4.11 | [AI rack power](../industry-map/applications/application-ai-rack-power.md)、[power](../industry-map/ai-server/power.md)、[power discrete](../industry-map/semiconductor/power-discrete.md)、[電力瓶頸](../industry-map/themes/power-bottleneck.md) | [研究與案例](../industry-map/research/research-ai-facility-to-board-power.md)；設備、備援、交期及負載分層 | 以假設 60／100 kW 及 5+1 案例驗證；預留容量、架構與削峰抵銷。Revision 4 已通過預覽。 |
| C 5.10–5.11 | [chip integration](../industry-map/applications/application-chip-integration.md)、[advanced packaging](../industry-map/ai-server/advanced-packaging.md)、[substrate](../industry-map/ai-server/substrate.md)；另有材料、設備、測試與 PCB | [規格傳導案例](../industry-map/research/research-chip-integration-abf-demand.md)；分中介層、載板、PCB 及相關交付 | 同材料和規格解讀良率及資格；局部矽橋、排版與設計改變作反向。Revision 5 已通過預覽。 |
| 共用 6.1–6.6 | 三方向、共用公司與角色 | 影響路徑、delta specs 及最終同版的各階段 | 6.1、6.2 已核對。部署、Boris 走讀和靜態快照依[驗收紀錄](research-expansion-acceptance.md)各自記錄。 |

## 矩陣建置核對（task 1.2）

2026-11-24 對照 design D3：14 個明列核心 product ID 與 22 個優先 company ID 均有獨立列且檔案存在；12 個既有供應 role 依 taxonomy 展開。A 的 2 個、B 的 6 個、C 的 3 個廣度範圍逐項列入，不因尚未取得證據刪除。三批入口、比較、需求案例與網站驗收各有 task 對照。

這項核對只驗收矩陣覆蓋與欄位，沒有宣稱產品、公司或新增角色的研究完成。後續每個內容 task 必須更新其列中的實際本文、主張、原文定位、期間、查核日及閱讀結果。


### 光纖組件新增角色公司審閱（3.5）

| 公司 | 九段閱讀位置與已讀原文 | 交付與限制 | 狀態 |
|---|---|---|---|
| [安費諾 APH](../industry-map/companies/company-aph.md) | 逐段核對供應角色至財務可取性。MPO Cable Assemblies 的 Features／Specifications、既有 FY2025 10-K Item 1 Markets／Customers、MD&A；2026-11-24 補查產品。 | offering 回到 mpo-fiber-assembly-capability。同 APC 介面及芯數時與貿聯比對，尚缺同條件數據。個別終端認證、客戶、出貨及營收未揭露。 | 內容已審閱，A 批 revision 3 預覽通過 |
| [貿聯 3665.TW](../industry-map/companies/company-3665-tw.md) | 逐段核對九個公司段落；BizLink 2026-01-05 公告、MPO Connectors All Products 與既有 114 年年報交付及集中度。2026-11-24 補查產品及集團歸屬。 | offering 回到 xfs-optical-assembly-capability。既有 3665.TW／BizLink 識別沿用。XFS 是集團子公司；官網尚缺指定光組件的合格客戶、料號損耗及收入。 | 內容已審閱，A 批 revision 3 預覽通過 |


### 主機介面卡新增角色公司審閱（3.6）

- [博通 AVGO](../industry-map/companies/company-avgo.md) 的 NIC 角色、交付與同用途比較已核對 57708-PB103；既有製造、客戶、曝險與申報邊界依 FY2025 Form 10-K 逐段閱讀，下一步依 3.7 完成交換、光與網路產品合併審閱。offering 指向 bcm57708-host-adapter-delivery，卡別採用及出貨未核實。
- [輝達 NVDA](../industry-map/companies/company-nvda.md) 九段已按該角色逐項審閱。C8180 OPN／FW、硬體規格與 FY2026 Form 10-K Item 1／1A／7；沿用 NVDA 與 CIK，按封面確認 Nasdaq。offering 指向 connectx8-host-adapter-delivery；指定料號收入、套件客戶與同條件對照未揭露或未取得。研究深度限主機介面卡，其餘產品線缺口留在公司頁。兩家均待 A 批網站預覽。

## B 批需求案例

[設施、機櫃與板端的供電](../industry-map/research/research-ai-facility-to-board-power.md#案例同一機房由-60-kw-升到-100-kw-的機櫃)（4.10）。分開假設的 60／100 kW 機櫃持續負載、5+1 PSU 備援、機房接入容量與實際設備交期。沿變壓、開關、UPS、BBU、幹線、架端及板端追蹤。預留容量、集中式 HVDC、削峰或提高單 shelf 功率可抵銷，追蹤單線圖、型號、末期續航及驗收。

## C 批需求案例

[先進封裝與 ABF 載板的規格傳導](../industry-map/research/research-chip-integration-abf-demand.md)（5.10）。用 Ibiden 的尺度例示範面積和層數如何改變翹曲、微孔、曝光、填鍍與終檢，固定同材料、排版及驗收才推有效產出。附假設算例、不同公司證據階段、設計及良率的反向條件。
