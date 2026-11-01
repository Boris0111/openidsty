# Proposal

## Why

`separate-research-production-deployment` 的 code review 留下兩個範圍外的缺口，修正過程中又找到一個：

- **備份救不回 Prefect**（code review #12）：
  - 每日與部署前備份只傾印 `industry_research` 與角色（`scripts/research_lab.py` 的 `backup()`），不含同一個 cluster 裡 Prefect server 自己的 `prefect` 資料庫（`docker/research-init.sql` 建立）。
  - Prefect 版本不同時，`rollback` 的拒絕訊息叫維護者「restore a backup instead」，但沒有任何備份含 `prefect` 資料庫，這條路走不通。
  - 部署若升級了 Prefect，它的部署前備份沒有標為回退邊界，30 天後會被清理，屆時連舊的 `industry_research` 狀態也一起失去。
- **原服務互斥檢查有漏洞**（code review #14）：
  - `deploy`、`start`、`reader-start` 會先檢查原服務（project `industryflow`）是否在運行、共用 port 是否被占用；`scheduler-start` 與 `rollback` 沒有。
  - 原服務的 worker 同樣抓官方來源，兩邊同時運行會重複抓取，並爭奪 3010／8010／4201。這違反 `platform-runtime`「新舊開發環境相互隔離」的要求。
  - 這個漏洞早於前一個 change：`main` 文件中手動啟用排程的 compose 指令本來就不檢查。
- **`bootstrap` 會把 CRLF 編進研究內容**（修正時發現）：
  - `research_lab.py bootstrap` 的 `git archive` 沒有 `-c core.autocrlf=false`。
  - 部署目錄是 Windows 上的 clone（`core.autocrlf=true`），在那裡重跑時，編譯內容會帶 CRLF，與 managed Git 的 LF 內容雜湊不一致。
  - 映像建置（`build_images`）與演練的 `rebuild-check` 都已改用 `autocrlf=false`，只剩這一處。

這些都要等前一個 change merge 並完成正式環境切換後才能實作與驗證：`scheduler-start`、`rollback` 與部署目錄都是它引入的。

## What Changes

- **備份納入 `prefect` 資料庫**：
  - 每日與部署前備份另外以 `pg_dump -Fc` 傾印 `prefect` 資料庫為 `prefect.dump`，與其他檔案一樣記錄 SHA-256 並複製到第二份副本。
  - manifest 增加 `prefect` 欄位：Prefect 自己的遷移版本，以及 deployments、work pools、flow runs 的筆數。欄位只增不改；較舊的 manifest 沒有它。
- **Prefect 升版的部署前備份是回退邊界**：
  - 目標的 Prefect 版本與運行中的不同時，部署前備份標記 `rollback_boundary`，30 天清理不刪除它（與收縮遷移相同）。
  - 部署紀錄記下這是 Prefect 邊界。
  - `rollback` 因 Prefect 版本不同而拒絕時，訊息改為指出這份邊界備份，以及同時還原 `industry_research` 與 `prefect` 的事故程序。
- **演練還原並核對 `prefect` 資料庫**：
  - `research_drill.py restore` 遇到含 `prefect.dump` 的備份時，在演練 cluster 建立 `prefect` 資料庫並還原，核對遷移版本與筆數。
  - 舊備份沒有這個檔案時略過，報告註明。
  - 演練仍不啟動 Prefect server。
- **互斥檢查補齊**：`scheduler-start` 與 `rollback` 在改變任何狀態前執行原服務互斥檢查，與 `deploy`、`start` 相同。`restore`（從原服務匯入）刻意不檢查，因為它的來源就是運行中的原服務資料庫。
- **`bootstrap` 只用版本控制內容**：`git archive` 加上 `-c core.autocrlf=false`。
- **文件**：
  - `docs/research-backup.md`：檔案表與 manifest 欄位、事故時還原 `prefect` 的程序。
  - `docs/research-deployment.md`：Prefect 邊界、回退訊息、互斥檢查。
  - `docs/research-lab.md`：`scheduler-start` 的互斥檢查。
- **不在範圍內**：
  - 正式 Prefect 中卡住的 run：`research-publication-reconciliation/minute` 有一筆自 2026-10-21 停在 PENDING／Submitting，這個 deployment 最後一次完成在 2026-10-22。這是維運狀態，不是程式缺陷，清理方式由 Boris 決定；本 change 只在 design 記錄它與部署的關係。
  - 演練啟動 Prefect server 或排程。
  - 異地備份。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `platform-runtime`：
  - 「故障可恢復且不偽裝新鮮度」：定期備份涵蓋排程元件自己的資料庫，並在獨立環境核對還原；排程元件升版前的備份保留為回退邊界。
  - 「新舊開發環境相互隔離」：互斥檢查涵蓋所有會啟動或替換正式服務的操作，包括啟用排程與回退。

## Impact

- **維運腳本**：
  - `scripts/research_lab.py`：`backup()`、`deploy_target()` 的邊界判斷、`rollback_refusals()` 的訊息、`scheduler-start` 與 `rollback` 的互斥檢查、`bootstrap` 的 archive。
  - `scripts/research_drill.py`：`restore()` 還原並核對 `prefect`。
- **測試**：root `tests/` 的備份、部署、回退、互斥與演練測試。
- **文件**：`docs/research-backup.md`、`research-deployment.md`、`research-lab.md`。
- **資料**：備份資料夾多一個 `prefect.dump`。現有 flow run 歷史規模下約數 MB，每份備份的耗時會增加，實際數字在驗證時量測。
- **依賴**：
  - 需先 merge 並完成 `separate-research-production-deployment` 的正式環境切換。
  - 本 change 只修改主 spec 中既有的 requirement，但程式建立在該 change 的部署紀錄、`scheduler-start` 與 `rollback` 之上，所以要在它 archive 之後才 archive。
  - 不新增套件。
