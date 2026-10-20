# 技術來源實際取得核對

2026-10-16；只記錄實際讀過範圍。來源權威仍在 `industry-map/sources.yaml`，固定引用在 `technical-documents.yaml`，本表不是第二個 registry。

| 官方入口 | 已讀範圍／版本辨認 | 免費範圍與實際取得限制 |
|---|---|---|
| [OCP Cold Plate](https://www.opencompute.org/projects/cooling-environments/cold-plate/) | web 工具可讀 Scope、工作流與已採納文件列表；冷板需求文件標示 Revision 1.0，介紹自述是 requirements document，非 specification | 本機索引及指定冷板、歧管 PDF GET 403，未取得可供本機轉換的檔案。web 章節擷取與本機完整 PDF 取得分開，不宣稱全部文件已讀 |
| [OCP Rack & Power](https://www.opencompute.org/projects/rack-and-power/) | web 工具已讀供電轉換、儲能、控制及機構支撐 scope；檢索可見 ORv3 BBU Shelf rev1.1 | 本機索引與 BBU Shelf 文件 GET 403；未核讀完整電氣／認證條文，不把 48V 架構規範套成 800VDC 認證 |
| [OIF IA](https://www.oiforum.com/technical-work/implementation-agreements-ias/) | 本機與 web 索引均可讀；可分 normative IA 與 informative framework／白皮書。CPO Module 01.0 PDF 封面日期 2023-03-29 | CPO PDF 實際 GET 200、2,348,869 bytes，SHA256 `586d0ed09f2e19d49bf92b23bb681c266d63db6c477d9c8e8c6cd6cf1d6a304f`，已用 pdf-to-markdown bundled converter 轉換，核讀 scope、介面、熱與測試定位；不據此確認客戶採用 |
| [UCIe](https://www.uciexpress.org/specifications) | 本機 GET 200；已讀 1.0–3.0 介紹與 die-to-die／DFx 範圍 | 個別全文連結為 REQUEST；未登入、未送申請、未取得完整規格。公開介紹不等於已核對 bump map、BER 或完整 compliance 條文 |
| [IEEE IRDS](https://irds.ieee.org/) | web 可讀路線圖目的與研究協調範圍 | 本機 GET 403；未取得各 edition／chapter。入口說明為 informative，只有實際 roadmap 章節才可列 roadmap，不把預測當強制規範或量產承諾 |
| [JEDEC 公開搜尋](https://www.jedec.org/standards-documents) | web 工具 robots 拒絕；本機 GET 200 可讀 Standards & Documents Search、分類與下載導覽 | 沒有取得個別標準全文。頁面同時含 Members Login 不表示整個公開搜尋頁不可讀，也不表示任何規格都免費無登入；逐文件確認 |

本機 HTTP 原始紀錄、必要 PDF 與轉換稿放在忽略的 `.work/technical/`，不公開重散布全文。OIF CPO 本次下載內容仍以官方 01.0 標示；沒有據此宣稱其內容完全等於首次發行時的 bytes。CMIS 5.4 下載成功 15,702,841 bytes，已使用 bundled converter 轉 Markdown，核讀封面及 1.1 Purpose and Scope（頁 30–31）；發布日依封面為 2026-05-21。原檔 SHA256 為 `cd57ebb1cfb8e0a9e9c7b63862b5b261855e9b77844f4cf85bd36ea3808911db`。其餘 register／timing 條文未完整核讀。CPO 與 CMIS 的 runtime 主體 hash 使用鎖定的 pypdf 6.20.1 及 technical-text-v1 計算，與人工已讀範圍分開。

正式規範、草案、路線圖、廠商說明及 informative 的分類按文件本身，不按組織知名度。自動監測只針對明列文件及已驗證 parser；OCP 本機 403 必須保留實際診斷，不能用測試 fixture 取代取得成功。取得失敗仍保留已核對基準與必要短摘錄。
