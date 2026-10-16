# 本機維護者登入

此功能屬於 task 4.1：單一 owner 設定、session 與管理 API 的授權基礎。草稿編輯、發布 UI 與私人網路 reader gateway 仍由後續 tasks 交付；一般讀者不需要登入，也不建立 reader account。

## 設定及重設

先在新版 worktree 啟動隔離預覽，再於本機互動終端執行：

```powershell
python scripts/research_lab.py up
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml exec api python -m app.research_owner setup
# 已有 owner 遺失密碼時：
docker compose --project-name industryflow-research --env-file .env.research -f compose.research.yaml exec api python -m app.research_owner reset
```

密碼由隱藏輸入連續確認兩次，至少 12 個字元、最多 1024 UTF-8 bytes；不可透過命令列參數、環境變數或 pipe 傳入。`setup` 拒絕覆寫已有 owner；`reset` 更新 credential version、撤銷所有 session，並清除登入封鎖。這兩個命令只使用獨立 writer login，不會修改舊版服務。本輪驗證只在 `industry_research_test` 使用合成密碼，未替 Boris 設定或挑選實際密碼。

Argon2id 使用 `argon2-cffi` 高階 `PasswordHasher`，目前參數為 64 MiB、3 次、parallelism 4；登入成功時若參數已過時會重新雜湊。DB 不保存密碼原文。依據：[官方用法與參數說明](https://argon2-cffi.readthedocs.io/en/stable/howto.html)。

## API 操作

所有回應為 `Cache-Control: no-store`。Next 的 `/api/admin/session` 為獨立明列代理，公開 GET proxy 仍不能任意轉送管理路徑。

1. 同 origin `GET /api/admin/session` 取得 `authenticated` 與 `csrf_token`；未登入時另設 10 分鐘有效的 HttpOnly 登入 challenge cookie。
2. 同 origin `POST /api/admin/session`，JSON 為 `{ "password": "使用者輸入" }`，header 帶 `X-CSRF-Token`；cookie 由瀏覽器正常附帶。登入仍須驗證 challenge，避免 login CSRF。
3. 登入成功後取得新的 CSRF token，後續管理寫入都要使用該 token；`GET /session` 可在已登入狀態重新取得它。登入會更換 session token，舊 token 立即撤銷。
4. `DELETE /api/admin/session` 帶目前 CSRF token 登出，伺服器撤銷 token 並清除 cookie。重播舊 cookie 無法恢復登入。

Session 為 256-bit 隨機 opaque token，DB 只保存 SHA-256；CSRF token 亦只保存 hash。伺服器以最後成功使用時間判定閒置 30 分鐘到期，且最長 8 小時；cookie 的 Max-Age 不取代伺服器期限。session 與 owner credential version 綁定，重設即失效。設定與成功登入／登出記入稽核，不記錄密碼、cookie、CSRF 原文或 request body。

Origin、Host 採明列 allowlist；管理寫入缺少 Origin、跨站 Origin／Fetch Metadata、CSRF 不符或未登入皆拒絕。登入每個 transport peer IP 每分鐘最多 5 次，第 6 次封鎖 15 分鐘並回 `429`／實際 `Retry-After`。限制保存在 PostgreSQL，無法靠 API 重啟歸零；不信任 `X-Forwarded-For`。目前經 Next 的本機登入共用 Next proxy 的 peer bucket，不能透過自行填入 IP header 分散嘗試。

Session 行為依據：[OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)、[OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。

## HTTP 開發例外與 HTTPS

未設定 `RESEARCH_ADMIN_MODE` 時管理入口停用。隔離 Compose 明確使用 `loopback-http`：只允許 `http://127.0.0.1:3014` 及 `http://localhost:3014` 的 Origin，web／API ports 綁 `127.0.0.1`；cookie 仍為 HttpOnly、SameSite=Strict、Path=/api/admin，僅此開發模式不設 Secure。API Host 允許明列的本機入口與容器內 `api:8000`，不接受任意 Host 或轉送主機 header。

跨裝置／私人網路須另完成 reader gateway 與 TLS 設定。HTTPS 管理模式為 `RESEARCH_ADMIN_MODE=https`，`RESEARCH_ADMIN_ORIGINS` 必須全部為 `https://`，cookie 設 Secure；Next 同樣要設定完全一致的 Origin allowlist。不能只將 HTTP profile 的 bind 改成 `0.0.0.0`，或藉由偽造 `X-Forwarded-Proto` 取得開發例外。cookie 安全模式由伺服器明確設定，不從客戶端 header 猜測。

資料庫故障或 writer 設定缺少時回 `503`，不回退到 reader／bootstrap 身分。管理 validation error 不回顯使用者輸入；錯誤附 request_id，方便核對。

## 驗證

`python scripts/research_lab.py pg-check` 在獨立測試 DB 執行 owner/session 契約，涵蓋設定／重設、hash 保存、匿名、跨站、CSRF、過期、登出撤銷、重播、登入輪替、持久限流與 HTTPS cookie。合成登入不寫入 application DB；實際 owner 密碼由 Boris 於本機自行設定。

2026-10-17 實際驗證：34 項隔離 PostgreSQL／API 契約全部通過（含 12 項 owner 測試），另有 3 項真實 Next 管理代理測試與 6 項既有研究走讀通過。新 web production build 通過，容器更新後來源、版本、手機與鍵盤閱讀仍可用。原版及 Valuflow 依本輪使用者資源調整指示保持停止，檢查期間未重新啟動；後台編輯與發布 UI 仍依後續 tasks 交付。

後續同日 tasks 4.2–4.3 已加入 `/admin` 草稿編輯頁與明列的草稿代理，整體擴充為 71 項 PostgreSQL／容器與 13 項 live browser 通過。草稿操作見 [research-drafts](research-drafts.md)；完整發布流程仍待 tasks 4.4–4.6。實際 owner 密碼仍由 Boris 本機自行設定。
