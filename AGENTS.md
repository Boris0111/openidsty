# AGENTS.md

任何 AI agent 接手這個 repo 前，先讀這份。它只負責指路 —— 細節都在它指向的檔案裡，不要在這裡重複，兩份會漂移。

## 這個專案在做什麼

建立半導體與 AI 伺服器產業的**結構化、可遍歷地圖**，讓「一則新聞 → 受影響的環節與公司」這個推導能自動完成。

交付形態刻意是 **repo 內的純文字 Markdown ＋ agent skill**：無伺服器、無資料庫、無排程、無 API key。消息的即時性靠查詢當下的 web search，不靠建置時抓取。

## 產物在哪

| 路徑 | 是什麼 |
|---|---|
| `industry-map/README.md` | **Schema 的唯一真實來源。動任何地圖檔之前必讀。** |
| `industry-map/ai-server/`、`semiconductor/` | 環節檔。YAML frontmatter 承載結構，散文承載解釋 |
| `industry-map/themes/` | 題材檔，含生命週期狀態與里程碑 |
| `industry-map/sources.yaml` | 免費公開資訊來源註冊表（尚未建立，見 `add-industry-map` 第 9 組 tasks） |
| `scripts/validate_map.py` | 結構驗證器 |
| `tests/run_validator_tests.py` | 驗證器自身的測試套件 |
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
