# Design

## Context

動機見 `proposal.md`。2026-11-23 以主 checkout `a0791de` 的檔案盤點：95 家公司中 26 家 deep、69 家 basic；59 個產品頁中 57 個 `claims: []`。這只是 authoring 基準；空 claims 不代表沒有相連公司證據，也不代表正式發布版本與工作目錄相同。

已核對的基礎如下：

- `industry-map/README.md` 已支援產品用途、邊界、採用條件、瓶頸、替代限制、主張與引用，以及分類、能力與具型別關係。本次內容可使用現有格式。
- `product-liquid-to-liquid-cdu.md` 示範了產品頁本身的原文主張、具體選型條件及公司交付界線；`product-optical-transceiver.md`、`product-datacenter-switch.md`、`product-abf-substrate.md` 仍多為分類與待研究項目。
- `application-ai-networking`、`application-ai-rack-power`、`application-chip-integration` 已有閱讀步驟，可持續擴充；不必重新開發供應鏈 UI。
- `docs/research-drafts.md`、`docs/research-publication.md` 與 `docs/public-snapshot.md` 分別規範草稿、研究發布及公開快照。部署 image 不會代替研究發布。
- `company-research` 主 spec 的 Purpose 仍提及財報，但現行 requirements 明定不提供財報功能；部分早期文件也含過時的 runtime 說明。本次依現行 requirements 及部署文件操作，不藉內容深化恢復已移除功能。

此 design 用來解決跨三方向的分類、證據粒度、驗收與版本交付問題，符合需要事先釐清設計取捨的條件；不涉及新的程式架構。

## Goals / Non-Goals

**Goals:**

- 一個 change 管理三個有明確邊界的研究批次，先形成可讀樣本，再逐批擴大。
- 讓讀者能沿應用、產品、公司、證據及需求推論完成一段研究；研究深度與涵蓋範圍分開驗收。
- 使用既有格式、讀取頁與發布管線，使內容成果可在私人研究與公開快照中一致呈現。

**Non-Goals:**

- 不以這次規劃承諾產業全覆蓋、固定新增公司數或所有 basic 公司升級；不把零缺口當成研究完成標準。
- 不新增互動規格圖、前端參數比較器、欄位自動抽取、財報數值功能或新資料庫欄位。
- 不把工具安裝、沙箱權限、Prefect 清理與正式服務修復混進內容任務。驗證環境不可用時保留未完成，另外處理具體阻礙。

## Decisions

### D1：一個 change，三個批次，共用一次深度校準

建議順序：共用準備 → A 的光模組樣本 → 完成 A → B → C → 全圖核對與最終驗收。

A 已有七家公司的研究可沿用查核線索，適合先校準產品層內容。樣本由 Boris 走讀後再擴大，避免三個方向同時大量產出卻使用不同的深度標準。樣本審閱與最終閱讀驗收是實作 task，不代表本次 propose 要等待才能交付。

替代方案是三個獨立 changes，可較早分別合併，但會重複定義研究標準與交叉關係；本次依需求整合為單一 change。批次可分開 commit 與審閱，依 repo 規則仍須整份 tasks 完成、archive 後才交付 merge。若日後需要提前發布其中一批，須先明確拆分 change，不能略過其餘未完成任務。

### D2：以產品問題驗收深度，既有欄位承載證據

每個核心產品在原有固定段落內，使用必要的次標題回答以下問題，不新增必填 Schema 欄位：

| 面向 | 內容與證據要求 |
|---|---|
| 原理與用途 | 系統位置、輸入／輸出、作用機制及相鄰產品分工；核心用途與原理需有已讀原文支持 |
| 規格／製程與成本因素 | 挑出會改變性能、製造難度或採用條件的參數，解釋原因；數值附型號、版本、單位與測試條件，不寫無條件排名 |
| 路線比較 | 交代比較對象、適用情境、整合／維修依賴及替代不成立的情況；推論有前提，未取得同口徑資料則保留缺口 |
| 公司交付 | 公司交付材料、元件、設備、成品或服務的哪一部分；能力、認證、採用、量產、收入分別判定 |
| 需求傳導與風險 | 至少列出相關規格或需求改變如何影響本產品的條件、可能抵銷效果及追蹤證據；公司層的曝險保留限制 |

