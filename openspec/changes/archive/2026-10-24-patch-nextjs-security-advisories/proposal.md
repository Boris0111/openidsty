# Proposal

## Why

`npm audit` 回報前端鎖定的 `next@16.4.0` 有 3 個安全漏洞，都影響 16.0.0 到 16.4.0：

- **critical [GHSA-2464-fhr4-w9xw](https://github.com/advisories/GHSA-2464-fhr4-w9xw)**：圖片最佳化 API 處理 SVG 時，可能讓未登入的人在伺服器上執行程式碼。
- **critical [GHSA-673q-mjm6-r5xr](https://github.com/advisories/GHSA-673q-mjm6-r5xr)**：`use cache` 函式回傳 typed array 時，可能讓未登入的人在伺服器上執行程式碼。
- **high [GHSA-p3m5-59mp-jv5r](https://github.com/advisories/GHSA-p3m5-59mp-jv5r)**：App Router 的 Server Actions 可能被用來癱瘓服務。

修補版是 16.4.3，也是目前的 latest。

這個專案實際暴露的風險偏低（inference）：
- 程式沒有用 `use cache`、`use server` 或 `next/image`。
- 私人網站只綁 127.0.0.1。
- 公開網站是純靜態檔，沒有 Next.js 伺服器。

但第一個漏洞的端點是 Next.js 伺服器預設就有的，不需要程式主動使用。patch 升級的成本低，所以現在就處理，不留著已知的 critical 漏洞。

## What Changes

- 前端依賴 `next` 從 `16.4.0` 升到 `16.4.3`，維持精確鎖定版本，更新 `package-lock.json`。其他依賴不變。
- 正式研究服務重建 web image，讓執行中的網站跑修補後的版本。
- 不改任何應用程式碼、設定或 API。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

（無。這次只升級依賴的 patch 版本，沒有 spec 層級的行為改變，`.openspec.yaml` 設定 `skip_specs: true`。）

## Impact

- **檔案**：`frontend/package.json`、`frontend/package-lock.json`。
- **正式服務**：web 容器以新 image 重建，期間有短暫的閱讀中斷。api、排程與資料庫不受影響。
- **公開網站**：`industryflow.pages.dev` 是靜態輸出，不執行有漏洞的伺服器程式碼，這次不重新部署。下次發布研究、重建公開版時，就會自然用到新版。
- **與 PR #7 的關係**：PR #7（公開快照）也改了 `frontend/package.json`，但改的是 `scripts`，和 `dependencies` 不在同一處，預期可以自動合併。建議 PR #7 先 merge，這個 change 再 rebase，這樣也能一起驗證公開版建置。
- **不在範圍內**：
  - CI 加上 `npm audit` 門檻：任何新公告都會擋住無關的 PR，另案評估。
  - 升級其他套件。
  - 把圖片最佳化 API 關掉的額外加固。
