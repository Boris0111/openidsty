# Design

## Context

動機見 proposal.md。以下是做法的前提：

- **前端依賴是精確鎖定的**：`next` 寫成 `16.4.0`，沒有 `^`，CI 用 `npm ci` 安裝。
- **只有 `next` 有漏洞**：`npm audit` 只列出這一個套件，修補版是 `16.4.3`，屬於 patch 升級（`isSemVerMajor: false`）。
- **16.4.3 和現有依賴相容**：它的 peerDependencies 支援目前的 React `19.3.0` 與 `@playwright/test` `1.63.0`。
- **正式服務的 web image**：`industryflow-research-web:dev` 由 `research_lab.py up` 從當下的 checkout 建置。
- **暴露程度**：
  - **web**：只綁 127.0.0.1:3010，只在本機和私人網路可連。
  - **公開網站**：靜態輸出（`output: 'export'`），沒有 Next.js 伺服器。
  - **程式內容**：沒有用到 `use cache`、`use server`、`next/image`。

## Goals / Non-Goals

**Goals:**

- `npm audit` 對前端回報 0 個已知漏洞。
- 現有的自動檢查全部照舊通過：型別檢查、production build、離線 E2E；PR #7 merge 後還包括公開版建置與靜態頁面測試。
- 正式服務的 web 改用修補後的版本，閱讀功能不變。

**Non-Goals:**

- 不升級其他套件，也不升到下一個 minor 或 major 版本。
- 不在 CI 加上 audit 門檻。
- 不重新部署公開網站。

## Decisions

### 1. 只升到 16.4.3，維持精確鎖定

用 `npm install next@16.4.3 --save-exact` 更新 `package.json` 與 lockfile。

- **為什麼**：patch 版只含修補，行為改變的風險最低。精確鎖定也維持 CI 與 Docker 建置一致。
- **替代方案**：
  - `npm audit fix`：可能連帶更動其他間接依賴，範圍不好控制。
  - `next upgrade --agent=security`：Next.js 提示建議的指令，但它會做什麼不夠透明。手動指定版本一樣能達到目的，而且 diff 只有一行加上 lockfile。

### 2. 正式服務只重建 web

Next.js 只存在 web image 裡，API image 是 Python，不受影響。

- **做法**：沿用 `research_lab.py up`。它會重建 api 與 web，api 的內容不變，重建無害。
- **驗收**：在正式服務跑既有的讀者端 live E2E，並抽查主要頁面。

### 3. 公開網站不重新部署

三個漏洞都在 Next.js 的伺服器端：圖片最佳化 API、`use cache`、Server Actions。公開網站是純靜態檔，CDN 上沒有任何 Next.js 伺服器在執行，這三個漏洞都觸發不到。

- **為什麼不重新部署**：重新部署屬於對外發布，依專案慣例每次都要維護者同意。這次的修補對公開網站沒有安全效益，所以不做。
- **之後會自然更新**：下次發布研究、重建公開版時，就會用新版建置。

### 4. 先 merge PR #7，再 rebase 這個 change

- **為什麼**：兩者都改 `frontend/package.json`，但不在同一處，預期能自動合併。先 merge PR #7，這個 change 就能用 `build:static` 驗證公開版建置。
- **如果 PR #7 還沒 merge**：apply 時只做 standalone 的驗證，在 tasks 裡如實註明。

## Risks / Trade-offs

- **[patch 版仍可能改變行為]** → 用完整的離線 E2E（64 項）與 live E2E 驗證，任何失敗都先查原因，不靠自動重跑掩蓋。
- **[`next build` 的升級提示可能消失或改變]**：16.4.0 在 agent 環境中每隔一次會中止建置。升級後應該不再提示，這也一併當作 16.4.3 已經生效的旁證，但不視為驗收條件。
- **[web 重建時短暫中斷]** → 和以往一樣在主 checkout 執行，只停 web 幾秒；排程與資料庫不受影響。
