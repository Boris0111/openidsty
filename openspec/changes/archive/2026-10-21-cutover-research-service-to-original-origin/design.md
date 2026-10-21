## Context

動機見 proposal.md。目前狀態（2026-10-21 實查）：

- `compose.research.yaml` 把 web／API／Prefect／reader 寫死綁在 `127.0.0.1:3014／8014／4204／3015`；`RESEARCH_ADMIN_ORIGINS` 與 `RESEARCH_ADMIN_HOSTS` 也寫死 3014／8014。
- `scripts/research_lab.py` 的 `PORTS` 與 `validate_config()` 要求 port 綁定完全等於上述值，`up` 只在沒有既有 api 容器時才探測 port。
- 原服務 `compose.yaml`（project `industryflow`）以 `${WEB_PORT:-3010}`、`${API_PORT:-8010}`、`${PREFECT_PORT:-4201}` 綁 port，另有 Caddy profile；所有容器已停止，image 與 volume 都保留。
- 讀者端已有 v1 題材收藏遷移（`frontend/lib/research-watchlist.tsx`，`v1_migrated` 旗標、v1 原值不刪），以及 `#candidates` 錨點（`frontend/app/themes/[id]/page.tsx`）；這些依瀏覽器 origin 運作，所以只有在 3010 上才會讀到讀者既有的 v1 資料。
- 還原演練 `compose.research-drill.yaml` 用 3016／8016，`frontend/tests/offline` 用 3011。

## Goals / Non-Goals

**Goals:**
- 正式研究服務在 3010／8010／4201 提供讀者與管理入口，管理入口的 allowlist 與實際 origin 一致。
- 工具層面保證正式服務與原服務不會同時搶同一組 port，回復路徑清楚。

**Non-Goals:**
- 不改 port 以外的應用程式行為（v1 遷移、舊連結相容沿用現有實作，只在新 origin 實測）。
- 不刪除原服務的 image、volume 或 `compose.yaml`；也不把 port 改成可由環境變數覆寫。
- 不處理 HTTPS／跨裝置（第 5 步）、scheduler 與資料補抓。

## Decisions

1. **直接沿用原服務的 port 組合：web 3010、API 8010、Prefect 4201。** 讀者書籤與 localStorage 綁定的是 web origin，所以 web 一定要 3010；API 與 Prefect 跟著原服務的慣例，文件和使用者習慣都不必再記一組。替代方案「web 3010 但 API 保留 8014」會讓 README 與原服務說明對不起來，因此不採用。
2. **reader gateway 維持 3015。** 原服務沒有對應的唯讀入口，3015 也沒有衝突；3011 已被離線 e2e 使用，不能拿來用。
3. **Port 繼續寫死在 compose 並由 `validate_config()` 精確核對，不改成 `${WEB_PORT}` 這類變數。** 研究服務的安全檢查依賴「綁定值完全可預期」（只綁 127.0.0.1、不多開 port）；改成變數會讓 `.env` 一個值就能悄悄改綁定。代價是將來換 port 仍要改程式，這可以接受。
4. **互斥檢查放在 `research_lab.py up`／`start`，只拒絕、不自動停止。** 以 Docker label `com.docker.compose.project=industryflow` 找出原服務正在運行的容器；不論既有 api 容器存不存在，都探測 3010／8010（以及有啟用時的 4201）。若 port 被占用，但占用者是本 project 自己的容器，則允許（例如重跑 `up` 時）。自動停止原服務會違反「不覆寫既有服務」的原則，所以只回報占用者。
5. **測試常數一併改為 3010／8010。** `test_research_auth.py` 等測試以 monkeypatch 設定 origin，數值本身不影響結果；統一改掉，避免之後有人誤以為 3014 仍是正式 origin。歷史驗收紀錄（`docs/research-acceptance.md` 前面幾節、`docs/research-backup.md` 等）保留當時的 3014，不改寫歷史，只新增切換紀錄。
6. **3014 上的收藏不自動搬移。** 瀏覽器不允許跨 origin 讀取 localStorage；沿用既有的 JSON 匯出／匯入功能，並在切換紀錄裡寫出操作步驟。

## Risks / Trade-offs

- [瀏覽器快取了原服務的舊 JS 或 service worker 回應] → 切換後以無痕視窗與一般視窗各走讀一次；研究頁回應原本就帶版本化 cache key，manifest 不快取。
- [原服務 `restart: unless-stopped` 在 Docker 重開機後自行啟動，搶走 3010] → 原服務容器是手動停止的，`unless-stopped` 不會自動拉起；互斥檢查也會在研究服務啟動時攔下來。切換紀錄註明不要對原服務執行 `docker compose up`。
- [在 3014 有登入中的 owner session] → session secret 已在切換時輪替，舊 session 本來就已失效；改 origin 後重新登入即可。
- [忘了改某處 3014 引用，管理入口回 403] → apply 時以 grep 清點；live e2e 涵蓋管理登入與寫入的 Origin 檢查。

## Migration Plan

1. 確認原服務 `industryflow` 沒有容器在運行（`docker ps --filter label=com.docker.compose.project=industryflow`）。
2. 修改 compose、工具、測試、文件，跑 `python -m pytest -q backend/tests`。
3. `python scripts/research_lab.py up`：重建並重新建立 api／web 容器（volume 不變），確認綁在 3010／8010。
4. 以 `E2E_BASE_URL=http://127.0.0.1:3010` 跑 live e2e，並手動檢查舊連結、`#candidates`、v1 收藏遷移。
5. **回復**：`docker compose --project-name industryflow-research ... stop`（不加 `-v`），再到原服務以原 image 執行 `docker compose up -d`，3010 就回到原服務；研究服務的 volumes 保留。
