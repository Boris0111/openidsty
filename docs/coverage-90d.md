# 近 90 日資料覆蓋矩陣

取得基準：2026-10-14T15:24:24.158330+00:00；規則：industry-rules-2026-10-14-v2

直接事件僅計發布日可確認、非預告、非例行的內容分類；背景統計、公司提及、未知日期與 inference 分開。來源設定範圍不代表有事件。

| 種類 | 環節／題材 | 研究 | 來源設定／成功 | 直接 30／90 日 | 背景 90 日 | 未知發布日 | 缺口 |
|---|---|---|---|---|---|---|---|
| segment | 先進封裝 (advanced-packaging) | 有 | 3／2 | 40／140 | 0 | 0 | 1 個來源取得失敗 |
| segment | 運算晶片 (compute) | 有 | 5／4 | 34／105 | 0 | 0 | 1 個來源取得失敗 |
| segment | 資料中心與雲端業者 (datacenter) | 有 | 7／6 | 90／293 | 1 | 0 | 1 個來源取得失敗 |
| segment | EDA 工具與矽智財 (eda-ip) | 有 | 2／2 | 11／18 | 0 | 0 | — |
| segment | 半導體設備 (equipment) | 有 | 4／4 | 19／71 | 1 | 2 | — |
| segment | 晶圓代工 (foundry) | 有 | 5／3 | 39／107 | 3 | 0 | 2 個來源取得失敗 |
| segment | 連接器、線材與滑軌 (interconnect) | 有 | 3／3 | 6／9 | 0 | 0 | — |
| segment | 半導體材料 (materials) | 有 | 4／4 | 10／38 | 0 | 0 | — |
| segment | 記憶體 (memory) | 有 | 3／3 | 42／161 | 0 | 0 | — |
| segment | 網通與光通訊 (networking) | 有 | 6／5 | 26／108 | 4 | 2 | 1 個來源取得失敗 |
| segment | 系統組裝與機櫃整合 (odm) | 有 | 4／4 | 1／7 | 4 | 2 | — |
| segment | 印刷電路板與銅箔基板 (pcb) | 有 | 5／5 | 13／35 | 4 | 2 | — |
| segment | 電源與供電架構 (power) | 有 | 7／7 | 26／72 | 2 | 2 | — |
| segment | 功率與分離式元件 (power-discrete) | 有 | 5／5 | 18／41 | 3 | 0 | — |
| segment | ABF 載板 (substrate) | 有 | 4／4 | 8／26 | 0 | 0 | — |
| segment | 測試與探針 (test) | 有 | 3／3 | 8／10 | 3 | 0 | — |
| segment | 散熱 (thermal) | 有 | 5／5 | 8／21 | 0 | 0 | — |
| theme | 高壓直流供電架構 (800vdc) | 有 | 4／4 | 9／24 | 0 | 0 | — |
| theme | 先進製程節點推進 (advanced-node-2nm) | 有 | 4／3 | 11／33 | 0 | 0 | 1 個來源取得失敗 |
| theme | 共同封裝光學與矽光子 (cpo-silicon-photonics) | 有 | 4／4 | 19／82 | 0 | 0 | — |
| theme | 客製 ASIC 與通用 GPU 的路線競爭 (custom-asic-vs-gpu) | 有 | 3／3 | 9／33 | 0 | 0 | — |
| theme | HBM4 世代轉換 (hbm4) | 有 | 3／3 | 1／9 | 0 | 0 | — |
| theme | 液冷散熱 (liquid-cooling) | 有 | 4／4 | 6／15 | 0 | 0 | — |
| theme | 資料中心電力瓶頸 (power-bottleneck) | 有 | 4／4 | 4／8 | 1 | 0 | — |

## 題材判讀與指標覆蓋