`claims` 記錄本頁真正需要負責的主張，`evidence` 使用既有來源 ID、定位、讀取範圍、期間及 stance；`gaps` 分類原因。產品頁可以連到公司主張，但不能只靠一條公司連結代替整個產品原理。role 頁仍可作分類，不要求為湊數新增 claims。

數值只用於有查核日期的技術說明與比較；動態值不寫入 `kpis`／`signals`。本次新增公司內容以產品與業務質性研究為主，不新增財務數值面板或把總營收當產品收入。

替代方案是為每個參數新增結構化規格與比較欄位；目前沒有必要，會把內容研究擴成資料模型與 UI 工程，故不採用。

### D3：三方向的必做範圍與新增邊界

下列是實作的研究範圍，不是已查核的產業結論。新增類別的名稱與 ID 由原文確認交付界線後決定，維持 kebab-case；不得以資料不足為由默默刪除必做範圍。若核心來源確實無法取得，保留 task 未完成並提出具體範圍修訂。

#### A：光通訊與 AI 網路

既有主入口：`applications/application-ai-networking.md`、`ai-server/networking.md`；相關題材 `themes/cpo-silicon-photonics.md`。

| 工作組 | 必做產品／研究問題 |
|---|---|
| 光鏈路 | `product-optical-transceiver`、`product-optical-dsp`、`product-inp-laser-chip`、`product-optical-epiwafer`：用途、內部分工、速率／距離與介面限制、製程與測試瓶頸 |
| 電與交換系統 | `product-retimer`、`product-active-electrical-cable`、`product-ethernet-switch-asic`、`product-datacenter-switch`：端點、交換與連接角色、系統採用條件 |
| 廣度補強 | 研究光纖連接組件、主機端網路介面兩個交付範圍；辨認是否需獨立 role／product，至少各提供有證據的閱讀位置與供應者／缺口，不擴至電信全產業 |
| 比較與傳導 | 在既有格式整理可插拔光模組、LPO／CPO、銅互連的比較條件；分清 scale-up／scale-out／跨機房用途，不把架構名稱當單一商品 |

優先重查既有 `company-avgo`、`company-mrvl`、`company-crdo`、`company-alab`、`company-2345-tw`、`company-3081-two`、`company-4979-two`。新增角色先查既有公司是否有相關能力；需要新增公司時按 D4 選取，不預填尚未查核的客戶關係。

#### B：資料中心供電

既有主入口：`applications/application-ai-rack-power.md`、`ai-server/power.md`、`semiconductor/power-discrete.md`；相關題材沿用 `themes/` 中供電題材的現有 ID。

| 工作組 | 必做產品／研究問題 |
|---|---|
| 既有機櫃與板端 | `product-power-shelf-psu`、`product-pmic-voltage-regulator`、`product-power-module`：轉換位置、負載、損耗、熱與保護條件 |
| 設施端廣度 | 資料中心用變壓、開關／配電設備、UPS：電網接入介面、設備交付邊界、容量／冗餘／交期的查核條件 |
| 機櫃介面廣度 | BBU、母線／busway、PDU／供電分配：功能、介面與適用範圍；是否拆為不同產品依可替換交付角色判定 |
| 比較與傳導 | 電網／設施容量、機櫃架構與晶片供電分層；比較條件包含轉換位置、備援時間、負載與維修，不把不同層級的額定能力直接相加 |

優先重查 `company-delta-electronics`、`company-2301-tw`、`company-6282-tw`、`company-mpwr`、`company-vicr`，並檢查 `company-vertiv` 對新增設施角色的證據；缺少代表供應者的角色另查官方來源。以既有 power／datacenter 及 application／role 延伸，必要時新增 application；不預設增加一個涵蓋全部電網的頂層產業。

#### C：先進封裝與 ABF

既有主入口：`applications/application-chip-integration.md`、`ai-server/advanced-packaging.md`、`ai-server/substrate.md`；延伸至現有 materials／equipment／test 入口時保持既有角色邊界。

