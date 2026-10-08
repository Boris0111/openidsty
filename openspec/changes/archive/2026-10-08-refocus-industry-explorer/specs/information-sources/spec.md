## MODIFIED Requirements

### Requirement: 來源以單一結構化註冊表宣告
所有資訊來源 MUST 宣告於單一結構化註冊表中，依市場與資料類型分組。每個條目 MUST 包含穩定唯一 ID、名稱、位址與資料類型；自動來源 MUST 有擷取設定與範圍。註冊資訊、人工網頁可讀性及實際擷取健康 MUST 分開，消費端可直接列舉而無需解析散文。

#### Scenario: 列舉特定市場的特定資料類型
- **WHEN** 消費端要求台股的公開申報類來源
- **THEN** 取得該分組下的所有來源條目，每筆含穩定 ID、名稱與位址

#### Scenario: 來源條目缺少必填欄位
- **WHEN** 某來源缺少 ID、名稱、位址、類型或自動設定格式錯誤
- **THEN** 結構驗證失敗並指出該條目

## ADDED Requirements

### Requirement: 來源覆蓋全部環節與題材
每個環節及題材 MUST 至少有一個免費自動來源設定，涵蓋科技新報半導體／零組件／伺服器／能源、Semiconductor Engineering RSS、TPCA 公開消息及經濟部／Census M3／EIA 電力月報；設定範圍 MUST 不代表實際已取得直接事件。

#### Scenario: 來源存在但擷取失敗
- **WHEN** 自動來源設定可解析但實際 HTTP 失敗
- **THEN** 保留來源設定並顯示 failed，不以 reachability 的 verified 取代 runtime 狀態