| 題材 | 判讀 | 原查核基準 | 指標設定／取得 | 指標缺口 |
|---|---|---|---|---|
| 高壓直流供電架構 (800vdc) | 可讀 | 2026-10-07 | 1／1 | 台達電單月總營收 (proxy)：代理總營收未提供題材專屬收入 |
| 先進製程節點推進 (advanced-node-2nm) | 可讀 | 2026-10-07 | 2／1 | 台積電 2nm 晶圓營收占比 (direct)：尚未取得有效數值；不補零；台積電 2nm 晶圓營收占比 (direct)：來源 tsmc-node-metrics：ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403；台積電單月總營收 (proxy)：代理總營收未提供題材專屬收入 |
| 共同封裝光學與矽光子 (cpo-silicon-photonics) | 可讀 | 2026-10-07 | 1／1 | 聯亞單月總營收 (proxy)：代理總營收未提供題材專屬收入 |
| 客製 ASIC 與通用 GPU 的路線競爭 (custom-asic-vs-gpu) | 可讀 | 2026-10-07 | 1／0 | Broadcom 單季總營收 (proxy)：尚未取得有效數值；不補零；Broadcom 單季總營收 (proxy)：來源 sec-facts-avgo：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；Broadcom 單季總營收 (proxy)：代理總營收未提供題材專屬收入 |
| HBM4 世代轉換 (hbm4) | 可讀 | 2026-10-07 | 1／0 | Micron 單季總營收 (proxy)：尚未取得有效數值；不補零；Micron 單季總營收 (proxy)：來源 sec-facts-mu：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；Micron 單季總營收 (proxy)：代理總營收未提供題材專屬收入 |
| 液冷散熱 (liquid-cooling) | 可讀 | 2026-10-07 | 2／2 | 奇鋐單月總營收 (proxy)：代理總營收未提供題材專屬收入 |
| 資料中心電力瓶頸 (power-bottleneck) | 可讀 | 2026-10-07 | 1／0 | Vertiv 單季總營收 (proxy)：尚未取得有效數值；不補零；Vertiv 單季總營收 (proxy)：來源 sec-facts-vrt：ValueError: 需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email；Vertiv 單季總營收 (proxy)：代理總營收未提供題材專屬收入 |

## 真實分類樣本

