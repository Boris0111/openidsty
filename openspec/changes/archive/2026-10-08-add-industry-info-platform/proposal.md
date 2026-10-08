# Proposal

## Why

既有產業地圖已具備可遍歷結構，但使用者無法在瀏覽器由環節深入公司，也沒有可持續更新的官方事件與財報資料。本次先把可追溯資訊與圖形導覽接起來，作為之後 Claude 摘要的資料基礎。

## What Changes

- 建立公開唯讀網站：產業 Graph View、環節詳細資訊、公司比較、固定模板公司頁與企業 Node-link diagram。
- 以 Next.js、Cytoscape.js、FastAPI、PostgreSQL 實作；保留 Markdown 地圖為產業結構唯一來源，不修改既有環節 Schema。
- 優先介接台美官方公告、法說與基本財報資訊；保留原始來源、發布／取得時間、財報期間與資料缺口。
- 公司關係分開記錄方向、供應／策略合作類型、業務關聯分級及查證狀態；已確認關係預設顯示，候選可切換查看。
- 使用 Prefect 每小時更新資料，提供失敗、重試與最後成功更新狀態；重跑不得重複入庫。
- 新增 Docker Compose、開發啟動設定、備份與公開部署操作文件。現有其他專案佔用 3000／8000，本專案預設使用 3010／8010。
- 更新專案指引以說明新增的應用層。股價、行情估值、帳號、Redis 業務快取、Neo4j 與 Claude 摘要均不在本次實作範圍。

## Capabilities

### New Capabilities

- `industry-explorer`: 產業環節圖、環節資訊、公司比較與事件影響路徑的公開導覽。
- `company-research`: 以 ticker 識別的公司頁、企業關係圖、基本財報及相關事件。
- `official-information-ingestion`: 官方資料介接、正規化、去重、公司對應、財報口徑與來源健康狀態。
- `platform-runtime`: 容器啟動、資料初始化、Prefect 排程、持久化、開發設定及操作文件。

### Modified Capabilities

無。主 specs 尚未歸檔；本次沿用已完成 `add-industry-map` 的行為契約，不重複宣告地圖能力。

## Impact

- 新增前端、後端、資料庫遷移、公司關係維護檔、容器與整合測試。
- 新增公開唯讀 API，圖形資料以 nodes／edges 傳遞；公司以 ticker 作為跨層識別鍵。
- PostgreSQL 保存應用資料，Prefect 使用獨立資料庫；管理介面與資料庫不對外公開。
- 來源失效屬可見的資料狀態，不以假資料補滿。資訊來源仍維持免費公開；來源擷取無需 Claude API key。
