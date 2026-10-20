# Tasks

實作前置：使用 `b613d53` 已完成成果；保留 `add-evidence-based-theme-assessments` 未歸檔。需求見本 change 的六份 specs，設計與相容策略見 design.md；以下均為尚未執行的實作任務。

## 1. 保存現況與效能基準

- [x] 1.1 核對 Git、OpenSpec、目前環節／題材清單與前置 change，將實際基準記入驗收文件；以 `openspec list`／`status` 與 API 清單確認 17 環節、7 題材，不修改前置 artifacts。
- [x] 1.2 建立可重跑的唯讀負載腳本與 `docs/reading-performance.md`，在隔離還原 DB、既有 production build 記錄現有 endpoint 的 baseline，新文件 endpoint 標為 N/A；確認 10 位讀取者、60 秒暖機、至少 5 分鐘、每類 endpoint 至少 100 樣本及硬體／資料規模／proxy 路徑紀錄齊備。
- [x] 1.3 保存 app DB 備份及隔離環境的事件／財報／觀測／判讀版本、coverage 與三類 token 基準；以還原檢查及固定 reference 回應確認可供後續語意比較，負載測試不寫正式 DB。

## 2. 改善一般閱讀與數值呈現

- [x] 2.1 建立共用中文名稱、狀態及三種 confidence 顯示，套用環節、題材、來源、路徑、breadcrumb 與版本差異；離線瀏覽器確認主要研究使用指定中文、未知對照有明確說明、進階資訊仍可讀原值。
- [x] 2.2 統一數值尺度、幣別、單位與精確值展開；以大額營收、比例／百分點、零、負值、未知與不可比較案例確認顯示正確，既有 Decimal 比較與原始 API 值不變。
- [x] 2.3 將診斷移至進階區、保留中文取得說明與重試，更新 `docs/frontend.md`；以來源失敗及局部 API 失敗的手機／鍵盤走查確認研究仍可讀、原始證據連結未被文字取代破壞。

## 3. 擴充可回溯研究 schema

- [x] 3.1 在唯一 schema 定義 optional `downstream-relations`、`technical-profile`、文件 manifest 與引用規則，附新舊格式及未知日期範例；依文件建立合法測試副本，full／skip-prose 驗證均通過。
- [x] 3.2 擴充來源分類以支援 `global`／`technical-documents`，建立 `industry-map/technical-documents.yaml` 的已核對基準結構；以既有來源與新公開技術入口混合測試確認無重複來源權威，舊 adapter 仍可解析。
- [x] 3.3 擴充 validator 的邊型別、實存下游、文件／版本／論述引用與日期檢查；執行 `python tests/run_validator_tests.py`，確認舊合法基準通過及新增單點失敗案例被精確攔下。
- [x] 3.4 擴充研究匯入的事前驗證與 transaction，維持 Markdown authoring／DB 唯讀投影；以非法引用匯入測試確認無部分寫入，原研究、歷史及三類 token 保留，文件補充說明此分工與維護指令。

## 4. 解釋產業連線並保留導覽

- [x] 4.1 擴充 graph／segment payload 的關係型別與說明，保留 edge ID 與原拓樸；backend 測試確認 `datacenter → compute` 是需求回饋、舊檔顯示未核對，三種遍歷及回路終止案例不退化。
- [x] 4.2 為現有全部下游邊補型別、供應項目或需求機制、介面依賴、條件及證據／具體缺口；逐邊矩陣與 full map 驗證確認雙向宣告一致、不新增虛構客戶交易。
- [x] 4.3 在 Cytoscape 與文字清單提供同一連線詳情、線型圖例及 `relation` URL 選取；瀏覽器測試確認分享、返回、清除、非法連線與快速切換一致，resize 保留視角。
- [x] 4.4 補上手機與鍵盤的開啟／關閉及焦點返回，更新 `docs/frontend.md`／`docs/api.md`；桌機與手機走查確認不需點擊畫布也能讀同一份關係資訊，原環節連結相容。

## 5. 優先完成五個環節的技術研究