### 先進封裝 (advanced-packaging)
- [Accelerating Advanced IC Package Design: A Methodology for Early and Iterative Optimization of Chiplet Integration](https://semiengineering.com/accelerating-advanced-ic-package-design-a-methodology-for-early-and-iterative-optimization-of-chiplet-integration/)；發布 2026-10-14T07:02:00+00:00；事件 2853
- [先進封裝角色躍升！英特爾晶圓代工揭「晶片三道牆」：客戶信任成關鍵](https://technews.tw/2026/10/14/semicon-west-intel-foundry-lalitha-immaneni/)；發布 2026-10-14T06:06:01+00:00；事件 2813
- [日月光投控 2026 年第三季優於預期，美銀力挺目標價至 900 元](https://finance.technews.tw/2026/10/14/ase-technology-holding-co-ltd-reported-better-than-expected-results-for-the-third-quarter-of-2026/)；發布 2026-10-14T02:50:13+00:00；事件 2816
- 來源 ir-tsmc：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 運算晶片 (compute)
- [晶片自主化仍追不上需求，中國科技公司今年狂掃逾 100 萬顆輝達 GPU](https://technews.tw/2026/10/14/chinese-ai-companies-buy-1-million-nvidia-gaming-and-workstation-gpus-in-a-single-year/)；發布 2026-10-14T06:20:33+00:00；事件 2812
- [攻智慧感測！智原推 MIPI C/D Combo PHY IP，通過聯電 14 奈米 FinFET 矽驗證](https://technews.tw/2026/10/13/faraday-powers-intelligent-sensing-with-new-14nm-mipi-cd-combo-phy-ip/)；發布 2026-10-13T14:43:51+00:00；事件 2830
- [英特爾發表代號 Crescent Island 之 AI 推論晶片與 Xeon 伺服器架構](https://technews.tw/2026/10/13/intel-unveils-its-ai-inference-chip-codenamed-crescent-island-and-xeon-server-architecture/)；發布 2026-10-13T07:15:06+00:00；事件 2710
- 來源 ir-microsoft：success；歷史觀察 未取得；尚未取得回補紀錄
- 來源 ir-nvidia：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 資料中心與雲端業者 (datacenter)
- [雲豹能源攜手旗下子公司亮相能源展，跨足 AI 資料中心能源基建](https://technews.tw/2026/10/14/cloud-leopard-energy-subsidiaries-showcase-energy-expo-venturing-ai-data-center-energy-infrastructure/)；發布 2026-10-14T07:30:34+00:00；事件 2846
- [東元搶攻全球電力商機，儲能、變壓器雙線出擊](https://technews.tw/2026/10/14/teco-targets-global-power-market-energy-storage-transformers/)；發布 2026-10-14T06:07:30+00:00；事件 2836
- [輝達中國 AI 晶片市占下滑，華為加速追趕](https://technews.tw/2026/10/14/nvidias-china-ai-chip-share-falls-as-huawei-closes-gap/)；發布 2026-10-14T00:15:42+00:00；事件 2824
- 來源 eia-monthly：success；歷史觀察 2026-09-24T00:00:00+00:00；本輪僅最新公開月報；未取得歷史發布快照，保留回補缺口
- 來源 ir-delta：success；歷史觀察 未取得；尚未取得回補紀錄
- 來源 ir-microsoft：success；歷史觀察 未取得；尚未取得回補紀錄
- 來源 ir-nvidia：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-energy：success；歷史觀察 2026-07-08T17:54:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### EDA 工具與矽智財 (eda-ip)
- [Simplify Electronic-Photonic Design Workflows: eBook](https://semiengineering.com/simplify-electronic-photonic-design-workflows/)；發布 2026-10-14T07:02:41+00:00；事件 2852
- [Agentic AI Automates RTL Waveform Analysis And Debugging (Columbia, Google)](https://semiengineering.com/agentic-ai-automates-rtl-waveform-analysis-and-debugging-columbia-google/)；發布 2026-10-13T20:20:40+00:00；事件 2793
- [Blog Review: Oct. 7](https://semiengineering.com/blog-review-oct-7-3/)；發布 2026-10-07T07:01:12+00:00；事件 319
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 半導體設備 (equipment)
- [AI 強勁需求推升 ASML 第三季營收獲利創新高，全年營收展望上調](https://finance.technews.tw/2026/10/14/asmls-third-quarter-revenue-and-profit-hit-record-highs/)；發布 2026-10-14T06:50:37+00:00；事件 2810
- [應材獲利目標夯、未給營收展望  市場失望股價摔](https://finance.technews.tw/2026/10/14/applied-materials-stock-could-be-flashing-a-sell-signal-on-this-investor-day-omission/)；發布 2026-10-14T01:30:31+00:00；事件 2819
- [全球半導體設備支出爆發！SEMI 估 2029 年達 2,270 億美元，美國擴產加速](https://finance.technews.tw/2026/10/14/semicon-west-clark-tseng/)；發布 2026-10-13T19:50:30+00:00；事件 2828
- 來源 census-m3：success；歷史觀察 2026-10-02T00:00:00+00:00；目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tpca-news：success；歷史觀察 2026-04-23T00:00:00+08:00；以公開消息列表及免費正文可取範圍為限

### 晶圓代工 (foundry)
- [先進封裝角色躍升！英特爾晶圓代工揭「晶片三道牆」：客戶信任成關鍵](https://technews.tw/2026/10/14/semicon-west-intel-foundry-lalitha-immaneni/)；發布 2026-10-14T06:06:01+00:00；事件 2813
- [應材矽谷 EPIC 中心開幕！台積電魏哲家：加速 2 奈米以下量產](https://technews.tw/2026/10/13/applied-materials-epic-center/)；發布 2026-10-13T14:58:12+00:00；事件 2829
- [Chip Industry Technical Paper Roundup: Oct. 13](https://semiengineering.com/chip-industry-technical-paper-roundup-oct-13-2/)；發布 2026-10-13T07:01:36+00:00；事件 2792
- 來源 ir-tsmc：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tsmc-node-metrics：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403

### 連接器、線材與滑軌 (interconnect)
- [CPO Testing Faces A Moving Target Problem](https://semiengineering.com/cpo-testing-faces-a-moving-target-problem/)；發布 2026-10-08T07:01:36+00:00；事件 315
- [Crossing Chiplet Boundaries With PCIe Over UCIe](https://semiengineering.com/crossing-chiplet-boundaries-with-pcie-over-ucie/)；發布 2026-10-01T07:03:02+00:00；事件 342
- [PCIe 8.0 Over UCIe 3.0: Bringing A Proven Protocol Into The Chiplet Era](https://semiengineering.com/pcie-8-0-over-ucie-3-0-bringing-a-proven-rrotocol-into-the-chiplet-era/)；發布 2026-09-30T07:02:19+00:00；事件 349
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 半導體材料 (materials)
- [供應給台積電？富士軟片在美增產先進半導體材料](https://technews.tw/2026/10/14/fujifilm-to-expand-cmp-slurry-production-capacity-in-the-united-states/)；發布 2026-10-14T06:40:39+00:00；事件 2811
- [美銀唱多 Soitec、目標價翻倍  看旺矽光子題材](https://technews.tw/2026/10/12/bofa-bullish-on-soitec-sharply-raises-price-target/)；發布 2026-10-12T03:30:51+00:00；事件 2742
- [合晶四度申請臺商回臺投資，178.8 億元擴大中科二林廠布局](https://finance.technews.tw/2026/10/09/topco-scientific-4th-taiwan-investment-17-88bn-expand-erlin-plant/)；發布 2026-10-09T02:15:16+00:00；事件 2641
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tpca-news：success；歷史觀察 2026-04-23T00:00:00+08:00；以公開消息列表及免費正文可取範圍為限

### 記憶體 (memory)
- [長鑫存儲擬推出首款 4F² 伺服器 DDR5 記憶體，挑戰國際三大廠](https://technews.tw/2026/10/14/changxin-memory-plans-to-launch-its-first-4f%c2%b2-server-ddr5-memory/)；發布 2026-10-14T00:45:35+00:00；事件 2822
- [DDR4 漲幅超越 DDR5，記憶體供不應求可能繼續兩年](https://finance.technews.tw/2026/10/13/the-shortage-of-memory-chips-may-continue-for-another-two-years/)；發布 2026-10-13T07:30:07+00:00；事件 2833
- [Chip Industry Technical Paper Roundup: Oct. 13](https://semiengineering.com/chip-industry-technical-paper-roundup-oct-13-2/)；發布 2026-10-13T07:01:36+00:00；事件 2792
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 網通與光通訊 (networking)
- [光電測試平台成 CPO 量產關鍵，測試設備供應鏈版圖將迎新變局](https://technews.tw/2026/10/13/optoelectronic-testing-platforms-crucial-cpo-mass-production-ushering-new-changes-test-equipment-supply-chain-landscape/)；發布 2026-10-13T07:05:57+00:00；事件 2711
- [未來五年晶圓需求持續成長！Yole 看好 CPO、玻璃基板與 800V 供電成下波技術焦點](https://technews.tw/2026/10/13/semicon-west-yole-jean-christophe-eloy/)；發布 2026-10-13T04:15:16+00:00；事件 2716
- [台股企業獲利上看 40%！群益點名矽光子、低軌衛星引領第四季多頭](https://finance.technews.tw/2026/10/12/pcb-ccl-asic/)；發布 2026-10-12T08:02:16+00:00；事件 2735
- 來源 census-m3：success；歷史觀察 2026-10-02T00:00:00+00:00；目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值
- 來源 ir-nvidia：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 系統組裝與機櫃整合 (odm)
- [夏普攜手鴻海供應鏈，進軍 AI 伺服器市場](https://technews.tw/2026/09/16/sharp-takes-orders-for-ai-servers-backed-by-foxconns-supply-chain/)；發布 2026-09-16T05:40:09+00:00；事件 255
- [緯創 AI 伺服器出貨翻倍，美銀喊目標價 265 元](https://finance.technews.tw/2026/09/10/wistron-ai-server-2/)；發布 2026-09-10T05:58:55+00:00；事件 265
- [AI驅動高階載板升級，2026全球載板產值增幅3成，估達195.1億美元](https://www.tpca.org.tw/web/news_detail.php?menu_no=182&mod_no=5&news_no=500440)；發布 2026-09-09T16:00:00+00:00；事件 199
- 來源 census-m3：success；歷史觀察 2026-10-02T00:00:00+00:00；目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 印刷電路板與銅箔基板 (pcb)
- [雲端巨頭首度入股台灣 PCB 廠！亞馬遜為何押寶金像電？](https://technews.tw/2026/10/12/why-is-amazon-betting-on-gold-circuit/)；發布 2026-10-12T00:00:28+00:00；事件 2763
- [TPCA Show 2026 規模創新高！攜手 IMPACT 深度串聯 PCB 與先進封裝，聚焦AI 新局](https://technews.tw/2026/10/08/tpca-show-2026-impact-pcb/)；發布 2026-10-08T05:00:42+00:00；事件 135
- [議價能力提升與 AI 基礎建設布局顯著，外資力挺臻鼎-KY 目標價 750 元](https://finance.technews.tw/2026/10/08/foreign-investors-strongly-support-zhen-ding-ky-with-a-target-price-of-nt750/)；發布 2026-10-08T02:30:35+00:00；事件 207
- 來源 census-m3：success；歷史觀察 2026-10-02T00:00:00+00:00；目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tpca-news：success；歷史觀察 2026-04-23T00:00:00+08:00；以公開消息列表及免費正文可取範圍為限

### 電源與供電架構 (power)
- [輝達、AMD 點火 AI 機櫃戰局，800 VDC 電源、散熱族群蓄勢待發](https://technews.tw/2026/10/13/nvidia-amd-ai-server-rack-specs-emerge-800vdc-power-liquid-cooling-opportunities/)；發布 2026-10-13T09:21:47+00:00；事件 2840
- [未來五年晶圓需求持續成長！Yole 看好 CPO、玻璃基板與 800V 供電成下波技術焦點](https://technews.tw/2026/10/13/semicon-west-yole-jean-christophe-eloy/)；發布 2026-10-13T04:15:16+00:00；事件 2716
- [Chip Industry Week In Review](https://semiengineering.com/chip-industry-week-in-review-159/)；發布 2026-10-09T07:01:17+00:00；事件 2636
- 來源 census-m3：success；歷史觀察 2026-10-02T00:00:00+00:00；目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值
- 來源 eia-monthly：success；歷史觀察 2026-09-24T00:00:00+00:00；本輪僅最新公開月報；未取得歷史發布快照，保留回補缺口
- 來源 ir-delta：success；歷史觀察 未取得；尚未取得回補紀錄
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-energy：success；歷史觀察 2026-07-08T17:54:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 功率與分離式元件 (power-discrete)
- [嘉和半導體 GaNrich 布局 40V–1200V 全系列 GaN 功率元件，加速全球市場滲透](https://technews.tw/2026/10/13/ganrich-gan-on-si-sapphire/)；發布 2026-10-13T06:40:54+00:00；事件 2712
- [SIC 基板邁向 12 吋，台廠瞄準 AI 電源、先進封裝與通訊商機](https://technews.tw/2026/10/13/sic-substrates-12-inch-taiwan-firms-target-ai-power-advanced-packaging-communication-opportunities/)；發布 2026-10-12T22:00:54+00:00；事件 2730
- [跨入 8 吋主流規格 SiC 商機！廣運旗下盛新材料 10/15 登錄興櫃](https://finance.technews.tw/2026/10/12/mainstream-specifications/)；發布 2026-10-12T07:32:07+00:00；事件 2738
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-energy：success；歷史觀察 2026-07-08T17:54:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### ABF 載板 (substrate)
- [中長期獲利展望看俏，美銀給欣興電目標價 1,650 元](https://finance.technews.tw/2026/10/12/unimicron-technologys-medium-to-long-term-profit-outlook-is-promising/)；發布 2026-10-12T02:00:05+00:00；事件 2760
- [獲利持續改善與產品漲價前景，大和證券力挺南電目標價 2,460 元](https://finance.technews.tw/2026/10/05/daiwa-securities-strongly-supports-nan-ya-powers-target-price-of-nt2460/)；發布 2026-10-05T02:30:00+00:00；事件 1021
- [IMPACT 2026 聚焦節能 AI，產學齊聚研討先進封裝、異質整合](https://technews.tw/2026/10/05/impact-iaac-2026-ai-computing-to-systems-and-applications/)；發布 2026-10-05T01:00:00+00:00；事件 602
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tpca-news：success；歷史觀察 2026-04-23T00:00:00+08:00；以公開消息列表及免費正文可取範圍為限

### 測試與探針 (test)
- [旺矽：澄清115年10月13日經濟日報C07版之新聞報導內容](https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O)；發布 2026-10-13T02:43:27+00:00；事件 2807
- [小摩唱多探針卡巨頭特諾本  看好晶片測試需求](https://finance.technews.tw/2026/10/07/jpmorgan-bullish-on-technoprobe/)；發布 2026-10-07T04:00:17+00:00；事件 159
- [AI、矽光子需求旺：矽格測試價格調漲、資本支出擬再加碼](https://technews.tw/2026/10/06/ai-silicon-photonics-demand-boosts-gigasolution-testing-prices-capex/)；發布 2026-10-06T09:33:00+00:00；事件 567
- 來源 moea-industrial-production：success；歷史觀察 2026-07-23T16:00:00+08:00；以官方列表最近六期發布為限；保留工業生產口徑
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 散熱 (thermal)
- [康舒攜手 OmniOn 參展 OCP，秀 100kW 高功率電源與液冷技術](https://technews.tw/2026/10/08/acbel-omnioon-ocp-showcases-100kw-high-power-supply-liquid-cooling-tech/)；發布 2026-10-08T07:45:29+00:00；事件 193
- [奇鋐 Q3 營收創高，外資看好液冷動能延續至 2027 年](https://finance.technews.tw/2026/10/08/2027-avc/)；發布 2026-10-08T02:08:18+00:00；事件 208
- [800VDC 走向 AI 電源主流，台達電、光寶迎戰 OCP 2026](https://technews.tw/2026/10/05/800-vdc-mainstream-ai-power-delta-liteon-ocp-2026/)；發布 2026-10-05T08:20:00+00:00；事件 1017
- 來源 aaon-earnings-metrics：success；歷史觀察 2025-12-31；https://investors.aaon.com/investor-news/aaon-reports-strong-third-quarter-2025-results-driven-by-operational-improvements-and-share-gains: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-second-quarter-2025-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-fourth-quarter-and-full-year-2024-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-first-quarter-of-2024-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-third-quarter-of-2023-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計
- 來源 ir-delta：success；歷史觀察 未取得；尚未取得回補紀錄
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 高壓直流供電架構 (800vdc)
- [輝達、AMD 點火 AI 機櫃戰局，800 VDC 電源、散熱族群蓄勢待發](https://technews.tw/2026/10/13/nvidia-amd-ai-server-rack-specs-emerge-800vdc-power-liquid-cooling-opportunities/)；發布 2026-10-13T09:21:47+00:00；事件 2840
- [未來五年晶圓需求持續成長！Yole 看好 CPO、玻璃基板與 800V 供電成下波技術焦點](https://technews.tw/2026/10/13/semicon-west-yole-jean-christophe-eloy/)；發布 2026-10-13T04:15:16+00:00；事件 2716
- [Chip Industry Week In Review](https://semiengineering.com/chip-industry-week-in-review-159/)；發布 2026-10-09T07:01:17+00:00；事件 2636
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-energy：success；歷史觀察 2026-07-08T17:54:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 先進製程節點推進 (advanced-node-2nm)
- [應材矽谷 EPIC 中心開幕！台積電魏哲家：加速 2 奈米以下量產](https://technews.tw/2026/10/13/applied-materials-epic-center/)；發布 2026-10-13T14:58:12+00:00；事件 2829
- [Chip Industry Technical Paper Roundup: Oct. 6](https://semiengineering.com/chip-industry-technical-paper-roundup-oct-6/)；發布 2026-10-06T07:01:55+00:00；事件 323
- [N2、N3 供應續吃緊！高盛上修台積電明後年資本支出，目標價喊上 3,300 元](https://technews.tw/2026/10/06/goldman-sachs-see-tsmc/)；發布 2026-10-06T02:00:00+00:00；事件 582
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 tsmc-node-metrics：failed；歷史觀察 未取得；ValueError: HTTP 擷取失敗：HTTPStatusError HTTP 403

### 共同封裝光學與矽光子 (cpo-silicon-photonics)
- [光電測試平台成 CPO 量產關鍵，測試設備供應鏈版圖將迎新變局](https://technews.tw/2026/10/13/optoelectronic-testing-platforms-crucial-cpo-mass-production-ushering-new-changes-test-equipment-supply-chain-landscape/)；發布 2026-10-13T07:05:57+00:00；事件 2711
- [未來五年晶圓需求持續成長！Yole 看好 CPO、玻璃基板與 800V 供電成下波技術焦點](https://technews.tw/2026/10/13/semicon-west-yole-jean-christophe-eloy/)；發布 2026-10-13T04:15:16+00:00；事件 2716
- [台股企業獲利上看 40%！群益點名矽光子、低軌衛星引領第四季多頭](https://finance.technews.tw/2026/10/12/pcb-ccl-asic/)；發布 2026-10-12T08:02:16+00:00；事件 2735
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 客製 ASIC 與通用 GPU 的路線競爭 (custom-asic-vs-gpu)
- [DRAM 缺貨潮延續！南亞科看好 Q4 毛利率再迎高峰，ASIC 專案已少量出貨](https://technews.tw/2026/10/12/nanya-technology-2026-q3-financial-report-2/)；發布 2026-10-12T07:09:17+00:00；事件 2739
- [AI GPU 與 ASIC 測試介面需求帶動，外資花旗與大和都給予穎崴買進評等](https://finance.technews.tw/2026/10/07/foreign-investors-citigroup-and-daiwa-both-gave-yingwei-a-buy-rating/)；發布 2026-10-07T02:10:31+00:00；事件 215
- [AI、矽光子需求旺：矽格測試價格調漲、資本支出擬再加碼](https://technews.tw/2026/10/06/ai-silicon-photonics-demand-boosts-gigasolution-testing-prices-capex/)；發布 2026-10-06T09:33:00+00:00；事件 567
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### HBM4 世代轉換 (hbm4)
- [賣方主導市場，三星 HBM4 價格 2027 年將翻倍成長](https://finance.technews.tw/2026/10/07/samsung-hbm4-supply-prices-are-expected-to-double-by-2027/)；發布 2026-10-07T03:30:00+00:00；事件 562
- [加強供應市場 HBM4 需求，三星滿載 4 奈米製程至少 50% 產能提供生產基礎晶片](https://technews.tw/2026/09/08/samsung-is-utilizing-at-least-50-of-its-4nm-process-capacity-to-produce-base-chips/)；發布 2026-09-08T01:50:00+00:00；事件 901
- [韓媒：三星／SK 海力士庫存剩不到 10 天  恐無貨可賣](https://technews.tw/2026/09/07/samsung-and-sk-hynix-inventories-fall-below-10-days/)；發布 2026-09-07T06:10:00+00:00；事件 919
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-semiconductor：success；歷史觀察 2026-07-10T10:20:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 液冷散熱 (liquid-cooling)
- [康舒攜手 OmniOn 參展 OCP，秀 100kW 高功率電源與液冷技術](https://technews.tw/2026/10/08/acbel-omnioon-ocp-showcases-100kw-high-power-supply-liquid-cooling-tech/)；發布 2026-10-08T07:45:29+00:00；事件 193
- [奇鋐 Q3 營收創高，外資看好液冷動能延續至 2027 年](https://finance.technews.tw/2026/10/08/2027-avc/)；發布 2026-10-08T02:08:18+00:00；事件 208
- [800VDC 走向 AI 電源主流，台達電、光寶迎戰 OCP 2026](https://technews.tw/2026/10/05/800-vdc-mainstream-ai-power-delta-liteon-ocp-2026/)；發布 2026-10-05T08:20:00+00:00；事件 1017
- 來源 aaon-earnings-metrics：success；歷史觀察 2025-12-31；https://investors.aaon.com/investor-news/aaon-reports-strong-third-quarter-2025-results-driven-by-operational-improvements-and-share-gains: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-second-quarter-2025-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-fourth-quarter-and-full-year-2024-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-first-quarter-of-2024-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計；https://investors.aaon.com/investor-news/aaon-reports-third-quarter-of-2023-results: ValueError: AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-components：success；歷史觀察 2026-07-10T16:04:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取

### 資料中心電力瓶頸 (power-bottleneck)
- [美 AI 資料中心缺電 34%  大摩：輝達、博通不怕](https://technews.tw/2026/10/06/nvidia-broadcom-shielded-as-ai-power-crunch-hits-chip-supply-chain/)；發布 2026-10-06T01:45:44+00:00；事件 280
- [省下千億美元基建費，虛擬電廠攜手智慧調度成 AI 缺電時代救星](https://technews.tw/2026/10/01/power-grid-revolution-solutions-ai-era/)；發布 2026-10-01T00:30:29+00:00；事件 293
- [別再盲目蓋資料中心，AI 算力競賽轉向智慧控電與架構最佳化雙軌戰場](https://finance.technews.tw/2026/09/26/ai-compute-competition-pivots-intelligent-power-management-architectural-optimization-dual-track-battlefield/)；發布 2026-09-26T00:30:00+00:00；事件 1534
- 來源 eia-monthly：success；歷史觀察 2026-09-24T00:00:00+00:00；本輪僅最新公開月報；未取得歷史發布快照，保留回補缺口
- 來源 semiengineering：success；歷史觀察 2026-07-10T07:01:43+00:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-energy：success；歷史觀察 2026-07-08T17:54:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
- 來源 technews-server：success；歷史觀察 2026-07-08T15:15:00+08:00；以公開 RSS／分類列表可取範圍為限；付費文章不擷取
