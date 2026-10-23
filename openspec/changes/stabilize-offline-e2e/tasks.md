# Tasks

## 1. 修改前的基準

- [x] 1.1 （2026-10-23 結果：270 個測試全數通過、0 次失敗，**本機未重現**；產品修正改以 design D1 的機制分析為依據）在 frontend 執行 `npm ci` 與 `npm run build`，再以 `npx playwright test --config playwright.offline.config.ts tests/offline/research-cache.spec.ts tests/offline/research-navigation.spec.ts --repeat-each 30` 重跑修改前的寫法；在本 tasks 記錄失敗次數與失敗的行號。重現不出來時寫明「本機未重現」，之後不宣稱已在本機證實

## 2. 關係圖外框裁切

- [x] 2.1 對 `frontend/app/next/research.css` 的 `.rs-canvas` 與 `frontend/app/globals.css` 的 `.network` 加上 `overflow:hidden`，兩處各只加這一條；以 `npm run typecheck` 與 `npm run build` 驗證通過
- [x] 2.2 以 production build 逐一核對兩個關係圖。2026-10-23 結果：
  - 以暫時腳本核對兩個圖在 1440→390 下的縮放、重設、拖曳、canvas 尺寸跟上外框，並確認無水平溢出，全部通過，無頁面錯誤
  - 截圖：`research-graph-1440.png`、`research-graph-390.png`、`legacy-graph-1440.png`、`legacy-local-390.png`、`legacy-fullscreen-390.png`
  - 研究頁 390px 圖區空白：resize 時保留平移位置，節點落在可視範圍外。拿掉 CSS 修改的對照截圖（`research-graph-390-without-clip.png`）同樣空白，確認是**既有行為、與本修正無關**，另案處理
  - 原始檢查項目：
  - 研究頁的 `ResearchNetwork`，以及產業地圖的 `Network`（含全螢幕對話框中的圖）
  - 1440px 與 390px 兩種寬度
  - 縮放按鈕、選取外框、拖曳平移、重設視角都沒有被裁掉或失效
  - 截圖存在 `.work/stabilize-offline-e2e/`，並在本 tasks 列出檔名
- [x] 2.3 （2026-10-23 結果：270 個測試全數通過、0 次失敗。因 1.1 的修改前基準在本機同樣是 0 次，這只證明修正沒有弄壞既有行為，不代表本機已證實偶發失敗減少；實際效果以合併後的 CI 觀察為準）暫時保留原本的單次寫法，以與 1.1 相同的指令重跑 `--repeat-each 30`，確認 0 次失敗並記錄結果。這一步驗證的是產品修正本身，而不是測試的重試

## 3. 測試寫法改為等待穩定

- [x] 3.1 新增 `frontend/tests/offline/layout.ts`，匯出 `expectNoHorizontalOverflow(page)`，以 `expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)` 實作；`npm run typecheck` 通過
- [x] 3.2 把 13 處單次的 `scrollWidth` 斷言全部改為呼叫 helper，各自保留原容許值（`0`×6、預設 `1`×6、`2`×1），涵蓋 assessment、documents、navigation（apply 時發現的第 13 處）、reading（2 處）、relations、research-cache（38、80）、research-chains、research-content、research-financial、research-navigation、research-watchlist；改完以 `grep -rn "scrollWidth" frontend/tests/offline` 確認只剩 `layout.ts`，`npm run typecheck` 通過
- [x] 3.3 修改 `research-cache.spec.ts` 的「可見時每 60 秒查 manifest」測試：在設定 `hidden` 之前，以 `expect.poll` 等請求數穩定（apply 時由「預期數量」改為「穩定」，理由見 design D3），之後才記錄 `hidden` 基準；以 `--repeat-each 30` 重跑這個測試，0 次失敗（2026-10-23：與 3.4 合跑，270 個測試全數通過）
- [x] 3.4 （2026-10-23：以「下一頁」連結消失作為新一頁已渲染的訊號，270 個測試全數通過）依 design D5 修改 `research-navigation.spec.ts` 的「七類目錄」測試：按下一頁後，先以 `expect(locator)` 等待下一頁專屬內容出現才點選；第 39 行的請求檢查改用 `expect.poll`。以 `--repeat-each 30` 重跑這個測試，0 次失敗
- [x] 3.5 （2026-10-23：正常頁面通過；注入後在 5013ms，也就是預設 expect timeout 後失敗，暫時腳本已刪除）證明 helper 仍會擋下真正的回歸：暫時在測試頁注入一個 2000px 寬的元素，確認 `expectNoHorizontalOverflow` 在 timeout 後失敗，驗證完移除注入；在本 tasks 記錄結果
- [x] 3.6 在 `docs/frontend.md` 的離線測試段落補上慣例：非同步結果用 `expect(locator)` 或 `expect.poll`，不用單次的 `expect(await …)`；溢出檢查用 `expectNoHorizontalOverflow`；CI 刻意不設 retries 及其理由。以 grep 確認段落存在

## 4. 整合驗證

- [x] 4.1 （2026-10-23：`--repeat-each 3` 共 201 個測試全數通過；strict 驗證通過）執行完整的 `npm run test:e2e:offline` 3 次，全部通過；`openspec validate stabilize-offline-e2e --strict` 通過
- [ ] 4.2 push 後確認 CI 通過，並在本 tasks 記錄 run ID

## Workflow follow-up

- 合併後觀察 CI 一段時間（例如 20 次 run），在 `docs/` 或下一個 change 記錄離線 E2E 是否還有偶發失敗。
- 通過 review 後以 `/opsx:archive` 歸檔，確認 `industry-explorer` 與 `platform-runtime` 的主 spec 各新增一條 requirement。
