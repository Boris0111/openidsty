# 產業地圖 Schema 與撰寫規範

這份文件是地圖結構的**唯一真實來源**。新增環節、題材或來源時，只讀這份文件就應該能寫出通過 `scripts/validate_map.py` 的檔案，不需要逆向參考既有檔案。

欄位的新增或語意變更，必須同步更新本文件 —— 否則該變更視為未完成。

---

## 目錄組織

```
industry-map/
├─ README.md              # 本文件
├─ sources.yaml           # 資訊來源註冊表（欄位規範見下方）
├─ ai-server/*.md         # AI 伺服器層環節
├─ semiconductor/*.md     # 半導體層環節
└─ themes/*.md            # 題材
```

檔名（去掉 `.md`）必須等於該檔 frontmatter 的 `segment` 或 `theme` 識別碼。

---

## 環節檔 frontmatter

每個環節檔以 YAML frontmatter 開頭（前後以 `---` 包住），其後為散文段落。**結構放 frontmatter，解釋放散文** —— 消費端只讀 frontmatter 就能完成遍歷。

```yaml
---
segment: thermal                 # 必填。kebab-case，全圖唯一，須等於檔名
name_zh: 散熱                     # 必填
layer: ai-server                 # 必填。ai-server | semiconductor
position: 7                      # 必填。1–99，價值鏈大致序位，1 最上游
market_coverage:                 # 必填。見「市場覆蓋表態」
  tw: present
  us: present
  led_by: [KR]                   # 選填
companies:                       # 必填，至少一筆
  - ticker: "3017.TW"            # 必填。格式見「代號格式」
    name_zh: 奇鋐                 # 必填
    role: 氣冷散熱模組與 3D VC      # 必填。在本環節扮演什麼角色
    tier: 1                      # 必填。1=主要玩家 2=次要 3=邊緣或潛在
upstream: [interconnect]         # 必填。可為空陣列 []
downstream: [odm]                # 必填。可為空陣列 []
themes: [liquid-cooling]         # 必填。可為空陣列 []
kpis:                            # 必填，至少一筆。要看什麼指標
  - 液冷滲透率
signals:                         # 必填，至少一筆。什麼事件代表轉折
  - NVIDIA 機櫃世代規格轉換
---
```

### 重要原則：記錄「要看什麼」而非「現在是多少」

`kpis` 與 `signals` 寫的是**觀察對象**，不是當下數值。寫「液冷滲透率」而不是「液冷滲透率約 20%」—— 數字會過時，地圖不負責承載動態資訊。

---

## 代號格式

`ticker` 必須採下列其中一種形式，格式本身即編碼主體類型與所屬市場：

| 市場 | 格式 | 範例 |
|---|---|---|
| 台股上市 | 四位數字 + `.TW` | `2330.TW` |
| 台股上櫃 | 四位數字 + `.TWO` | `6525.TWO` |
| 美股 | 1–5 個大寫字母，無後綴 | `NVDA`、`MU`、`VRT` |
| 韓股 | 六位數字 + `.KS` | `000660.KS` |
| 日股 | 四位英數 + `.T` | `6967.T`、`285A.T` |
| 港股 | 四至五位數字 + `.HK` | `0981.HK` |
| 德股 | 代號 + `.DE` | `IFX.DE` |
| 荷股 | 代號 + `.AS` | `BESI.AS` |
| 未上市 | `PRIVATE:` + kebab-case 識別名 | `PRIVATE:boyd` |

同一公司可出現在多個環節（鴻海既是 ODM 也做連接器），以各環節的 `role` 區分。驗證器**不**禁止代號跨檔重複。

未上市主體的識別名目前自由命名，保持小寫、以連字號分隔即可。

---

## 市場覆蓋表態

`market_coverage` 強迫每個環節對台股與美股各自表態，避免「空白」同時代表「還沒寫」與「該市場沒玩家」兩種意思。

