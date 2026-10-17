# 新研究服務實作紀錄

## 採用規劃與查核紀錄

- 2026-10-16：Boris 在提案提交 `4592dff` 呈現後明確啟動 `$openspec-apply-change`，依 task 1.1 採用該版 proposal、design、9 份 specs 與來源限制，開始 `expand-industry-research-service`。
- 程式與驗證只在 `feat/expand-industry-research-service` 的獨立 worktree 進行；原 `main`、保存分支、既有服務及兩個 completed change 不作修改。
- 免費資料不足以保證全部公司／指標／歷史自動取得；官方補錄、明示缺口與來源核對仍屬必要行為。
- Task 3.4 的第一條真實研究流程需要桌機／手機畫面與 Boris 閱讀回饋；尚未取得回饋前不得將該項標為完成或越過其完整管理／全批深研驗收條件。

本文件隨實際驗證補充結果；未執行的功能與容量目標不記為成果。

## 還原及啟停驗證（2026-10-16）

來源為 `industryflow-reading-db / industry_reading`，還原至獨立 `industry_research`。Alembic 版本 `0006`；19 張 public 表的筆數與排序內容 MD5 全部一致，包含 companies 95、roles 100、segments 17、themes 7、events 2915、financials 147、assessment versions 7、技術文件／觀測／核對各 8。備份 SHA-256 為 `f77196bf261d29894683fb67176459769b9ef396856581fc48df9087f2a8787a`。

新版網站 3014 與 API 8014 啟動、停止、重啟後均回 200；原有 12 個容器的 ID、image、started_at、restart、mount 與 port fingerprints 未變。機器可讀紀錄保存在忽略目錄 `.work/research-lab/restore.json` 與 `isolation.json`，不含憑證。初始化改用 SQL，避免 Windows CRLF 令 shell shebang 失效；保留既有新 volume，以獨立建立 Prefect DB 修復首次初始化，沒有刪除任何 volume。共享 app image 改成只 build api 一次後以同 image 啟動 initializer，避免重複 image export。

## 研究身分與結構驗證

`research-v1` authoring 格式加入唯一 Schema 文件。95 家公司各有不可變 kind-prefixed ID；原 95 個 ticker／PRIVATE 鍵、100 筆角色、既有 aliases 與 CIK 完整對應，Boyd 沒有 listing。18 項新測試通過，涵蓋改名不改 ID、跨市場證券同主體、同名母子公司不合併、legacy／官方識別重複、listing 區間重疊、分類環、供需環、證據與資產。跨市場測試使用明確標記的合成資料，未把它寫進正式研究。

基本公司頁仍標示尚未深研，沒有添加未讀來源或升級既有判讀。全量地圖驗證通過（17 環節、7 題材、53 個現行來源）；DB 中其他來源及歷史未刪除。

`tests/run_validator_tests.py` 通過既有 66 類失敗案例、合法基準及新增 18 項 research-v1 測試；供需回路通過、分類回路拒絕。分類採有界 iterative traversal，不依賴 Python recursion depth。

## PostgreSQL 遷移及權限驗證

隔離新版已升級至 `0008`。獨立 `industry_research_test` 的 6 項 PostgreSQL 契約通過，包含跨 release FK、Numeric(38,10) 精度、A → B → A 修訂、raw fact／job 唯一鍵、ready head 拒絕、reader 的管理表拒絕與 RLS、writer 不可重寫 published 內容或建立資料表。實際 reader／writer login 均非 superuser／BYPASSRLS；reader 即使關閉預設 read-only 設定仍沒有 INSERT grant。

既有 public 表的欄位、型別、nullability、default 與所有公司／角色主鍵保持原狀。除 Alembic 版本及既有 initializer 重新匯入的 sources metadata 外，其他 17 張資料表的排序內容 hash 仍與備份相同；sources 仍有 73 筆，未刪歷史，不能把 metadata 刷新宣稱成重新研究。原服務的 fingerprints 再次核對一致。Docker 的 mount 清單先排序再比較，差異會留存安全診斷檔，避免順序差異誤報。

