# 官方資料來源與更新

執行 `docker compose run --rm ingestion python -m app.ingest` 更新全部來源；`--source twse-financials` 可只抓一個來源。來源 ID 與狀態見網站「來源狀態」或 `/api/sources`。程式不需要行情服務或 Claude key。

| 類型 | 實際介接 |
|---|---|
| TWSE | OpenAPI 重大訊息、月營收、一般業綜合損益表；失敗時嘗試官方 CSV |
| TPEx | OpenAPI `mopsfin_t187ap04_O`／`05_O`／`06_O_ci` |
| SEC | 維護檔有 CIK 的公司，各自 submissions 與 companyfacts |
| 台積電 IR | 季度索引與最近季度；未舉行活動標為預告，不標為已發布財報 |
| 台達電 IR | 具日期的法說簡報／逐字稿公開下載連結 |
| NVIDIA IR | 官方法說活動 RSS；外殼、封鎖或空 feed 如實顯示失敗 |
| 微軟 IR | 正文具發布日期的財報新聞稿，追蹤共用導覽列中的最新季度 |

來源 ID、提供者、端點、擷取設定及宣告範圍統一在 `industry-map/sources.yaml`，欄位見地圖唯一 Schema。`backend/app/registry.py` 讀取並依 CIK 展開 SEC 公司來源；manual 為研究入口，排程不擷取。verified 僅表示人工查核網頁可讀，runtime 的 status、last_attempt、last_success、error 與 fetch_meta 分開保存。

新增來源：科技新報 semiconductor／component／pcnotebook/伺服器／能源科技四個 RSS、Semiconductor Engineering RSS、TPCA 公開新聞稿、經濟部工業生產新聞稿、Census M3 最新完整月報及歷史先行報告索引、EIA Electric Power Monthly。僅有限摘錄，不發布免費範圍之外的正文。來源範圍涵蓋所有環節及題材，實際命中按內容規則判定。

首次執行 bounded 回補來源可提供的近 90 日，其後每小時由同一 Prefect deployment 更新最新頁；可手動強制回補：

```powershell
docker compose run --rm ingestion python -m app.ingest --backfill-days 90
docker compose run --rm ingestion python -m app.ingest --source technews-semiconductor --backfill-days 90
docker compose run --rm ingestion python -m app.ingest --reclassify
```

fetch_meta 記錄 requested_days、pages、cutoff_reached、oldest_observed、newest_observed、warnings 與 limit；backfill_meta 保留最近歷史回補，不被後續最新頁更新覆寫。科技新報 RSS 的 paged query 會轉向主 feed，回補使用免費分類列表 `/page/N/` 的發布標籤與公開摘錄，日常更新仍使用 RSS。重複回同頁或達頁數上限尚未觸及 90 日邊界時停止並標 partial；不能宣稱完整回補。Census 歷史索引僅記期別與原文件 URL，無發布日與數值；EIA 本輪只取得最新月報，歷史入口限制保留在報告。統計按 provider＋dataset＋period 去重，避免最新 URL 換期覆蓋前期；科技新報跨 feed 按 canonical URL 合併並保存 feeds。不同提供者不憑標題合併。

日期語意與覆蓋計數見 [industry-research](industry-research.md)。台灣出表日記 reported_at，TSMC／台達活動日記 activity_at；未知發布日維持 null，財報原始 Financial 欄位保留相容。