```yaml
market_coverage:
  tw: present | none     # 必填
  us: present | none     # 必填
  led_by: [KR, JP]       # 選填。若本環節由台美以外市場主導，列出市場代碼
```

驗證規則：

- `tw: present` → `companies` 至少一筆為 `.TW` 或 `.TWO`
- `tw: none` → `companies` 不得有任何 `.TW` 或 `.TWO`
- `us: present` / `us: none` → 同理，對應無後綴的純字母代號
- `led_by` 列出的每個市場代碼，`companies` 中必須至少有一筆屬於該市場

市場代碼：`TW` `US` `KR` `JP` `HK` `DE` `NL`。

`none` 是正當的答案。現有清單以 `datacenter.tw: none`（無對等台股大型雲端需求主體）與 `substrate.us: none`（未列美股實質載板製造玩家）示範，並在各檔「玩家格局」交代邊界。這是依目前供應角色與清單範圍表態，不是永遠沒有任何相關公司。

`eda-ip` 同時包含工具與矽智財，力旺及 M31 的 IP 授權角色使合併環節為 `tw: present`；EDA 工具子類未列台股對等供應商。創意、世芯提供整顆客製 ASIC 設計服務，歸 `compute`。不要為了表達工具子類的缺席，把整個 `eda-ip.tw` 改為 `none`。

---

## 上下游關係：雙向顯式宣告

若環節 A 的 `downstream` 含 B，則 B 的 `upstream` 必須含 A，反之亦然。驗證器強制檢查。

這是刻意引入的冗餘。消費端常只讀單一環節檔，若 `upstream` 要靠掃全圖推導，單檔讀取就失去意義 —— 用自動檢查換取讀取端的簡單。

### 圖可能含回路

真實供應鏈有回路：電源供應 ODM，也直接供應資料中心；資料中心的資本支出又回頭驅動運算環節。

`position` 只是**大致序位**，供排序與方向感之用，**不保證全圖無環**。

> **遍歷時必須記錄已訪問節點**，否則會無限迴圈。這不是建議，是必要條件。

---

## 環節邊界的裁決規則

切分依據是：**這群供應商在系統中扮演一個可彼此替換的角色。**

不依公司切（公司跨環節）、不依技術名詞切（名詞會變）、不依財報分類切（各家揭露不一致）。

套用範例：

- 散熱與電源是**不同**環節 —— 供應商不互相替換
- 氣冷與液冷是**同一**環節 —— 多數玩家同時供應兩者，客戶會在兩者間切換
- 晶圓代工與先進封裝是**不同**環節 —— 即使台積電同時做，兩者的競爭集合不同

邊界有爭議時，一律回到這條規則，而非個人直覺。

---

## 環節檔散文段落

frontmatter 之後必須包含下列六個段落標題，**順序固定**：

| 段落 | 內容 |
|---|---|
| `## 環節定義` | 在價值鏈的位置、負責什麼 |
| `## 技術變數` | 規格演進路徑與技術分歧點 |
| `## 玩家格局` | 市佔、定位、各市場對照 |
| `## 傳導鏈` | 上游變動如何影響本環節、本環節如何影響下游 |
| `## 監測指標` | 看什麼數字、去哪裡看 |
| `## 風險` | 客戶集中、技術替代、地緣 |

「玩家格局」提到的公司都必須出現在 `companies` 清單中 —— 散文與結構不得脫鉤。

「傳導鏈」是後續事件判讀的基礎，需具體寫出影響路徑，而非泛泛而談。

---

## 題材檔 frontmatter

```yaml
---
theme: liquid-cooling            # 必填。kebab-case，全圖唯一，須等於檔名
name_zh: 液冷                     # 必填
status: scaling                  # 必填。見下方列舉
segments: [thermal, power]       # 必填，至少一筆。須解析到既存環節
beneficiaries:                   # 必填，至少一筆。須為某環節 companies 中已存在的代號
  - "3017.TW"
  - "VRT"
milestones:                      # 必填，至少一筆
  - date: 2026-Q1                # 必填。YYYY | YYYY-Qn | YYYY-MM
    event: 主要 CSP 液冷機櫃標案放量   # 必填。發生什麼
    evidence: 得標公告或法說會訂單指引  # 必填。用什麼確認它真的發生
---
```

