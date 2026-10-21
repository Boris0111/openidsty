# 唯讀入口與本機管理分開

本機維護使用 `http://127.0.0.1:3010/admin`。可選的 reader gateway 使用 `http://127.0.0.1:3015/next`，只允許新版 `/next`、必要的靜態檔案、v2 GET，以及無寫入副作用的更新查詢 POST。管理頁、管理 API、legacy 診斷、API 文件與其他寫入一律拒絕；不以「沒顯示連結」代替授權邊界。

```powershell
python scripts/research_lab.py reader-start
python scripts/research_lab.py reader-stop
```

先以 `python scripts/research_lab.py up` 更新 API／web image，再啟動 gateway；gateway 沿用同一 app image，不新增資料庫、cache 或微服務。預設不啟動，驗證完可停止以節省記憶體。這個容器沒有 DB／session 憑證、Git／資產 volume 或 Docker socket，root filesystem 唯讀。固定上游為 Compose 的 `web:3010`，不是任意 URL proxy。

Gateway 檢查 Host、路徑、方法與大小，拒絕 dot traversal、雙重編碼及不必要的入口。它不轉送 Cookie、Authorization、CSRF、X-Forwarded-* 或客戶端 Host，也不向讀者回傳上游 Set-Cookie。對內部故障回 `503`／no-store，不偽裝成功的空資料。來源引用仍由讀者直接開啟官方網站，不由 gateway 抓取任意網址。

## 私人網路部署條件

此 Compose profile **仍只綁 loopback，尚未設定跨裝置 TLS**。要分享給私人網路上的裝置，請在 gateway 前設定 HTTPS reverse proxy，限制可連線的私人網段／裝置；對內 upstream 為 `127.0.0.1:3015`，Host 設 `127.0.0.1:3015`。不要轉送管理入口，或改成直接暴露 3010、8010、4201、DB。不要做公網 port forwarding。

TLS 憑證、主機名稱及裝置信任須依實際私人網路設定；本輪沒有安裝 CA、調整防火牆、開啟 LAN bind 或對外部署。這和在本機 HTTP 的 owner 開發例外是兩回事；若未來改成跨裝置管理，還需要 [research-owner](research-owner.md) 的 HTTPS owner 設定。

目前 gateway 只供新版研究入口，legacy `/` 會導向 `/next`，不把舊版診斷整套公開。完整新舊研究導覽仍由 task 6.1 接續；此入口不能被描述為已完成全站切換。不同 port／host 的收藏各自存在瀏覽器，交換功能依 task 7 實作。

## 驗證方式

原生單元測試：`python -m pytest -q backend/tests/test_reader_gateway.py`。Live reader 測試需先啟動 reader，設定 `RESEARCH_READER_E2E=1`、`E2E_BASE_URL=http://127.0.0.1:3015`，執行 `frontend/tests/research-reader-entry.spec.ts`。驗證研究—公司—圖解仍可讀、release pin 留在同一入口，以及匿名／偽造 cookie／Host／管理路徑均被拒絕。
