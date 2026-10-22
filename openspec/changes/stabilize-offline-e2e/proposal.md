# Proposal

## Why

CI 的前端離線 E2E 會偶發失敗。`playwright.offline.config.ts` 沒有設 retries，一次偶發就讓整個 run 變紅。2026-10-17 至 10-23 間 CI 共失敗 6 次，全都出在這一步。10-23 那次是 PR #4：它只改文件，同一個 commit 的 push run 也通過了，失敗的是 `research-navigation.spec.ts:39`。同一份程式碼重跑就會通過，維護者只能憑經驗判斷「這次是偶發」，失敗訊號因此失去可信度。

查得到原因的部分：
- `research-cache.spec.ts:38` 在 10-21 與 10-22 各失敗一次。
- 根因一半在產品：Cytoscape 會把 canvas container 寫成固定像素寬度（`cytoscape.cjs.js:31497`），而外層 `.rs-canvas` 沒有裁切。視窗縮窄時，在 `ResizeObserver` 呼叫 `cy.resize()` 之前，頁面會被撐寬一個 frame。
- 另一半在測試：縮窄後立刻量 `scrollWidth`，而且只量一次。
- 真實使用者在手機轉向或縮放視窗時，也可能看到一閃而過的水平捲動。

## What Changes

- **產品**：關係圖外框 `.rs-canvas` 裁切內容（`overflow:hidden`），讓舊尺寸的 canvas 不再撐寬頁面。只影響溢出，關係圖的縮放、平移與互動不變。
- **測試**：
  - 離線 E2E 的 12 處單次 `scrollWidth` 斷言，改用共用的會重試斷言，等版面穩定後才判定。
  - `research-cache.spec.ts:56` 先等請求數穩定，再記錄「隱藏時」的基準數，不把隱藏前已發出的請求算進去。
- **規則**：寫明離線 E2E 的斷言慣例：畫面或網路的非同步結果要用 `expect(locator)` 或 `expect.poll` 等待，不用單次的 `expect(await …)`。
- **測試：導覽後先等新內容**：`research-navigation.spec.ts`「七類目錄」測試按「下一頁」後，要等新一頁的內容渲染完成才點選項目，讓帶 cursor 的請求確實發出並完成，第 39 行的請求檢查才有意義。
- **刻意不做**：不在 CI 加 retries。retries 會把真正的回歸也藏起來。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `industry-explorer`：新增 requirement：手機寬度與視窗縮放過程中，閱讀頁不得產生水平溢出。測試早已在檢查這件事，但 spec 從未寫明。
- `platform-runtime`：新增 requirement：自動檢查的結果不得因畫面或網路時序而偶發失敗，非同步結果必須等待到穩定才判定。

## Impact

- **前端**：`frontend/app/next/research.css`（`.rs-canvas`）。若 `components/Network.tsx` 的舊版圖也有同樣情況，一併處理。
- **測試**：`frontend/tests/offline/` 下 11 個 spec 檔，新增一個共用的溢出斷言 helper。
- **文件**：`docs/frontend.md`（測試慣例）。
- **與其他 change 的關係**：與 `harden-research-operations`（PR #3）互不依賴；任一個先合併都可以。
- **不動的部分**：API、資料、排程、live E2E（`frontend/tests/*.spec.ts`），以及 CI 的 workflow。