操作與資料模型見 [research-data-model](research-data-model.md)。本段只驗證資料模型；發布、登入、財務 adapters 及新版讀者功能仍依後續 tasks 交付。

Backend 回歸：150 passed、8 skipped（需專用 PostgreSQL 的 6 項與既有 reading PG 2 項）；新增 6 項已另在真實 PostgreSQL 執行通過。既有 Starlette/httpx deprecation warning 保留，不在此更換依賴。Git diff 格式檢查通過。

## Git 編譯與重建驗證

從 `dad167a94fafe9499702356fc8842d6f79b858ce` 的 Git archive 編譯 119 個物件（17／7／95），兩次內容 hash 均為 `412609b03e6a66b7aa62da819f19487690c7ab48c13527f3053786d3a9a8a6a1`。在獨立 PostgreSQL 的 rollback-only transaction 逐筆核對實際 Markdown、metadata、日期與 hash，保留 7 份判讀、9 個指標定義、11 筆觀測及技術文件／觀測／核對各 8 筆，沒有將測試資料寫進 application DB。5 項編譯單元測試通過，含惡意 archive 路徑與 symlink 拒絕。

初期檢查時未建立 application head；首條內容提交後已從 `8480da4af6d6cac11c6f62836a1fcc2feced4012` 完成一次 bootstrap。Release 為 `03799774-3553-5ff6-9910-13a68468af15`，125 物件的內容 hash 為 `3d39adcbc033817b0d8d9da4cd0c6934a3c19cbd48c0bbc37acdb3a958caa0c6`。同一提交在 PostgreSQL rollback-only transaction 重建比對一致，原歷史筆數仍保留。管理發布與後續切換不在本 bootstrap CLI 假裝完成。

## V2 讀取契約

加入搜尋後共 22 項 PostgreSQL／API／圖形／搜尋契約通過，另保存 119 物件的 reader SQL EXPLAIN 計畫。功能、查詢限制與量測範圍見 [research-search](research-search.md)；未把單條 SQL 時間當成容量保證。

Typed graph 與三種 impact 加入後共 19 項 PostgreSQL／圖形契約通過；原地圖的真實供需環可終止，thermal 經共同下游 odm 找到 pcb，題材與線性理由分別保留，超限顯示 truncated。能力沒有被轉為具名供應，SQL 每層有數量限制。

新增 manifest、catalog、清單／詳情、舊識別解析及固定引用，保留舊 API。獨立 PostgreSQL 共 13 項契約通過（6 資料模型＋7 API），涵蓋分頁／篩選／pin、歧義 409、未知 404、ready／preparing 拒絕、未引用或未發布文件拒絕、legacy version key 與資料庫故障 503。技術維護歷史另由 `0009` 的 RLS 保留在管理側，固定引用只提供來源及必要摘錄。完整契約見 [research-api-v2](research-api-v2.md)。

## 隔離設定驗證

`compose.research.yaml` 為獨立設定，經 Docker Compose 解析確認所有共用 app image 的服務都使用新版 tag，port 只綁 loopback，PG volume／network 使用新版 namespace，排程預設不啟動。額外注入五種不安全設定（舊 initialize image、公網 API bind、原 PG volume、external volume、取消 worker profile）皆被操作工具拒絕。

`.env.research` 已獨立產生，DB／session／reader／writer 祕密各自不同且由 Git 忽略。啟停、設定核對與還原方法見 [research-lab](research-lab.md)。DB roles 已另驗證；owner 管理與私人網路 gateway 尚待後續 tasks。

## 首條流程的技術驗證與閱讀回饋

最新 backend 回歸 158 passed、21 skipped；新版的 19 項 PostgreSQL 契約另以真實 DB 驗證，連同 3 項圖形走法共 22 項通過。其餘 2 項既有 reading PG 情境本輪未重跑，留待完整整合驗收。既有 offline browser 36 項通過。新 live browser 6 項通過，涵蓋產品—公司—來源、固定版分享／返回、鍵盤搜尋、手機與文字連線、慢回應、圖解失敗仍可讀研究。Production build 與地圖 full 驗證通過（17／7、58 現行來源），validator 的 66 類突變及 18 項新測試通過。

