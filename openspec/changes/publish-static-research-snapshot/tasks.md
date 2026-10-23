# Tasks

## 1. 後端快照匯出

- [ ] 1.1 `research_compare.py` 抽出 `company_columns(session, release, ids)`，`compare()` 改成呼叫它，回應不變。驗證：既有的 `test_research_compare.py` 在臨時 PostgreSQL 上通過。另補一個測試，確認 N 家比較等於 N 次單家欄位依序排列。
- [ ] 1.2 新增 `backend/app/public_snapshot.py` 的純函式，並以離線單元測試涵蓋（`pytest backend/tests` 通過）：
  - 路由表：請求 key → 快照路徑。
  - 剝除規則：環節、題材的 `events`；判讀的事件候選與計數；`evidence_sources[].runtime`；執行期的 `source_warnings`。
  - 圖解 URL 改寫。
  - 外洩掃描：排除欄位名、`/api/` 字串、指定的祕密值。
- [ ] 1.3 實作匯出主流程：以 `TestClient(app)` 逐一呼叫讀者端點，寫出 design 決策 2 的目錄版面。
  - 用 `page()` 匯出每個單一條件的目錄成員名單。
  - 用 `company_columns` 匯出每家公司的比較欄。
  - 用研究唯讀角色匯出 alias 表。
  - 複製圖解檔。
  - 寫入 manifest，含版本、發布時間、匯出時間與各類筆數。
  - 指定的版本不是目前發布版本時拒絕匯出。
  - 驗證：在臨時 PostgreSQL 上以測試資料匯出，manifest 筆數與資料庫一致，外洩掃描通過，重跑的輸出位元組相同。
- [ ] 1.4 `scripts/research_lab.py` 新增 `public-snapshot` 指令：以 `docker compose run --rm --no-deps` 起 API 容器，掛上輸出目錄，輸出到 `public-snapshot/<release_id>/`（列入 `.gitignore`），並把 `.env.research` 的祕密值傳給外洩掃描，指令輸出不印出祕密。驗證：`tests/` 的 research_lab 測試涵蓋指令組裝與祕密遮蔽。

## 2. 前端快照轉接層

- [ ] 2.1 新增兩個模組：
  - `lib/public-snapshot.ts`：提供 `PUBLIC_SNAPSHOT` 與版本資訊，來源是建置期常數 `NEXT_PUBLIC_SNAPSHOT_RELEASE`。
  - `lib/snapshot-routes.ts`：純函式，不 import 其他模組，負責路由表對應、目錄交集與排序分頁、比較組裝與輸入檢查、搜尋的正規化與排序。

  驗證：`tests/snapshot-routes.node.mjs` 以 node 直接執行，涵蓋以下案例：
  - 路由表：每個路由的對應，以及路由表以外的 key 回「公開版未收錄」。
  - 目錄：多條件交集、最後一頁不再提供下一頁。
  - 比較：比較 1 家或 5 家被拒、公司重複被拒。
  - 搜尋：中文前綴與子字串、英文字詞邊界、完全相同排第一、空字串被拒。
  - 版本：指定其他研究版本時回「不在公開版」。
- [ ] 2.2 新增 `lib/reader-fetch.ts`，讓 `request-cache.ts`、`research-cache.ts` 改經它取資料：公開版回傳合成的 `Response`，錯誤訊息同時放在 `message` 與 `detail`；standalone 照舊打網路。驗證：既有的離線 E2E（`npm run test:e2e:offline`）與 `research-cache.node.cjs` 全數通過。
- [ ] 2.3 公開版的 UI 調整：
  - 導覽只留地圖、供應鏈、公司、題材、公司比較。
  - 環節頁隱藏事件區塊與覆蓋連結。
  - 題材頁隱藏指標、判讀歷史、事件與「待納入判讀」。
  - 公司頁隱藏「近期資訊」。
  - 隱藏收藏按鈕與「檢查更新」。
  - 頁尾顯示快照發布日期、不構成投資建議與推論說明。
  - 版本提示改寫成「此公開版只收錄某日發布的版本」。

  驗證：`npm run typecheck` 通過；standalone 的離線 E2E 不受影響。
- [ ] 2.4 調整路由：
  - `themes/[id]` 拆成 server page（提供 `generateStaticParams`）加上 client 元件。
  - 新增 `app/companies/page.tsx?ticker=`，公開版的 `companyUrl()` 改用 query 形式。

  驗證：standalone `npm run build` 通過，舊 `/companies/<ticker>` 與 `/themes/<id>` 的離線 E2E 照舊通過。