- [x] 5.1 逐入口評估 OCP、OIF、UCIe、IEEE IRDS、JEDEC，保存免費範圍、版本可辨識性、已讀內容及取得限制；以官方頁面／實際文件查核紀錄確認不把摘要、REQUEST 或受阻頁當成已讀全文，更新來源維護文件。
- [x] 5.2 補強 thermal 的產品邊界、迴路／介面、材料與維修條件及替代限制；將論述連到文件版本／章節或具體缺口，full map 驗證與散熱／液冷頁走查通過。
- [x] 5.3 補強 power 的轉換層次、PSU／BBU／UPS 邊界、安全及負載條件；以來源定位、供應角色與 800VDC／電力瓶頸題材交叉核對，full map 驗證及中文閱讀通過。
- [x] 5.4 補強 interconnect 的電氣／流體／電力／機構子角色與採用限制；以特定產品及文件定位核對 rail 混義、銅光取捨與公司角色，full map 驗證及關係詳情走查通過。
- [x] 5.5 補強 networking 的 scale-up／scale-out／跨機房範圍與 ASIC／DSP／模組／系統分工；逐項核對距離、耗電、互通、測試與維修條件，full map 驗證與 CPO 題材引用一致。
- [x] 5.6 補強 advanced-packaging 的中介層／載板／D2D／HBM 層次、良率與測試限制及替代條件；核對技術文件適用範圍，full map 驗證與封裝傳導案例通過，不以 roadmap 推定客戶量產。

## 6. 完成其他環節與七題材覆蓋

- [x] 6.1 補強 compute／memory／foundry 的技術面向、採用條件與缺口；逐檔保存來源定位及查核日，以 full map 驗證與閱讀矩陣確認三個環節無泛泛佔位。
- [x] 6.2 補強 pcb／substrate／materials 的產品層次、介面與替代限制；以具名來源、公司子角色及 full map 驗證確認三檔與既有供應邊一致。
- [x] 6.3 補強 equipment／test／eda-ip／power-discrete 的能力邊界與瓶頸；逐項核對來源及未解條件，以 full map 驗證與四檔走查確認不把同環節公司視為同產品供應商。
- [x] 6.4 補強 odm／datacenter 的整合、驗收、設施條件與需求回饋；以來源定位、full map 驗證及原回路案例確認技術能力、部署與收入證據分開。
- [x] 6.5 核對全部七題材的技術引用、條件與既有判讀一致性，建立 `docs/technical-research-matrix.md`；逐列確認 17 環節／7 題材的五種技術面向、證據程度及具體缺口可回到原文，修改 assessment 時保留 change_reason 與原查核基準。

## 7. 建立文件觀測與待核對流程

- [x] 7.1 加入文件定義、內容觀測與核對紀錄的 additive migration／model，串接 manifest 原子匯入及 initialize；以空 DB 與還原 PostgreSQL 驗證初始基準、歷史引用及既有資料筆數保留。
- [x] 7.2 實作有界文件列表／詳情／歷史的只讀 API 與 proxy，提供版本、章節、必要摘錄及可讀範圍；backend tests 確認分頁、未知文件、失效引用與沒有公開 review 寫入入口，更新 `docs/api.md`。
- [x] 7.3 為 OCP／OIF 指定公開文件實作有界監測及內容正規化，必要時鎖定最小 PDF 解析依賴；以真實來源衍生的 parser 正反例驗證新版、同位址變更、空白／版面／ETag 雜訊、解析器變更與登入頁，fixtures 不載入正式環境。
- [x] 7.4 將每日到期檢查接到既有 hourly flow、來源隔離及 advisory lock；整合測試確認失敗不影響其他來源、相同內容重跑無新候選、部分失敗與超量／timeout 有診斷，API 不呼叫外部來源。
- [x] 7.5 實作 manifest 的採納／不影響研究核對紀錄及文件閱讀區；以新版本待核對、採納、無影響與原來源失效案例確認原研究不被自動覆寫，原三類 watchlist token 不因文件取得時間改變。
- [x] 7.6 擴充 coverage／可保存報告並更新 `docs/sources.md` 與文件維護操作指南；逐列走查確認技術研究、文件性質、待核對與缺口可辨認，既有新聞及指標計數沒有混算。

## 8. 改善 backend 讀取效率

- [x] 8.1 以 SQL 聚合及 window rank 改善 coverage 計數與每組樣本，在一致讀取快照使用相同 reference；固定資料對照與 PostgreSQL 整合測試確認 30／90 日、背景、未知日、公司提及、例行資料及同時 ingestion 語意正確。
- [x] 8.2 將 assessment 候選 COUNT／LIMIT 移入 SQL，重用同次查詢資料；測試台北日界、直接／非例行、未來及 preview 排除、未知日及超過八筆候選，確認總數完整且樣本有界。
- [x] 8.3 將最新觀測與每期修訂讀取改為 SQL 排名及明確分頁，串接載入更多操作與 API 文件；測試多次修訂、失效最新版、不可比較及超過預設歷史上限，確認不退回失效前舊值、不無聲截斷。
- [x] 8.4 將 theme-updates 改為批次摘要查詢，於 request 內共用來源／版本資料；以基準快照確認摘要相同、三類 token 完全相容，未把完整 token 集合套 UI limit，取得時間變動不產生提示。
- [x] 8.5 在隔離 PostgreSQL 保存改善前後 EXPLAIN ANALYZE／SQL 次數，加入量測需要的 additive 索引並更新效能文件；確認摘要不全量載入 raw 歷史，migration 與既有 backend suite 通過。

