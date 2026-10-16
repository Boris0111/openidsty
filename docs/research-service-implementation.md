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

Application DB 尚未建立研究 head；首條產品閱讀流程的內容備妥後才做一次 bootstrap。管理發布與後續切換不在本 bootstrap CLI 假裝完成。

## V2 讀取契約

加入搜尋後共 22 項 PostgreSQL／API／圖形／搜尋契約通過，另保存 119 物件的 reader SQL EXPLAIN 計畫。功能、查詢限制與量測範圍見 [research-search](research-search.md)；未把單條 SQL 時間當成容量保證。

Typed graph 與三種 impact 加入後共 19 項 PostgreSQL／圖形契約通過；原地圖的真實供需環可終止，thermal 經共同下游 odm 找到 pcb，題材與線性理由分別保留，超限顯示 truncated。能力沒有被轉為具名供應，SQL 每層有數量限制。

新增 manifest、catalog、清單／詳情、舊識別解析及固定引用，保留舊 API。獨立 PostgreSQL 共 13 項契約通過（6 資料模型＋7 API），涵蓋分頁／篩選／pin、歧義 409、未知 404、ready／preparing 拒絕、未引用或未發布文件拒絕、legacy version key 與資料庫故障 503。技術維護歷史另由 `0009` 的 RLS 保留在管理側，固定引用只提供來源及必要摘錄。完整契約見 [research-api-v2](research-api-v2.md)。

## 隔離設定驗證

`compose.research.yaml` 為獨立設定，經 Docker Compose 解析確認所有共用 app image 的服務都使用新版 tag，port 只綁 loopback，PG volume／network 使用新版 namespace，排程預設不啟動。額外注入五種不安全設定（舊 initialize image、公網 API bind、原 PG volume、external volume、取消 worker profile）皆被操作工具拒絕。

`.env.research` 已獨立產生，DB／session 祕密不同且由 Git 忽略。啟停、設定核對與還原方法見 [research-lab](research-lab.md)；本段不代表後續 DB role、管理身分或私人網路 gateway 已完成。
