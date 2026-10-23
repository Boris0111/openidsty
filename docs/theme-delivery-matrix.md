# 七題材交付矩陣

> 2026-10-23 註記：公司財報已由 OpenSpec change `remove-company-financials` 移除；題材代理指標仍使用月營收與 SEC 營收。本文提及的財務資料、頁面與測試為當時紀錄，不再代表現況。

2026-10-14 實際公開 API 與網站走查；判讀保留 2026-10-07 基準。

| 題材／支持程度 | 有條件結論 | 成立條件 | 主要不確定性 | 下一確認點 |
|---|---|---|---|---|
| 高壓直流供電架構／needs-verification | 800VDC 的平台計畫、生態系與供應商原型有依據；具名終端客戶認證與可區分產品收入仍待確認，保留 emerging 基準。 | 具名機房完成高壓直流的安全、隔離及保護驗證；端到端供電與降壓方案符合實際機櫃規格；供應商財務揭露區分 800VDC 與既有產品 | 未取得具名終端客戶完成認證／試運轉及現場驗收資料；缺少可區分 800VDC 的量化商業收入；原型與 roadmap 不是負面商用證據，亦未取得同口徑反證 | 原型是否轉為具名客戶驗證與採購？；需要 現場試運轉／驗收及獨立產品訂單／收入 |
| 先進製程節點推進／well-supported | 台積電已揭露當季 2nm 晶圓營收占比，支持原商業放量基準；上游採購份額、海外產能與後續節點的良率不能由單季占比推定。 | 客戶產品與該節點良率／產能匹配；上游設備與材料具有實際驗收及採購份額；逐節點收入與後續變體不得合併 | 未公開的逐客戶良率、上游供應商份額與海外廠爬坡仍待核實；未取得同口徑節點商業收入下滑的反向證據 | 節點放量是否轉為具名上游採購及後續變體收入？；需要 capex／驗收、逐節點收入與客戶產品交付 |
| 共同封裝光學與矽光子／well-supported | 商用 CPO 產品已出貨及生產；原 validating 表示量化放量證據仍有限，不能把商業出貨描述成純研究，也不能以 AI 網路總收入升級狀態。 | 具名客戶的實際驗收與部署可確認；平台距離、功耗、良率及維修條件適配；財報或法說會能區分 CPO 訂單／出貨與其他網路產品 | 未取得可分辨 CPO 的量化財報收入或放量訂單；候選光通訊公司的實際產品適配與得標尚待核實；未取得具名客戶轉回可插拔方案的可核對反向證據 | 生產公告是否轉為具名客戶量化部署？；需要 客戶驗收、部署量與可區分 CPO 的收入／出貨 |
| 客製 ASIC 與通用 GPU 的路線競爭／well-supported | Broadcom 量化已實現 AI 半導體收入並連結客製加速器需求，支持原放量基準；ASIC 與 GPU 可同時擴張，個別設計服務商得標及成本優勢仍待核對。 | 相同工作負載下具有可核對的軟體、利用率及 TCO 優勢；客戶專案實際完成 tape-out 與量產採購；設計服務、NRE 與量產收入分開 | 缺少各雲端 ASIC／GPU 實際採購分配與台廠具名得標資料；尚未取得同口徑專案取消或量產延後的反向證據 | 客製需求是否轉成具名專案與量產收入？；需要 客戶確認、NRE／量產收入與可比較工作負載成本 |
| HBM4 世代轉換／well-supported | 原 scaling 基準有 HBM4 高量出貨及量化收入依據；各供應商份額、堆疊規格與 HBM4E 路線仍需分別驗證。 | 供應商實際完成特定平台的 HBM4 規格與認證；base die／先進封裝產能及良率能支援交付；各世代收入與各客戶分配採同一口徑 | 尚未取得逐供應商 HBM4 份額、16-Hi 認證與 HBM4E 交付資料；尚未取得同口徑反向商業出貨證據；法說會量化措辭的原檔與精確收入起迄仍需再次核對，不能改為未揭露的單季值 | 高量出貨是否擴及更多已認證平台？；需要 分世代收入／出貨、具名客戶認證與原始法說文件 |
| 液冷散熱／well-supported | 液冷已有具名產品收入，支持放量基準；個別冷板、CDU 與設施水路供應商能否受惠，仍取決於採購項目與產品口徑。 | 具名平台採購冷板／CDU 與相應設施水路；候選供應商具有該平台的實際料號、驗收及交付；量化收入須區分液冷、氣冷與混合設備 | 四家候選公司的液冷收入與毛利尚未逐一核對；缺少同口徑的 L2L／L2A 與改造案樣本 | 收入是否隨新平台交付持續放量？；需要 具名採購／交付與分產品財報，不以總月營收代替 |
| 資料中心電力瓶頸／inference | 供電與關鍵基礎設施採購已有商業收入脈絡，保留原 scaling 範圍；設備收入不表示電網瓶頸已解決，也不能把所有雲端容量限制都歸因於電力。 | 具名機房限制確實來自併網、供電或相應設施；採購與設備交付能對應該瓶頸；PPA、許可、併網與實際上線容量分開確認 | 缺少逐案電力與其他設備限制的分解；未取得候選設備公司各自的電力產品收入與 PPA 即時可用容量 | 供電改善是否讓具名機房如期上線？；需要 公用事業併網、許可、交付及 IT 上線容量的同案紀錄 |

