# 此裝置收藏（research-watchlist，task 7.1）

新版研究頁（`/next`）可以收藏公司、產品、題材與研究頁，集中在導覽列「此裝置收藏」查看更新。舊題材關注（v1）的遷移在 task 7.2，JSON 匯出入在 task 7.3。

## 讀者看到什麼

- 在上述四類研究頁按「加入收藏」；應用、角色、術語與環節不提供收藏。最多 100 項。
- 收藏只保存在**這個瀏覽器、這個網址**（localStorage `industryflow.research-watchlist.v2`）。不會跨瀏覽器、裝置或不同 host／port 同步，也**不含研究全文**：清單只記錄目標身分、名稱與已讀基準，閱讀內容仍需連線。
- 每項收藏分開顯示三個面向：
  - **研究**：已發布研究有更新／研究無變更
  - **數值**：公司的有效財務、題材的指標；產品與研究頁沒有這一項
  - **事件**：「N 則新事件（依發布日）」與「M 則新收錄，發布日未知，不代表剛發生」分開列出
- 「將目前顯示標為已讀」只記錄畫面上這次回應；之後伺服器才出現的內容，下次檢查仍會顯示為未讀。

## 判定規則

| 面向 | 依據 | 不會造成未讀 |
|---|---|---|
| 研究 | 該物件在已發布版本的 `semantic_hash`，加上觸及它的關係與產品能力列 | 整站發布但這個物件沒變、未發布草稿與候選版本 |
| 數值 | 公司：每個財務序列目前有效的 observation；題材：與 v1 相同的指標 token | 同值新申報（不產生新 revision）、抓取或檢查時間 |
| 事件 | 已讀到的最大事件 ID；只計官方與報導，不含傳聞 | 來源重試（事件依 identity 去重，不產生新 ID）、來源健康變化 |

**首次收藏的已讀基準**：
- 研究以畫面上固定的 release 計算；之後讀者採用新版，若這個物件有變，就會顯示研究更新。
- 數值與事件以加入當下的狀態為基準。
- 如果加入時無法取得摘要（例如 API 暫時失敗），三個面向都標「待確認」，不會自動全部標為已讀；之後在收藏頁按「以目前顯示建立已讀基準」補上。

**限制**：如果一則舊事件之後才被連結到這個物件，因為它的 ID 早於已讀標記，不會顯示為新事件。

## 儲存失敗

- 儲存內容部分損壞時，保留有效項目並提示，改用本次記憶體暫存。
- 瀏覽器拒絕寫入時仍可收藏與閱讀更新，但重新整理可能不保留。
- 已失效的目標會顯示原因，可以移除。

## 驗證

```powershell
python scripts/research_lab.py pg-check --suite research-dynamic   # test_research_updates：三面向分開、整站發布、重試／草稿、邊界
python scripts/research_lab.py pg-check --suite reader-navigation  # gateway 只放行此 POST
cd frontend
npx playwright test --config playwright.offline.config.ts research-watchlist.spec.ts
# 隔離 preview up 後：
$env:RESEARCH_E2E='1'; $env:E2E_BASE_URL='http://127.0.0.1:3014'
npx playwright test research-watchlist.spec.ts
```
