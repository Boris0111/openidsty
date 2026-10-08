# Design

## Context

動機見 proposal.md。既有 Segment 有全文、Theme 只有 JSON；Event 要求 ticker／published_at，沒有內容關聯；來源設定硬編於 connectors。使用 PostgreSQL／FastAPI／Next.js／Cytoscape.js／Prefect，沿用每小時排程及 advisory lock。

## Goals / Non-Goals

Goals：以可稽核規則串接研究、事件及覆蓋，部署 migration 保留歷史資料。Non-Goals：AI 判讀、全文重發布、行情及公司財報 UI。

## Decisions

- Additive migration：Theme 增 prose／checked；Event nullable ticker／published_at，增出表／活動日期、精度、統計期間／口徑、規則版本、routine 與 provider identity。EventSegment／EventTheme 保存 direct 或 background 證據。不同於以公司角色推斷，分類以可辨識技術詞與句內語境為依據；一般公司提及僅作 mentioned。
- 單一 sources.yaml：每條穩定 id、provider、可選 ingestion 設定（adapter、URL／feed、分頁上限、範圍）；SEC 使用公司 CIK 模板展開。研究入口也登記為 manual，不以可讀性推論擷取成功。
- RSS／HTML adapters 只保存標題、有限摘錄及來源 URL；不爬付費內容。首次 bounded 分頁回補近 90 日，RSS 上限與 partial errors 寫入來源 metadata；統計以月份與 dataset ID 去重，保留官方口徑。不同提供者不合併。HTTP 確認入口與 parser，離線 fixtures 獨立且不載入 runtime。
- API 以關聯表過濾，覆蓋只計 published／direct／非 routine 的真實發布日期；背景、未知日、例行及提及另外顯示。未知時間置後，例行財報預設隱藏。事件 impact seeds 只讀 direct 環節，包含既有三種圖走法與回路終止。
- 紙白 #F7F8FA／深墨 #182C3A／藍 #2563EB／題材青 #0D9488／線灰 #CBD5E1；正文 16px、標題 28–32px。以供應序位分組的關係圖與閱讀側欄同步，側欄研究展開，代表公司置後。沿用繁中系統字型，避免外部字型依賴。桌機圖佔約 55%、閱讀約 45%，手機清單與內容優先，局部圖補充、全螢幕完整圖另開。標籤 14px 以上；序位不是 DAG，曲線保留反向回饋。
- useApi 以 request key＋AbortController 防舊資料；URL 記錄 layer／segment，返回自動同步；ResizeObserver 只 resize，不 fit。搜尋三種結果均為可鍵盤連結。
- 保留 company／compare／financial／graph API，輕量公司 UI 不請求關係圖；compare URL server redirect 到探索的說明訊息。

## Risks / Trade-offs

- [公開來源限流／格式改變] → 部分失敗隔離、保留既有研究與資料、顯示實際範圍及錯誤。
- [規則誤命中] → 中英文邊界、句內語境、財報排除、真實正反 fixtures，保存命中摘錄可人工核對；不宣稱 AI 判讀。
- [舊事件發布時間不可靠] → 依 raw 與 adapter 重新正規化、重新分類；無可靠依據保留 unknown，不以 fetched 補值。
- [圖節點多造成縮字] → 有意分組、標籤縮放補償、手機清單及局部圖，跨產業預設收合。

## Migration Plan

先備份現有 app DB，新增欄位／關聯表，重新匯入研究及註冊來源、正規化歷史事件，再嘗試 90 日回補；建置與重啟本專案服務、測試 readonly API、桌機／手機及 restart 持久化，輸出實際覆蓋矩陣。回滾應用 image 可讀原欄位；新增表留存，不移除歷史財報與關係。