### 狀態列舉

狀態對應的是**證據強度**，不是時間先後：

| 狀態 | 判定依據 |
|---|---|
| `emerging` | 僅有技術討論或供應商宣稱，無客戶導入 |
| `validating` | 有具名客戶試產或認證中，尚無放量訂單 |
| `scaling` | 有訂單與出貨，且在財報或法說會中被量化 |
| `mature` | 已成標準配置，成長回歸終端需求 |
| `fading` | 被替代技術取代中，份額下滑 |

`milestones` 的 `evidence` 欄位必填，因為「有人在談」與「有訂單佐證」是兩回事 —— 不寫清楚用什麼確認，狀態判定就無法稽核。

里程碑日期是查核或預期時間，**不代表事件已完成**。未來事件寫成「待確認」或「追蹤」，證據寫明要查的具名文件、出貨或收入；回顧已發生事件則在散文保留查核日期、來源期間與連結。財報年度不能直接當曆年季度。

狀態按可核對的證據判定：原型展示及合作名單不等於客戶驗證，總營收不等於題材收入。已出現局部商業出貨但缺少可辨別題材的量化財務資料時，保留 `validating` 並明寫此證據限制，不宣稱完全沒有商業出貨。`beneficiaries` 是需持續查核的受惠候選，不表示每家都已取得訂單；散文須交代供應角色、推論與可能的負向影響。

### 題材與環節雙向一致

題材的 `segments` 含 S，則 S 的 `themes` 必須含該題材，反之亦然。驗證器強制檢查。

### 題材檔散文

必須包含 `## 狀態判定依據` 段落，寫明為何目前是這個狀態。其餘段落自由。

### Optional 結構化判讀

題材可在 frontmatter 新增 `assessment`。無此欄位的舊檔仍合法；有此欄位時，下面欄位必須齊備。判讀與研究均由此 Markdown 維護，匯入到 Theme JSON；事件與動態指標不自動改寫判讀。里程碑可新增集合內唯一、穩定 kebab-case `id`，供核對引用；日期仍是預期時間。

| 欄位 | 規則 |
|---|---|
| summary | 非空文字，說明有條件結論及適用範圍 |
| confidence | well-supported／inference／needs-verification，支持程度而非報酬機率 |
| reviewed | 加引號的有效 YYYY-MM-DD，full 驗證須等於散文「查核日期」 |
| evidence | 至少一筆；每筆 id 為集合內唯一 kebab-case，source_id 引用 sources.yaml canonical ID，url 為完整 HTTPS；excerpt／period 必須非空，published 是有效日日期或 null |
| claims | 至少一筆；穩定唯一 id、statement、stance（supporting／counter）、confidence、至少一筆可解析 evidence_ids |
| conditions／gaps | 非空文字陣列，conditions 至少一筆；gaps 可空，未取得反證需明示，不能杜撰 |
| next_checks | 至少一筆，question／evidence_required 為非空文字 |
| paths | 可空；每筆穩定唯一 id、mechanism、direction（positive／negative／mixed／unknown）、至少一筆 conditions 與 claim_ids，及連續有序 steps；傳導均為 inference |
| milestone_reviews | 可空；每筆 milestone_id 引用 milestones 的 id 且不重複；state 為 unconfirmed／confirmed／contradicted，reviewed 為日日期、note 非空、evidence_ids 陣列；confirmed／contradicted 至少一筆證據，occurred 可空 |
| change_reason | optional 非空文字；版本功能建立後，實質修改必須有原因，由匯入端核對 |

