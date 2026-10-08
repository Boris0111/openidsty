# 產業研究投影與分類

研究內容仍以 `industry-map/` Markdown 為唯一來源。匯入完整環節／題材散文，題材 `checked` 從原文「查核日期」擷取，匯入日不能改寫原查核基準。`milestones` 為預期查核點，與自動事件不同。

規則在 `data/classification-rules.yaml`，涵蓋全部環節／題材。規則匹配正文技術詞與需要的語境；ASCII token 有邊界，中文別名由公司 aliases 獨立處理。修改規則時更新 version，執行後端 fixtures tests，再 `python -m app.ingest --reclassify` 重新投影既有事件。證據存於 event_segments／event_themes，提供 term、matched、excerpt，API 明示 direct／background；財報及法說例行資訊不作 direct。

initialize 使用 `--reclassify --only-stale`，只處理未分類或規則版本過期的事件；手動 `--reclassify` 仍可全量重分類。兩者均使用擷取 advisory lock，並保留原 fetched_at，避免把純分類處理記成取得來源內容。

背景統計依資料集、期間及原口徑入庫，不代表特定公司、純 AI 需求或題材收入。Census 最新全文發布頁與歷史先行報告索引口徑不同，identity 按 dataset＋period 區分；索引無發布日與數值，保留 unknown。EIA 只在取得實際月份時建立事件，不用取得日當發布日。

覆蓋 `/api/coverage` 為所有環節及題材計算近 30／90 日直接事件：發布日可確認、已發布、非例行且 direct。background、unknown_date、routine 與公司提及分開。`/api/coverage/report` 下載 Markdown 矩陣，保留來源狀態、限制及真實樣本。
