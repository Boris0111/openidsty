# Design

## Context

動機見 proposal.md。以下是決定做法的現況：

- **前端全部是 client-side 取資料**：閱讀頁幾乎都是 `'use client'` 元件，在瀏覽器裡經兩個快取層向 API 取 JSON。
  - `lib/request-cache.ts` 負責舊 `/api/*`：環節、題材、產業圖。
  - `lib/research-cache.ts` 負責 `/api/v2/*`：研究、目錄、圖、搜尋、比較。
  - 頁面本身沒有伺服器端資料依賴。所以只要讓這兩層的 `fetch` 改讀靜態檔，就能用 Next.js 的 `output: 'export'` 產出靜態網站。
- **有三類請求的參數組合無法逐一預先產生**：
  - **搜尋**（`/api/v2/search?q=`）：任意字詞。
  - **目錄**（`/api/v2/{companies|products|roles|…}`）：市場 × 角色或環節 × 應用的篩選，加上游標分頁。公司目錄約 8 × 74 × 13 種組合。
  - **公司比較**（`/api/v2/compare?company_ids=`）：95 家公司任選 2 到 4 家。
- **正式版本 `a5df290c` 的規模**（2026-10-20 發布）：
  - 研究實體 254 筆、alias 713 筆、圖解 14 張（33 kB）。
  - 資料量小，所以「每個實體一個檔案」完全可行。
- **舊端點的 payload 夾帶非公開資料**：
  - `/api/segments/{id}`、`/api/themes/{id}` 帶有 `events`。
  - `/api/themes/{id}/assessment` 帶有事件候選（`candidates`、`undated_candidates` 及計數）與來源執行狀態（`evidence_sources[].runtime`、執行期的 `source_warnings`）。
- **舊端點沒有版本概念**：環節、題材、產業圖的舊端點讀的是匯入的地圖表，不是研究版本。快照取的是「匯出當下」私人服務的回應。
- **有 4 個 route handler 無法靜態匯出**：`app/api/[...path]`、`app/api/admin/*` 是動態的 route handler，`output: 'export'` 不支援。
- **公司代號頁有 Windows 檔名問題**：`/companies/[ticker]` 會遇到 `PRIVATE:shinko` 這類含冒號的代號，Windows 不能用它當檔名。
- **研究內文的內部連結只有 `/next?…`**：全部 626 處，沒有 `/companies/<代號>` 形式。

## Goals / Non-Goals

**Goals:**

- 公開版的研究內容和私人服務對同一版本的回應**逐位元組相同**（只差剝除的欄位），不在前端重寫任何查詢語意。
- 一份前端原始碼同時支援兩種建置：
  - 既有的 standalone 建置不受影響。
  - 公開版只靠建置期開關切換。
- 建置驗證要能抓出三種問題：快照缺檔、`/api` 請求、排除資料外洩。抓到就讓建置失敗。

**Non-Goals:**

- 不提供公開版的增量更新或自動部署，每次都是整份重新匯出。
- 不支援多個研究版本並存。公開版只有一個快照版本。
- 不改私人服務的 API、資料表或快取行為。

## Decisions

### 1. 匯出在 API 容器內，以 TestClient 呼叫既有端點

新增後端模組 `app/public_snapshot.py`，由 `research_lab.py public-snapshot` 執行。執行方式是：

- 以 `docker compose run --rm --no-deps` 起一個 API 容器。
- 把主機的輸出目錄掛進容器。
- 在容器內用 FastAPI `TestClient(app)` 逐一呼叫讀者端點，直接寫下回應 JSON。

- **為什麼**：
  - 走真正的路由、驗證與序列化，內容和正式服務相同。
  - 不需要對外開 port。
  - 也不用在主機上裝後端依賴。
- **替代方案**：
  - 在主機用 HTTP 爬 `127.0.0.1:8010`：可行，但搜尋索引需要 alias 表，沒有任何讀者端點提供它，最後還是要碰資料庫。
  - 經 `reader` gateway 爬：會多一層 Next.js proxy，速度慢，也沒有比較安全。
- **三種組合型資料直接呼叫後端函式**：
  - **目錄篩選名單**：呼叫 `research_v2.page()`，每次只帶一個篩選條件，取得每個條件值選中哪些實體。
  - **公司比較欄**：把 `research_compare` 抽出 `company_columns(session, release, ids)`，`compare()` 改成呼叫它，回應不變。
  - **搜尋 alias 表**：以研究唯讀角色查 `research.entity_aliases`。
