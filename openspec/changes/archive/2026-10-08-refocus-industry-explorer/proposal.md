# Proposal

## Why

現有網站研究內容被折疊、事件多為例行財報，公司完整模板有大量缺口。改以產業研究為入口，讓全部環節與題材都能閱讀、連到內容直接相關的事件並追溯證據。

## What Changes

- 完整保留 Markdown 研究、題材狀態查核日與預期里程碑。
- 接入科技新報四個分類、Semiconductor Engineering、TPCA、經濟部工業生產、Census M3、EIA Electricity Monthly；來源統一宣告、每小時更新、首次回補可取得的近 90 日。
- 建立全部環節與題材中英文規則分類，保存命中詞、摘錄、版本；公司提及、直接事件、背景統計及 inference 分開。
- 新增題材、整合搜尋、事件篩選及覆蓋 API／頁面，修正發布日、出表日、活動日與取得日語意。
- 桌機完整圖＋閱讀側欄，手機清單＋局部圖；URL 選取、返回、分享、鍵盤與快速點選一致。
- **BREAKING** 移除公司頁財報／企業關係圖展示與比較操作，改為輕量定位及事件。舊 compare URL 導回探索並說明入口調整；資料與既有 API 保留。

## Capabilities

### New Capabilities
- `data-coverage`: 全環節／題材研究、來源與近 30／90 日直接事件覆蓋及缺口。

### Modified Capabilities
- `industry-explorer`: 研究優先、題材導覽、互動與手機可讀性，移除公司比較。
- `company-research`: 公司輕量頁，保留財報／關係資料與 API。
- `official-information-ingestion`: 產業媒體、背景統計、內容分類、日期語意、回補與去重。
- `information-sources`: 穩定來源 ID、擷取設定及獨立健康狀態。
- `industry-map`: 題材全文與查核日期投影。

## Impact

影響 backend models、Alembic additive migration、connectors／Prefect 流程、唯讀 API、Next.js／Cytoscape.js、來源註冊表與結構驗證器、測試與操作文件。不新增行情、帳號、AI 判讀、付費來源或新技術棧。不改已有產業邊界。
