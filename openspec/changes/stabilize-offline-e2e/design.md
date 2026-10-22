# Design

## Context

動機見 proposal.md 的 Why，行為要求見 `specs/industry-explorer/spec.md` 與 `specs/platform-runtime/spec.md`。

### 已確認的機制（2026-10-23 診斷）

- **Cytoscape 寫死 container 寬度**：Cytoscape 3.34.3 在 `matchCanvasSize` 把 `canvasContainer.style.width` 設成固定的像素值（`node_modules/cytoscape/dist/cytoscape.cjs.js:31497`）。這層 container 自己是 `overflow:hidden`，但它的外框沒有裁切：
  - `.rs-canvas{width:100%;height:275px}`（`frontend/app/next/research.css`），由 `ResearchNetwork.tsx` 使用
  - `.network{height:480px;width:100%}`（`frontend/app/globals.css`），由 `Network.tsx` 使用
- **ResizeObserver 晚一個 frame**：兩個元件都靠 `ResizeObserver` 呼叫 `cy.resize()`（`ResearchNetwork.tsx:48`、`Network.tsx:46`），而 `ResizeObserver` 要到下一個 rendering frame 才會觸發。
- **測試量測得太早**：`setViewportSize` 一回傳，`page.evaluate` 立刻讀 `scrollWidth`，強制同步 layout。這時 canvas container 還是舊寬度，頁面就被撐寬了。
- **失敗截圖**（run 39831168184）是在斷言之後才拍的，版面正常。這與「只溢出一個 frame」的推論一致。

### 現況盤點

- 離線 spec 裡有 12 處 `expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true)`，分布在 11 個檔案。其中只有 `research-cache.spec.ts:38` 與 `research-navigation.spec.ts:50` 是在測試中途改變視窗大小、而且頁面上有關係圖。
- 已用 `expect.poll` 的只有 3 個檔案。
- **`research-cache.spec.ts:56`**（10-21 失敗一次）：60 秒快轉觸發的 manifest 與 30 秒財務輪詢請求，可能在記下 `hidden` 之後才抵達 route handler。
  - 信心：inference。這是從程式碼推得的，沒有 trace 可以證實。
- **另外兩次歷史失敗已經修好或不再適用**：
  - `relations.spec.ts:45`：已由 `61512ef` 修好。
  - `research-navigation.spec.ts:49`：改寫後已經是會自動重試的斷言。

## Goals / Non-Goals

**Goals：**
- 消除已知的兩個偶發來源。
- 讓「等待非同步結果」成為一致的寫法，未來新增的測試也照這個寫法。

**Non-Goals：**
- 不改 Cytoscape 的版本或設定，也不改關係圖的 layout 與縮放行為。
- 不處理 live E2E（`frontend/tests/*.spec.ts`）。它們不在 CI 跑，寫法另案檢視。
- 不加 CI 的 Playwright retries，也不改 workflow。

## Decisions

### D1：在外框裁切，不去追 resize 的時機
- 對 `.rs-canvas` 與 `.network` 加上 `overflow:hidden`。舊寬度的 canvas container 被外框裁掉，頁面寬度就與 resize 的時機無關。
- **不選：在 `window.resize` 時同步呼叫 `cy.resize()`。** 頁面寬度還是取決於事件順序；而且容器變寬不一定伴隨 window resize（例如側欄收合），仍然需要 `ResizeObserver`。
- **不選：用 CSS 強制覆寫 Cytoscape 內部元素的寬度。** 這依賴第三方的內部結構，升版後容易失效。
- **風險**：外框內若有刻意超出邊界的元素會被裁掉。目前縮放按鈕與 footer 都是外框的兄弟元素，不在裡面；apply 時要逐一確認兩個圖的手機與桌機畫面。

