# 三方向研究擴充驗收紀錄

本文件對應 `expand-ai-infrastructure-research`，紀錄操作與閱讀證據；實作進度以 [tasks.md](../openspec/changes/expand-ai-infrastructure-research/tasks.md) checkbox 及 OpenSpec CLI 即時結果為準。逐項範圍見 [研究矩陣](research-expansion-matrix.md)。

## 基準與工作目錄（task 1.1）

查核日期：2026-11-24（Asia/Taipei）。

| 項目 | 實際結果 |
|---|---|
| 基準 commit | `a0791ded84fa22fad6efc6224cdd341481aad167` |
| 實作 branch | `research/expand-ai-infrastructure-research` |
| 實作 worktree | `C:\Users\User\openspec_pjt\.work\worktrees\expand-ai-infrastructure-research` |
| 主 checkout | `C:\Users\User\openspec_pjt`，仍在 `main`；原有修改保留 |
| 規劃來源 | 從主 checkout 複製同名 change；proposal／design／三份 delta specs／tasks 均已讀 |
| 本地 CLI 前置檔案 | 原樣複製主 checkout 的 `AGENTS.md`、`README.md`、`.npmrc`、`package.json`、`package-lock.json`；這些是使用者既有未提交檔案，並非本次新設計 |
| 已讀規範 | `AGENTS.md`、`industry-map/README.md` 全文；`docs/research-deployment.md`、`docs/research-backup.md` 還原演練與 `docs/research-drafts.md` 操作規則 |
| OpenSpec | worktree 以 `npm.cmd ci --cache C:/Users/User/openspec_pjt/.cache/npm --offline` 安裝鎖定依賴，70 packages、0 vulnerabilities；`npm.cmd run openspec -- --version` 為 `1.14.1` |
| Node | `v24.14.0`；本次不升級 runtime |
| root／schema | `npm.cmd run openspec -- list --json` 指向本 worktree；`status --change expand-ai-infrastructure-research --json` 回報 `spec-driven`，規劃 artifacts 齊備；不把規劃完成視為實作完成 |
| Python | 共用既有 `C:\Users\User\openspec_pjt\.venv\Scripts\python.exe`，沙箱外實測 `Python 3.12.10`；沒有新增 venv 或重裝 Python |
| 地圖基準驗證 | 從 worktree 執行既有 Python 的 `scripts/validate_map.py`（full）：通過，17 個環節、7 個題材、85 筆來源 |
| Docker CLI | 已安裝 `29.2.1`，API `1.53`，`desktop-linux` context |
| Docker engine | 沙箱外 `docker version` 與 `docker ps` 均無法連線：`//./pipe/dockerDesktopLinuxEngine` 不存在；尚未取得 server 版本或運行容器狀態 |

### 權限與主機狀態分辨

- `git worktree add` 在沙箱內因無法寫入 `.git/refs/heads/` 失敗；取得提權核准後建立成功。
- 沙箱內既有 venv 回報找不到 WindowsApps 下的 Python；提權後 Python 與地圖驗證成功，故不是主機未安裝 Python。
- 沙箱內 Docker 設定檔存取被拒絕、context 回落為 `default`；提權後可讀 `desktop-linux` 設定，但 engine pipe 仍不存在。這是目前的執行環境阻礙，不是缺 Docker CLI。
- 已有演練 `.env.research-drill`；沒有讀取或啟用正式 owner 憑證，沒有啟動／重啟 Docker Desktop，也沒有操作正式服務。

## 範圍矩陣建置（task 1.2）

2026-11-24 對照 design D3 完成 14 個核心產品、11 個廣度研究範圍、22 家優先公司及 12 個既有 role 的索引，五面向、來源定位／適用範圍／查核日、具體缺口、審閱與網站閱讀欄位均已保留。全部分類與證據狀態分開記錄；沒有將既有 deep 標記當成本次查核完成。

核對結果：D3 的 14 個 product ID 與 22 個 company ID 全數涵蓋；兩份文件的 93 個 Markdown 連結目標檔案存在，表格欄數一致。廣度範圍按 A 2 項／B 6 項／C 3 項逐列對照，沿用或新增分類仍待相應內容 task 裁決。此結果只完成交付索引，不代表產業內容或讀者驗收完成。

## 隔離演練可用性（task 1.3）