- **匯出全程唯讀**：
  - 使用研究讀者角色。
  - 不呼叫任何 POST。
  - 不經 `/api/admin`。

### 2. 快照目錄以「路由表」對應，不用雜湊

輸出版面固定為 `snapshot/<release_id>/` 底下的可讀路徑：

```text
snapshot/<release_id>/
  manifest.json                       # 版本、發布時間、匯出時間、各類筆數
  v2/manifest.json
  v2/<collection>/<entity_id>.json    # 研究詳情（8 種 collection）
  v2/graphs/<entity_id>.json          # depth=1 關係圖
  v2/chains.json  v2/chains/<segment-id>.json
  v2/documents/<document_id>/<revision_id>.json
  v2/resolve.json                     # 代號／legacy key → 公司摘要
  v2/directory/<collection>.json      # 排序後摘要 + 單一條件的成員名單
  v2/search.json                      # 摘要、角色、alias（原文與正規化）
  v2/compare/<company_id>.json        # 單家公司比較欄
  legacy/industries.json  legacy/industries/<layer>/graph.json
  legacy/segments.json  legacy/segments/<layer>.json  legacy/segments/<id>.json
  legacy/themes.json  legacy/themes/<id>.json  legacy/themes/<id>/assessment.json
  assets/<sha256>.<ext>
```

前端的轉接層 `lib/snapshot-routes.ts` 與匯出端各維護一份同樣的路由表：把正規化後的請求 key 轉成檔案路徑，或交給本地計算。

- **為什麼不用 key 的雜湊**：
  - 瀏覽器 `URLSearchParams` 與 Python 的百分比編碼規則不完全相同，一個字元不同就對不到檔案。
  - 可讀路徑也方便人工檢查與 diff。
  - 路由表以外的請求一律回「公開版未收錄」。
- **路徑加上 `release_id`**：
  - 檔案不會因新快照而改變，可以設成 immutable 長期快取。
  - 新版部署是原子切換：新 HTML 只會指向新路徑。

### 3. 組合型查詢：資料由後端算，前端只做交集、排序與切頁

- **目錄**：
  - 匯出端以 `page()` 取得無篩選的完整排序清單，當作基準順序。
  - 對每個市場、角色或環節、應用，各取一次「只帶這一個條件」的成員名單。
  - 後端 SQL 中三個條件是各自獨立的 `EXISTS`，所以多條件的結果等於各單一條件結果的交集。前端取交集、照基準順序排列、依 `limit` 切頁，游標用最後一筆 ID。
  - 遞迴 taxonomy、`company_offerings` 的語意都留在後端，前端不重寫。
  - 排序也不交給 JavaScript 字串比較，因為 PostgreSQL collation 和它可能不同。
- **比較**：每家公司的比較欄獨立計算（offerings 的 `row_number` 依公司分區），所以 N 家的比較就是 N 個單家欄位依請求順序排列。輸入檢查照搬：2 到 4 家、不得重複。
- **搜尋**：唯一需要在前端重現的語意，規則都來自 `research_search.search_query`：
  - 字詞先正規化：NFKC、「臺」轉「台」、轉小寫（對應 Python 的 casefold）、空白壓縮。
  - 字詞含中日韓文字：
    - 2 個字以內做前綴比對，rank 1。
    - 超過 2 個字做子字串比對，rank 2。
  - 其餘字詞做英數字詞邊界比對，rank 2。
  - 完全相同為 rank 0。
  - 結果依（rank, 基準順序）排列，`matched_aliases` 為命中的 alias 去重後排序。
  - 這部分以 parity 腳本對照正式 API 驗證（見決策 8）。

### 4. 剝除規則集中在匯出端，並在建置時再檢查一次

匯出端以明確的欄位清單處理非公開資料：

- **刪除的欄位**：
  - 環節、題材的 `events`。
  - 判讀的 `candidates`、`undated_candidates`、`candidate_count`、`unknown_date_count`。
  - `evidence_sources[].runtime`。
  - 執行期的 `source_warnings`。只保留 `unverified`，因為它屬於研究內容的說明。