## 9. 合併讀取與按需歷史

- [x] 9.1 在 useApi 建立依完整 path／query 的共用 in-flight registry、訂閱取消及有界 LRU；以同時掛載、卸載其中一位、快速切題材及獨立失敗重試的瀏覽器測試確認請求合併且不出現取消傳染或舊回應覆蓋。
- [x] 9.2 實作設計中的 60／30 秒 TTL、動態資源只合併請求及強制重新取得，proxy／backend 保持 no-store；測試查詢隔離、TTL 到期、更新後重試、錯誤恢復及顯示快照已讀基準，文件列出各資源新鮮度。
- [x] 9.3 將版本列表與比較改為展開後載入，分享指定比較自動展開；以 request 記錄確認初次閱讀無歷史請求、單一版本無自我比較、選版才取得差異，原版本分頁與鍵盤操作通過。
- [x] 9.4 更新前端維護文件及離線 Playwright 案例，執行 typecheck／production build／offline suite；確認 fixture 只在 tests，主要導覽與手機閱讀仍可重現，記錄改善前後請求數。

## 10. 整合與交付驗收

- [x] 10.1 在隔離還原環境連續兩輪相同文件／事件／指標更新，再重啟 API／worker／DB；確認研究、必要摘錄、判讀／文件版本、三類 token 與候選不產生假更新，保存來源失敗及恢復紀錄。
- [x] 10.2 用與 baseline 相同環境／快照／workload 重跑 10 位讀取者驗收；逐 endpoint 記錄 p95、冷暖、錯誤及樣本數，常用 API < 500ms、coverage 摘要 < 1 秒全部達標才勾選，否則保留瓶頸與未完成狀態。
- [x] 10.3 完成 17 環節／7 題材的桌機、手機、鍵盤與來源失效走查，輸出當次可保存矩陣；確認閱讀、供應／回饋、證據定位、取得限制及具體缺口均可追溯，不把離線樣本當真實取得。
- [x] 10.4 從乾淨 tracked checkout 執行 map／validator／backend、typecheck／build／offline 與隔離 live 整合檢查；保存本 change 驗收結果、備份還原及回滾紀錄，執行 OpenSpec strict validation 與 Git diff 格式檢查，前置 change 仍保持原狀。

## Workflow follow-up

- 本輪只交付規劃；另行啟動 apply 後才執行上述任務。
- 完成實作後再依使用者指示處理提交與歸檔；先歸檔 `add-evidence-based-theme-assessments`，再歸檔本 change，確認主 specs 包含兩者需求。


## 11. 預覽回饋修正（2026-10-16）

本節依使用者實際閱讀回饋調整，取代 2.1／2.3／7.5／7.6 中對一般使用者展示進階資訊及文件待核對清單的 UI 決策；已完成的資料、監測及效能工作保留。

- [x] 11.1 比對原版與預覽，修正本 change 的 proposal／design／specs，記錄內容重複與維護資料干擾閱讀的問題及修正方向。
- [x] 11.2 移除一般頁面的進階資訊、診斷、原始欄位及文件待核對清單；保留必要數值口徑、原文證據及來源受限說明，固定引用頁不展示監測歷史。
- [x] 11.3 重排環節與題材閱讀任務，合併重複里程碑，加入可鍵盤切換與 hash 分享的分頁，保留既有深連結及原研究內容。
- [x] 11.4 讓技術引用跟隨論述按需載入指定版本章節與摘錄；未知或失效引用顯示缺口，來源故障仍保留研究。
- [x] 11.5 更新操作文件及有意義的瀏覽器案例，完成 typecheck／build／offline suite；驗證分頁、深連結、請求數、錯誤恢復及必要口徑。
- [x] 11.6 更新隔離預覽，完成 17 環節／7 題材的桌機手機閱讀與鍵盤走查，保存畫面及這輪 review 結果，完成 OpenSpec strict 與 diff 格式檢查。
