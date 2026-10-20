# 官方財務核對補錄

此功能處理免費摘要未提供的 CFO、capex、現金、歷史及其他已核對財務。Owner 先讀官方原文，再把數字整理為 JSON／CSV；系統不自動解析 PDF，不因來源是官方就推測產品收入或替你確認會計口徑。

## 操作

1. 開啟 `/admin` 並登入，在維護區選「財務補錄」。不需要建立研究草稿。
2. 選 JSON 或 CSV，下載空白範本；填入已發布公司 ID、已登錄官方申報／公司 IR 來源、文件 URL／標題／識別、日期、報表期間、原幣、會計範圍及每列定位。
3. 上傳或貼上內容（最多 1 MiB／100 列），按「驗證並預覽財務」。只保存私人預覽，尚未建立 raw facts／財務值。
4. 比對原始值、單位倍率、換算後值與既有值；點文件連結核對實際原文，勾選確認並填理由，再按「確認財務入庫」。只有此步驟成功才建立數值及稽核。
5. 回應中斷時保留原內容／理由並重試，沿用相同確認 key。預覽後其他流程已有數值修訂會回 409，須重新預覽；不要以換 key 繞過核對。

修改輸入或格式會清除畫面上的舊預覽，避免確認不同內容。失敗保留輸入。已確認批次與結果不可改寫；修正必須建立另一份有依據的補錄，不刪舊歷史。來源失效不影響已確認資料；這兩個 API 都不讀外網。

## 格式 `official-financial-import-v1`

JSON 最外層為 `{format, document, rows}`，只接受明列欄位。CSV 使用相同 row 欄位，document 欄位加 `document_` 前綴並在每列重複；一批只能引用同一文件。UTF-8（可有 BOM）／CP950 CSV 可解析；原始數值與倍率使用十進位字串，不能先轉 Float。

| 範圍 | 必填欄位與用途 |
|---|---|
| document | `source_id`、`source_family`、`source_url`、`title`、`accession`、`filed_at`；申報日未提供時明列 null，不以抓取時間代替 |
| document optional | `source_as_of` 保存提供者彙整日，與 filed_at 兩者不能同時使用；來源族的日期模式須一致 |
| row 身分 | `company_id`、`metric_id`、`period_start`、`period_end`、`basis`、`scope`、`unit`、`currency` |
| row 原值與定位 | `raw_value`、`raw_unit`、`multiplier`、`tag`、`locator`，定位需能找回頁碼／表格／報表列或 XBRL tag |
| row optional | `share_class`（EPS 必須明列股別或 unspecified）；`supersedes`、`revision_note`（同日修正指定觀測 UUID 與依據）；`normalization_note`（符號換算依據） |

金額千元可填 raw_unit 的原始文字、multiplier 為 `"1000"`；元為 `"1"`。EPS 不跟金額一起乘千元，期末現金與負債不可相減。Capex 定義為正值購置支出；原文以負號列支出時，只有明確提供符號核對說明才可用負倍率，不對未知值取絕對值。未知值不填 0。`instant` 的起迄應為相同期末；來源日期不能早於實際財務期間。

`source_family` 必須沿用真正來源族，例如 SEC 為 `sec`、MOPS 彙整摘要為 `tw-mops-summary`；正式 MOPS 文件與 issuer IR 各用明確來源族。人工核對性質存為 `manual-official`，不能藉任意改來源族來掩蓋同一期衝突。來源 URL 僅允許與已發布 registry 相同的官方主機（含登錄 ingestion/fallback、SEC 官方三主機），不自動下載 URL。

## API 與一致性

| 方法／路徑 | 行為 |
|---|---|
| POST `/api/admin/financial-imports` | `application/json`／`text/csv`，回 201、batch_id、payload_hash、預覽 items、原始送達內容 upload_sha256；payload_hash 綁定正規化輸入及當時數值基準 |
| GET `/api/admin/financial-imports/{batch_id}` | 讀取既有私人預覽或已確認結果 |
| POST `/api/admin/financial-imports/{batch_id}/confirm` | 必須附 Idempotency-Key，body 為 `{payload_hash, reason, confirmed_official_source:true}`；回儲存的原結果或 409／422 |

全部驗證 owner、CSRF／Origin，回 no-store；私人 reader gateway 不提供這些路徑。缺少來源、期間、幣別、定位、超精度、未知欄位或重複群組拒絕；不把來源格式錯誤當空成功。

確認在同一 DB 交易內檢查基準、保存 raw facts／值／結果／稽核。相同 key＋相同內容只完成一次；key 用於不同批次或理由不同回 409。整批有一列衝突即回滾，不讓前幾列偷偷入庫。自動 adapters 與人工確認先依相同群組排序取得鎖，避免手動核對與背景更新交錯。

同日／未知日期不同值，必須在預覽輸入附 `supersedes` 指定同一群組觀測及至少六字 `revision_note`，確認後才追加修訂；指定不相干公司／期間拒絕。同一原始 fact 身分若原值變動，仍拒絕覆寫，須核對文件版本。批次保存完整文件定位、payload hash、輸入、數值基準、確認人／時間、結果及理由稽核。upload_sha256 是送達 API 的內容 hash，不冒充外部官方 PDF 的 hash。

## 驗證範圍

`python scripts/research_lab.py pg-check --suite financial-imports` 執行財務解析／storage／補錄 API 的隔離 PostgreSQL 測試；不在 application DB 設定測試 owner 或數值。瀏覽器測試 `financial-imports.spec.ts` 的桌機／手機情境採合成 API 回應，真實 DB 行為由上述測試驗證。測試通過不代表每份 owner 匯入的會計內容已由程式自動查證。