桌機與手機截圖在 `.work/first-flow-review/`，另以新手機 viewport 檢視公司頁，修正小圖自動排版將標籤縮得過小的問題。2026-10-16 Boris 回覆「目前頁面操作體驗尚可，可依此模式繼續其他分析產出」，task 3.4 已完成。技術驗證與 agent 截圖仍與使用者回饋分開保存，不將繼續指示擴張成全部研究內容及完整導覽驗收。回饋與走讀範圍見 [research-first-flow-review](research-first-flow-review.md)；其關於新舊地圖操作關係的提問，現況與後續方向見 [research-navigation](research-navigation.md)。完整管理、動態財務、全鏈導覽與 26 家深研仍由後續 tasks 交付，沒有切換或合併 main。

## Owner 實作與環境阻礙

Task 4.1 的 owner 設定／重設、session、CSRF、Origin、到期與持久登入限流程式已加入。Docker 中斷當時尚未通過真實 PostgreSQL 及瀏覽器驗證，因此當時 checkbox 保持未完成；恢復後結果見下段。Docker 於 2026-10-16 23:41 發生 BuildKit history nil pointer panic，VM 隨後關閉，Desktop backend 殘留使重新開啟 UI 未恢復 engine。唯讀診斷、可信程度及恢復後的檢查順序見 [runtime incident](research-runtime-incident-20261017.md)。本輪未重設或刪除任何 Docker／WSL 資料。

2026-10-17 恢復後，Boris 授權暫停不重要服務並繼續 apply；已停止原版與 Valuflow 的 7 個容器，僅保留新版研究環境。34 項真實 PostgreSQL／API 契約通過（含 12 項 owner），production build 通過，3 項管理代理與 6 項研究走讀共 9 項 live browser 通過，task 4.1 完成。沒有設定實際 owner 密碼或重新 bootstrap 研究。登入操作與安全設定見 [research-owner](research-owner.md)。

## 草稿及 managed Git（tasks 4.2–4.3）

`/admin` 提供表單／Markdown、修訂、diff、整份驗證及私有閱讀預覽；CLI 以原始研究檔案交換相同草稿，不保存登入憑證。預覽共用正式 detail／graph 與前端內容元件，在 savepoint rollback 臨時投影；正式 head 不動。Managed Git 僅在專用 volume 及臨時 worktree 寫入研究 allowlist，保留不可改寫的 release refs。資產先檢查內容／SVG，再以 hash 保存，讀者仍只能取得已發布版本引用的資產。操作範例見 [research-drafts](research-drafts.md)。

2026-10-17 實際結果：71 項隔離 PostgreSQL／Linux 容器測試全部通過，含真實研究編譯、表單／檔案同結果、修訂衝突、預覽無殘留、匿名管理拒絕、資產、symlink、managed worktree 與開發 index 不變。Windows 同樣實跑 managed worktree／index 及 CLI，原先往返測試揭露 CRLF 自動轉換，已改成保留 bytes 並以 LF／CRLF 案例驗證；Windows 不具建立 symlink 的權限，因此該項在 Linux 容器實跑，未宣稱 Windows 已跑過。唯一現有 warning 為 Starlette 的 httpx 測試介面棄用提示。

Production build、typecheck 通過，13 項 live browser 全通過：6 項既有讀者、3 項 session proxy、4 項草稿桌機／手機／入口／資產邊界。編輯情境採合成 API 回應，真實寫入／驗證／預覽另由 PostgreSQL 整合測試覆蓋；未在 application DB 設定合成密碼。桌機／手機截圖已檢視，保存在忽略的 `.work/editor-review/`，不視為 Boris 對管理 UI 的使用者驗收。

本輪已初始化 managed clone 並保護目前發布 commit；公開研究仍是原 bootstrap release。原版／Valuflow 仍停止，只運行研究版 web、API、DB。Task 4.4 的持久發布與恢復、4.5 還原及同步、4.6 完整管理流程尚未完成，不把草稿功能當成發布交付。

