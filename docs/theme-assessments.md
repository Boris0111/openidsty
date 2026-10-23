# 題材判讀維護

`industry-map/themes/*.md` 同時保存全文與 optional assessment；唯一欄位規範見 [Schema](../industry-map/README.md)。不要在另一份研究 YAML 或 DB 手動維護同一結論。當前七題材的來源期間、核對方法及缺口見 [來源核對](theme-source-audit.md)。來源存取受阻不刪除既有研究。

判讀摘要說明目前證據支持到哪裡；confidence 是 well-supported、inference 或 needs-verification。支持與反向論點都引用可解析的 evidence_ids。風險與成立條件不充當已發生反證；沒有具名反向證據就寫明缺口。公司總營收不能直接代表題材收入，公開架構、合作與原型不能代表終端認證。

編輯順序：核對具名來源及原期間，保留必要短摘錄與 HTTPS URL；寫論點、條件、缺口與下一確認點，再補有依據的傳導假設。canonical source_id 引用 sources.yaml，不使用 per-company runtime ID。每組 id 與 milestone id 保持穩定，刪除／改名之前核對所有引用。

研究 reviewed 必須與散文「查核日期」一致。只是整理舊研究、重新匯入或檢查網址可讀性，不更改原查核日；重新完成內容查核後才同步兩處日期。published 與 occurred 未知時留 null，不能以 fetched 或文件可讀性 checked 補值。里程碑日期是預期查核時間；confirmed／contradicted 必須有具體證據與適用對象，部分完成仍明列尚缺什麼。

paths 的機制、條件及引用屬人工研究，所有傳導皆為 inference。upstream／downstream、theme、sibling 必須符合已宣告結構，且步驟連續。結構可達不代表公司已取得訂單，候選清單與支持論點分開。

```powershell
# repo 根目錄，修改後先驗證，再匯入
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe scripts/validate_map.py
.\.venv\Scripts\python.exe tests/run_validator_tests.py
docker compose build api
docker compose run --rm --no-deps ingestion python -m app.import_map
```

full 驗證會核對原查核基準。只寫骨架可用 `--skip-prose`，但交付／匯入仍須 full；錯誤地圖在 DB 寫入前被拒絕。既有 import_map 的 Theme JSON 可直接攜帶新增欄位，保留全文、status、checked，無 assessment 的舊題材仍可讀。事件／營收的新數值不覆寫判讀。

版本功能建立後，實質修改要填非空 change_reason；相同內容重跑、排版、來源 HTTP 嘗試、候選資訊與動態指標不是研究版本變更。恢復歷史內容也需記錄原因，不能抹掉中間版本。首次結構化不是虛構過去版本。相關版本 API 與操作在 P3 驗收後記入 API／前端文件。

判讀版本形成、退場與還原操作見 [theme-version-operations](theme-version-operations.md)。
