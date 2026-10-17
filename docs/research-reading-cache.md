# 研究版本與閱讀快取（task 6.4）

## 讀者操作

頁面首次從 manifest 取得已發布版本，寫入網址 `release_id`；所有研究、關係、目錄與固定引用沿用此版。進入頁面、導覽、按「檢查更新」、回到可見頁面及可見時每 60 秒檢查 manifest。發現新發布或還原只提示，不自行換入新邊線或引用。

按「載入新版研究」才一起切換頁面 context。物件、目錄篩選及原地圖返回位置保留；跨版本 cursor、選中連線、財務修訂選取及歷史分頁清除。原目錄返回連結改用新 release 並回第一頁。歷史及引用仍按需讀取，沒有轉查 `latest` 的備援。

「檢查更新」重新讀取本機 DB 的已發布研究及目前已開啟的資料，不會觸發 SEC 或台灣來源擷取，也不開背景 worker。更新失敗保留同一物件最後成功讀取的內容並提供重試；第一次讀取就失敗則顯示錯誤，不用另一物件或另一 release 補畫。若新版刪除原物件，顯示不存在，讀者可回目錄。

## 各層責任

| 資料 | HTTP 與瀏覽器記憶體策略 |
|---|---|
| manifest、未指定單一 release 的 GET | `no-store`；僅合併同時進行的相同請求，不保存成功快取 |
| 指定 published release 的研究、目錄、搜尋、圖與固定文件引用 | weak ETag、最多 24 小時；key 包含路徑、release 及排序後的完整參數／分頁 |
| 財務、事件、傳聞、含財務的公司比較 | weak ETag、最多 30 秒；比較 key 含 release，內容 validator 含數值／來源／修訂；可見頁面到期重驗 |
| 財務 observation 詳情 | 同樣最多 30 秒，因 wrapper 還包含目前有效 ID 及修訂清單，不能只因 observation ID 固定就 immutable |
| 已發布研究引用的 hash 資產 | 固定 bytes、ETag、最長一年 immutable；未指定 release 仍 no-store；錯誤不快取 |
| admin、session、owner preview、錯誤 | no-store；不進讀者共用記憶體快取，草稿的 If-Match ETag 只用於衝突檢查 |

後端每次仍執行 published release／引用／檔案檢查，再決定 200 或 304；沒有新增伺服器 payload cache、Redis 或可繞過授權的條件式短路。JSON 回應超過 8 MiB 不製作 validator，改以 no-store 串流回傳。Next proxy 本身不保存 payload，轉送 `If-None-Match`、ETag、Age、Vary、必要安全標頭及 304 空回應；私人 reader gateway 同樣保留條件標頭並移除認證／cookie。

`research-cache.ts` 只存在瀏覽器記憶體，完成項依 LRU 最多 100 筆，同時進行最多 100 個 request key。共用請求按消費者計數：其中一個離開不取消其他人，最後一個離開才取消。已取消的舊 request 即使晚回，也不能寫入完成快取或覆蓋新 generation。Response 的 release 必須符合請求；錯版、失敗及 no-store 不進成功快取。重新開頁不宣稱具完整離線研究副本。

採用新版時保留可安全重用的靜態版本快取，清除動態快取及舊動態 in-flight 工作；還原舊研究也會重新取得財務，避免把當時瀏覽過的舊財務值帶回畫面。隱藏頁面不自動輪詢，回到可見時再檢查；動態 no-store 回應亦以 30 秒間隔更新，不密集重送。

## 時點與限制

`as_of` 是成功表示內容的讀取時間，不是官方申報日。ETag 計算排除單純變動的 `data.as_of`，其餘回應內容及完整 query key 均參與；未改值的 304 沿用原 payload 及原 `as_of`，不把檢查成功時間偽裝成數值更新。來源期間、申報日、修訂與缺口照舊保留。

這個階段減少重複傳輸及瀏覽器相同讀取，沒有以 304 宣稱 SQL 已不執行，也未量測 10 人 p95。效能與故障恢復目標仍待 task 9.2／9.3。HTTP 條件語意依 [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.2)，快取新鮮度依 [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.2)。

## 驗證入口

```powershell
python scripts/research_lab.py pg-check --suite research-dynamic
python scripts/research_lab.py pg-check --suite publication-interfaces
python scripts/research_lab.py pg-check --suite reader-navigation
cd frontend
node --test tests/research-cache.node.cjs
npm run build
npx playwright test --config playwright.offline.config.ts research-cache.spec.ts research-financial.spec.ts research-content.spec.ts research-navigation.spec.ts
# 隔離 preview up 完成且 API healthy 後：
$env:RESEARCH_E2E='1'
$env:E2E_BASE_URL='http://127.0.0.1:3014'
npx playwright test research-cache.spec.ts research-dynamic.spec.ts research-financial.spec.ts research-service.spec.ts research-navigation.spec.ts research-content.spec.ts
```

合成快取／新版提示與中斷測試只 mock 瀏覽器 API，DB 測試只使用獨立 test DB。Application 的既有研究及 1793 筆真實財務沒有改寫，沒有為截圖建立假發布或新財務。工程畫面存於忽略的 `.work/research-cache-review/`，不等同 Boris 的閱讀驗收。