## 持久發布與管理流程（tasks 4.4–4.6）

後續已加入持久 outbox、Prefect 派送／每分鐘 reconciliation、job／release refs、候選投影與單交易 head 啟用；重複請求回原 job，基準衝突保留草稿，還原不修改財務或事件。`research/published` 同步作業重讀當前 head，避免晚到同步倒退。Owner 管理頁已提供發布理由、進度、失敗重試、已發布版閱讀、還原、來源健康及操作紀錄；草稿另可與目前正式版本比較。操作見 [research-publication](research-publication.md)。

驗證：88 項真實 PostgreSQL／容器測試完整通過，另以最新程式通過 1 項完整檔案介面流程（CLI 檔案交換→import→preview→publish→HTTP retry→restore，並以真正 reader login 查閱前後內容）。故障注入涵蓋 Git／asset／投影實際操作失敗、六個中斷位置、啟用交易回滾、回應遺失、基準競爭、相同內容不假更新、Prefect client 暫時失效及 lease 到期補送。另讓 child worker `os._exit(77)` 後由全新程序續跑，同一 job 僅一筆發布稽核。Prefect transport 本輪以 client 契約替身驗證；實際啟動 scheduler、流程註冊與消費作業的 runtime 整合仍由 task 9.1 驗收，不宣稱已在 application DB 實際發布。

測試期間曾誤開兩個共用測試 DB 的程序，造成最後一個 projection 案例與另一輪 owner setup 互相干擾；該輪結果未採計為完整通過。已在測試入口加入 DB session advisory lock，鎖定遷移與整輪 pytest，隨後序列重跑 88 項通過。Application DB 另核對：head 仍為 `03799774-3553-5ff6-9910-13a68468af15`、owner 0、publish jobs 0。未把測試帳密、候選版本或合成內容放進 application DB。

唯讀 gateway 使用相同 app image 的 opt-in reader profile，沒有 DB／session 憑證及持久 volumes；3 項原生安全測試、2 項真實 gateway browser 通過，研究、圖解與公司導覽可讀，管理／legacy 診斷／偽造 cookie／Host／寫入被拒絕。Gateway 測完已停止，仍只保留 web／API／DB。13 項管理及既有閱讀 browser 通過；管理寫入畫面採合成 API，真實 DB 行為由上述整合測試覆蓋。Build／typecheck 通過，未增加讀者端維護資料。跨裝置 TLS／私人網路設定尚未執行，條件見 [research-reader-entry](research-reader-entry.md)。

## 財務基礎（task 5.1）

新增 13 個明確口徑的 metric 定義（含毛利輔助值）、Decimal／Numeric(38,10)、raw fact／canonical group 雙身分、同值新申報只補 provenance、重編與晚到歷史、同日衝突核對、公式版本與 input lineage。基本／稀釋 EPS 及普通股／ADR 不互換，EPS／比率／期末值禁止相減；缺前期或相容申報時回缺口，不填零。Migration `0011` 保護 raw fact、group 與觀測值不被改寫，最新值依申報日而不是單看 revision。

`pg-check --suite financial-core` 實際 35 passed（24 計算／身分、5 writer storage、6 原有 PG 模型／權限），包含千元倍率、有效零、同值新申報、重編後回到舊值、晚到歷史不蓋新值、非曆年 Q4、同日歧義及不可改寫。未抓取外部來源或填入合成 application 財務；指標與限制見 [research-financial-metrics](research-financial-metrics.md)。台美 adapter、官方補錄與查詢／比較仍按 tasks 5.2–5.6 接續。

## 台灣官方摘要（task 5.2）

2026-10-17 實讀 TWSE／TPEx 六個 JSON 入口及 MOPS 單位／累計表頭，保存台積電與雙鴻原始列及來源 hash。新版解析保留別名、千元倍率、EPS 元、母公司與總淨利差異、期末負債、缺值與有效零。未提供申報日／合併範圍時不杜撰，季度須先有已核對財年；非曆年或未知財年保留原列與缺口。出表日期使用 migration `0012` 的 source_as_of，不混成公司申報日。詳見 [台灣摘要能力及限制](research-financial-tw.md)。

