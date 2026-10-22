# Spec Delta

## ADDED Requirements

### Requirement: 排程在重啟後自動恢復

正式研究服務的排程中樞與執行 worker MUST 與資料庫、API、網站採用相同的自動重啟策略：Docker 或主機重啟後，已啟用的排程 MUST 自動恢復，不需要維護者重新手動啟動。一次性的部署設定服務 MUST NOT 自動重複執行。被維護者手動停止的服務（包括原服務）MUST 在重啟後維持停止，不得因自動恢復而與研究服務同時占用共用 port。服務設定檢查 MUST 拒絕缺少自動重啟策略的常駐排程服務。

#### Scenario: 主機重開機後排程自動恢復
- **WHEN** 排程已啟用的研究服務所在主機重開機，Docker 重新啟動
- **THEN** 排程中樞與 worker 自動回到運行狀態，下一個每小時時段照常執行，不必重新以排程 profile 啟動

#### Scenario: 排程中樞比 worker 晚就緒
- **WHEN** 重啟時 worker 先啟動，排程中樞或資料庫尚未就緒，導致 worker 結束
- **THEN** worker 依重啟策略重試，直到連上排程中樞；部署設定服務不重複執行，也不建立重複排程

#### Scenario: 原服務維持停止
- **WHEN** 原服務在切換時已被手動停止，之後主機重開機
- **THEN** 原服務維持停止，研究服務的共用 port 不發生衝突

#### Scenario: 設定缺少重啟策略
- **WHEN** 研究服務設定中的排程中樞或 worker 未設定自動重啟策略
- **THEN** 服務設定檢查失敗並指出該服務，不啟動研究服務

### Requirement: 自動檢查與 runtime 一致

自動檢查 MUST 使用與 runtime image 相同的鎖定 Python 依賴版本，不得在檢查時解析出不同的間接依賴。測試 fixtures 在任何平台 checkout 後 MUST 與版本控制中的位元組內容一致，不得因換行轉換改變內容或雜湊。版本控制中的 runtime 與維運腳本測試 MUST 納入自動檢查；需要 Docker、真實資料庫或外部來源的檢查仍與自動檢查分開。

#### Scenario: Windows checkout 執行雜湊測試
- **WHEN** 在預設會轉換換行的 Windows checkout 執行依賴 fixture 雜湊的離線測試
- **THEN** fixture 位元組與版本控制內容相同，測試結果與 Linux checkout 一致

#### Scenario: 間接依賴發布新版
- **WHEN** 某個未直接鎖定的間接依賴在套件庫發布新版
- **THEN** 自動檢查仍安裝 runtime 使用的版本，不因新版而產生與 runtime 不同的結果

#### Scenario: 維運腳本測試
- **WHEN** 有人修改研究服務的啟動、互斥或設定檢查腳本
- **THEN** 自動檢查執行對應的測試，不需要 Docker 也能驗證設定規則