- **改寫的欄位**：圖解 URL 從 `/api/v2/assets/<sha>?release_id=…` 改成 `/snapshot/<release>/assets/<sha>.<ext>`。
- **刪除而不是改成空值的原因**：設成空陣列或 0，前端會顯示「沒有事件」或「0 筆」，等於把「未公開」說成「沒有資料」。所以欄位直接刪除，前端在公開版不渲染那些區塊。
- **建置端的二次檢查**（任一命中就讓建置失敗）：
  - 輸出中出現上述欄位名。
  - 出現 `/api/` 開頭的字串。
  - 出現祕密環境變數的值。

### 5. 前端以建置期常數切換，排除路由在暫存副本中刪除

- **公開版開關**：
  - `NEXT_PUBLIC_SNAPSHOT_RELEASE` 有值時是公開版。這個值是建置期內嵌的常數。
  - `lib/public-snapshot.ts` 匯出 `PUBLIC_SNAPSHOT` 與版本資訊。
  - 兩個快取層的 `fetch` 改經 `readerFetch()`：公開版走路由表並回傳合成的 `Response`，否則照舊打網路。
- **公開版的 UI 調整**：
  - 導覽只留地圖、供應鏈、公司、題材、公司比較。
  - 隱藏事件、指標、判讀歷史、收藏與覆蓋連結。
  - 頁尾顯示版本日期與免責聲明。
  - 「有新版研究」的提示改寫成「此公開版只收錄某日發布的版本」，並沿用既有的「載入此版本」按鈕。
- **排除路由**：
  - Next.js 的 route segment config 必須是字面值，不能依環境變數排除路由。所以 `scripts/build-static.mjs` 會先把 `app/`、`components/`、`lib/` 與設定檔複製到 `frontend/.static-build/`，再刪掉這些路由後建置：
    - `api`、`admin`、`coverage`、`sources`、`events`
    - `watchlist`、`technical-documents`、`compare`
    - `companies/[ticker]`
  - 複製到 `frontend/` 底下，`node_modules` 會沿上層目錄解析，不需要 symlink。
  - 替代方案是暫時把原 repo 的路由目錄移走。不採用：中途失敗會留下被改動的工作目錄。
- **動態路由**：
  - `themes/[id]` 拆成 server page（提供 `generateStaticParams`，公開版從快照讀題材清單，standalone 回傳空陣列）加上原本的 client 元件。
  - 公司代號改用新的 `app/companies/page.tsx?ticker=`，兩種建置都提供。公開版的 `companyUrl()` 產生 query 形式，避開含冒號的檔名；standalone 仍用 `/companies/<ticker>`。

### 6. 主機無關的輸出，建議 Cloudflare Pages

- **輸出內容**：
  - 純靜態目錄：HTML、`_next/static`、`snapshot/`、`404.html`。
  - 附一份 `_headers`，Cloudflare Pages 與 Netlify 共用同一格式：
    - **全站**：nosniff、`frame-ancestors 'none'`、限制來源為 self 的 CSP（Next 的 inline script 需要 `'unsafe-inline'`）、Referrer-Policy。
    - **`/_next/static/*` 與 `/snapshot/*`**：immutable 長期快取。
    - **`/snapshot/*/assets/*`**：再加上 `default-src 'none'; sandbox`，比照現有圖解端點，避免 SVG 在本站來源執行。
  - HTML 不設長期快取。
- **建議 Cloudflare Pages**：
  - 免費方案不限頻寬。
  - 直接上傳不佔建置次數。
  - 有 `*.pages.dev` 網域。
  - 公開版約數百到一千個檔案，在單次部署的檔案上限內。
- **Netlify 也可以**：新的免費方案以點數計費，部署與流量都扣點，超額會暫停網站。
- **repo 是 private**：GitHub Pages 免費方案不能用。

### 7. CI 用手寫的小型 fixture 快照

- **為什麼要手寫**：CI 沒有 PostgreSQL，不能跑匯出端。
- **做法**：
  - `frontend/tests/static/fixture-snapshot.ts` 以 TypeScript 型別寫一份小而完整的研究世界：兩層產業各一個環節、一個題材、兩家公司、產品、角色、應用與供應鏈。
  - 由 `scripts/write-fixture-snapshot.mjs` 依路由表寫成快照目錄。
  - `build:static` 用它建置，Playwright 再對輸出目錄逐頁瀏覽。