| 工作組 | 必做產品／研究問題 |
|---|---|
| 核心產品 | `product-2p5d-interposer-package`、`product-flip-chip-package-service`、`product-abf-substrate`：各層功能、交付差異、製程路徑與認證 |
| 材料與設備廣度 | 增層介電材料、載板微孔加工、線路形成：材料／製程／設備分別交代，與既有 role／product 去重，不擴成整個材料或設備產業 |
| 規格與路線 | 線寬／線距、孔徑、層數、面積、翹曲與可靠度如何影響良率／交付；玻璃核心等路線依已讀文件定位為研究、認證或商業化，不預設替代結論 |
| 比較與傳導 | 分開中介層、封裝載板與 PCB；建立「規格改變—製程限制—有效產出—公司能力」案例與反向條件 |

優先重查 `company-tsmc`、`company-3711-tw`、`company-amkr`、`company-6239-tw`；深化五家載板公司 `company-4062-t`、`company-private-shinko`、`company-3037-tw`、`company-8046-tw`、`company-3189-tw`。新增材料／設備角色按來源挑選代表供應者，不把既有公司只因名稱相近或同產業就配對上去。

### D4：先證據、後公司能力與關係

每個工作組依序讀標準／官方技術文件、具體產品資料與公司公開文件。標準付費或型號資料未公開時保留限制；不以二手摘要冒充已讀原文，不複製未授權圖表。

每個新增交付角色都要檢查台股、美股及已發現的其他關鍵市場，記錄候選與納入／排除理由。優先完整研究能支持該角色的代表公司；取得兩家可比較公司的證據時提供比較，只有一家或沒有公開可用證據時記錄限制，不以數量硬湊。公司選取紀錄是界線核對，不是另做一份無限擴張的名單。

新增公司先查 `companies/` 的 ID、aliases、legacy keys、listings 與官方身分。公司深研遵守原九個內容段落；其中「財務可取性」只交代來源／缺口，不實作財報功能。公司必須完成段落的實質檢閱才標 deep。

先完成主張，再新增 `offerings`；具名供應必須引用支持該交付與雙方的 well-supported 主張。需求案例可以是帶條件的 inference，不強行轉成公司對公司的具名供應。共享公司與關係只維護一份。

### D5：交付矩陣與研究本文分工

在 apply 建立下列文件，規劃階段不建立：

- `docs/research-expansion-matrix.md`：共同矩陣與三方向索引，保留基準提交、範圍、選取理由、產品五面向的定位、證據／缺口、審閱狀態與對應 task。
- `docs/research-expansion-acceptance.md`：樣本回饋、各批閱讀結果、修正、演練提交／release、裝置、既有連結核對，以及正式發布／公開快照的後續紀錄。
- `industry-map/research/`：各方向的比較與需求傳導研究頁；只有對讀者有用的研究問題、判斷與限制，不展示內部工作清單。

分類表存在、來源已取得、內容已核對、讀者已走讀是不同狀態。矩陣是本次內容審查紀錄，`tasks.md` checkbox 仍為實作進度的唯一依據，不另造百分比分數。

產品核心用途／原理沒有原文支持時不能以「未取得」整頁交付。具名客戶未公開、產品收入不公開等非必要結論可保留缺口；未研究則仍是未完成。刪減必做範圍須先更新 change，不將缺口當成自動豁免。

替代方案是替所有缺口開 Issue 或做新的管理端進度功能；目前已有 coverage，且本次沒有此 UI 需求，故不採用。

### D6：分層驗證，保留真實閱讀與版本證據