### D2：溢出檢查集中到一個會重試的 helper
- 新增 `frontend/tests/offline/layout.ts`，提供 `expectNoHorizontalOverflow(page)`。內部用 `expect.poll(() => page.evaluate(...)).toBe(true)`，沿用 Playwright 預設的 expect timeout。12 處檢查都改成呼叫它。
- 有了 D1，縮窄當下本來就不會溢出，所以 poll 通常第一次就成功。poll 只是避免把「量測時機」當成判定條件。
- 真正的回歸（持續溢出）在 timeout 後仍會失敗，符合 spec 的「真正的溢出回歸」情境。
- **不選：只修那 2 處。** 剩下 10 處目前沒有中途 resize，但寫法相同，日後加入 resize 就會重現同樣的問題；集中成一個 helper 也比較容易維持慣例。

### D3：請求數基準等到穩定才記錄
- `research-cache.spec.ts:56` 在設定 `hidden` 之前，先等 60 秒快轉觸發的請求都抵達：以 `expect.poll` 等 manifest 與財務的請求數達到預期值，之後才記錄基準。
- **不選：用 `waitForLoadState('networkidle')`。** 這個測試裝了 fake clock，networkidle 的判定與 fake clock 的互動不直觀，結果不夠確定。

### D5：導覽後先等新內容，再進行下一步

- **失敗案例**：`research-navigation.spec.ts:39` 在 PR #4 的 pull_request run 失敗（run 39860457607，2026-10-22 22:04 UTC）；同一個 commit 的 push run 通過。
- **推論的時序**（inference，沒有 trace 證實）：
  1. 第 33 行按「下一頁」後，只等到 URL 出現 `cursor=synthetic-next`。
  2. 第 34 行立刻點 `.rs-directory li a`，這時畫面可能還是第一頁的那一筆。
  3. 頁面導走，帶 cursor 的 companies 請求被取消，或根本沒有發出。
  4. 之後「回原目錄」若命中快取，也不會補發這個請求。
  5. 第 39 行一次性檢查請求清單時，就找不到它。
- **不能只改用 `expect.poll`**：如果那個請求根本沒有發出，等多久都不會出現。
- **做法**：按下一頁後，用 `expect(locator)` 等待只有下一頁才有的內容（fixture 中下一頁的那一筆）出現，再點選；第 39 行的檢查改用 `expect.poll`。
- **驗證**：apply 時以 `--repeat-each 30` 重跑；若仍失敗，用 trace 修正。

### D4：慣例寫進文件，不靠 lint
- `docs/frontend.md` 的離線測試段落寫明：非同步結果要用 `expect(locator)` 或 `expect.poll`，溢出檢查要用 helper。
- 目前沒有 ESLint，這次不為了一條規則引入 lint 工具。

## Risks / Trade-offs

- **[風險] 在本機可能重現不出 flake**：CI 機器較慢，時序差異比較容易出現。
  - → apply 時先在修改前以 `--repeat-each` 重跑原本的寫法。重現不出來時，在 tasks 記錄「未能本機重現」，改以 D1 的機制分析與修改後的重跑結果作為依據，不宣稱已證實。
- **[風險] `overflow:hidden` 裁掉關係圖的某些互動元素。**
  - → 逐一確認兩個圖的手機與桌機畫面：縮放按鈕、選取外框、拖曳平移。
- **[取捨] poll 讓失敗的測試要等到 timeout 才回報，失敗時比較慢。**
  - → 只影響失敗的情況；成功時通常第一次就通過。
- **[風險] D3 的根因是推論，修改後仍可能失敗。**
  - → 若之後仍失敗，CI 會保留 trace（`retain-on-failure`），屆時以 trace 修正，不改用 retries 掩蓋。

## Migration Plan

純前端 CSS 與測試修改，不涉及資料或部署。合併後下一次重建 web image 時，CSS 才會生效。

**回滾**：還原這兩條 CSS 與 helper 的提交即可。

## Open Questions

- CI 上的發生頻率要合併後觀察一段時間（例如 20 次 run）才知道是否歸零。這不影響做法。