steps 每步 `{from, to, type, via?}` 都引用既存環節。upstream／downstream 須有顯式關係；theme 的 via 必須為同時包含兩端的題材；sibling 的 via 必須為共同下游。前一步 to 必須等於下一步 from。結構通過不證明經濟因果；來源對象、成立條件、正負影響仍由研究查核。

例如一筆證據可寫 `{id: product-sales, source_id: aaon-liquid-cooling-filing, url: "https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm", excerpt: "來源的必要摘錄", period: "2025 Q3", published: null}`。source_id 必須已登錄；未知期間寫明「原文未提供」而不補數字。此為欄位範例，不代表已驗證網址或業務事實。

`--skip-prose` 可暫略散文查核基準比對，其餘判讀結構仍檢查；交付與匯入必須 full 通過。來源的 verified／runtime 成功只是網頁或擷取狀態，不表示論點剛被重新查核。詳細維護操作見 `docs/theme-assessments.md`。

---

## 來源註冊表

### 題材指標定義

`data/theme-indicators.yaml` 是獨立定義檔，最外層 version 文字與 indicators 陣列。每項有唯一 kebab-case id、name、themes（至少一筆可解析題材）、entity（衡量對象）、scope、limitations、source_id（canonical 來源）、dataset（穩定資料集識別）、measure、unit／currency、frequency 及 basis。文字欄位不得為空。

kind 為 direct／proxy／background；unit 為 amount／percent，amount 需 USD／TWD，percent 的 currency 為 null。首輪 frequency 與 basis 都為 monthly 或 quarterly 且一致；measure 為 revenue／liquid-cooling-sales／wafer-share。proxy 的 entity 必須是地圖公司 ticker，direct 可衡量地圖外具名公司的特定產品。定義檔禁止 value／observations／period_start／period_end；動態數字保存在 DB，kpis／signals 繼續只寫要監測什麼。

`python -m app.indicator_definitions`（在 backend 執行）驗證所有欄位、來源／題材／公司引用後才匯入；不因定義存在而宣稱已取得值。其具體升級與數值投影操作見 `docs/theme-indicators.md`。新定義匯入會更新目前關聯，不刪除未關聯的歷史觀測。

`sources.yaml` 是一般 YAML，沒有 Markdown frontmatter 或散文。最外層依市場分組，目前使用 `tw`、`us`；市場表示研究入口的分類，不限制網站語言或其報導的公司國籍。第二層固定使用下列資料類型，其下為來源條目的陣列：

| 分組／`type` | 用途 |
|---|---|
| `filings` | 公司公開申報、年報、季報、財報附件 |
| `earnings_call` | 公司免費法說會、簡報、逐字稿或 webcast 入口 |
| `industry_media` | 免費公開的產業文章、協會新聞稿；只收可直接閱讀的部分 |
| `official_stats` | 政府／官方統計報告、表格與公開查詢網頁 |

### 來源欄位與完整範例

| 欄位 | 必填 | 規範 |
|---|---|---|
| `id` | 是 | 穩定且全表唯一 kebab-case，runtime 與研究入口共用 |
| `provider` | 否 | 跨 feed 提供者識別，例如 `technews`；不同提供者不按標題合併 |
| `name` | 是 | 能辨識提供者及來源範圍的文字名稱 |
| `url` | 是 | 免費公開網頁或文件的完整 HTTPS 位址；不包含憑證、API key 或登入後專屬連結 |
| `type` | 是 | 上表四值之一，必須等於所在第二層分組 |
| `access` | 是 | 只允許 `free`；需付費、私有憑證或 API key 的來源不得加入 |
| `reachability` | 是 | `verified` 或 `unverified`，判定方式見下方流程 |
| `checked` | 是 | 最後實際查核日期，`YYYY-MM-DD`，加引號保留為字串 |
| `segments` | 否 | 環節識別碼陣列，每筆須能解析；一般全市場申報入口可省略，不表示沒有覆蓋 |
| `themes` | 否 | 題材識別碼陣列，每筆須能解析；設定涵蓋不表示已取得直接事件 |
| `ingestion` | 否 | 自動擷取設定；省略等同 manual。`adapter` 可為 manual／tw／tsmc／delta／nvidia／microsoft／sec-submissions／sec-facts／rss／tpca／moea／census／eia／aaon-metrics／tsmc-metrics；`url`、`fallback` 為 HTTPS；`max_pages` 1–200；`paged` 表示 RSS 支援頁碼；`kind` 為 tw 的 announcements／revenue／financials；`per_company` 將 SEC URL 的 `{cik}` 展開為有 CIK 的公司；兩個指標 adapter 另有 `max_reports` 1–8、`history_days` 1–730，首次受限回補，其後核對最新兩季 |
| `notes` | 否 | 說明免費內容邊界、查核方法／結果、未驗證原因及統計口徑；為維護者閱讀用文字 |

