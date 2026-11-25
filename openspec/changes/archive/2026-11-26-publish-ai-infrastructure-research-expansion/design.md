# AI 基礎設施研究發布設計

## Context

研究實作分支 `research/expand-ai-infrastructure-research` 在 `0788ef2` 歸檔，已驗收的內容提交為 `7c3fd36`，演練 release 為 `d973c2d1-0a30-5221-ac20-adf00a0632bd`。查核時正式部署序號為 4，image 提交為 `7ebb8f9`，正式研究與 Cloudflare Pages 使用 `a5df290c-0b6d-5011-b842-ae73cd8a1f99`。執行前重新讀取各環境狀態。

`884b443` 於 2026-10-23 移除季度財報來源。正式研究的基準內容是 2026-10-20 的 `7a0bda2`，演練發布沿用該基準，兩份研究清單均含 `twse-financials`、`twse-balance`、`tpex-financials` 與 `tpex-balance`。唯讀編譯已確認，將這四筆從演練的 243 筆來源中移除後，其他編譯區段與已驗收內容一致。

## Goals / Non-Goals

補齊研究 release 的來源清單，保留研究版本歷史與正式基準的其他內容，並為三個發布階段保存可核對的版本證據。API、資料庫 Schema、排程與來源擷取行為沿用現行規格。範圍限於已驗收的研究擴充及四筆既有退役修正。

## Decisions

### 以正式基準合成可驗證的候選版本

以實作分支相對 `a0791de` 的 84 個研究路徑界定內容範圍，從最新正式 release 匯出草稿。逐檔核對正式基準、原始基準與目標內容。`sources.yaml` 依市場、分類及來源 ID 整合 154 筆新增資料與四筆退役移除，保留其他合法項目及既有引用。正式基準與已查核版本相同時，候選預期有 239 筆來源。沿用草稿的 Schema 說明與資產。如正式基準已變，重新核對新增或異動資料，記錄衝突裁決與新的預期數量，並以受影響的驗證重建候選證據。

整包匯入演練草稿會帶入演練基準的設定，也可能覆寫正式的獨立編輯。逐檔比對讓發布內容可從正式基準及已驗收差異重現，並能在匯入前辨認重疊改動。

### 補驗結果成為正式內容的比對基準

在既有隔離演練 release 上只移除四筆退役來源，以完整草稿驗證檢查引用與資產。發布後比較編譯結果，確認除來源清單外其餘區段一致。記錄草稿修訂、job、release 和 content hash。針對同一 release 重建並查核公開快照。正式草稿發布前以 content hash 核對已驗收候選內容。研究 release ID 由各環境實際發布作業取得。

### 依序切換程式、研究及公開站

正式部署從獨立部署目錄執行，目標為 `main` 第一父鏈上的 merge SHA。備份、smoke 與 Prefect 狀態通過後，由本機 owner 提交確切草稿修訂，保留同一發布請求的 `Idempotency-Key`。確認 job 為 `published`／`complete`、研究 Git ref 同步且 manifest 服務該 release，才產出公開站。

公開產物從正式 release 重新匯出。legacy 地圖端點依賴匯出當時的正式資料。輸出通過靜態建置、parity、逐頁檢查及外洩掃描後，由具權限的 Cloudflare OAuth session 部署。Wrangler 記錄使用正式部署中的 merge SHA。

## Risks / Trade-offs

- 正式草稿基準或修訂在發布前前進 → 從最新 release 重新整合，待衝突、content hash 及驗證結果可核對後提交。
- Prefect 正在執行或部署 smoke 失敗 → 等排程空檔，查部署紀錄定位失敗，依 runbook 判斷是否回退至前一成功部署。
- 正式研究已發布但讀取驗收失敗 → 依研究 restore 流程重新啟用上一個相容 release。
- 公開匯出期間 active release 改變 → 重新確認要公開的正式版本，完成同版匯出及檢查才部署。
- Cloudflare 驗收失敗 → 回復先前的 Cloudflare deployment 或先前保存的靜態產物，檢查公開站恢復後的 release。

## Migration Plan

1. 在既有實作 worktree 完成 [tasks.md](tasks.md) 的補驗與文件修正，依序歸檔本提案、通過 PR CI 並合併。保留主 checkout 的既有修改。
2. 依 `docs/research-deployment.md` 避開每小時第 7 分鐘的來源更新。以正式部署紀錄核對合併提交、備份、smoke、Alembic 與排程狀態。
3. 依 `docs/research-drafts.md` 與 `docs/research-publication.md` 匯入、驗證、預覽並發布。核對 job、正式研究 Git ref 與 manifest，抽查三條閱讀鏈、舊代號及歷史版本入口。
4. 依 `docs/public-snapshot.md` 以同一正式 release 建置及部署公開站，確認版本、代表頁面、安全標頭與瀏覽器請求。將各階段結果回填驗收紀錄。
