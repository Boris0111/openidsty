# platform-runtime Specification

## Purpose

提供可重現的本機開發及自架執行環境，讓產業資訊網站、資料庫與每小時資料流程能一致初始化、持續更新、保留資料並透過操作文件維護，而不影響同機其他專案。

## Requirements

### Requirement: 可重現啟動與持久化

系統 MUST 提供容器設定、環境變數範例、資料庫遷移與地圖初始化；停止／重啟服務 MUST 保留資料。公開 API MUST 為唯讀，資料庫與流程管理介面 MUST 預設只在本機或內部網路可達。

#### Scenario: 新環境與重啟
- **WHEN** 維護者依 README 啟動並重啟服務
- **THEN** 可開啟產業圖，資料庫保留既有事件，其他專案服務不受影響

### Requirement: 每小時排程獨立執行

資料流程 MUST 每小時嘗試更新，並獨立於公開 API worker 運作。重啟或重複觸發 MUST 不造成重複入庫；同一輪任務不得併發執行。

#### Scenario: API 重啟與排程
- **WHEN** API 服務重啟或增加 worker
- **THEN** 不額外建立排程，資料流程可繼續運作

### Requirement: 開發與維護操作可驗證

README MUST 提供前後端開發、容器啟動與停止、單次資料更新、測試、日誌、來源狀態、備份還原及公開部署步驟；專案 MUST 提供 dev server 啟動設定。

#### Scenario: 執行單次更新與備份
- **WHEN** 維護者依文件執行更新、備份與還原
- **THEN** 能查詢更新結果，且在獨立還原環境核對資料，不覆寫其他專案
