# 題材判讀來源核對

> 2026-10-23 註記：公司財報已由 OpenSpec change `remove-company-financials` 移除；題材代理指標仍使用月營收與 SEC 營收。本文提及的財務資料、頁面與測試為當時紀錄，不再代表現況。

2026-10-14 整理既有 2026-10-07 研究基準，沒有把本輪文件可讀性查核當成整份題材判讀已重新查核。狀態、全文及原查核日保留；下表記錄新增結構化證據的核對方式與界線。registry 的 checked 只表示指定入口可讀性檢查。

## 液冷／HBM4／CPO

| 題材／證據 ID | 來源及原期間 | 本輪核對 | 支持界線 |
|---|---|---|---|
| 液冷 aaon-q3-product-sales | [AAON 附件](https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm)，2025 Q3；發布 2025-11-06 | HTTPS 200，摘錄與正文比對一致 | BASX 液冷產品收入，非所有候選公司收入 |
| 液冷 aaon-q3-margin | 同上，公司整體毛利率 | HTTPS 200，原文保留同季及前一年比較 | 收入擴張不保證公司整體毛利同步提高；非液冷專屬毛利 |
| 液冷 aaon-q4-product-sales | [AAON 後續附件](https://www.sec.gov/Archives/edgar/data/824142/000082414226000003/liveaaonpressreleaseexs.htm)，2025 Q4；發布 2026-03-02 | HTTPS 200，摘錄與正文一致 | 同一具名產品的後續收入，不擴張成全市場滲透率 |
| HBM4 micron-volume-shipments | [Micron 公告](https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx)，FY2026 Q3 截至 2026-05-28；發布 2026-06-24 | web open 可讀產品段落；本機一般 GET 403 | lead customer 平台高量出貨，不代表所有送樣客戶已認證 |
| HBM4 micron-hbm4-revenue | [原法說會文件](https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe)，2026-06-24 prepared remarks | 官方 URL 搜尋可核對原收入段落；本機 GET 403，web open 原檔轉向 IR 首頁 | 已實現收入措辭，不能直接標為單季數值；原檔再次取得仍是缺口 |
| HBM4 hynix-commercial-shipment | [SK hynix](https://news.skhynix.com/en/q2-2026-business-results/)，2026 Q2；發布 2026-07-29 | HTTPS 200，摘錄與正文一致 | 另一供應商商業出貨，未推出逐客戶份額 |
| CPO broadcom-shipping | [Broadcom 公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)，發布 2025-10-08 | HTTPS 200，摘錄與正文一致 | 商用交換器出貨，非 CPO 獨立財報收入 |
| CPO nvidia-production | [NVIDIA 公告](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory)，發布 2026-05-31 | HTTPS 200，摘錄與正文一致 | 產品生產與採用資訊，非全部客戶現場驗收與量化部署 |

本輪嘗試用 pdf-to-markdown 核對 Micron 原法說檔；因未取得 PDF 位元組，未執行轉換、未宣稱完整原檔已重新閱讀。官方搜尋的原文段落與入口限制均具名記錄；資料匯入不使用此 QA 方法或測試 fixtures。

各論點以來源期間為準；未取得反向證據時明示，不拿風險假設充當反證。液冷的反向論點僅指公司整體利潤率界線。全部新傳導路徑均標 inference；里程碑仍 unconfirmed 的項目保留具體原因，不因已有部分收入或時間經過勾成完成。

## 2nm／ASIC／800VDC／電力瓶頸

| 證據 ID | 來源與期間 | 本輪核對 | 支持界線 |
|---|---|---|---|
| tsmc-q2-node-sales | [TSMC](https://pr.tsmc.com/japanese/news/3326)，2026 Q2；發布 2026-07-16 | web open 有當季期間及占比；本機 GET 403 | 分母是晶圓營收，非市占／公司全部收入；只有此具名節點收入里程碑確認 |
| broadcom-ai-revenue／custom-demand | [Broadcom](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)，FY2026 Q3 截至 2026-08-02；發布 2026-09-02 | HTTPS 200，收入及管理層需求段落可讀 | AI 半導體口徑包含網路，不是純 ASIC 收入 |
| nvidia-power-plan | [NVIDIA](https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-generation-of-ai-factories/)，發布 2025-05-20 | HTTPS 200，架構與 2027 計畫可讀 | roadmap 不等於終端驗收或正式出貨 |
| delta-prototype | [台達](https://www.deltaww.com/en-US/press/40334)，發布 2026-05-28 | HTTPS 200，GTC 展示原文可讀 | 展示不等於客戶認證或專屬產品收入 |
| vertiv-infrastructure-sales | [Vertiv SEC 附件](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)，2026 Q2；發布 2026-07-29 | HTTPS 200，當季收入及期末可讀 | 含熱管理與服務，只提供設備商業採購脈絡 |
| microsoft-capacity-limit | [Microsoft](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)，FY2026 Q4 法說，2026-07-29 | HTTPS 200，capacity constraints／demand exceeds supply 原文可讀 | 整體容量限制，不將所有限制歸因電力 |

## 七題材完整度

| 題材 | 原查核基準 | 支持程度 | 證據／論點／路徑 | 主要仍待核實 |
|---|---|---|---|---|
| 液冷 | 2026-10-07 | well-supported | 3／2／2 | 候選公司液冷收入、方案分配與產能利用 |
| HBM4 | 2026-10-07 | well-supported | 3／1／1 | 原法說檔、精確收入起迄、各廠份額及堆疊認證 |
| CPO | 2026-10-07 | well-supported | 2／1／1 | 題材專屬量化放量與逐案現場驗收 |
| 2nm | 2026-10-07 | well-supported | 1／1／1 | 上游份額、海外產能及後續節點良率 |
| ASIC／GPU | 2026-10-07 | well-supported | 2／1／1 | 純 ASIC 分項、台廠專案及客戶部署 |
| 800VDC | 2026-10-07 | needs-verification | 2／1／1 | 終端認證、客戶訂單與產品收入 |
| 電力瓶頸 | 2026-10-07 | inference | 2／2／1 | 逐案電力限制、PPA 與上線容量 |

每題材都有 conditions、gaps、next_checks 與三個穩定里程碑核對。當前只確認台積電 N2 的具名當季收入；其餘未滿足全部查核點的里程碑不勾成已完成。以上是結構化既有研究與引用核對，不是投資建議或市場預測評分。