1. 每個內容工作組完成後跑全量 `python scripts/validate_map.py`，核對穩定 ID、來源、taxonomy 與雙向環節邊。未改 validator 不新增鏡像式測試。
2. 每方向都逐項審查矩陣中的來源與敘述。樣本及最終三方向的桌機／手機閱讀由 Boris 確認；等待回饋時可繼續獨立的來源查核，不能把等待中的驗收勾完。
3. 樣本走讀前從 worktree 依 `research_drill.py` 建立隔離演練環境，供樣本及各批草稿匯入、驗證與預覽使用；最終再對同一內容提交核對既有 CI、部署演練與研究發布。CLI 用 `--base-url http://127.0.0.1:3016`；演練沒有 scheduler，單筆發布由既有 `run-job --job <uuid>` 執行。不得使用正式 owner 憑證。
4. 以演練發布的同一 release 匯出公開快照並建置／逐頁檢查，核對新增研究、來源、資產及既有連結。使用演練容器內既有 `app.public_snapshot` 匯出至演練輸出，不能從 worktree 呼叫正式 `research_lab.py public-snapshot`。相關操作紀錄確切容器、release 與輸出路徑。
5. 不修改編譯或投影程式時，不要求為內容新增 full rebuild 性能測試；保留既有 CI 及內容匯入／閱讀驗收。若範圍另行擴至程式，重新評估適當測試，不自動擴大本 change。

Docker、Python 或 CLI 無法執行時先分辨沙箱權限與主機實際狀態，不將沙箱內「找不到」等同未安裝。不得為通過任務自動重啟 Docker Desktop 或改動正式服務。

### D7：讀者圖解只在有助理解時加入

先用既有 Markdown 表格、概念頁與流程欄位表達。遇到純文字難以辨認的層次或介面，再加入原創或可使用的靜態示意圖，依現有 `research-assets.yaml` 登錄 hash、來源與授權；概念頁仍須符合既有 diagram-assets 要求。不加入圖解引擎或產品專屬互動元件。

## Risks / Trade-offs

- **範圍隨公司與設備名單膨脹** → 以 D3 工作組為界，只研究完成該鏈所需的交付與代表公司；新方向另列後續，不因搜尋結果持續擴張。
- **同一來源被泛用至不同世代或產品** → 型號／版本／期間附在主張與引用旁；比較前核對相同條件，廠商自述保留性質。
- **先前深研或分類存在造成完成錯覺** → 分別審查產品五面向與公司新能力；不能因公司為 deep 就省略查核。
- **官方來源只支持能力，交易資料不足** → 保留能力連結與具體缺口，不承諾補出所有客戶及產品收入。
- **單一 change 延後合併** → 逐批 commit、逐批走讀，維持可審查粒度；要提前發布必須先正式拆分 scope。
- **工作目錄與已發布研究分歧** → 演練與正式發布都從最新 release 建立草稿，匯出後整合本 change 的內容差異，不能整包覆蓋正式期間新增的研究。

## Migration Plan

沒有資料庫遷移、API 切換或 Schema 升級。

1. apply 在專用 branch／worktree 修改研究；所有 merge 前 tasks 完成並在 branch archive，檢查 CI 後交付維護者 merge。
2. merge 後，如需部署 repository 內的地圖與來源更新，依 `docs/research-deployment.md` 從獨立部署目錄部署已合併提交並保留 smoke 紀錄。
3. 依 `docs/research-drafts.md` 從正式最新研究建立／匯出草稿，整合已驗收內容，核對基準、diff、來源與資產後，依 `docs/research-publication.md` 發布。記錄 content commit、release ID 與閱讀結果；不把 initialize 或部署成功等同研究發布。
4. 依 `docs/public-snapshot.md` 匯出該正式 release、建置、parity 核對，再由維護者發布公開站，分別記錄私人與公開版本。
5. 內容問題用既有研究還原流程恢復先前 release，保留新舊歷史；公開版回復已保存的靜態產物。程式 image 回退與研究還原分開處理。

正式部署與公開發布在 merge 後紀錄，不放進會阻止 merge 的前置 checkbox；合併前必須完成可在演練環境驗證的內容與閱讀項目。

## Open Questions

- 各新增角色有哪些免費且足以支持型號／交付差異的官方文件？由對應工作組查核，來源不足依 D5 處理，不能自動縮小必做範圍。
- 在資料足以比較的範圍內，哪些新供應者最能補足台美及其他市場代表性？依 D4 的角色與證據選取，不影響既定三方向及產品問題。
