# 台灣官方財務摘要 adapter

`backend/app/financial_tw.py` 解析 TWSE／TPEx 公開 JSON／CSV；到期排程與單次更新見 [來源更新](research-source-updates.md)。樣本僅供隔離測試，不自動修改研究主張。

## 實際提供範圍

| 資料集 | 可取值／衍生 | 期間與限制 |
|---|---|---|
| 月營收 `t187ap05` | 當月及去年同月營收、來源年增；必要時由兩筆營收衍生年增 | 月份明列；不把累計月營收當成財報營收 |
| 一般業損益 `t187ap06_*_ci` | 營收、毛利、營業利益、歸屬母公司淨利、總淨利、基本 EPS；同報表衍生毛利率 | Q1–Q3 為截至該季的年度累計，Q4 為年度；不以 EPS 相減取得單季 |
| 一般業資產負債 `t187ap07_*_ci` | 負債總計 | 期末餘額；不是有息負債，不由總資產／負債倒推現金 |

這些入口未提供 CFO、capex、現金及約當現金、稀釋 EPS。金融業專用報表及全市場完整歷史不在此一般業摘要能力內；未提供項目由官方文件核對補錄或顯示缺口。各 metric 的程式能力可由 `capabilities(kind)` 查詢，預設每日到期，背景服務運行時才會擷取。

金額欄位以 Decimal 由新台幣千元轉為元，保留原值與 1000 倍率；EPS 已為元／股，倍率為 1。原始年增可能超過 Numeric(38,10) 可保存的小數精度，完整原始列仍保存為證據，canonical 值改用同列兩筆營收的可追溯公式，不能偷偷捨入後冒充官方原值。零與空白／缺值分開，缺少母公司淨利時不能以總淨利替代。

## 日期、範圍及公司識別

- `出表日期`／`Date` 是提供者彙整日期，存 `source_as_of`，`filed_at` 保持 null；不以擷取時間製造申報日。來源族為 `tw-mops-summary`，與正式申報文件分開排序；新彙整日同值只增加 provenance／日期 metadata，不新增數值 revision。
- 季度摘要只列年度、季別。呼叫端須提供已核對的 `fiscal_year_end=(12,31)` 才能建立實際季度起迄；未知或非曆年結算者保留原列及 `calendar-unverified`，不猜 1 月起算。月資料有明列年月，不需要猜財年。
- 摘要未明列合併／個體旗標；預設 `issuer-summary-unspecified`，不把「綜合損益表」誤認為「合併報表」。股別未明列時 EPS 保留 `unspecified`。這些值不能在比較介面宣稱已核對為相同會計範圍。
- TWSE 使用中文欄位；TPEx 損益使用 `Year`／`Season`、資產負債仍用中文年度／季別，公司代號使用 `SecuritiesCompanyCode`。NFKC 正規化處理全半形括號，別名衝突拒絕，不任選一欄。
- `issuer` mapping 由正式 release 公司識別提供，不能把名字相似者合併。上市／上櫃依官方入口的公司代碼辨識，不以舊 `.TW` 後綴決定。此次真實樣本證實 3324 在 TPEx；舊公司 listing 的 exchange 待 task 8.2 一併核對，尚未改寫發布研究。

## 官方查核及 fixtures

2026-10-17（台北）實際取得六個入口 HTTP 200，選取上市台積電 2330、上櫃雙鴻 3324 原始列。測試 fixtures 保留原始 JSON object 文字；`backend/tests/fixtures/official-tw-20261017/provenance.json` 記錄 URL、UTC 擷取時間、完整回應與選取檔的 SHA-256、筆數及大小。完整下載放在忽略的 `.work/tw-financial-official/`，測試資料只進獨立 `industry_research_test` 並回滾。

來源與欄位定義：[TWSE OpenAPI](https://openapi.twse.com.tw/v1/swagger.json)、[TPEx OpenAPI](https://www.tpex.org.tw/openapi/swagger.json)。金額單位另實讀 [MOPS 月營收表](https://mopsov.twse.com.tw/nas/t21/sii/t21sc03_115_9_0.html) 的「千元」表頭；以官方 [MOPS 損益查詢](https://mopsov.twse.com.tw/mops/web/ajax_t163sb04)、[資產負債查詢](https://mopsov.twse.com.tw/mops/web/ajax_t163sb05) 的唯讀查詢（TYPEK=sii、year=115、season=02），核對新台幣仟元及截至該季累計的表頭。實際 HTML 回應保存在上述忽略目錄，不依 JavaScript 空外殼判定可讀。

API 通常提供目前彙整期，不能宣稱可重建任意歷史；本機自後續成功擷取累積歷史。未來相同提供者日期卻不同值須核對，來源失敗不得刪有效資料。兩筆負債來源使用 `tw / balance` 接入新流程，不送入舊損益投影；同一回應不重複下載。

## 驗證

原生解析：`python -m pytest -q backend/tests/test_financial_tw.py -k 'not storage'`。真實 PostgreSQL：`python scripts/research_lab.py pg-check --suite financial-core`，涵蓋實際上市／上櫃樣本、欄位別名、千元與 EPS、淨利口徑、CSV、缺值／零、空外殼、格式變更、未知財年、原始精度、同值新快照與晚到歷史。測試通過不等於每家公司財年、合併範圍或產品收入都已查核。