| 檢查 | 結果與證據 |
|---|---|
| `research_drill.py check` | 2026-11-24 成功，回傳演練命名空間的 `pg-data`、`research-assets`、`research-git` 三個 volume 名稱；只證明 Compose 隔離設定合法 |
| check 的限制 | `current_tag()` 在讀不到運行中的 API 時使用 placeholder tag；`compose config` 不需 engine，因此 check 成功不能證明容器或網站可用 |
| engine 可用性 | Boris 啟動 Docker Desktop 後，沙箱外查到 server `29.2.1`，演練容器可正常啟動 |
| 備份副本／manifest hash | `20261120T193010Z`，複製到 worktree 的 `.work/drill-backup/` 後核對 manifest SHA-256，從副本還原 |
| 容器／image／部署提交 | `industryflow-research-drill-{db,api,web}-1` 運行中，db／api healthy。API 與 web 重用 tag `7ebb8f92c801`，基準部署提交 `7ebb8f92c8010c92dba27269891a1d9eaf01f634` |
| 基準 release／研究 head | `a5df290c-0b6d-5011-b842-ae73cd8a1f99`，generation 4，研究 Git commit `7a0bda265c3e83e2d86c6a03476cfc5be3ad55eb` |
| 演練 owner | `research_drill.py owner` 回報 `drill owner reset` |
| 草稿建立／匯出 | 經 `http://127.0.0.1:3016` 驗證 owner，建立草稿 `5c41068e-20ce-4974-b920-b7da5822df3f`，revision 1，匯出 261 檔，草稿基準與演練 active release 相同 |
| task 1.3 判定 | 通過。還原報告 `.work/research-drill/restore-20261123T183040Z.json`，84.3 秒，資料表、release、Git refs、資產、遷移版本與 Prefect 核對通過，`/next` HTTP 200 |

此次還原依 [合併前演練](research-deployment.md#合併前演練) 與 [還原演練](research-backup.md#還原演練) 進行。清除前核對上次演練的停止狀態與來源。還原報告確認受保護服務及正式容器指紋相同。

## 樣本深度校準（tasks 2.1–2.3）

預定路徑：`application-ai-networking → product-optical-transceiver → A 的代表公司 → 已讀來源`。代表公司待證據選取，不預填採用或完整模組供應關係。

| 欄位 | 紀錄 |
|---|---|
| 內容 commit／draft UUID／revision／基準 release | 未建立 |
| 匯出 → 整合差異 → 匯入 → validate → preview | 未執行 |
| 桌機：裝置、瀏覽器、時間、閱讀結果 | 待 Boris 實際走讀 |
| 手機：裝置、瀏覽器、時間、閱讀結果 | 待 Boris 實際走讀 |
| 閱讀問題／修正位置／修正後驗證 | 尚無回饋；不等於沒有問題 |
| 深度標準確認人／時間／結論 | 尚未確認；確認前不擴大撰寫 A／B／C |

## 各批內容與閱讀驗收

| 批次／task | 同版閱讀鏈與範圍 | 內容 commit／草稿 revision | 證據與內容審閱 | 網站閱讀、修正及限制 |
|---|---|---|---|---|
| A／3.11 | 光／電互連、交換系統、光纖連接、主機端介面；應用 → 產品 → 公司 → 來源／比較／需求案例 | 未建立 | 未開始，依矩陣逐項核對 | 未預覽；待補實際結果 |
| B／4.11 | 變壓／配電 → UPS／BBU／供電分配 → 電源架 → 板端轉換 | 未建立 | 未開始，依矩陣逐項核對 | 未預覽；待補實際結果 |
| C／5.11 | 中介層／封裝整合 → 載板 → 介電材料／微孔／線路形成，區分 PCB | 未建立 | 未開始，依矩陣逐項核對 | 未預覽；待補實際結果 |

## 整合、發布與公開版本

| task／階段 | 必要證據 | 目前結果 |
|---|---|---|
| 6.1 | 穩定 ID、aliases、legacy keys、offerings、雙向邊；線性、題材、手足及回路的實際路徑 | 未執行 |
| 6.2 | 三份 delta specs 的 requirement／scenario 對照、矩陣完整度、三個需求案例 | 未執行；task 1.2 只建立範圍索引 |
| 6.3 | 同一內容 commit 的地圖、後端離線、前端與既有靜態快照 CI 檢查 | 未執行；基準 full 驗證不代替最終 CI |
| 6.4 | 演練部署報告、同一內容 commit、draft revision、成功 job、release／研究 head、新舊連結 | 未執行；image 部署不等於研究發布 |
| 6.5 桌機 | Boris 的裝置、release、三方向逐條閱讀結果、回饋、修正與確認 | 未執行 |
| 6.5 手機 | Boris 的裝置、release、三方向逐條閱讀結果、回饋、修正與確認 | 未執行 |
| 6.6 演練快照 | 演練容器、同一 release、內容 commit、輸出路徑、build／parity／逐頁及資產引用檢查、私人資料核對 | 未執行 |
| 正式部署 | merge 後部署目錄中的 commit、smoke 與部署紀錄 | 待 merge 後執行 |
| 正式研究發布 | 正式最新 release 草稿整合、發布 job／release 與閱讀核對 | 待 merge 後執行 |
| 公開發布 | 正式同版快照、公開產物、發布時間及 URL | 待 merge 後執行；未宣稱正式站或公開站已更新 |