下例可獨立解析；若加入既有檔案，只把條目併入既有 `us.filings` 陣列，**不要重複建立 `us:` 或 `filings:` 鍵**。名稱與 URL 的用途須人工確認，驗證器不會證明頁面真的免費或內容正確。

```yaml
us:
  filings:
    - id: aaon-liquid-cooling-filing
      name: AAON 液冷產品財報附件
      url: "https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm"
      type: filings
      access: free
      reachability: unverified
      checked: "2026-10-07"
      segments: [thermal]
      notes: "範例展示欄位；實際新增時自行查核可讀性並更新日期與狀態。"
```

### 新增或更新來源的流程

1. 選市場與資料類型，確認來源可不用付費、登入憑證或 API key 閱讀。沿用公開資訊觀測站、SEC EDGAR 與公司 IR 等公開入口；研究 skill 中的券商報告或付費逐字稿不在本表範圍。
2. 用瀏覽器、web open 或一般 HTTP GET **唯讀**檢查位址，辨認重新導向及實際內容。HTTP 200 若只回 JavaScript 外殼、登入／驗證頁，仍標 `unverified`；讀到目標公開頁面才標 `verified`。阻擋、逾時、404 或尚未完成可讀性確認時保留 `unverified`，在 `notes` 記錄原因，並填本次實際查核日期。
3. 依上例併入條目，讓 `type` 與分組一致。媒體或協會網站如混有會員內容，只登錄免費公開區並在 `notes` 明確排除收費子頁；EIA 等網站的公開表格與需金鑰的 API 是不同入口。
4. 若來源聚焦特定環節，以檔名／`segment` 的識別碼填 `segments`，不要填中文名稱、題材名或 ticker。來源可跨環節，無須在環節檔反向宣告。
5. 執行 `python scripts/validate_map.py` 全量模式。修正欄位、分組或引用錯誤後再跑一次；人工再確認免費範圍與查核紀錄，將檔案納入 git diff 審閱。測試新增範例可在地圖副本執行 `python scripts/validate_map.py --map-dir <副本路徑>`。

`verified` 只表示該查核日的指定公開入口可讀，不保證所有子頁或未來存取。若之後失效，改為 `unverified` 並更新日期與原因，保留入口供重試。runtime 依 ingestion 設定執行，`/api/sources` 的 status／last_attempt／last_success 與此人工查核分開；保留實際回補範圍與限制。題材網站投影保存完整散文，checked 從原文「查核日期」擷取，不以匯入日取代。

---

## 執行驗證

```bash
python scripts/validate_map.py              # 全量檢查
python scripts/validate_map.py --skip-prose # 只檢查 frontmatter，骨架階段用
```

骨架階段（frontmatter 已寫、散文未寫）用 `--skip-prose`。交付前必須以不帶旗標的完整模式通過。

驗證器本身的測試套件：

```bash
python tests/run_validator_tests.py
```

