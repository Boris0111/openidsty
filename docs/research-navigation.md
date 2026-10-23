# 讀者導覽：一個外框，從產業地圖進入供應鏈（task 10.2、10.3）

自 2026-10-20 起適用，取代 task 3.4 首條流程的專屬頁籤，以及 6.1 時新舊站分開的導覽。調整起因見 [驗收文件](research-acceptance.md) 第三節。

## 一個外框

| 項目 | 現在的行為 |
|---|---|
| 頁首 | 產業地圖 `/`、題材 `/themes`、事件 `/events` 與新版研究 `/next` 共用同一頁首，依序為：產業地圖、供應鏈、公司、題材、公司比較、事件、收藏。管理介面 `/admin` 獨立 |
| 搜尋 | 只有一個搜尋框，用 v2 搜尋 8 類物件：<br>• 題材 → 題材頁<br>• 環節 → 地圖選取<br>• 其他 → `/next?focus=…`<br>在 `/next` 搜尋時沿用目前固定的研究版本 |
| 麵包屑 | 依分類產生「產業地圖 › 環節 › 供應鏈 › 本頁」；公司頁為「公司 › 名稱」。從地圖進來時，環節連結回到原本的地圖選取，包含選中的連線 |
| 收藏 | 只有一份此裝置收藏，題材頁與研究頁共用。舊版題材清單在第一次使用時遷移一次，原本的儲存保留為備份 |
| 事件 | 「官方與報導」（`/events`）與「傳聞觀察」（`/next?view=observations`）是同一個入口下的兩個分頁；傳聞仍有獨立入口 |

## 供應鏈

| 頁面 | 內容 |
|---|---|
| 供應鏈索引（`/next`） | 12 條鏈的卡片，標出所屬環節、讀者問題，以及圖解縮圖或文字步驟 |
| 鏈頁（`/next?focus=application-…`） | 依序為：<br>• 問題式標題<br>• 圖解（7 條鏈有圖，桌機左圖右步驟）；沒有圖解的 5 條用文字步驟<br>• 依步驟排列的產品卡，標出有產品證據的公司<br>• 這條鏈的其他產品<br>• 應用研究與缺口<br>• 關係圖 |
| 產品、角色、術語頁 | 頂端放位置列，標出所在步驟並連回鏈頁；不放完整圖解。手機第一屏就是該頁內容 |
| 公司頁 | 獨立頁面，不放圖解；列出所屬供應鏈，以及在該鏈有證據的產品，下接近期資訊（官方與報導、傳聞觀察） |
| 地圖的環節面板 | 列出「這個環節的供應鏈」卡片，連結保留原地圖選取作為返回 |

**資料來源**：

- 應用的 `question` 與 `flow-steps` 欄位；Schema 見 `industry-map/README.md`。
- 讀取 API：`/api/v2/chains`，以及物件詳情中的 `chain`、`chains`、`trail`；契約見 [API 文件](research-api-v2.md)。

步驟與產品卡只描述閱讀順序與產品能力，不代表公司之間有交易。

## 舊網址

| 舊網址 | 現在 |
|---|---|
| `/companies/<代號>` | 解析後轉到新版公司研究；無法解析時說明原因並連到公司索引。舊的公司 API 保留 |
| `/compare` | 轉到 `/next?view=compare` |
| `/watchlist` | 轉到 `/next?view=watchlist` |
| `/next?focus=segment-…` | 回到地圖的環節選取 |
| `/next?focus=theme-…` | 轉到 `/themes/<題材>`，判讀、指標與版本比較都在這裡 |
| `/coverage`、`/sources` | 本機仍可開啟，但不在讀者導覽中；唯讀入口一律拒絕 |

## 唯讀入口（3015）

- **允許**：
  - 頁面：`/`、`/themes`、`/events`、`/companies/<代號>` 與 `/next`。
  - 唯讀 API：v2，以及舊版的 industries、segments、themes、events、technical-documents。
- **一律回 403**：管理頁、覆蓋、來源狀態、舊版搜尋、舊版收藏 API。
- 細節見 [唯讀入口](research-reader-entry.md)。

## 驗證

| 範圍 | 測試 |
|---|---|
| 前端離線 | `frontend/tests/offline/navigation.spec.ts`、`research-chains.spec.ts`、`research-navigation.spec.ts`、`watchlist.spec.ts` |
| live | `research-service`、`research-navigation`、`research-reader-entry`、`explorer` |
| 後端 | `backend/tests/test_reader_gateway.py`；`test_research_v2.py` 的 trail 與供應鏈契約 |
| 桌機／手機走查 | 見 [驗收文件](research-acceptance.md) |