SEC 依 [官方存取規範](https://www.sec.gov/about/developer-resources) 要求可聯絡的 User-Agent。在 `.env` 設 `SEC_USER_AGENT=IndustryFlow 維護者實際email`；空值時標記 configuration_required，不冒用聯絡人。本程式所有 HTTP 以最多約 4 requests/s 執行，逾時 20 秒、最多兩次嘗試；不可用不影響其他來源。

損益表「季別 2」表示半年**累計**，不是第二季單季；TW 金額從千元轉為完整 TWD 元。SEC 財報以期間、原幣及 accession 分組，避免把不同申報版本的 EPS、營收拼在一起。YoY 只在同口徑期間可比較時衍生。原始資料與修正版本可由 DB 或事件 API 回查；新來源加入不能以欄名相似直接假定單位。

IR 收錄的是法說日期與官方文件連結／正文節錄，不宣稱 PDF 或影片已轉錄。TSMC datePublished 的 1970 占位值不得採用。只有活動預告或部分季度遭封鎖會明示 preview／partial。主要公司來自官方 issuer，提及公司與地圖 inference 分開。

`backend/tests/fixtures` 全是離線測試資料，runtime 不讀取該目錄。來源失敗時保留歷史資料與 last_success，last_attempt／error 另行更新；來源頁不 cache。

## 單來源排查與恢復

先讀 `/api/sources` 的實際 runtime 狀態，不能把 sources.yaml 的 verified 當成擷取成功。最後一次失敗另有 `data.last_error_kind` 與 `data.last_http_status`，既有失敗在下一次重試後取得此分類；欄位尚未存在時仍可讀 error。來源重新註冊保留診斷與歷史回補資訊，成功重試才清除該次失敗診斷。

| 狀態／診斷 | 操作與結果判斷 |
|---|---|
| configuration_required／configuration | `.env` 填專案名稱與維護者實際 email 的 SEC_USER_AGENT；未提供就保留待設定，不使用 Git email 或假聯絡人 |
| failed／http，403 | 記錄封鎖，稍後單來源重試；官方替代入口獨立宣告、獨立查核，不把原來源改成成功 |
| failed／timeout 或 network | 核對 DNS／連線與實際端點，重試仍失敗保留原數據及最後成功時間 |
| failed／parse | 回到 URL 檢查必要欄位、期間、登入或 JavaScript 外殼；HTTP 200 本身不是資料取得成功 |
| partial | 核對 error、fetch_meta warnings 與取得範圍，不能宣稱完整回補 |

在已初始化的服務上，`--no-deps` 避免單來源重試另啟動 initialize 或其他服務。每次 tools 容器會讀目前 `.env`；排程 worker 使用新設定前需重新建立該 worker，不需重置 API／DB／Prefect。

```powershell
# SEC 聯絡設定由維護者自行填入已忽略的 .env，不要提交或印出內容
docker compose up -d --no-deps --force-recreate worker
docker compose run --rm --no-deps ingestion python -m app.ingest --source sec-facts-nvda
docker compose run --rm --no-deps ingestion python -m app.ingest --source ir-tsmc
$sources = Invoke-RestMethod http://localhost:8010/api/sources
$sources.sources | Where-Object id -eq 'ir-tsmc' | Select-Object id,status,last_attempt,last_success,new_count,error,data
```

確認 last_attempt 是本次、status／error 是真實結果，成功時再核對 last_success 及實際事件／財報內容；`new_count=0` 可以是重跑，但不能單獨證明成功。若回 skipped_overlap，原更新仍持有防重疊鎖，等該輪 finished_at 有值後再重試；不要清除 Prefect 歷史或停其他專案。網站保持唯讀，不開放公開觸發擷取。

2026-10-14 P0 重試：SEC 仍缺真實聯絡設定；TSMC／NVIDIA IR 仍回 403。新 image 已重新核對三來源，JSON 診斷分別為 configuration 與 http／403；台達／微軟原成功保留。詳見 [驗收結果](theme-assessments-verification.md)。ODM 規則依 [12 筆真實核對](odm-classification-audit.md) 更新，重分類保留事件 identity／取得時間與既有財報；完整正文與已取得短摘錄不同，未取得的供應角色不能靠公司名稱補判。

指標直接來源、受限發現範圍、重試與修訂核對見 [指標來源操作](metric-source-operations.md)；實際期別見 [live 矩陣](theme-indicator-live-matrix.md)。

跨市場技術入口放在同一 registry 的 global／technical-documents；目前為 OCP 冷板與機櫃電力、OIF、UCIe、IEEE IRDS、JEDEC。實際可讀範圍與 web／本機 HTTP 差異見 [當次來源核對](technical-source-audit.md)；固定文件版本、已讀章節及 adopted／no-impact 維護見 [文件操作](technical-document-operations.md)。索引／來源存在、規範發布與商業採用是不同資訊，技術文件不計入直接新聞量。


技術文件監測使用既有 worker 的每日到期分支，先處理 OCP／OIF 指定系列；其餘公開入口採人工核對。版本與人工處置見 [文件維護流程](technical-document-operations.md)，實際已讀範圍見 [來源查核](technical-source-audit.md)，逐環節／題材缺口見 [技術研究矩陣](technical-research-matrix.md)。文件候選不併入新聞或指標計數。
