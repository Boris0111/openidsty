# AGENTS.md

任何 AI agent 接手這個 repo 前，先讀這份。它只負責指路 —— 細節都在它指向的檔案裡，不要在這裡重複，兩份會漂移。

## 這個專案在做什麼

建立半導體與 AI 伺服器產業的**結構化、可遍歷地圖**，讓「一則新聞 → 受影響的環節與公司」這個推導能自動完成。

產業結構仍以 **Markdown ＋ agent skill** 維護，研究另可經網站草稿發布成版本。正式研究服務（`compose.research.yaml`）以 Next.js／Cytoscape.js、FastAPI、PostgreSQL 與 Prefect 呈現公司關係、官方事件與題材指標（公司財報已於 2026-10-23 移除），只綁本機 127.0.0.1；對外只公開不含伺服器的研究結構靜態快照（`docs/public-snapshot.md`）。排程在 scheduler profile，重啟後自動恢復。正式服務只執行 `main` 上已合併提交的 image，從獨立部署目錄部署（`docs/research-deployment.md`）。啟動及資料維護見 `README.md` 與 `docs/research-lab.md`。行情、帳號與 AI 摘要不在範圍內。

## 產物在哪

| 路徑 | 是什麼 |
|---|---|
| `README.md` | 專案環境設定、執行驗證與開發操作指南 |
| `industry-map/README.md` | **Schema 的唯一真實來源。動任何地圖檔之前必讀。** |
| `industry-map/ai-server/`、`semiconductor/` | 環節檔。YAML frontmatter 承載結構，散文承載解釋 |
| `industry-map/themes/` | 題材檔，含生命週期狀態與里程碑 |
| `industry-map/sources.yaml` | 免費公開資訊來源註冊表；欄位與維護流程見 `industry-map/README.md` |
| `scripts/validate_map.py` | 結構驗證器 |
| `tests/run_validator_tests.py` | 驗證器自身的測試套件 |
| `backend/`、`frontend/`、`compose.yaml` | 應用、離線測試與隔離 Docker 執行環境 |
| `data/company-research.yaml` | aliases、CIK 與有來源的公司關係；維護見 `docs/company-research.md` |
| `docs/research-deployment.md` | 正式服務的部署目錄與防護、部署與回退、遷移的擴充與收縮、合併前演練 |
| `docs/` | API、來源、前端操作與整合驗收記錄 |
| `openspec/` | 規格與變更記錄（見下方工作流） |

## 動手前後必做

```bash
python scripts/validate_map.py                # 改任何地圖檔後必跑
python scripts/validate_map.py --skip-prose   # 只寫了 frontmatter、散文未寫時
python tests/run_validator_tests.py           # 改了驗證器後必跑
```

驗證器只檢查**結構**（必填欄位、識別碼唯一性、引用可解析、上下游雙向一致、代號格式、列舉值、段落齊備）。它**不**檢查內容正確性 —— 某公司是否真屬於某環節、市佔是否正確，是人的判斷。

## 三個會讓你寫錯的地方

**1. 地圖是有向圖且含回路。** `compute → advanced-packaging → odm → datacenter → compute` 是真實存在的環（資料中心資本支出回頭驅動晶片需求），不是資料錯誤。`position` 只是粗略序位，**不保證無環**。遍歷時必須記錄已訪問節點，否則無限迴圈。

**2. 推導影響範圍需要三種走法，缺一種會漏掉重要標的：**

- 線性上下游 —— 沿 `upstream` / `downstream` 遞迴
- 題材橫向擴散 —— 經 `themes` 跳到題材，再由題材的 `segments` 擴散到非相鄰環節
- **共同下游的手足環節** —— 由 X 的下游 D 反查 `D.upstream`，取得與 X 並列供應同一客戶的環節

第 3 種最容易被忽略。實測證實：只實作第 1 種時，「液冷帶動 PCB/CCL」這類消息會整族漏掉，因為 `pcb` 不是 `thermal` 的鄰居。推導路徑的實測記錄在 `industry-map/README.md` 末段。

**3. 上下游是雙向顯式宣告。** 新增一條關係要改**兩個**檔案。這是刻意的冗餘（讓消費端只讀單檔就知道上下游），驗證器會強制一致。

## 慣例

- 地圖內容與 OpenSpec artifacts 以**繁體中文**撰寫；程式碼、識別碼、欄位名用英文 kebab-case
- 公司的正規識別鍵是代號而非名稱（中文名有別稱）。格式規則見 README
- `kpis` 與 `signals` 記錄「要看什麼」，不記錄「現在是多少」—— 數字會過時，地圖不承載動態資訊
- 環節邊界的裁決規則：**這群供應商是否扮演一個可彼此替換的供應角色**。有爭議時回到這條規則，而非個人直覺

## OpenSpec 工作流

規格與變更都在 `openspec/`，這是跨工具的專案記憶。不要用對話記憶代替它。

**查目前狀態**（不要相信任何文件裡寫死的進度數字，包括這一份）：

```bash
openspec list                                 # 進行中的 change
openspec status --change <name>               # 某個 change 的進度
openspec list --specs                         # 已歸檔的主 specs
```

**工作流**：propose（產生 proposal / specs / design / tasks）→ apply（照 tasks 實作）→ archive（歸檔並更新主 specs）。

各工具的呼叫方式：

| 工具 | 呼叫 |
|---|---|
| Claude Code | `/opsx:propose`、`/opsx:apply`、`/opsx:archive` |
| Codex | `$openspec-propose`、`$openspec-apply-change`、`$openspec-archive-change` |
| 其他 | `.agents/skills/` 下的同名 skill |

**apply 的進度記錄在該 change 的 `tasks.md` checkbox 裡**，不在對話裡。接手時跑 `openspec status` 就知道做到哪，從未勾選的第一項繼續。

規劃與實作分離：propose 只產生規劃文件、不碰程式碼；要實作必須另外啟動 apply。

**先驗證、再 merge**：change 的 tasks 全部勾完（包括演練環境的實機驗證）並在 branch 上 archive 之後，PR 才交給維護者 merge；還有未驗證的 task 時不要建議 merge。

- **merge 前**：需要實機的驗證從該 PR 的 worktree 在演練環境進行（`scripts/research_drill.py`，見 `docs/research-deployment.md`「合併前演練」）。不切換主 checkout，也不讓正式服務執行未 merge 的程式碼。
- **merge 後**：維護者依 `docs/research-deployment.md` 從部署目錄部署，部署紀錄的 smoke 結果就是紀錄。只有正式環境才有的行為（例如重開機後排程恢復）在部署後核對，記在 `docs/research-acceptance.md`。
- 會改變正式服務的指令只在部署目錄執行；開發 checkout 與 worktree 沒有正式祕密，`research_lab.py` 會拒絕。重啟 Docker Desktop 前，先徵得維護者同意。
