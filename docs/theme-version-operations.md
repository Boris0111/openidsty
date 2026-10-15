# 判讀版本維護

升級方式與資料保留原則沿用 [指標維護](theme-indicators.md)。先在還原 DB 執行 `alembic upgrade 0004`、`python -m app.import_map` 兩次，應只有七筆初始版本，不虛構 2026-10-07 以前的歷史。0004 為 additive；回退 image 保留表，禁止 destructive downgrade。

修改題材 frontmatter 的 assessment 時，在 `assessment.change_reason` 記載非空修改原因；查核日期只有實際重查才更新，並保持散文查核日一致。執行地圖驗證再匯入。匯入在同一 transaction 比較 semantic hash，相同內容或排版不新增；摘要、狀態、證據、條件或里程碑核對變更才追加。動態指標、新聞、來源狀態、fetched 不參與 hash。

還原較早研究時，還原其內容並填寫新的還原原因，再匯入；不得刪除中間版本。舊查核日期仍保留，recorded_at 是這次保存時間。欲退場題材，移除該 Markdown 並更新所有環節的 themes 引用及指標關聯，再跑驗證；DB 題材設為 inactive，事件／版本／觀測歷史保留，一般公開入口回 404。重新加入合法地圖時會啟用，內容相同不新增版本。

只有舊研究、沒有 assessment 的首次匯入仍可讀，版本可為空。已有判讀歷史不能以直接刪除 assessment 規避修改原因；退場請使用上述流程。

唯讀查核：`/api/themes/{id}/assessment/versions?limit=20&offset=0`（limit 1–100）；`/versions/{version_id}`；`/assessment/compare?from_version=...&to_version=...`。version_id 是全域識別、version_number 是題材內遞增序號。跨題材版本回 404；diff 依穩定 ID 表示新增／移除／修改，原始 URL 可追溯，不另生成結論。