## 3. 公開版建置與驗證

- [ ] 3.1 新增 `scripts/write-fixture-snapshot.mjs` 與 `tests/static/fixture-snapshot.ts`：用 TypeScript 型別寫一份小而完整的研究世界（環節、題材、公司、產品、角色、應用、供應鏈與圖解），依路由表寫成快照目錄。驗證：產生的目錄能通過 1.2 同一套外洩規則的 node 版檢查。
- [ ] 3.2 新增 `scripts/build-static.mjs` 與 `npm run build:static -- --snapshot <dir>`，依序做以下幾件事：
  - 複製原始碼到 `.static-build/`（列入 `.gitignore`）。
  - 刪除排除的路由。
  - 以 `output: 'export'` 建置。
  - 把快照複製到 `out/snapshot/<release>/`。
  - 寫入 `_headers`：安全標頭、immutable 快取、圖解的 sandbox CSP。
  - 對輸出做外洩掃描。

  驗證：以 fixture 快照建置成功，`out/` 不含 `api`、`admin`、`events`、`coverage`、`sources` 頁面。
- [ ] 3.3 新增 `scripts/serve-static.mjs`（clean URL 與 404.html，行為比照 Cloudflare Pages）與 `playwright.static.config.ts`、`tests/static/*.spec.ts`。測試以 fixture 公開版逐頁瀏覽，確認以下幾點：
  - 每頁完整載入，沒有「公開版未收錄」。
  - 沒有任何 `/api` 請求。
  - 沒有事件、指標、收藏、覆蓋的入口。
  - 頁尾有版本日期與免責聲明。
  - 搜尋、組合篩選、比較 2 到 4 家正常。
  - 不存在的研究 ID 顯示未收錄說明與返回連結。
  - 390px 寬度不水平溢出。

  建置與爬頁任一失敗，`build:static` 就以非零結束。驗證：`npm run test:e2e:static` 通過。
- [ ] 3.4 CI 加上 `build:static`（fixture 快照）與 `test:e2e:static` 兩個步驟。驗證：PR 的 CI 通過。
- [ ] 3.5 新增 `frontend/scripts/snapshot-parity.mjs`：讀一份快照，逐一比對轉接層與正式 API（`http://127.0.0.1:8010`）的結果。
  - 搜尋：所有 alias、1 到 2 字前綴、英文 token。
  - 目錄：所有單一條件，加上抽樣的組合條件與分頁。
  - 比較：抽樣組合。

  任何不一致就列出差異並以非零結束。驗證：在 4.2 的 live drill 中執行。

## 4. 文件與正式服務演練

- [ ] 4.1 新增 `docs/public-snapshot.md`，並更新 README 與 AGENTS.md 中「只綁本機」的描述（指向公開快照）。文件內容包括：
  - 公開內容邊界。
  - 匯出 → 建置 → parity → 部署的步驟。
  - Cloudflare Pages 與 Netlify 的直接上傳方式。
  - 保存每版輸出與回復的方法。
  - 外洩掃描與第一次部署前的確認事項。

  驗證：文件中的指令在 4.2 照著執行成功。
- [ ] 4.2 live drill：在主 checkout 切到 PR branch（先徵得維護者同意），對正式研究版本執行以下步驟，並記錄到 `docs/research-acceptance.md` 新的一節：
  - `research_lab.py public-snapshot`。
  - `build:static`。
  - 對所有實體頁爬頁，確認沒有缺檔、沒有 `/api` 請求。
  - 跑 parity 腳本，結果要全部一致。
  - 外洩掃描。
  - 停止私人服務後，再讀一次公開版的地圖、公司、題材、搜尋與比較，然後恢復服務。
- [ ] 4.3 公開部署：由維護者選定主機與專案名稱，並同意第一次公開部署後，上傳 4.2 的輸出。在公開網址抽查以下幾點，結果記錄到 `docs/research-acceptance.md`：
  - 地圖、公司、題材、搜尋、比較都能讀。
  - 安全標頭與快取標頭符合 `_headers`。
  - 網路請求中沒有 `/api`。

## Workflow follow-up

- tasks 全部勾完後在 branch 上 archive，確認 `public-research-snapshot` 主 spec 已建立、`platform-runtime` 已同步，再交給維護者 merge。
- 刪除 memory `product-scope-2026-10.md` 中已寫進 openspec 的部分。
