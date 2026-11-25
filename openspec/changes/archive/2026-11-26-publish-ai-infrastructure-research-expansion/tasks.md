# AI 基礎設施研究發布任務

## 1. 核對分支與發布基準

- [x] 1.1 將本提案帶入 `research/expand-ai-infrastructure-research` 的既有 worktree。用 OpenSpec 狀態及 Git diff 確認研究 change 已歸檔、研究差異為 84 個路徑，且保留兩個 checkout 的既有未提交修改。
- [x] 1.2 重新讀取正式部署紀錄、研究 manifest、演練 manifest 與公開站實際載入的 release。比對兩環境的基準研究樹及四筆來源 ID，以唯讀查詢確認正式資料庫狀態為 `retired`，記錄版本與後續可用的回退目標。
- [x] 1.3 修正 `docs/research-expansion-acceptance.md` 與 `docs/research-expansion-matrix.md` 中三個指向歸檔前位置的連結，逐一核對目標檔案存在。補記來源清單落差、`884b443` 及本次驗收依據。

## 2. 補驗研究發布與公開輸出

- [x] 2.1 在隔離演練環境從已驗收 release 建立草稿，移除四筆退役來源。以草稿 diff 確認異動限於四筆，完成全量驗證和預覽，確認來源為 239 筆、其餘編譯區段一致。
- [x] 2.2 使用演練 `run-job` 發布補驗草稿，確認 job 為 `published`／`complete`、研究 Git ref 同步，且 manifest 指向新 release。抽查光電互連、資料中心供電、先進封裝與 ABF 三條閱讀鏈、舊公司代號、來源引用及舊版入口。將草稿修訂、job、release、content hash 和抽查結果記入驗收文件。
- [x] 2.3 從補驗 release 匯出公開快照。執行靜態建置、API parity、逐頁瀏覽、資產與引用核對及外洩掃描。記錄 0 筆 parity 差異、檢查結果與留存產物路徑。
- [x] 2.4 確認 PR 預定內容與驗收範圍一致。執行全量地圖驗證、本提案的 OpenSpec 嚴格驗證及 Git diff 空白檢查，核對差異範圍後將結果記入驗收文件。

## Workflow follow-up

- 歸檔本提案後，從實作分支推送 PR。確認 `Offline verification` 對最終 PR 提交通過，並以 merge commit 合併至 `main`。若主線前進，先驗證整合差異及受影響檢查。
- 在 `C:\Users\User\industryflow-prod` 以 `research_lab.py deploy --commit <merge SHA>` 部署。保存部署序號、備份及 smoke 紀錄，確認正式 image、Alembic、Prefect 與讀者入口。
- 由本機 owner 從最新正式 release 建立草稿。依 [design.md](design.md) 整合研究差異和四筆退役修正，核對 content hash 並驗證、預覽後提交確切修訂。以固定 `Idempotency-Key` 處理重試。核對正式 job、manifest、研究 Git ref、三條研究閱讀鏈及舊版相容性後，記錄正式研究 release。
- 確認 Cloudflare OAuth 授權，匯出正式同版快照，完成 parity、逐頁檢查與外洩掃描並保存產物。在 Cloudflare Pages `industryflow` 的 `main` 部署，核對公開 manifest 實際載入的新 release、研究頁、搜尋、比較、安全標頭與瀏覽器請求。將 PR、merge SHA、部署序號、研究 job／release ID、Cloudflare deployment 與公開網址寫入驗收紀錄。
