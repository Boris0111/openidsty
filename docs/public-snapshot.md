# 公開研究快照

公開版是一份**不含伺服器**的靜態網站：把一個已發布的研究版本匯出成 JSON 檔，再建置成 HTML。部署到免費 CDN 後，私人研究服務停機時公開版照常可讀。規格見 `openspec/specs/public-research-snapshot/`。

## 公開什麼、不公開什麼

| 公開 | 不公開 |
|---|---|
| 產業地圖與環節閱讀 | 事件、事件候選、傳聞觀察 |
| 供應鏈、公司、產品、供應角色、術語、研究頁 | 題材指標數值、判讀版本歷史 |
| 題材全文、目前判讀與里程碑 | 此裝置收藏與更新檢查 |
| 關係圖、搜尋、公司比較 | 資料覆蓋、來源設定與執行狀態 |
| 研究引用的文件出處與摘錄 | 草稿、後台與所有 `/api` |

匯出時會刪除以下欄位：
- 舊版環節、題材的 `events`。
- 題材判讀的事件候選與計數、版本指標、`evidence_sources[].runtime`，以及執行期的來源警示（只保留「原文件可讀性待確認」）。
- 技術文件的監測紀錄。
- 關係圖的 `list_url`。

這些欄位是**刪除**，不是改成空值，所以畫面不會把「沒公開」顯示成「沒有資料」。

每一頁的頁尾都會顯示快照的研究版本日期，並註明「不構成投資建議」。

## 每次發布研究後的步驟

在主 checkout 執行。前提是正式研究服務在運行，而且它的 API image 已包含 `app.public_snapshot`。這個 change merge 之後，要先執行一次 `python scripts/research_lab.py up`，用 `main` 重建 image。

```powershell
# 1. 匯出目前發布的版本到 public-snapshot/<release_id>/
#    在一次性的 API 容器裡執行，容器只看得到輸出目錄。
#    容器內外各做一次外洩掃描，任一發現就失敗。
python scripts/research_lab.py public-snapshot

# 2. 建置並驗證：檢查快照內的引用與圖解都存在 → Next.js 靜態輸出 → 寫入 _headers
#    → 外洩掃描 → 逐頁瀏覽每個實體頁。任一失敗都不會留下 frontend/out。
cd frontend
npm run build:static -- --snapshot ../public-snapshot/<release_id>

# 3. 和正式 API 逐一比對搜尋、目錄篩選、公司比較、resolve、研究詳情與關係圖
node scripts/snapshot-parity.mjs --snapshot ../public-snapshot/<release_id>

# 4. 保存這一版的輸出，回復時使用（public-snapshot/ 不進 Git）
Copy-Item -Recurse out ..\public-snapshot\<release_id>-site
```

- **只要研究有發布，就要重新匯出**。舊版的環節與題材端點不分版本，取的是匯出當下的地圖表。所以匯出前要確認「目前發布的版本」就是要公開的版本。若研究在匯出途中又發布新版，匯出會失敗，重跑即可。
- **在 agent 環境中，`build:static` 可能被擋**。Next.js 16.4.0 偵測到 agent 時，大約每兩次建置會有一次因安全升級提示而中止。直接重跑即可繼續。CI 與人工執行不受影響。

## 部署

輸出目錄 `frontend/out` 是純靜態檔案，附有 `_headers`：

- **全站**：安全標頭與 CSP。
- **`/_next/static/*`、`/snapshot/*`**：長期快取。
- **圖解**：加上 sandbox CSP。

Cloudflare Pages 與 Netlify 都讀得懂 `_headers`。快照放在 `/snapshot/<release_id>/` 底下，新舊版本的路徑不同，所以部署是原子切換。

**第一次公開部署前**，維護者要確認四件事：

- 主機帳號與專案名稱。
- 步驟 2、3 都通過。
- 外洩掃描沒有發現。
- 接受「公開後可能被快取或索引」。

### Cloudflare Pages（建議）

免費方案不限頻寬。正式網址是 `https://industryflow.pages.dev`，專案 `industryflow` 已在 2026-10-23 建立。

```powershell
npx wrangler@4 login                      # 第一次；或設定 CLOUDFLARE_API_TOKEN 與 CLOUDFLARE_ACCOUNT_ID
npx wrangler@4 pages deploy frontend/out --project-name industryflow --branch main --commit-hash <commit> --commit-message "public snapshot <release_id>"
```

- **新建專案時要加 `--force`**：wrangler 4.152 會把 `pages project create` 轉交給「併入 Workers 的新版 Pages」流程，結果失敗。新建專案時要加 `--force`，直接建立在 Cloudflare Pages 上。`industryflow` 已經建好，之後部署不需要也不應該加 `--force`。
- **`_headers` 一條規則只能有一個 `*`**：Cloudflare Pages 不認得 `/snapshot/*/assets/*` 這種寫法，圖解的 sandbox 規則因此改用 `/snapshot/:release/assets/*`。
- **只會上傳有變動的檔案**：同一份快照重新部署時，只上傳內容改變的檔案。
- **建議使用 wrangler**：儀表板的拖放上傳有檔案數上限（needs verification），而公開版有上千個檔案。

### Netlify

```powershell
npx netlify-cli deploy --dir frontend/out --prod
```

Netlify 免費方案以點數計費，部署與流量都會扣點，超額會暫停網站。

### 部署後抽查

在公開網址檢查以下事項：

- 地圖、公司、題材、搜尋、比較都能讀。
- 開發者工具的網路分頁沒有 `/api` 請求。
- `curl -I https://<網址>/` 有 `X-Content-Type-Options`、`Content-Security-Policy`。
- `curl -I https://<網址>/_next/static/...` 帶有 `immutable`。

## 回復

公開版有問題時，有兩種回復方式：

- 重新部署前一份保存的 `public-snapshot/<release_id>-site`，或使用主機的「回復到先前部署」。
- 只想回到前一個研究版本時，對該版本的快照重新執行步驟 2 到 4。

兩種方式都不影響私人研究服務。

## 程式位置

- **匯出**：`backend/app/public_snapshot.py`。路由表與 `frontend/lib/snapshot-routes.ts` 共用測試案例 `frontend/tests/static/route-cases.json`。
- **前端轉接**：
  - `frontend/lib/reader-fetch.ts`：公開版讀快照，app 照舊打 API。
  - `frontend/lib/public-snapshot.ts`：建置期開關 `NEXT_PUBLIC_SNAPSHOT_RELEASE`。
- **建置與驗證**：
  - `frontend/scripts/build-static.mjs`
  - `frontend/scripts/serve-static.mjs`
  - `frontend/tests/static/`
  - `frontend/scripts/snapshot-parity.mjs`
- **CI**：以 `frontend/tests/static/fixture-snapshot.ts` 的合成快照建置公開版，並跑靜態頁面測試。