- **驗證範圍的分工**：
  - **CI 驗證**：公開版的行為，包括未收錄提示、隱藏的功能、無 `/api` 請求、版面。
  - **live drill 驗證**：資料是否與正式服務一致。
- **替代方案**：
  - 把真實快照 commit 成 fixture：約上千個檔案，每次研究更新都會產生大量 diff。
  - CI 加 PostgreSQL：屬於另一項待辦（P2），不在這個 change 內。

### 8. 驗證分三層

1. **後端離線單元測試**：剝除規則、圖解 URL 改寫、路由表的路徑對應、外洩檢查。這些都是純函式，不需要資料庫。
2. **前端**：
   - 轉接層的 node 單元測試：路由對應、目錄交集與分頁、比較組裝、搜尋排序與輸入檢查。
   - 靜態 E2E：以 fixture 快照建置，用本機靜態伺服器提供 clean URL，逐頁瀏覽。
3. **live drill**（在主 checkout 對正式資料執行）：
   - 匯出正式版本並建置。
   - 爬完所有實體頁，確認沒有缺檔，也沒有 `/api` 請求。
   - parity 腳本逐一比對三項，和正式 API 的結果相同：
     - **搜尋**：所有 alias、所有 alias 的 1 到 2 字前綴、英文 token。
     - **目錄**：所有單一條件與抽樣的組合條件。
     - **比較**：抽樣組合。
   - 對輸出做外洩掃描。
   - 停掉私人服務後，再讀一次公開版。

## Risks / Trade-offs

- **[搜尋語意在兩處實作會漂移]**
  - 緩解：
    - parity 腳本列入 live drill 與 `docs/public-snapshot.md` 的部署前步驟。
    - 搜尋規則在兩處都附上互相指向的註解。
  - 字詞邊界的 `[:alnum:]` 在 PostgreSQL 依 ctype 判定，JavaScript 用 `\p{L}\p{N}` 近似。如果 parity 出現差異，以實際結果修正前端，並把差異記錄下來。
- **[舊端點不是版本化的]**：環節、題材取的是匯出當下的地圖表，若維護者改了地圖卻還沒發布研究，兩者可能不同步。
  - 緩解：
    - 匯出前檢查目前發布版本就是要匯出的版本。
    - 文件要求「發布研究後才匯出」。
    - manifest 記錄匯出時間。
- **[公開後無法收回]**：已部署的內容可能被快取或索引。
  - 緩解：
    - 第一次部署前由維護者確認。
    - 外洩掃描是建置失敗條件。
    - 引用的文件摘錄沿用研究已記錄的出處（摘錄屬於合理引用的範圍，needs verification）。
- **[暫存副本建置與原始碼不一致]**：副本是每次建置前完整重新複製，`.static-build/` 列入 `.gitignore`，CI 每次都從乾淨狀態建置。
- **[CSP 需要 `'unsafe-inline'`]**：Next 靜態輸出依賴 inline script。
  - 緩解：公開版沒有使用者輸入、也沒有後端，XSS 的注入面限於研究內容。研究 Markdown 已經以 `skipHtml` 渲染。
- **[公開版沒有事件，價值較低]**：這是刻意的範圍取捨，事件留給 `publish-events-feed`。

## Migration Plan

1. 合併前：
   - 在主 checkout 的 PR branch 上執行 live drill，產出第一份正式快照。
   - 經維護者確認後，部署到維護者的 Cloudflare Pages 專案。
2. 之後每次發布研究，照 `docs/public-snapshot.md` 執行：匯出 → 建置驗證 → parity → 部署。輸出目錄以版本 ID 命名保存。
3. **回復**：重新上傳前一份保存的輸出目錄，或使用主機的「回復到先前部署」功能。私人服務不受影響。
4. 這個 change 不動資料庫與 API，所以私人服務沒有遷移或回復步驟。

## Open Questions

- **公開版用哪個主機帳號與專案名稱**：Cloudflare Pages 或 Netlify，由維護者在部署那一步決定。輸出與流程兩邊相同，不影響實作。
- **是否允許搜尋引擎索引**：預設允許。若要先觀察一段時間，只需在 `_headers` 加上 `X-Robots-Tag: noindex`。
