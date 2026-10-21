## MODIFIED Requirements

### Requirement: 新舊開發環境相互隔離

正式研究服務 MUST 使用獨立的容器 project、image、network、資料庫、volumes 與執行憑證，並占用原服務的讀者 origin（web `127.0.0.1:3010`、API `127.0.0.1:8010`、Prefect `127.0.0.1:4201`）；原服務 MUST 保留可回復的 image 與資料，但 MUST NOT 與正式研究服務同時運行。啟動正式研究服務前，操作 MUST 確認原服務沒有任何容器在運行、目標 port 未被占用，否則拒絕並說明原因，不得自動停止或刪除原服務。還原演練環境 MUST 使用自己的 project 與 port，不得占用正式 port。還原／遷移只在明確指定的研究資料庫執行；Git 分支回退不得被視為已還原資料庫。

#### Scenario: 預覽新版並保留原服務
- **WHEN** 啟動、重建或停止正式研究服務或還原演練環境
- **THEN** 原服務的容器、image、資料與連線保持原狀

#### Scenario: 原服務仍在運行時啟動正式服務
- **WHEN** 原服務仍有容器在運行或 3010／8010／4201 被占用，並嘗試啟動正式研究服務
- **THEN** 操作拒絕並指出占用者，原服務的容器、image、資料與連線保持原狀

#### Scenario: 在原 origin 閱讀
- **WHEN** 讀者在切換後開啟 `http://127.0.0.1:3010` 的舊 ticker 深連結、舊題材網址或含 `#candidates` 的連結
- **THEN** 由正式研究服務回應並解析到對應頁面，`#candidates` 轉到「數據與追蹤」，同一 origin 的 v1 題材收藏只遷移一次且 v1 原值保留

#### Scenario: 回復原服務
- **WHEN** 停止正式研究服務並以原 image 啟動原服務
- **THEN** 原服務使用原資料回到 3010，正式研究服務的 volumes 保留，不執行 destructive downgrade
