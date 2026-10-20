# 研究發布、重試與還原

研究發布不在 HTTP 請求內操作 Git。Owner 提交確切草稿修訂、基準 release、理由及 `Idempotency-Key`，API 先完整驗證，再把 job 寫進 PostgreSQL，提交交易後才嘗試送到 Prefect。回應為 `202`；Prefect 暫時不可用時，DB job 仍保留。相同識別與相同內容回原 job，不同內容回 `409`。

`research-publication/publish` deployment 與每 60 秒的 `research-publication-reconciliation/minute` 共用既有 process worker。啟用研究環境的 scheduler profile 才會運行；只啟動 web／API／DB 不會自動抓取來源或發布。CLI 不在 API 內開啟 ephemeral Prefect server。

本輪為節省資源，scheduler 保持停止；管理頁提交的作業會保留等待，不會由 API 直接執行。完整來源節奏／單次更新依 task 5.5 接續，實際 Prefect runtime 消費與背景更新由 task 9.1 驗收，現在不要為了試按發布而提前開啟來源排程。

## 發布步驟與恢復

1. Job 記錄草稿 UUID、修訂、基準及 payload hash，並取得 PostgreSQL session advisory lock。同一 job 的重複 worker 不重疊。
2. 從指定發布基準讀取內容，驗證草稿與資產，在 managed worktree commit。`refs/research/jobs/<job UUID>` 在 worktree 移除前保存 commit；worker 若中斷，重試核對這個 ref，不另做同內容 commit。
3. 保存不可改寫的 release ref 與 Git checkpoint；核對內容定址資產，再以單一 DB 交易完成完整候選投影及 ready checkpoint。
4. 啟用前重新核對 Git／投影／資產。以 transaction advisory lock 序列化正式 head 切換，重新檢查 base release、Schema 及狀態，同一交易更新 published、head、job、稽核及待同步 job。
5. Git 的 `research/published` branch 由持久同步 job 更新。同步時重新讀當前 head，持有相同鎖直到 ref 完成；舊同步 job 晚到也不會把分支倒退。讀者的真實版本仍以 DB head 為準。

Git、檔案與 DB 不構成分散式原子交易；切換前準備完成，切換交易失敗就維持舊 head，已保存候選由 refs 保留。啟用成功但回應中斷時，job 已在同一交易標記 published，重試會回原結果。內容編譯 hash 與基準相同時，不新增 release 或 head generation，不把純格式或重跑視為新的研究更新。

派送有 2 分鐘 lease，worker 在 checkpoint 更新為 5 分鐘 lease；中斷後 reconciliation 將到期作業補送。失敗階段與是否可重試只在 admin 顯示；暫時失敗最多自動嘗試 3 次，owner 可明確重試。過期基準、內容驗證失敗須人工處理，不自動覆寫。

## CLI 與 API

在 [草稿操作](research-drafts.md) 的互動 CLI 環境中，先匯出最新修訂到新的交換資料夾，再提交發布：

```powershell
python -m app.research_cli publish --draft <UUID> --directory .work/reviewed-draft --reason "補充已查核的產品採用條件" --idempotency-key <自行產生的唯一識別>
python -m app.research_cli status --job <回傳的 job UUID>
```

同一操作遇到連線中斷時保留原 key 與原內容；不要盲目換 key 重試。匯入後草稿 revision 已改變，舊匯出檔不能直接作為最新發布依據。所有操作仍需 session、Origin／CSRF，CLI 隱藏輸入密碼且登出，不把憑證存到交換檔。

| API | 契約 |
|---|---|
| `POST /api/admin/drafts/{id}/publish` | `{base_release_id, revision, reason}`，`Idempotency-Key`，回 `202` job |
| `GET /api/admin/jobs/{id}` | 狀態、checkpoint、失敗階段及是否可重試；no-store |
| `POST /api/admin/jobs/{id}/retry` | 明確重試可恢復的失敗 job，不建立新發布請求 |
| `POST /api/admin/releases/{id}/restore` | `{base_release_id, reason}`、唯一 key；只接受曾發布且相容的版本 |

基準已變時，原草稿保留；`GET /api/admin/drafts/{id}/diff?against=active` 可取得草稿與目前正式版本的可讀差異，回應同時標示原基準及比較版本。建立目前版本的新草稿，將實際要保留的修改整合進去，再驗證與發布。不透過修改匯出檔的基準或 revision 強行覆寫。

還原是一次新的 head 啟用與稽核，會先核對原 Git、Schema、投影及資產。它不刪除發布歷史，也不修改動態財務、事件或來源抓取記錄。GitHub push 是另外的備份／整合動作，網站沒有 GitHub 寫入憑證，本機發布不需要 GitHub 在線。
