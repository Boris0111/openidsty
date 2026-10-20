# 隔離真實資料環境的整合與安全驗收（task 9.1）

執行日：2026-10-19。目標是還原演練環境 `industryflow-research-drill`（web `127.0.0.1:3016`、API `127.0.0.1:8016`），細節見 [備份與還原](research-backup.md)。

- **資料**：由排程備份 `20261018T215359Z` 還原，內容就是預覽的真實資料（release `4969dd12…`，含財務、事件與歷史）。
- **owner**：還原後在演練 DB 內換成演練專用的測試密碼（`research_drill.py owner`），Boris 的密碼與預覽都不受影響。
- **隔離**：沒有啟動排程。發布作業由 `research_drill.py run-job` 在一次性容器內單次執行。

```powershell
cd scripts
python research_drill.py down; python research_drill.py restore --backup ..\backups\research\<時間>; python research_drill.py owner
..\..\openspec_pjt\.venv\Scripts\python.exe research_integration.py      # 報告：.work/research-drill/integration-<時間>.json
```

## 結果（報告 `integration-20261018T222158Z.json`）

| 項目 | 結果 |
|---|---|
| owner 流程 | 建草稿 → 匯出 → 修改雙鴻摘要 → 匯入 → 驗證 → 預覽（200）→ 差異（200）→ 發布（202）→ 單次執行 job（28.4 秒，published）→ 還原前一版（16.8 秒，published，內容 hash 與原版相同） |
| 衝突與冪等 | 用舊修訂匯入回 409；同一 Idempotency-Key 重送回同一個 job；同 key 但內容不同回 409 |
| 發布期間閱讀 | 4 個讀者經 web 代理與 API 交替讀雙鴻頁，共 1,543 筆：舊版 1,447、新版 104、錯誤 0、混版 0 |
| 還原期間閱讀 | 708 筆：0 錯誤、0 混版；切換後回到原版內容 |
| 未發布 release | 刻意讓一個發布作業停在啟用前，留下 `ready` 狀態的候選版本。用它的 release_id 讀目錄與公司頁，API 與 web 都回 404；隨機 release_id 也回 404。head 前後都是 `4969dd12…:4`，沒有切換 |
| 匿名 | 草稿清單、匯出、建立、還原、coverage 一律 401；讀者端 POST／DELETE 回 405 |
| CSRF 與來源 | 缺 token、錯 token、跨站 Origin、沒有 Origin、偽造 Host 一律 403 |
| 惡意資產 | SVG 含 script、事件屬性、外部 href、DTD／entity，路徑穿越，放在 assets 以外，格式與內容不符：全部 422；超過 10 MiB：413。資產數前後都是 14 |
| 惡意草稿 | 路徑跳出、夾帶程式檔、修改 Schema 說明、`javascript:` 連結：409；超過 5 MiB：413。草稿修訂號不變 |
| SSRF | 把網址當來源 ID、未登記的來源：404；人工來源要求自動更新：422。沒有任意網址參數 |
| 來源失效 | 在只連得到 DB、沒有外網的網路上更新 `twse-revenue`：作業轉為 `deferred`（可重試，並記錄稍後重試時間），共試 3 次請求。財務觀測與原始事實筆數不變；讀者看到的台達電財務數值不變（不含回應時間）；研究 release 不變；保留最後成功時間 |
| 登出 | 登出後同一 cookie 讀草稿回 401 |
| 隔離 | 原服務與預覽的容器指紋在整輪前後相同 |

SSRF 的連線層防護另由後端單元測試覆蓋，兩項都在後端離線 pytest 通過：

- `test_source_updates.py::test_private_hosts_redirects_and_retry_after_not_shortened`：私有、link-local、metadata 主機，以及每次重新導向的重新驗證。
- `test_sec_http.py` 的兩個重新導向案例。

## 讀者流程（真實瀏覽器）

在演練站（`E2E_BASE_URL=http://127.0.0.1:3016`）執行 12 個 live spec，共 36 項：

- **讀者閱讀**：research-service、navigation、content、dynamic、financial、watchlist、cache。
- **管理介面**：owner、coverage、editor、source-updates、financial-imports。

36 項全部通過。

## 驗收過程發現並修正的問題

1. **owner 覆蓋頁經代理回 404**：task 6.5 新增的 `/api/admin/coverage` 與 `/api/admin/coverage/entities` 沒有列入 Next 管理代理的 allowlist。真實 owner 打開覆蓋頁會被代理擋下，當時的 live 測試攔截了這個路徑，所以沒發現。已補進 allowlist；`research-owner.spec.ts` 也加上匿名經真實代理讀取這些資源必須回 401（而不是 404）的斷言（`0cd7844`）。
2. **四個 live 測試寫死了第 8 段之前的內容**：包括雙鴻的第一則引用、液冷應用的公司數，以及「尚未設定 owner」的畫面。已改成依目前發布內容斷言；owner 測試改為依 `owner_configured` 分支（`0cd7844`）。
3. **讀者文字夾帶工具細節**：第 8 段的條件、內文與缺口出現「全文抽取時欄位錯位」、「-table 模式」與「SEC companyfacts」。已改成讀者看得懂的說法，例如「已依合計逐項核對」（`0cd7844`）。
4. **整合腳本自身的錯誤**：例如迴圈變數蓋掉 release ID、子程序輸出編碼。這些都已修正，最後一輪報告是乾淨重跑的結果。

## 對預覽的影響

為了部署第 1 項修正，以 `research_lab.py up` 重建 image，並重啟預覽的 web 與 API。預覽的資料與 release（`4969dd12…`）沒有改變，原服務指紋也相同。第 3 項的文字修正先在演練站驗證，之後在 9.4 首輪（2026-10-20）由 Boris 以 owner 身分發布到預覽，成為 release `a7c1bb50…`。
