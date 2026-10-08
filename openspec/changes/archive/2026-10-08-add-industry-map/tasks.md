# Tasks

## 1. 規範與驗證基礎

- [x] 1.1 建立 `industry-map/README.md`，定義 frontmatter 必填欄位、代號格式（`.TW` / `.TWO` / 純字母 / `.KS` / `.T` / `.HK` / `PRIVATE:`）、固定散文段落標題、題材狀態列舉值、環節切分的裁決規則（可彼此替換的供應角色），並明示圖可能含回路、遍歷須記錄已訪問節點。驗證：僅依此文件（不參考既有檔案）寫出一個新環節檔並通過 1.3 的驗證器
- [x] 1.2 建立 `requirements.txt` 記錄 PyYAML 依賴。驗證：`pip install -r requirements.txt` 成功結束
- [x] 1.3 實作 `scripts/validate_map.py`，檢查必填欄位、環節識別碼唯一性、上下游與題材引用可解析、上下游雙向一致、代號格式、題材狀態列舉值、散文段落齊備；提供 `--skip-prose` 旗標供骨架階段使用。驗證：對 `tests/fixtures/` 下每一類刻意錯誤的檔案各跑一次，確認每類都失敗且訊息指出檔案路徑與具體欄位
- [x] 1.4 建立 `tests/fixtures/`，每一類驗證規則各一個失敗案例與一個合法案例。驗證：合法案例全部通過、失敗案例全部被攔下，無漏網

## 2. 地圖骨架（僅 frontmatter，不寫散文）

此組先把整張關係圖建起來並驗證參照完整性，再投入散文。關係圖是本次最高風險的部分，必須先驗。

- [x] 2.1 建立 11 個 AI 伺服器環節檔的 frontmatter：`compute`、`memory`、`advanced-packaging`、`substrate`、`pcb`、`networking`、`odm`、`thermal`、`power`、`interconnect`、`datacenter`，含公司清單（台股、美股，以及該環節若由韓日等市場主導則一併列入）與上下游關係。驗證：`validate_map.py --skip-prose` 通過
- [x] 2.2 建立 6 個半導體環節檔的 frontmatter：`foundry`、`equipment`、`materials`、`eda-ip`、`test`、`power-discrete`，並接上與 AI 伺服器環節的上下游關係。驗證：`validate_map.py --skip-prose` 通過，且無跨層孤島環節
- [x] 2.3 建立 7 個題材檔的 frontmatter：`cpo-silicon-photonics`、`hbm4`、`liquid-cooling`、`800vdc`、`custom-asic-vs-gpu`、`advanced-node-2nm`、`power-bottleneck`，含狀態、涵蓋環節、受惠公司與里程碑。驗證：`validate_map.py --skip-prose` 通過，題材與環節雙向一致
- [x] 2.4 補齊每個環節的市場覆蓋表態：確認台股與美股各自有主要玩家，或明確標記該市場無實質玩家。驗證：驗證器檢出零個留空的市場欄位

## 3. Schema 可查詢性實測（進入散文前的關卡）

- [x] 3.1 取 3 則真實近期新聞（分屬不同環節，至少一則為上游美系或韓系廠商消息），**手動**沿 frontmatter 的上下游推導受影響環節與公司，逐則記錄推導路徑於 `industry-map/README.md` 的實測章節。驗證：三則都能推導出下游受影響的台廠，且推導過程只讀地圖檔案
- [x] 3.2 若 3.1 有任一則走不通，修正 frontmatter 欄位設計並回頭更新 `README.md` 與驗證器，然後重跑 3.1。驗證：三則全部走通後才進入第 4 組；不得以「散文補足」繞過結構缺陷

## 4. AI 伺服器散文：上游（運算、記憶體、先進封裝）

- [x] 4.1 填寫 `compute.md` 六個段落（環節定義、技術變數、玩家格局、傳導鏈、監測指標、風險），涵蓋 GPU 與自研 ASIC 兩條路線的分歧。驗證：`validate_map.py`（不帶旗標）通過
- [x] 4.2 填寫 `memory.md`，交代 HBM 與傳統記憶體兩塊、韓廠主導格局與台廠位置。驗證：驗證器通過，傳導鏈段落明確指出對下游哪些環節的影響路徑
- [x] 4.3 填寫 `advanced-packaging.md`，涵蓋 CoWoS 與 OSAT 分工。驗證：驗證器通過
- [x] 4.4 跑全量驗證並以本組三檔抽查散文與 frontmatter 的一致性（玩家格局提到的公司都在公司清單中）。驗證：驗證器通過且抽查無不一致