## 指標及來源界線

| 題材 | 指標／類型 | 實際取得 | 限制 |
|---|---|---|---|
| 高壓直流供電架構 | 台達電單月總營收／proxy | 2026-09：65399563000 TWD；修訂 1 | 包含其他電源與業務，不等於 800VDC 商業收入；代理總營收未提供題材專屬收入 |
| 先進製程節點推進 | 台積電 2nm 晶圓營收占比／direct | 未取得有效數值 | 非公司全部收入占比、非市占率，也不表示每個客戶良率；尚未取得有效數值；不補零；來源 tsmc-node-metrics：ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403 |
| 先進製程節點推進 | 台積電單月總營收／proxy | 2026-09：511857399000 TWD；修訂 1 | 含不同製程與業務，不等於 2nm 收入；代理總營收未提供題材專屬收入 |
| 共同封裝光學與矽光子 | 聯亞單月總營收／proxy | 2026-09：540492000 TWD；修訂 1 | 不區分 CPO 與其他光通訊產品，不代表 CPO 訂單；代理總營收未提供題材專屬收入 |
| 客製 ASIC 與通用 GPU 的路線競爭 | Broadcom 單季總營收／proxy | 未取得有效數值 | 含軟體及網路業務，不等於純 ASIC 或 AI 半導體收入；尚未取得有效數值；不補零；來源 sec-facts-avgo：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；代理總營收未提供題材專屬收入 |
| HBM4 世代轉換 | Micron 單季總營收／proxy | 未取得有效數值 | 含不同 DRAM／NAND 業務，不等於 HBM4 收入；尚未取得有效數值；不補零；來源 sec-facts-mu：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；代理總營收未提供題材專屬收入 |
| 液冷散熱 | AAON 液冷產品單季收入／direct | 2026 Q2：126600000 USD；修訂 1 | 不代表全市場滲透率，也不代表其他冷板／CDU 供應商收入； |
| 液冷散熱 | 奇鋐單月總營收／proxy | 2026-09：21018128000 TWD；修訂 1 | 包含氣冷等業務，不等於液冷產品收入；代理總營收未提供題材專屬收入 |
| 資料中心電力瓶頸 | Vertiv 單季總營收／proxy | 未取得有效數值 | 包含熱管理與服務，不等於純供電收入或瓶頸解除程度；尚未取得有效數值；不補零；來源 sec-facts-vrt：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；代理總營收未提供題材專屬收入 |

