# Proposal

## Why

要掌握半導體／AI 伺服器產業動態，困難不在找不到消息，而在**單一消息的意義取決於它落在價值鏈的哪個位置、會往誰傳導**。「HBM4 提前量產」對記憶體廠、對散熱、對 ODM 是三件不同的事；缺少結構化的產業地圖，每次看到新聞都得從零重建上下文，也無法判斷一則消息該不該在意。

本次刻意先建地圖、而非先建消息流。消息流的價值完全取決於能否把事件對應到環節與公司，地圖是它的前置條件；順序顛倒的話，之後得整張重寫。

## What Changes

- 新增 `industry-map/`：每個價值鏈環節一個檔案，以 **YAML frontmatter 承載結構**（公司清單、上下游、題材、監測指標），Markdown 散文承載解釋。結構與解釋分離，讓後續自動化能遍歷地圖而不需資料庫。
- 覆蓋 **AI 伺服器 11 個環節**（運算、記憶體、先進封裝、載板、PCB、網通光通訊、ODM、散熱、電源、連接器線材、資料中心）與**半導體 6 個環節**（晶圓代工、設備、材料、EDA/IP、測試、功率與類比）。
- **台美並重**：台股與美股公司並列於同一環節檔，而非按市場分家 —— 判讀傳導鏈時需要同時看到上游美系大廠與下游台廠。
- 新增 `industry-map/themes/`：題材檔，含 `status` 生命週期（emerging／validating／scaling／mature／fading）與 `milestones`，作為題材追蹤的狀態基礎。
- 新增 `industry-map/sources.yaml`：免費公開資訊來源註冊表，依市場與資料類型分類。只收免費來源，不含付費 API。
- 新增 `scripts/validate_map.py`：驗證 frontmatter 結構完整性與上下游雙向一致性。
- 新增 `industry-map/README.md`：schema 與撰寫規範，作為維護時的唯一真實來源。

本次**不含**（留待後續 change）：任何抓取或排程程式、查詢用的 Claude Code skill、個股深度研究檔、dashboard 或任何 UI。

## Capabilities

### New Capabilities

- `industry-map`: 半導體與 AI 伺服器價值鏈的結構化、可遍歷地圖。擁有環節與題材的資料結構、覆蓋範圍、交叉引用一致性，以及「給定一個環節能推導出受影響的上下游與公司」這項可查詢性保證。
- `information-sources`: 免費公開資訊來源的註冊表。擁有來源如何被宣告、分類（市場／資料類型）與可達性標記。與 `industry-map` 分開，因為兩者變動驅動力不同 —— 地圖隨產業結構演進，來源表隨可取得性變動；後續的消息流會擴充這個能力而非擴充地圖。

### Modified Capabilities

無。專案目前尚無既有 spec（`openspec list --specs` 為空），兩個能力皆為新增。

## Impact

- **新增目錄**：`industry-map/`（含 `ai-server/`、`semiconductor/`、`themes/`）、`scripts/`
- **執行環境**：驗證器使用 Python 3 + PyYAML。本機已具備（Python 3.12.10、PyYAML 6.0.1），無需安裝；仍會以 `requirements.txt` 記錄以確保可重現。
- **無外部依賴**：不需 API key、無執行期服務、無資料庫、無排程。地圖為純文字檔，隨 git 版控。
- **後續依賴**：之後的消息流 change 會消費本次的 frontmatter schema 與 `sources.yaml`。schema 一旦被消費就具契約性質，因此本次需在交付前以真實新聞實測可查詢性（見 design.md）。
