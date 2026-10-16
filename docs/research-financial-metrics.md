# 財務指標、身分與修訂

此文件說明 task 5.1 的資料規則；adapter、官方補錄、查詢／比較與實際資料驗收由 tasks 5.2–5.6 接續，不代表所有公司已有完整財務。

## 指標與單位

`financial_core.METRICS` 定義營收、營收年增、毛利、毛利率、營業利益、歸屬母公司／股東淨利、淨利總額、基本／稀釋 EPS、CFO、capex、現金及約當現金、負債總額。毛利是計算毛利率的輔助指標；淨利主畫面使用歸屬母公司／股東，不能把總淨利改名混用。

| 單位 | 定義 |
|---|---|
| `amount` | 原幣金額；來源千元等倍率先明確換算，保留原值、raw unit 與 multiplier |
| `per-share` | 原幣／股；基本、稀釋與股別各自識別，不互換 ADR／普通股 |
| `percent` | 百分點；例如 33.3 表示 33.3%，不是 0.333 |

Capex 限購置不動產、廠房及設備的現金支出，正規化為正值；不把併購、租賃或資產變動混入，不直接對未知符號取絕對值。負債總額不叫作有息負債。現金及約當現金不默默加入受限制現金。

所有數值使用 `Decimal`／`Numeric(38,10)`，API 必須傳十進位字串，不經 Float。超出可保存精度、NaN／Infinity 或不明格式拒絕，不悄悄捨入官方原值。只有衍生公式以 50 位中間精度運算，再按 `ROUND_HALF_EVEN` 保存至 10 位小數。有效零與缺值分開。

## 兩層身分

Raw fact 身分為公司、來源族、accession、原始 tag 與 context hash。Context 包含實際起迄、原始單位、幣別、會計範圍、股別及維度；不把 canonical metric mapping 或猜測的季度標籤當成原始 context。Raw fact 保存原值、原始 payload、官方 URL、申報日與換算倍率。同一身分的原值／申報日期意外改變時要求核對，不改寫已保存 fact。

Canonical group 身分為公司、來源族、metric、原始期間、basis、scope、unit、currency、share_class；**不含 accession 或抓取時間**。Canonical semantic hash 僅使用 group 與精確值。新文件揭露同值，只追加來源關聯並推進支持該值的申報日期，不新增數值 revision。新申報把數字改回更早的值，仍建立新 revision，保留實際修訂鏈。

Revision 是寫入順序，不是假定的申報先後。晚取得的舊申報保留為歷史，預設以真正申報日排序、同日再按已確認 revision 選取；不能使用 `MAX(revision)` 代表最新有效資料。相同申報日或都未知日期卻出現不同值時，保留 raw facts，回 `needs-verification`；只有來源的更精確修訂證據或 owner 核對能指定被取代觀測，不以下載順序或 accession 字串猜時間。每筆 fact 原始申報日仍保留，觀測的 filed_at 表示目前最新支持申報，數值本身不更新覆寫。

## 來源與公式

公司必須有明確主要申報來源。相同主要來源的官方值優先，其次為同來源人工官方核對；其他來源保留，不把不同報表的零散欄位拼在一起。Legacy-import 與衍生值另標性質，不假裝官方原值。人工核對是 provenance_kind，來源族仍須指向真正的官方來源，而非任意改成另一家公司或資料集。

| 公式 `financial-v1` | 必要條件 |
|---|---|
| `gross-margin` | 同公司／來源／原幣／範圍／原始期間／申報的毛利÷正值營收×100 |
| `ytd-difference` | 可加總金額，同年度實際起點的累計差，結果為 70–110 天單季；年度減前三季可得跨曆年的 Q4 |
| `revenue-yoy` | 同口徑營收，前期為正值；單季須明確同財季及相鄰 fiscal year，月資料須同月份，實際期間也須能對齊 |

不同 accession 的累計不能自動假定相容；須核對重編／會計範圍後明列相容申報，否則保留原累計與缺口。EPS、比率、現金及負債等期末值一律不得相減。衍生結果保存公式版本與有序 input observation IDs；跨公司、來源、範圍、股別或幣別的輸入拒絕。沒有足夠資料就回 `FinancialGap`，不填零、不做換匯或猜財季。

SEC companyfacts 的 `fy`／`fp` 不能直接視為每筆 comparative fact 的原始財季；必須核對實際起迄。SEC 文件說明 companyfacts 聚合標準 taxonomy、整個申報主體的 facts，並提醒不同公司財務日曆與期間可不同。依據：[SEC API 範圍](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)。這不提供產品營收占比或具名客戶收入的保證。

## 操作與驗證

Initializer 執行 `python -m app.financial_store definitions`，只建立／核對定義，不填假數值。Migration `0011` 加入申報日期索引及原始 fact／group／數值不可改寫的 DB guards；metadata 的支持申報日期可推進，數值修正追加歷史。

原生計算測試：`python -m pytest -q backend/tests/test_financial_core.py`。真實 PostgreSQL：`python scripts/research_lab.py pg-check --suite financial-core`；檢查換算、零／缺值、同值新申報、重編、晚到歷史、同日歧義、lineage、不可改寫與 reader role 隔離。這是財務基礎測試，不是所有 adapter 或全站效能驗收。