它以 `tests/fixtures/valid` 為合法基準，施加單點突變產生各類錯誤，確認每一類都被攔下。改動驗證器後必須重跑。

驗證器只檢查**結構**：必填欄位、識別碼唯一性、引用可解析、雙向一致、代號格式、列舉值、段落齊備。

它**不**檢查內容正確性 —— 不驗證某公司是否真屬於某環節、市佔是否正確。那是人的判斷。

---

## Schema 可查詢性實測記錄

地圖交付前以真實新聞驗證過：**只讀 frontmatter 的 `upstream` / `downstream` / `themes`，能否推導出受影響的環節與公司。** 走不通代表 schema 失敗，應修結構而非以散文補足。

實測日期：2026-10-07。三則皆走通。

### 第 1 則：SK hynix 2026 年供給售罄，HBM4 16-Hi 由三家記憶體廠競標

- **歸屬環節**：`memory`（`000660.KS` 為 tier 1，`led_by: [KR]`）
- **往下游**：`memory` → `advanced-packaging` → `odm` → `datacenter` → `compute`（**此處進入回路，需記錄已訪問節點才會停**）
- **推導出的台廠**：`advanced-packaging` 的台積電、日月光投控、力成；`odm` 的鴻海、廣達、緯創、緯穎、技嘉、英業達
- **非顯而易見的收穫**：`memory.signals` 直接命中「傳統記憶體轉產 HBM 造成的排擠」，因此同環節的南亞科、華邦電、群聯也在影響範圍 —— 新聞本身沒提這三家

### 第 2 則：台廠液冷進入結構性成長，新世代機櫃帶動快接頭、電源、PCB/CCL 升級

- **歸屬環節**：`thermal`（新聞點名的 AVC 即 `3017.TW` 奇鋐）
- **往上游**：由 `thermal.upstream` 取得 `interconnect`，推導出嘉澤、貿聯、信邦、安費諾等介面候選；安費諾有快接頭產品證據，其他玩家須按料號查核，不能將整份清單都當快接頭供應商
- **經題材橫向擴散**：`thermal.themes` → `liquid-cooling.segments` 含 `power`，推導出台達電、光寶科 —— 對應新聞提到的電源升級
- **兩跳取得 PCB**：新聞提到 PCB/CCL，但 `pcb` 不是 `thermal` 的鄰居。經由共同下游 `odm` 可達（`odm.upstream` 含 `pcb`），取得台光電、台燿、金像電

### 第 3 則：台積電 CoWoS 擴產，面板級封裝推進

- **歸屬環節**：`advanced-packaging`
- **往上游**（擴產的候選影響方向）：`materials` 環球晶、中美晶；`equipment` 弘塑、辛耘；`substrate` 欣興、南電、景碩；`test` 京元電、旺矽
- **非顯而易見的收穫**：新聞完全沒提 ABF 載板，但 `advanced-packaging.upstream` 含 `substrate`，地圖自動把載板三雄帶出來
- **訊號命中**：`advanced-packaging.signals` 的「封裝技術世代轉換（中介層轉面板級）」直接對應新聞的面板級封裝進展

### 實測得出的遍歷規則

三則實測確認了消費端必須實作的三種走法，缺一則會漏掉重要標的：

1. **線性上下游** —— 沿 `upstream` / `downstream` 遞迴，**必須記錄已訪問節點**（第 1 則實際撞到回路）
2. **題材橫向擴散** —— 經 `themes` 跳到題材，再由題材的 `segments` 擴散到非相鄰環節（第 2 則取得 `power` 的方式）
3. **共同下游的手足環節** —— 由 X 的下游 D 反查 `D.upstream`，取得與 X 並列供應同一客戶的環節（第 2 則取得 `pcb` 的唯一路徑）

第 3 種最容易被忽略。只實作第 1 種的話，第 2 則就會漏掉整個 PCB/CCL 族群。

---

## 整體驗收記錄（2026-10-07）

### 實際零組件定位與市場覆蓋