## 證據與里程碑核對

預期日期與已確認核對分開；只有 N2 具名公司收入節點已確認，其餘沒有足夠證據的項目保持 unconfirmed，不因逾期或指標上升而自動完成。每個傳導假設仍標 inference。

### 高壓直流供電架構
- [nvidia-power-roadmap](https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-generation-of-ai-factories/)；期間 NVIDIA 2025-05-20 架構文章；2027 是 roadmap 計畫；發布 2025-05-20
- [delta-800vdc-release](https://www.deltaww.com/en-US/press/40334)；期間 台達 2026-05-28 回顧 GTC 2026 展示，非終端驗收；發布 2026-05-28
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### 先進製程節點推進
- [tsmc-quarterly-pr](https://pr.tsmc.com/japanese/news/3326)；期間 TSMC 2026 Q2，當季晶圓營收占比；期末 2026-06-30；發布 2026-07-16
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### 共同封裝光學與矽光子
- [broadcom-cpo-release](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)；期間 Broadcom TH6-Davisson 商用 CPO 交換器公告；發布 2025-10-08
- [nvidia-photonics-release](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory)；期間 NVIDIA 2026-05-31 生產／採用公告，非 CPO 獨立收入；發布 2026-05-31
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### 客製 ASIC 與通用 GPU 的路線競爭
- [broadcom-earnings-research](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)；期間 Broadcom FY2026 Q3，截至 2026-08-02；包含網路；發布 2026-09-02
- [broadcom-earnings-research](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)；期間 Broadcom FY2026 Q3，管理層對客製加速器與網路的需求描述；發布 2026-09-02
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### HBM4 世代轉換
- [micron-earnings-research](https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx)；期間 Micron FY2026 Q3，財報期末 2026-05-28；不是曆年第三季；發布 2026-06-24
- [micron-hbm4-remarks](https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe)；期間 Micron FY2026 Q3 prepared remarks；累計措辭，非單季專屬收入；發布 2026-06-24
- [sk-hynix-earnings-research](https://news.skhynix.com/en/q2-2026-business-results/)；期間 SK hynix 2026 Q2，產品出貨，非逐客戶份額；發布 2026-07-29
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### 液冷散熱
- [aaon-liquid-cooling-filing](https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm)；期間 AAON 2025 Q3，單季 BASX 液冷產品；發布 2025-11-06
- [aaon-liquid-cooling-filing](https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm)；期間 AAON 2025 Q3，公司整體毛利，非液冷產品毛利；發布 2025-11-06
- [aaon-liquid-cooling-filing](https://www.sec.gov/Archives/edgar/data/824142/000082414226000003/liveaaonpressreleaseexs.htm)；期間 AAON 2025 Q4，單季 BASX 液冷產品；發布 2026-03-02
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

### 資料中心電力瓶頸
- [sec-search](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)；期間 Vertiv 2026 Q2，含熱管理與服務的公司整體收入；發布 2026-07-29
- [ir-microsoft](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)；期間 Microsoft FY2026 Q4，2026-07-29 法說會；整體部署容量限制；發布 2026-07-29
- 判讀／核對查核 2026-10-07；版本功能只建立當時初始基準，沒有較早歷史。

## 實際操作結果

七個題材頁均走查：先讀結論，再找成立條件、不確定性、下一確認點與原始來源；可展開商業化核對及指標原期別／修訂。版本查核日與記錄時間分開，桌機／手機可比較版本並返回目前研究。此裝置關注三類提示各自指向版本、指標、候選區，來源失敗另列。

未取得：TSMC 指標索引 HTTP 403；MU／AVGO／VRT SEC 缺實際聯絡設定。CPO／800VDC 的已有代理值仍不代表題材專屬收入。Micron 舊 PDF 原位址不可讀，原論點使用官方搜尋可核對摘錄並保留可讀性限制，詳見 theme-source-audit.md。