最新 `pg-check --suite financial-core` 56 passed（既有 35＋台灣 21），在獨立測試 DB 通過 migration、真實 writer 入庫、同值新出表日不假更新、晚到資料不蓋新值、原始高精度 JSON 數字保存及日期模式隔離。Full 地圖驗證通過（17 環節、7 題材、60 來源），兩筆新負債來源先 manual 註冊，避免誤交 legacy adapter；到期流程由 task 5.5 串接。未自動發布研究或把樣本寫進 application DB。

此次接續時 Docker 引擎原為停止，啟動 Desktop 後恢復三個新版容器；原版／Valuflow 仍停止，隔離測試核對 protected services 不變。沒有執行 reset、prune、volume 刪除或重新 bootstrap。

## SEC 財務接續點（task 5.3 尚未完成）

已實作 US GAAP 標準 tag mapping、原始 accession／日期／可取得 context／股別、不同期間與淨利口徑、未知／自訂 tag 缺口、同一申報衝突拒絕及 Decimal storage。所有 SEC HTTP（包含 retry、redirect 與一般 IR 跳入 SEC）共用 PostgreSQL session gate，每次間距至少 0.5 秒；不使用各 client 獨立的 SEC 限流，也不向外部 redirect 洩露聯絡 email。

2026-10-17 `pg-check --suite financial-sec` 最新 16 passed，含真實 DB 修訂／冪等及三個獨立程序限流；數字場景為明示合成，HTTP 使用 MockTransport。另既有擷取／來源診斷與財務原生回歸 102 passed、4 skipped，這四項須獨立 PostgreSQL，已分別由 financial-core／financial-sec 執行；最後新增 IR→SEC 跳轉契約另包含在最新 16 項。

**待使用者設定：** 新版 `.env.research` 尚無有效 SEC_USER_AGENT。未自行填假 email，實際 SEC companyfacts 樣本仍未取得，task 5.3 checkbox 保留未完成。設定步驟與官方限制見 [SEC adapter](research-financial-sec.md)；接手先確認設定存在（不印值），再用共用 gate 擷取官方樣本、保存 hash／selected fixtures、逐項核對並重跑測試，才能完成 5.3，再續 5.4 官方補錄。這是資料來源設定前提，並非 Docker 或測試失敗。

隔離 application 已升級 `0012`，health、manifest、`/next` 均 HTTP 200；head 仍為原 `03799774-3553-5ff6-9910-13a68468af15`，owner／publish jobs／新 financial observations 均 0，legacy events 2915、financials 147。Initializer 只加入指標定義及來源 metadata，不把測試數值寫入 application DB。

## SEC 官方樣本補驗（task 5.3 完成）

Boris 設定後已核對 SEC_USER_AGENT 存在、唯一及格式有效，未輸出內容。以隔離 initialize 的當次環境、既有 HTTP 與 PostgreSQL gate 實際取得 Vertiv／NVIDIA companyfacts，各 HTTP 200；來源 hash、UTC 時間及精確 Decimal selected fixtures 已保存，不含請求 header。補驗揭露非 US GAAP namespace 不一定為 issuer extension，已修正為 unmapped-taxonomy 缺口，避免誤標 ECD 等標準分類。

最新 `pg-check --suite financial-sec` 19 passed，包含官方年度值、NVIDIA 非曆年期間、實際 comparative EPS 重列、同值新申報只補 provenance，整批重新入庫沒有假修訂；原有合成邊界及三程序共用限流亦通過。只在可回滾的獨立 test DB 驗證，沒有向 application 寫入這批數字或啟動定時抓取。詳見 [SEC adapter](research-financial-sec.md)。

## 官方財務補錄（task 5.4）