| 零組件 | 環節 | 台股角色 | 美股或無玩家標記 | 判讀邊界 |
|---|---|---|---|---|
| 冷板 | `thermal` | 雙鴻 `3324.TW`，液冷冷板 | Vertiv `VRT`，熱管理／CDU | 美股條目支持環節覆蓋，不表示 Vertiv 與冷板廠具有相同收入邊界；Boyd 另以非上市鍵列入冷板供應 |
| ABF 載板 | `substrate` | 欣興 `3037.TW`，載板 | `market_coverage.us: none` | 日本主導玩家與台廠並列，不能拿美國客戶或上游材料商填成美股載板廠 |
| switch ASIC | `networking` | 智邦 `2345.TW`，交換器系統 | 博通 `AVGO`，交換器 ASIC | 台廠的系統組裝與美廠的 ASIC 設計屬不同子角色；不能由環節覆蓋宣稱台廠製造同一晶片 |

三項皆能定位，且各環節清楚表態台股／美股。抽查讀取 frontmatter 的 `companies`、`role` 與 `market_coverage`，不依中文別名推測 ticker。

### 散文與結構一致性

逐檔複核「玩家格局」的公司皆在同檔 `companies`，並檢查傳導鏈與題材引用。核對上市身分後將辛耘改為 `3583.TW`、嘉晶改為 `3016.TW`；新光電氣工業下市後改用 `PRIVATE:shinko`。滑軌以川湖 `2059.TW` 的實際供應角色補入 `interconnect`，安費諾角色明列已有產品證據的液冷快接頭，其他公司的快接頭適配仍須逐案確認。

地圖只提供影響範圍與供應角色。`tier` 不等同精確市佔；沿關聯找到公司，不表示它已取得訂單或一定受惠。量產、平台 roadmap、客戶驗證及推論均於散文分開說明，指標未寫入當下股價、營收或滲透率數字。

### 三則既有新聞案例重跑

以「Schema 可查詢性實測記錄」的原始案例為輸入，僅讀 frontmatter 重走路徑，再對照散文判讀。此處驗收的是原記錄的環節與列名公司能否取得，不把測試標題當作查詢當下的新消息。

| 案例 | 重跑結果 | 散文的必要條件 |
|---|---|---|
| HBM4 供給與認證 | `memory → advanced-packaging → odm → datacenter → compute` 取得原記錄五個節點，回到封裝時由 visited set 停止；封裝三家、ODM 六家台廠均保留 | 傳統 DRAM 與儲存玩家仍進入影響範圍，但排擠、價格及受惠方向列為推論；送樣不能代替認證／量產 |
| 液冷與整櫃升級 | 上游取得 `interconnect`，經 `liquid-cooling` 取得 `power`，經共同下游 `odm.upstream` 取得 `pcb`；原列名公司皆可解析 | 沿上游遍歷不代表液冷系統出售連接器；需分辨供應方向與影響方向。PCB 升級須平台規格支持，滑軌與快接頭也不混用 |
| CoWoS 擴產與面板級 | 封裝六個上游仍為材料、設備、測試、載板、記憶體及運算；原材料／設備／載板／測試列名公司可取得，面板級訊號仍存在 | 公司角色、實際料號與訂單決定受惠；晶圓轉面板的研發／試產不等於量產，也不等於玻璃核心載板已替換所有載板 |

三條原推導結論與結構一致。新增的川湖是機構滑軌角色，擴充候選清單而不改變原路徑；新光下市及兩家台廠的上市後綴修正只改正識別，未更動原上下游邊。題材的受惠候選與狀態調整不會把尚未核實的訂單變成既定事實。

全量結構檢查通過；驗證器自身以合法基準的 full／skip-prose 兩種模式與 22 類失敗案例確認檢查行為。此結果不代表市佔、客戶歸屬或股價反應已驗證，這些仍依各檔來源與信心標籤查核。
