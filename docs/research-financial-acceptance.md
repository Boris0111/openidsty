# 台灣／SEC 財務整合的驗收狀態

## 為什麼預覽頁面沒有財務

2026-10-17 查核並於 2026-10-18 階段完成時複核隔離預覽 `industryflow-research`：新版 `research.financial_observations` 為 0、source refresh jobs 為 0；來源排程及 worker 沒有開啟。研究頁在 task 6.2 階段提供公司／產品／術語及來源，尚未完成 task 6.3 的財務圖表、修訂查閱及公司比較操作畫面。

已完成的 5.1–5.6 是 Decimal 財務模型、台灣／SEC adapters、官方補錄、共用更新機制及讀者 API。實際官方樣本已在獨立 test DB 驗證，不曾把測試 fixtures 灌進預覽 application DB。因此「後端驗證通過」不能當作「頁面有完整真實財務可驗收」。既有 legacy Float 財務另保留原契約，不冒充新版精確觀測。

## 現在可驗證什麼

| 範圍 | 證據／入口 |
|---|---|
| 台灣上市／上櫃官方原始列、單位與來源 hash | `backend/tests/fixtures/official-tw-20261017/`，含台積電／雙鴻的月營收、損益與負債樣本，以及 provenance |
| SEC 真實資料、非曆年期間及 comparative EPS 重列 | `backend/tests/fixtures/official-sec-20261017/`，含 Vertiv／NVIDIA selected facts 與 provenance；不含聯絡 header |
| 程式行為與限制 | [台灣 adapter](research-financial-tw.md)、[SEC adapter](research-financial-sec.md)、[財務指標](research-financial-metrics.md)、[動態 API](research-dynamic-api.md) |
| 預覽 API 的真實目前狀態 | `http://127.0.0.1:3014/api/v2/companies/company-auras/financials`、`http://127.0.0.1:3014/api/v2/companies/company-vertiv/financials`；沒有值時回空 items 與缺口，不填零 |

重跑官方 fixtures 與真實 PostgreSQL 契約（只使用獨立 `industry_research_test`，不抓外網、不寫入預覽數值）：

```powershell
python scripts/research_lab.py pg-check --suite financial-core
python scripts/research_lab.py pg-check --suite financial-sec
python scripts/research_lab.py pg-check --suite research-dynamic
```

## 頁面財務驗收需要完成的流程

先完成 6.3 財務閱讀、原幣／期間／累計、來源及修訂、2–4 公司比較與不可比較原因；再對少量真實公司單次更新官方來源並核對 API 與頁面。不能用合成數值或舊 Float 補畫完整曲線。SEC 沿用已設定的 User-Agent 及共用限流，無須重新提供聯絡資訊。

台灣月營收可直接依原年月整理；季度摘要須有證據支持的財年日期設定，否則保留待核對缺口。官方摘要沒提供的 CFO／capex／現金、未核對合併範圍、EPS 股別及公司主要申報來源，仍不能假設已完整。單次更新與開啟常駐排程分開處理；本輪不因查核而自動啟動排程。
