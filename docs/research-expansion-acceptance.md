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
| Docker engine | 起初沙箱外 `docker version` 與 `docker ps` 均無法連線：`//./pipe/dockerDesktopLinuxEngine` 不存在；Boris 啟動 Docker Desktop 後再完成 task 1.3 |

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

研究路徑：`application-ai-networking → product-optical-transceiver → company-4979-two（華星光）→ luxnet-annual-report-2025`。產品頁另以 Cisco 成品模組、Marvell DSP 元件與指定 AEC／LPO／CPO 文件說明交付差異；不推定華星光供應 Cisco 或 Marvell 型號。產品頁與華星光公司頁互相連結，`industry-map/research-relations.yaml` 的 `offering-4979-two-optical-transceiver` 連回 `product-mix` 主張。

| 欄位 | 紀錄 |
|---|---|
| 內容 commit／draft UUID／revision／基準 release | 內容 checkpoint `34a8633`。演練 draft `5c41068e-20ce-4974-b920-b7da5822df3f`，revision 3，基準 release `a5df290c-0b6d-5011-b842-ae73cd8a1f99`，generation 4，研究 head `7a0bda265c3e83e2d86c6a03476cfc5be3ad55eb`。 |
| 匯出 → 整合差異 → 匯入 → validate → preview | 首次匯入沿用未套用研究差異的 261 檔，revision 1 為基準內容，先前預覽只查到實體存在。2026-11-24 套用產品、公司與來源註冊表的三份差異後升至 revision 2。再從 revision 2 匯出並匯入公司 800G ZR 證據界線及產品條列，升至 revision 3。與基準比較恰為上述三檔，驗證通過，且依序確認 AI networking、光模組角色、光模組產品（指定 Cisco 料號、主張、華星光連結）、華星光（800G ZR 交付界線、年報連結、營收比重）皆可於 revision 3 的預覽回應讀取。 |
| 讀者入口 | 在演練主機開啟 `http://127.0.0.1:3016/admin`，登入演練 owner，選取上述草稿及 `industry-map/applications/application-ai-networking.md` 後按「閱讀預覽」。`/next` 顯示已發布的基準 release。演練網站只綁 loopback，手機可讀另提供的研究內容，實機網站未走讀。 |
| P1–P5 證據定位 | P1：LPO MSA §§6.1–6.2、Marvell brief Features／Description、Cisco 料號產品段落；P2：Cisco QSFP-DD800 表 2–5 與 VR8／FR／FR4 產品段落；P3：LPO MSA §§6–7、Broadcom TH6 公告、Arista FAQ p.3；P4：Cisco 可訂購料號、華星光年報第 72 頁（PDF 73）與 Marvell MV-CD822 brief；P5：Cisco 分接支援、Arista 1–3 m AEC 例與 CPO／LPO 反向條件。查核日 2026-11-24。 |
| 完成的內容 task | 2.1 完成產品五面向與缺口。2.2 完成華星光年報商品與營收主張、offering 及雙向閱讀連結核對。全量 validator 通過（17 個環節、7 個題材、89 筆來源），OpenSpec strict validation 通過。2.3 已完成 revision 3 的匯入、驗證及 API 預覽內容核對。 |
| 裝置走讀紀錄 | Boris 於 2026-11-24 回報樣本驗收完成。裝置、瀏覽器與個別走讀結果未提供。 |
| 閱讀問題／修正位置／修正後驗證 | Boris 於 2026-11-24 回報先前的閱讀模板可用，研究內容未提供。更正匯入並提供 revision 3 的正確入口與內容。 |
| 深度標準確認人／時間／結論 | Boris 於 2026-11-24 確認沿用既有閱讀模板、樣本驗收完成，並要求每間公司研究至少達到樣本標準。各公司逐家依[研究矩陣的最低驗收標準](research-expansion-matrix.md#公司研究最低驗收標準)審查。 |

## 各批內容與閱讀驗收

| 批次／task | 同版閱讀鏈與範圍 | 內容 commit／草稿 revision | 證據與內容審閱 | 網站閱讀、修正及限制 |
|---|---|---|---|---|
| A／3.11 | AI networking → 光電互連比較 → 主機 NIC → 博通；另走光纖連接組件 → 安費諾。草稿預覽涵蓋既有環節及新增角色。 | `d444314`；draft `ea2dedde-ea70-4d85-980a-21e5b5b5891a` revision 3，基準 release `a5df290c-0b6d-5011-b842-ae73cd8a1f99`。 | 2026-11-24；全量 validator 通過（17 個環節、7 個題材、143 筆來源），OpenSpec strict validation 通過。Revision 2 匯入 28 份差異檔、查 34 個 API 預覽。Revision 3 重驗 5 份閱讀調整及對應預覽。 | 1440×1000、390×844 的 Chromium viewport 均驗證連續閱讀和引用連結。將讀者頁未渲染的 Markdown 表格改寫為標題與清單，重查比較、需求案例與公司來源。實體手機最終走讀留待 6.5；同條件成本、BER、料號收入等缺口依矩陣保留。 |
| B／4.11 | AI 機櫃供電 → 設施至板端比較 → 變壓器／東元 → 原文；另走高密度電源模組／芯源系統 → 原文。開關櫃、UPS、BBU、busway、rPDU 與電源架均在同版。 | `be2db8b`；與 A 使用同一草稿 `ea2dedde-ea70-4d85-980a-21e5b5b5891a` revision 4，基準 release `a5df290c-0b6d-5011-b842-ae73cd8a1f99`。 | 2026-11-24；全量驗證 17 個環節、7 個題材、181 筆來源；矩陣連結與表格結構通過。匯入 29 檔差異，草稿 validate 與 27 頁 API 預覽通過。 | Chromium 1440×1000、390×844 均顯示完整的分層比較與 4 步案例，沿上述路徑看到東元與 MPS 引用。案場配置、同負載測試、各品項收入待依矩陣補件。 |
| C／5.11 | 晶片整合 → 規格傳導 → ABF 載板／Shinko → 原文；另走中介層／台積電 → 原文及原有多層 PCB。產品頁連到增層膜、微孔和曝光。 | `c300212`；草稿 `ea2dedde-ea70-4d85-980a-21e5b5b5891a` revision 5，基準 release `a5df290c-0b6d-5011-b842-ae73cd8a1f99`。 | 全量驗證 17 個環節、7 個題材、239 筆來源。匯入 31 檔，validate 與 29 個頁面 API preview 通過。重驗使用相同 revision。 | Chromium 1440×1000、390×844 均完成分層與案例閱讀，能走到舊 PCB 頁、Shinko 與台積電來源。修正查核腳本的 `semiconductor` segment 路徑和 PCB 頁標題。CoWoS 5.5× 口徑、不同載板的合格產出和料號收入依矩陣留缺口。 |

## 整合、發布與公開版本

| task／階段 | 必要證據 | 目前結果 |
|---|---|---|
| 6.1 | 穩定 ID、aliases、legacy keys、offerings、雙向邊；線性、題材、手足及回路 | 全量驗證通過。與 `a0791de` 核對 95 家既有公司的 ID、aliases、legacy keys 及 listings。NVDA 依 10-K 從 `UNKNOWN` 校正為 `XNAS`，沿用 ID／ticker；Shinko 保留 `PRIVATE:shinko`，舊 6967 只列歷史。74 筆 offering 的公司／產品／角色組合唯一；新增與更動的 offering 和兩筆關係均對到有證據的 well-supported 主張。444 個文字研究連結可解析。 |
| 6.2 | 三份 delta specs 的 requirement／scenario 對照、矩陣完整度、三個需求案例 | 已逐項核對，見下方對照。章節、原文與例證均已讀，已修正矩陣的基準占位；6.3–6.6 的驗收各依實際結果記錄。 |
| 6.3 | 同一內容 commit 的地圖、後端離線、前端與既有靜態快照 CI 檢查 | `7c3fd3630fb78b3acf38171f329339a9b54ed069`。本機重現既有 CI：全量地圖（17 個環節、7 個題材、239 筆來源）、66 類 validator 案例、267 個 unittest 均通過。後端依 CI 的 Python 3.12 與鎖定依賴，在無網路 Linux 容器從該 commit 執行，283 passed／103 skipped（需獨立 PostgreSQL 的案例依離線設定跳過）。Windows 的 managed Git worktree 用例另在 Linux 通過。前端使用鎖定依賴，typecheck、23 個 unit tests、production build、64 個 offline Playwright 與合成快照 build／52 個 static Playwright 均通過；建置依 workflow 環境重跑本機 agent 升級提示造成的中斷。兩項既有相容性測試改為比對舊代號映射及 Git archive 的公司 ID，既有 95 家及 100 個角色的檢查保留，四家新增公司使用 listings。 |
| 6.4 | 演練部署報告、同一內容 commit、draft revision、成功 job、release／研究 head、新舊連結 | `7c3fd3630fb78b3acf38171f329339a9b54ed069`。Deploy report `.work/research-drill/deploy-rehearsal-20261124T104756Z.json` 的 smoke 與隔離檢查均通過，Alembic 維持 `0017`。從 release `a5df290c-0b6d-5011-b842-ae73cd8a1f99`（generation 4）開草稿 `19700086-74e0-40cd-85bb-03e33c62d0a1`，整合 84 份檔案，revision 2 驗證及 82 個實體預覽通過。發布 job `07ebbc87-510b-47ed-8c0d-11de5c4e57f5` 經 `run-job` 回 `published`／`complete`，啟用 release `d973c2d1-0a30-5221-ac20-adf00a0632bd`（generation 5，2026-11-24 18:49 UTC+8）。同步 job `c3ec4ac1-07dd-465f-9dfc-8364dcbb67e8` 完成，`research/published` 由 `7a0bda265c3e83e2d86c6a03476cfc5be3ad55eb` 前進至 `4be36cf61c13e4108df0a0179ec64a149b6085af`。新舊 release 保留於版本紀錄，五個舊代號在兩版均解析至相同 ID，四個新公司的上市代號可解析，`/companies/2330.TW` 及固定舊版的台積電頁均可讀。 |
| 6.5 桌機 | Boris 的裝置、release、三方向逐條閱讀結果、回饋、修正與確認 | 同一 release 的 1440×1000 Chromium 自動走讀已通過。待 Boris 桌機走讀。 |
| 6.5 手機 | Boris 的裝置、release、三方向逐條閱讀結果、回饋、修正與確認 | 同一 release 的 390×844 Chromium 自動走讀已通過。待 Boris 確認裝置、連線並以手機走讀。 |
| 6.6 演練快照 | 演練容器、同一 release、內容 commit、輸出路徑、build／parity／逐頁及資產引用檢查、私人資料核對 | 待 6.5 確認 release 後匯出。 |
| 正式部署 | merge 後部署目錄中的 commit、smoke 與部署紀錄 | 待 merge 後執行 |
| 正式研究發布 | 正式最新 release 草稿整合、發布 job／release 與閱讀核對 | 待 merge 後執行 |
| 公開發布 | 正式同版快照、公開產物、發布時間及 URL | 待 merge 後執行；未宣稱正式站或公開站已更新 |

### 最終走讀入口（6.5）

Chromium 以 1440×1000 與 390×844 驗證三條鏈的比較、案例、產品、公司和固定 release 的引用展開。Boris 的桌機與實體手機走讀結果待回覆。

- 光／電互連比較與 800GbE 需求案例 → 主機 NIC → 博通，展開 Broadcom 57708 的引用。 [AI 叢集網路](http://127.0.0.1:3016/next?focus=application-ai-networking&release_id=d973c2d1-0a30-5221-ac20-adf00a0632bd)
- 設施、機櫃與板端的供電比較與需求案例 → 變壓器 → 東元電機，展開東元變壓器原頁的引用。 [AI 機櫃供電](http://127.0.0.1:3016/next?focus=application-ai-rack-power&release_id=d973c2d1-0a30-5221-ac20-adf00a0632bd)
- 先進封裝與 ABF 載板的規格傳導 → ABF 封裝載板 → 新光電氣，展開 Shinko DLL 載板的引用。 [晶片與記憶體整合封裝](http://127.0.0.1:3016/next?focus=application-chip-integration&release_id=d973c2d1-0a30-5221-ac20-adf00a0632bd)

桌機可在演練主機直接開啟。實體手機仍待確認裝置與連線方式。驗收紀錄需包含裝置、瀏覽器、三條鏈與案例的閱讀結果，以及任何需修正的頁面。

## 影響路徑與相容性（6.1）

| 判定 | 本版驗證案例 |
|---|---|
| 線性上下游 | `substrate → advanced-packaging → odm → datacenter`。逐邊核對前節點 `downstream` 與後節點 `upstream`。 |
| 題材橫向 | `networking → cpo-silicon-photonics → advanced-packaging`。兩環節均宣告題材，題材的 segments 包含兩者；兩環節沒有直接上下游邊。 |
| 共享下游手足 | `thermal → odm ← pcb`。由 thermal 的下游 ODM 回查 `odm.upstream` 找到 PCB，並核對 PCB 也宣告 ODM 為下游。 |
| 回路 | `compute → advanced-packaging → odm → datacenter → compute`。從 compute 以 visited 去重遍歷，正確終止於四個節點。 |
| 同一公司與關係 | NVDA、AVGO、台達、Vertiv、ASE、Shinko 沿用原 ID。光通訊與設施端新增 offering 另引用直接能力，既有供應範圍不擴張到個別料號。新增 `relation-3189-tw-supplies-nvda-abf` 有雙方公告，已供應與未來擴充分開；Credo 與 Astera 的比較引用交付證據。 |

## Delta spec 逐項核對（6.2）

| 規格 requirement | 各 scenario 的驗收證據 |
|---|---|
| industry-map／重點產品原理、規格與替代 | 光收發模組 → 800GbE 比較連到 AEC，能讀端點、距離、速率、功耗／成本比較條件。14 個核心產品及 11 個廣度產品均有五面向、實質主張和指定來源，初始的通用定義已補實；各產品的未取得數據列於矩陣。 |
| industry-map／三方向沿用途到供應角色 | B 預覽可走設施、變壓、開關、UPS、BBU、幹線、rPDU、電源架與板端。C 的 ABF 頁連增層膜、微孔、線路，另分中介層及 PCB。角色證據不足的市場與相鄰供應者保留排除理由（如 BBU 其他市場、台灣曝光設備）；未建立無證據的 offering。 |
| industry-map／需求成立及失效條件 | A 為 800GbE 啟用埠與傳輸介質，B 為同供電架構及冗餘的持續負載，C 為更大尺寸、多布線層與良率。三例有情境、反向條件及待核訊號。C 的 12／9 片排版及 90%／80% 為假設，未用來估任何公司的出貨或收入。 |
| company-research／以交付為公司深化依據 | Vertiv 從開關、UPS、busway、rPDU、電源架各連對應產品和型錄。安費諾、貿聯與 Broadcom 等能力按產品證據，缺客戶與數量仍保留。景碩具名關係有雙方公告。 |
| company-research／代表公司選取 | D4 的台股、美股與其他市場逐列紀錄。台達、Vertiv、NVIDIA 沿用既有公司；東元母公司與 TECOBAR、ASE 投控與 ASE Inc.、MKS 與 ESI 分開。晶化與積水等比較候選列在矩陣，角色證據不足的市場保留缺口。 |
| data-coverage／逐項證據矩陣 | 矩陣的 14 個核心產品、22 家優先公司、11 個廣度範圍、12 個既有角色及三個案例各有可核列。確認公司能力與產品五面向均已補，狀態分為分類、證據、內容及預覽。檢查清單、原文、限制和三批實測載於矩陣及上述驗收。 |
| data-coverage／缺口與未完成分開 | CoWoS 5.5× 的兩份公開資格口徑、功耗同條件測試、料號收入及未具名客戶保留具體限制。已用可取得的公司技術／官方文件補核心原理。5.11 以前的草稿預覽有各自版本，Boris 最終裝置走讀以 6.5 的獨立記錄為準。 |
| data-coverage／預覽、發布及公開版可核對 | 草稿修訂 3／4／5 均已完成對應批次預覽。後續逐一記錄 6.3 CI、6.4 演練部署及研究發布、6.5 最終走讀、6.6 演練公開快照。正式部署、正式研究發布及公開部署留在各自的 merge 後欄位。 |