## 5. AI 伺服器散文：載板、電路板、網通、系統

- [x] 5.1 填寫 `substrate.md`（ABF 載板，含日廠與台廠對照）。驗證：驗證器通過
- [x] 5.2 填寫 `pcb.md`（CCL 與高多層板）。驗證：驗證器通過
- [x] 5.3 填寫 `networking.md`（switch ASIC、光通訊模組、CPO 路線）。驗證：驗證器通過
- [x] 5.4 填寫 `odm.md`（系統組裝與機櫃整合）。驗證：驗證器通過，且傳導鏈段落能接上第 4 組的上游環節
- [x] 5.5 跑全量驗證並抽查本組四檔的散文與公司清單一致性。驗證：驗證器通過且抽查無不一致

## 6. AI 伺服器散文：熱、電、連接、資料中心

- [x] 6.1 填寫 `thermal.md`（氣冷與液冷，含滲透率作為監測指標）。驗證：驗證器通過
- [x] 6.2 填寫 `power.md`（電源、BBU、800VDC 架構轉換）。驗證：驗證器通過
- [x] 6.3 填寫 `interconnect.md`（連接器、線材、rail）。驗證：驗證器通過
- [x] 6.4 填寫 `datacenter.md`（hyperscaler 資本支出與電力瓶頸作為需求源頭）。驗證：驗證器通過，傳導鏈段落說明資本支出如何回頭驅動運算環節（含回路）
- [x] 6.5 跑全量驗證並抽查本組四檔一致性。驗證：驗證器通過且抽查無不一致

## 7. 半導體散文

- [x] 7.1 填寫 `foundry.md` 與 `equipment.md`。驗證：驗證器通過
- [x] 7.2 填寫 `materials.md` 與 `test.md`。驗證：驗證器通過
- [x] 7.3 填寫 `eda-ip.md` 與 `power-discrete.md`，其中 `eda-ip` 的玩家格局需說明台廠是以矽智財授權參與（力旺、M31），EDA 工具本身無台廠，而客製 ASIC 設計服務業者（創意、世芯）依可替換性規則歸於 `compute`。驗證：驗證器通過。`market_coverage` 的 `none` 標記由 `datacenter.tw` 與 `substrate.us` 兩處驗證
- [x] 7.4 跑全量驗證並抽查本組六檔一致性。驗證：驗證器通過且抽查無不一致

## 8. 題材散文與里程碑

- [x] 8.1 填寫 7 個題材檔的說明與里程碑，每個里程碑需載明用以確認該事件的證據（而非僅陳述事件）。驗證：驗證器通過，每個題材至少一個里程碑帶證據欄位
- [x] 8.2 校準每個題材的生命週期狀態，並在檔案中寫明判定該狀態的依據。驗證：七個狀態值皆在列舉內，且各有書面依據

## 9. 來源註冊表

- [x] 9.1 建立 `industry-map/sources.yaml`，依市場（台／美）與資料類型（公開申報、法說會、產業媒體、官方統計）分組，沿用 `industry-quick-research` 已列出的來源作為基礎。驗證：驗證器通過註冊表結構檢查
- [x] 9.2 逐筆以唯讀方式確認可達性，標記已驗證或未驗證並記錄查核日期；確認無任何需付費或需 API key 的來源混入。驗證：每筆都有可達性狀態與日期，且人工複核零筆付費來源
- [x] 9.3 為涵蓋特定環節的來源補上環節關聯。驗證：驗證器確認所有環節引用可解析
- [x] 9.4 在 `industry-map/README.md` 補上來源註冊表的欄位規範與新增來源的流程。驗證：僅依文件可新增一筆通過驗證的來源

## 10. 整合驗收

- [x] 10.1 跑全量 `python scripts/validate_map.py`（不帶旗標）。驗證：17 個環節檔、7 個題材檔、來源註冊表全部通過，零未解析引用、零單向關係
- [x] 10.2 覆蓋度抽查：任選 3 個 AI 伺服器實際零組件（例如冷板、ABF 載板、switch ASIC），確認各能定位到對應環節且該環節列有至少一家台廠與一家美廠（或明確的無玩家標記）。驗證：三項皆可定位
- [x] 10.3 重跑第 3 組的三則新聞推導，確認加入散文後結論未與 frontmatter 衝突。驗證：三則推導結果與第 3 組記錄一致
- [x] 10.4 跑 `openspec validate "add-industry-map" --type change --strict` 與 `openspec status --change add-industry-map`。驗證：validate 回報 valid、status 顯示規劃與實作皆完成
