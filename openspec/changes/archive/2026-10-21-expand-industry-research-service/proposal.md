# Proposal

## Why

目前網站以環節散文與題材判讀為主，公司頁只有角色與事件，缺少可連續探索的產品分類、公司業務、具體供應內容及財務比較。參考兩個產業地圖的導覽與研究服務，這次應把產品與公司研究做深，建立可持續維護的內容流程，讓 Boris 與小群讀者能完成「找到供應角色 → 理解產品與公司 → 查證關係 → 追蹤研究與財務變化」。

## What Changes

- 全鏈導覽擴展為「應用 → 供應角色／子領域 → 產品與技術 → 公司」，提供搜尋、關係閱讀、術語圖解與技術比較；保留有向回路、三種影響遍歷、分享返回及鍵盤操作。既有產業地圖與新版研究共用同一頁首、搜尋與麵包屑：地圖選環節後進入該環節的供應鏈；每條供應鏈以同一版型呈現問題、圖解或文字步驟、產品與缺口；公司研究為獨立頁面。
- 公司研究新增商業模式、產品線、客戶／供應商、競爭者、業務曝險、風險、來源與基本財務。供應能力、具名交易關係、合作與結構推論分開；傳聞只進觀察區，不自動成為正式關係。
- 保留全部既有環節、題材與公司。首批深研採散熱、電力、互連、網通、先進封裝目前列入的 26 家公司；此數字是本次交付範圍，不是永久產業邊界。其餘公司維持有來源的基本角色頁，逐步深化。
- 台美官方財務優先自動整理營收與成長、毛利率、營業利益、淨利、EPS、營業現金流、資本支出、現金與負債；逐項交代期間、幣別、來源、修訂與可取得範圍。公開摘要未提供的項目，以官方檔案人工核對補錄或明示缺口，不承諾全市場全指標自動取得。
- 收藏擴及公司、產品、題材及研究頁，維持裝置本機保存，加入 JSON 匯出／匯入及既有題材收藏遷移；讀者不註冊帳號，不建立伺服器個人收藏資料。
- 網站表單與既有 agent／檔案編輯共用草稿、diff、驗證與發布流程。已發布 Markdown／YAML 的 Git commit 是正式研究來源；PostgreSQL 保存查詢投影、事件、財務與修訂。agent 由維護者既有環境操作，不新增前台問答或付費模型 API。
- 單一維護者後台處理草稿、核對、來源健康、發布與稽核；一般讀者只看研究、數值、必要限制與引用，不展示待核對佇列、parser 錯誤或「進階資訊」抽屜。
- **BREAKING（研究編輯格式 v2）**：新增跨上市市場與未上市公司的穩定 `company_id`，上市代號改為 listing／alias；以映射及版本化投影保留舊 ticker API、連結與歷史，不直接改寫既有主鍵。
- 沿用同一 repo、功能 branch、獨立 worktree 與隔離 Docker 環境；本機及私人網路供小群閱讀。新舊服務並存驗收，完整設計經使用者查核後才另行 apply。

### 本版邊界

採免費公開來源與既有 Next.js、FastAPI、PostgreSQL、Cytoscape.js、Prefect。不加入行情、資金流／籌碼、選股器、投組績效、推播、讀者帳號／同步、前台 AI、Redis、圖資料庫或微服務。圖解與研究自行整理，參考網站不作未經核對的事實資料庫，也不複製其授權研究圖表。

## Capabilities

### New Capabilities

- `research-publishing`：單一維護者的表單與檔案草稿、差異、衝突檢查、Git 研究版本、發布／還原及管理安全邊界。
- `research-watchlist`：跨公司、產品、題材與研究頁的裝置收藏、實質更新與已讀、備份交換及舊題材清單遷移。

### Modified Capabilities

- `industry-map`：產品、應用、技術、術語、穩定公司身分及具證據的型別關係，維持單一 Schema 與離線遍歷。
- `company-research`：新版完整公司研究、財務修訂與可比較口徑，取代新版公司頁僅能輕量顯示的限制；legacy 保持相容。
- `industry-explorer`：分層地圖、搜尋、關係細節、技術學習與公司比較，以讀者任務驗收。
- `official-information-ingestion`：標準化財務觀測、來源能力、報導與傳聞區分、更新節奏及重跑一致性。
- `information-sources`：註冊來源可提供的指標／歷史範圍、官方與報導性質、引用與使用範圍。
- `data-coverage`：研究交付矩陣與後台維護資訊分離，區分已研究、未公開、未取得與不適用。
- `platform-runtime`：隔離環境、v2 讀取與獨立管理介面、版本快取、私人網路、備份與故障恢復。
- `theme-assessments`：待納入判讀的事件／文件候選與處理狀態移至管理端；讀者保留公開事件、財務及已發布研究的條件與缺口。

### Retired Capabilities

- `theme-watchlist`：由 `research-watchlist` 取代，移除全部 requirements；`.openspec.yaml` 宣告 `retire_capabilities: true`。需在前兩個 change 歸檔、主 specs 已含此 capability 後才同步。

## Impact

- 預計影響研究 Schema／validator、公司與產品編輯資料、API／投影／migrations、來源 connectors、網站導覽／公司／比較／收藏／後台，以及 Docker、備份與驗收工具；本次 propose 僅建立本 change 的規劃 artifacts。
- 新增 `/api/v2` 讀取契約與 `/api/admin` 維護契約；讀者介面不因取得外部資料而同步等待網路。財報改用 Decimal／Numeric，保留舊 Float 與歷史來源的遷移脈絡。
- 基準為保存分支 commit `026a484`。`main` 仍為 `b613d53`；兩個既有 completed change 保持未歸檔，不改寫其 artifacts、不在本輪 sync 主 specs。未來歸檔依 evidence-assessments → industry-reading → 本 change 順序處理。
- 新版預覽使用 `industryflow-research` Docker project，獨立 image、network、資料庫、volumes 與 ports。10 位讀取者的 API p95 與恢復時間是待驗證目標；現有測試不代表新版已實作或已驗收。
- 2026-10-20 Boris 閱讀驗收回饋：新舊站互動不清、只有液冷有專屬入口、財務只有近期資料。前兩項由本 change 第 10 段處理；財務中長期歷史（SEC 擴及全部美國公司、顯示期數、台灣歷史來源）另開 change，本 change 交付時列為已知缺口。