新增 JSON／CSV 同格式驗證、1 MiB／100 列界線、原始數值／倍率／期間／原幣／範圍／定位預覽，以及 owner 明確核對後確認入庫。Payload hash 綁定輸入與當時數值基準，確認重試使用同一 key／原結果；過期預覽、同日衝突缺修訂依據、未知官方主機、缺欄與錯誤數值拒絕。確認將 raw facts、觀測修訂、批次結果及 audit 原子寫入，整批任一錯誤回滾。Migration `0013` 保護已確認批次／結果及原預覽不可改寫，詳見 [補錄操作與 API](research-financial-imports.md)。

`pg-check --suite financial-imports` 最新 **90 passed**：21 補錄解析／真實 API、24 財務 core、5 storage、21 台灣、19 SEC／限流；原先測試固定 key 被前一案例使用後遭正確拒絕，已改成每批獨立 key，未把該失敗輪視為通過。共同群組鎖採排序，人工與自動 adapters 沿用同一順序。

Admin 新增「財務補錄」、JSON／CSV 空白範本、文件連結與差異表、明確勾選／理由及重試；修改內容即清舊預覽。Production build（隔離 Compose）、typecheck、16 項 live browser 通過（新增 3 財務，既有 13）；加入空白範本下載檢查後另重跑 3 項通過。桌機 1440×1000／手機 390×844 截圖已實際檢視，存於忽略的 `.work/financial-import-review/`。畫面寫入使用明示合成 API，真實 DB 行為另由上述測試覆蓋；未將截圖當 Boris 使用者驗收。

Application 已升級 `0013`，head 不變；owner、financial observations、financial import batches 均 0。僅研究版 web／API／DB 運行，scheduler 仍關閉。下一項為 5.5 到期排程、共用重試、來源隔離及單次更新。

## 來源到期更新完成（task 5.5）

Migration `0014` 保存 source jobs、每 URL 重試預算、提供者退避及有界派送索引。每小時檢查到期來源、財務每日到期；單次更新與 CLI／Prefect 共用相同流程。429 持久保存 Retry-After，403／外殼停止當輪，資料交易失敗保留舊值。程序中斷可續原 job，不重設預算或製造財務修訂；事件 official／report／rumor 與 direct／mention／background 分開，研究 head 及正式關係不變。來源操作見 [research-source-updates](research-source-updates.md)。

台灣兩筆負債 adapter 已接入新流程；同一官方回應兼供 canonical／相容 legacy 投影。季度日期只採用同一 published release 中有證據、信心與適用期間的 `financial-reporting` 設定，未知或失效設定保留缺口，不為填圖表猜財年。Schema／validator 同步擴充，尚未替實際公司填入未核對設定。

驗證：`pg-check --suite source-updates` **17 passed**（HTTP、真實 writer、429 跨 client、實際子程序 exit 77 後續跑、派送失敗恢復、日曆適用期與傳聞隔離）；`financial-imports` **90 passed**；既有 ingestion／technical／metric 六套原生測試 **78 passed**；full 地圖驗證及 validator **66 類失敗案例＋20 research tests** 通過。早先 JSON／JSONB fixture 錯誤已修正，失敗輪未列入通過。

Typecheck、隔離 production build 通過；live browser **19 passed、2 skipped**（唯讀 gateway 未啟動，該兩項不列通過）。來源手機走查發現表格橫向操作不便，改為逐筆上下排列並補明確 table roles；狀態 cell 的輔助標籤納入可存取名稱後修正測試比對，最新來源三項 **3 passed**。桌機與手機截圖實際檢視，位於忽略的 `.work/source-update-review/`，畫面是合成 API，非 Boris 驗收。

Application 為 `0014`，已確認 history index、兩筆 balance adapter；head 仍 `03799774-3553-5ff6-9910-13a68468af15`，owner／publish jobs／financial observations／financial import batches／source jobs 均 0。僅新版 web／API／DB 運行，scheduler 仍關閉；原 project fingerprints 未變。Prefect 真實服務整合另由 task 9.1 驗證，沒有宣稱排程已開啟。下一項為 5.6 財務、事件、觀察與比較 API。
