# 財務、事件、觀察與公司比較 API

所有入口使用 `/api/v2`、reader role 及 published release 檢查，回 `{release_id,schema_version,data}`。動態 `data.as_of` 是這次讀取時間，不是申報日或研究日期；未指定 release 時為 `no-store`；固定研究 release 時採 ETag 與最多 30 秒快取，304 保留原 `as_of`，詳見 [版本與快取](research-reading-cache.md)。指定研究 release 只固定公司身分與研究內容，不會將財務／事件凍結於當時，也不會在讀取時擷取外部網站。

## 財務與來源

`GET /companies/{company_id}/financials` 接受 `metric`、`basis`（monthly／quarterly／ytd／annual／instant）、`currency`、`source_family`、`scope`、`period_from`／`period_to`、`limit`（50／上限 100）、`cursor` 及 `release_id`。

每個來源／指標／口徑／範圍／原幣／股別的 SQL 窗口最多 8 季、8 個累計期、8 個期末、3 年或 36 月，再按期末日期篩選及分頁。改日期條件不會擴大這個最近窗口。相同來源及原期間有合併值時預設採合併；沒有時保留原範圍，不把未知變成合併。可指定 `scope`，或 `all_scopes=true` 檢閱其他範圍。不同來源保持各自曲線，`preferred_source_family` 取自已核對的公司設定，沒有設定就明示缺口。

每筆包含精確十進位字串 `value`、原始起迄、basis、scope、currency、share_class、來源族、數值 revision、provenance_kind、限制及來源。`sources` 最多 20 筆，保留原始數值／單位／倍率、申報 accession／tag、申報日或提供者彙整日、文件 URL 與可取得定位；超過明示 `sources_truncated`。完整 raw payload、owner 的操作理由與診斷不提供讀者。

衍生值附 `formula_version`、公式與依序輸入的觀測 ID／數值／期間／口徑及可到達連結。每筆最多兩個公式輸入，進一步沿各輸入連結查核，避免一次遞迴載入全部歷史。基本 EPS／稀釋 EPS 與母公司淨利／總淨利是不同指標，API 不做替代或新衍生。

`GET /companies/{company_id}/financials/observations/{observation_id}` 回指定值、真正最新有效值 ID，以及該群組的數值修訂，含 `supersedes`。修訂依加入序號列出，晚到舊申報不會變成 active；用 `before_revision` 及 `limit`（20／上限 100）續讀。相同值新申報只增加來源，不虛增 revision。單筆入口可查窗口外已知的舊觀測，仍要求公司存在於指定 published release。

例如，若年度營收原申報 100，後續改為 110，再抓到更早的 90，預設仍顯示 110；修訂清單可同時追到 100、110、90。這是合成範例，不是 application DB 的實際數字。

## 公司比較

`GET /compare?company_ids=company-auras,company-vertiv&basis=annual` 接受 2–4 家不同公司；basis 為 annual（預設）／quarterly／ytd／monthly。期末餘額獨立用 instant，不把累計現金流當單季。回公司角色、產品、商業模式、風險、主張／來源與已知缺口，以及各 metric 的原值與 `comparable`／`reasons`。

比較採各公司已核對主要來源的最近實際期間；未設定主要來源仍可檢閱原值，但不宣稱可直接排名。缺少主要來源的某欄不從另一份報表拼入。合併範圍優先；同期間仍有多個候選時不任選，最多列每公司兩個候選並明示截斷。淨利與 EPS 的不同種類各自檢查。

| 情境（假設已核對來源及合併範圍） | 結果 |
|---|---|
| 兩家公司均 USD、2025-01-01 至 2025-12-31 年度營收 | 可比較，原值仍各附來源；不產生額外排名 |
| 同期間毛利率，一家 TWD、一家 USD | 可比較百分點；不對金額換匯 |
| 一家 TWD、一家 USD 營收／EPS | 不可直接比較金額，保留原幣 |
| 2025-10-01 至 12-31，對 2025-11-01 至 2026-01-31 | 不可當同一季，明列實際期間不同 |
| 普通股基本 EPS 對 ADR 基本 EPS | 不可直接比較；不換算 ADR 比例 |
| 公司 A 只有基本 EPS，公司 B 只有稀釋 EPS | 各欄顯示缺值，不把兩者合併成 EPS 排名 |
| 只有累計 CFO，沒有相容前期 | 列原累計，沒有偽造單季值 |

## 事件與獨立觀察

`GET /events` 提供 official／report；`GET /observations` 只提供 rumor。可依 `entity_id`、`source_id`、`source_nature`、`relevance`（direct／background／mention）、`period_from`／`period_to`、`include_unknown`、`limit`／`cursor` 與 `release_id` 篩選。向 events 要求 rumor 或向 observations 要求 official／report 回 422，避免默默混入。

只讀取連到該 published release 物件的 published 事件，不讓 private research 身分透過事件浮現。依真正 published_at／reported_at 排序，沒有日期者排在後面並回 null／`date_unknown=true`；不以 fetched_at 補成發布日。`include_unknown` 預設 true，即使有日期篩選仍保留明示未知項；若只要期間內確切事件，指定 false。來源名稱優先取指定 release 的已保存名稱。回必要摘要與外部 URL，不回 raw、抓取診斷或管理狀態。

每事件最多 100 個相關物件；截斷明示。來源性質和 direct／mention／background 不互相替代：官方發布中的公司提及仍是 mention；匿名供應消息即使指向公司，仍只在觀察入口，不會成為正式供應圖。

既有事件可用 writer CLI `python -m app.source_links` 重新對應穩定 ID；每批最多 500，單次最多 100000，超過回 partial／last_id，以 `--after <last_id>` 續跑。重跑不新增事件、不改研究、不抓網站；新版 initializer 會執行這個索引維護，首次尚無研究 head 時略過。若發布後增加 legacy mapping，重跑此命令即可將既有事件對應到新版身分。未知／歧義公司不按名稱猜測。

## 驗證及界線

`python scripts/research_lab.py pg-check --suite research-dynamic` 使用真實 reader role 測精度、重編、lineage、視窗與分頁、異幣／財季／範圍／EPS、缺值、觀察分流與未發布拒絕。引用經 `0015` 的 curated view 提供，reader 仍不能 SELECT raw facts payload。既有事件索引另由 `source-updates` suite 驗證。

此 API 完成資料契約；公司財年／主要申報來源與全批深研仍須逐公司附證據核對。舊財務 Float 表不會冒充精確 canonical 觀測；新入口沒有值時保留缺口，舊版入口仍可讀原契約。圖表與比較操作畫面由 task 6.3 接續。
