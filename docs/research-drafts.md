# 草稿編輯與同一份研究

研究的正式來源仍為 Git 內的 Markdown／YAML。網站表單只是另一個編輯入口：表單保留原 frontmatter 未顯示的欄位，與內文一起轉回 Markdown。每次儲存將整份研究草稿存成 PostgreSQL 修訂；這時不寫開發工作目錄、不 commit、不切換正式 release。

## 本機開始

在主專案根目錄（2026-10-21 切換前為 worktree `openspec_pjt-research-service`）執行 `python scripts/research_lab.py seed-git`，把目前分支的 Git bundle 初始化到隔離的 managed Git volume。既有 repository 不會被覆寫；目前已發布版本會保留在不可改寫的 `refs/research/releases/<release UUID>`。API 僅唯讀掛載這個 volume；後續發布 worker 才有 Git 寫入權。

依 [維護者設定](research-owner.md) 建立自己的密碼，開啟 `http://127.0.0.1:3010/admin`。登入後「從目前正式研究建立草稿」，選擇研究檔案。表單可改名稱、摘要、查核日期及內文；其他欄位用「切換 Markdown」編輯。YAML manifest 直接使用文字編輯。`industry-map/README.md` 是 Schema 說明，不允許透過草稿變更。

範例：選 `industry-map/companies/company-auras.md`，在摘要末尾加一段自己的草稿說明，儲存、驗證、與基準比較，再按閱讀預覽。預覽顯示同一份研究的判斷、來源、圖解及關係圖；正式 `/next` 的摘要應保持原狀。修改真實研究判斷仍須核對來源，結構驗證不代表研究內容正確。

儲存與匯入都帶 `If-Match: "修訂號"`。較舊修訂回 `409`，不覆寫新版本；管理頁保留輸入，讓維護者自行比對或明確重新載入。重複儲存完全相同內容不新增修訂。切換檔案／草稿前須儲存目前輸入；「重新載入草稿」明示會捨棄未儲存內容。

儲存與匯入只對新增或內容改變的檔案重做單檔檢查（raw HTML、連結、YAML 結構），沒改的檔案沿用上一個已接受修訂的結果；整份草稿的大小、檔案數與路徑檢查仍每次全做。**驗證與發布仍檢查全部檔案**，所以規則收緊後才變得不合格的舊檔案，會在驗證或發布時被擋下。同一修訂的完整驗證只做一次：驗證、閱讀預覽與預覽中的圖解共用結果（API process 內最多保留兩個修訂，重啟後重算）。

## CLI／agent 編輯相同 Markdown

使用可匯入 `backend/app` 的 Python 環境（安裝 `backend/requirements.txt`），在 repo 根目錄設定 `PYTHONPATH=backend`。下列指令每次由互動終端隱藏輸入維護者密碼，密碼及 session 不寫入檔案、參數或環境變數。HTTP 僅允許 loopback；遠端須 HTTPS。登入限流仍適用，不要自動高速重試。

```powershell
$env:PYTHONPATH='backend'
python -m app.research_cli create
python -m app.research_cli export --draft <草稿 UUID> --directory .work/my-draft
# 編輯 .work/my-draft/industry-map/ 下的 Markdown 或 YAML。
python -m app.research_cli import --draft <草稿 UUID> --directory .work/my-draft
python -m app.research_cli validate --draft <草稿 UUID>
python -m app.research_cli preview --draft <草稿 UUID> --entity company-auras
```

匯出資料夾必須尚未存在，避免覆寫開發 checkout。`draft.json` 保存草稿 UUID、基準、修訂、Schema 及既有資產 hash；實際 Markdown／YAML 各自成檔，不把整份研究塞進 JSON 文字欄位。匯入仍走與網站相同的 API、allowlist、大小限制及編譯器；資料夾不得含 symlink、`.env` 或程式碼。匯入後再次編輯須匯出新修訂到另一個新資料夾，舊檔案的 revision 不會自行更新。請勿手改 revision 來跳過衝突。

資產內容不直接放入 5 MiB 草稿 JSON。上傳新圖解可先執行下列命令（上限 10 MiB）：

```powershell
python -m app.research_cli upload-asset --file .work/new-diagram.svg --asset-path industry-map/assets/new-diagram.svg --media-type image/svg+xml
```

將回傳的 path/hash 加入交換檔 `draft.json` 的 `assets`，在 `industry-map/research-assets.yaml` 登錄一致的 path/hash、media-type、alt、license、attribution，再由研究文件的 `diagram-assets` 引用該 asset ID。完成後 import／validate；不完整引用無法預覽或發布。上傳會先驗證副檔名、media-type、內容及 SVG 主動內容／外部引用，再保存到內容定址 store。單純上傳不會讓資產公開；公開 endpoint 仍要求已發布版本引用。匯出不是可獨立離線發布的副本。

## API 與隔離

所有路徑以 `/api/admin` 開頭，皆需 owner session；寫入另需 Origin 與 CSRF。Next 只代理明列路徑與方法，不提供任意上游轉送。

| 方法與路徑 | 用途 |
|---|---|
| `GET /drafts`、`POST /drafts` | 有界草稿清單／從已發布基準建立 |
| `GET /drafts/{id}` | 讀取完整草稿（含全部檔案內容） |
| `GET /drafts/{id}/summary` | 修訂號、檔案路徑清單與資產對照，不含檔案內容；管理頁選擇草稿時使用 |
| `PATCH /drafts/{id}` | 以文字或表單更新檔案；回應為上述摘要加上 `documents`（這次變更且仍存在的檔案，格式同 `document`），不含其他檔案內容 |
| `GET /drafts/{id}/document?path=...` | 取得完整文件及表單表示 |
| `POST /drafts/render-document` | 轉換表單與 Markdown，不儲存修訂 |
| `POST /drafts/asset-upload?path=...` | owner 上傳圖解，raw bytes 與明確 Content-Type |
| `GET /drafts/{id}/export`、`POST /drafts/{id}/import` | 可往返的完整草稿交換 |
| `GET /drafts/{id}/diff` | 與確切基準 commit 比較；超過 1 MiB 顯示截斷 |
| `POST /drafts/{id}/validate?revision=N` | 同一編譯器檢查完整草稿與引用 |
| `GET /drafts/{id}/preview?entity_id=...&revision=N` | owner 私有閱讀預覽 |
| `GET /drafts/{id}/assets/{sha}?revision=N` | 僅提供這份修訂引用且驗證通過的資產 |

草稿 JSON 上限 5 MiB，文字／路徑及 YAML 結構另有界限：每份 YAML（含 Markdown frontmatter）的巢狀深度最多 32 層、parser 事件最多 400,000 個、alias 展開後節點最多 400,000 個，不接受遞迴 alias；超過時錯誤訊息以檔案路徑開頭。上限依 300 家公司、3,000 條關係的擴大資料校準（關係檔約 9.8 萬個事件、4.7 萬個節點）。YAML 以 libyaml 解析，重複鍵規則不變。拒絕 raw HTML、外部 Markdown 圖片及危險連結；圖解由資產 manifest 管理。預覽在 DB savepoint 建立臨時投影，使用正式 detail／graph 函式組合結果，回應序列化後立即 rollback；不建立正式 head。Reader 的 RLS 及已發布 release 檢查維持生效。資產使用內容 hash，預覽 URL 另有 owner 驗證，不讓猜中 hash 的讀者取得未發布資產。

草稿與預覽完成不等於發布完成；發布排程、衝突協調、還原及完整管理流程由 tasks 4.4–4.6 接續。
