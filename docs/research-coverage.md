# 研究覆蓋與缺口分工（task 6.5）

維護者在 `/admin` →「研究覆蓋」排定研究與核對工作。待核對候選、缺口分類與計數只在管理端呈現；讀者頁只在主張旁保留影響判斷的限制（例如「目前來源只能支持產品能力，尚不能確認具名客戶採用」）。

## 兩個 owner 端點

兩者都需 owner session，回應 `Cache-Control: no-store`，私人讀者入口不轉送 `/api/admin`。

| 端點 | 內容 |
|---|---|
| `GET /api/admin/coverage` | 17 環節＋7 題材的維護矩陣。直接事件 30／90 日、背景 90 日、未知發布日、公司提及 90 日、例行分開計數，沿用既有 SQL 聚合定義。每列另有技術文件核對：已核對版本、查核日、讀取範圍、定位章節、引用該版本的論述（claim → version／locator）、核對狀態計數，以及最多 5 筆待核對候選。題材另有 `assessment_candidates`：查核基準、基準後的直接事件數、未知發布日數、最多 5 筆樣本，狀態為 `awaiting-assessment`（待納入判讀）。 |
| `GET /api/admin/coverage/entities` | 正式 release 的研究物件（公司、應用、角色、產品、術語、研究頁）缺口矩陣。參數 `kind`、`status`（四類或 `unclassified`）、`cursor`、`limit`（預設 50，上限 100）。回傳各類合計 `totals` 與分頁 `items`，每筆含研究深度、查核日、主張數、四類計數、未分類數與逐筆缺口理由。 |

計數都在 PostgreSQL 執行：事件統計是 `GROUP BY` 聚合，缺口分類用 `jsonb_array_elements` 加 `FILTER` 計數；樣本與候選以 `row_number`／`LIMIT` 截斷。測試證實新增 30 則事件後，同一請求的 SQL 次數不變。

## 缺口四類

Schema 規範見 [industry-map/README.md](../industry-map/README.md) 的 gaps 欄位。`gaps` 每筆可以是 `{status, reason}` 或文字：

- `not-researched` 未研究、`not-public` 未公開、`not-obtained` 未取得、`not-applicable` 不適用。
- 文字缺口列為「未分類」。93 家 basic 公司的模板句「尚未完成公司產品、客戶、競爭與風險的獨立深研」仍是文字；`research-depth: basic` 的公司另自動計一筆未研究，所以這 93 家同時有「未研究 1」與「未分類 1」。task 8.x 深研時逐家改寫成結構化缺口。
- 不屬於四類的研究限制（例如「額定能力不等於場址驗收」）維持文字，不代表待辦。
- 讀者 API（`/api/v2/{collection}/{id}` 與公司比較）只輸出 reason 文字，契約仍是 `string[]`；status 與計數不進一般閱讀。

本輪把 6 筆非模板缺口改為結構化：兩個角色頁 → 不適用；AI 機櫃散熱應用、雙鴻、Vertiv、冷板 → 未研究。CDU 額定能力與液冷迴路場址條件屬研究限制，維持文字。這些是 authoring 檔案的變更，要經研究發布流程才會進入預覽環境的正式 release；目前 application release 仍是原版。

## 讀者端分工

- 舊題材頁 `#candidates` 轉到「數據與追蹤」，以一句話說明待核對資訊已移至維護端，下方照常閱讀公開事件與指標。
- 舊 v1 關注頁不再顯示「候選資訊有變化」與待納入摘要。
- 搜尋歧義候選、公司比較候選、影響遍歷的結構候選都是讀者功能，不受影響。

## 驗證

```powershell
python tests/run_validator_tests.py                         # gap 格式正反例
python scripts/research_lab.py pg-check --suite admin-read   # owner 邊界、分開計數、有界 SQL、技術候選、缺口分頁
cd frontend
npx playwright test --config playwright.offline.config.ts   # 舊題材頁與關注頁不再顯示候選
# 隔離 preview up 後：
$env:RESEARCH_E2E='1'; $env:E2E_BASE_URL='http://127.0.0.1:3014'
npx playwright test research-coverage.spec.ts
```

`research-coverage.spec.ts` 使用合成 admin API，驗證畫面分工與手機排版；真實資料的計數由 PostgreSQL 測試在 rolled-back 交易內匯入實際地圖驗證，不寫入 application DB。
