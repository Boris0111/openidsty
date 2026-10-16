# 產業閱讀與技術證據驗收

Change：`improve-industry-reading-and-technical-evidence`。實作基準為 `b613d53b7facc97be090348e864bf9fdd9611bc9`；2026-10-15 起執行。任務狀態以 OpenSpec CLI 及 tasks checkbox 為準，本文件只記錄當次實測。

## 起始核對

- `git rev-parse HEAD origin/main`：兩者均為上述提交；當時只有本 change 規劃與另項 Dashboard 的 outputs 尚未追蹤。
- `openspec list --json`／`status`：本 change 0/44、spec-driven、ready；前置 `add-evidence-based-theme-assessments` 45/45，完成、未歸檔。前置 artifacts 與主 specs 保持原狀。
- 真實 API `/api/segments` 共 17 個：advanced-packaging、compute、datacenter、eda-ip、equipment、foundry、interconnect、materials、memory、networking、odm、pcb、power、power-discrete、substrate、test、thermal。
- 真實 API `/api/themes` 共 7 個：800vdc、advanced-node-2nm、cpo-silicon-photonics、custom-asic-vs-gpu、hbm4、liquid-cooling、power-bottleneck。
- 基準執行環境：既有 Docker production API／web，非 dev server；映像識別及量測方式見 [讀取效能](reading-performance.md)。

## 備份與隔離

本次 dump：`backups/industry-20261015-235419.dump`，SHA256 `30F0BA37B390830331290D556AC00DA4A16805015454508DF8A9D443257CF1A0`。使用 pg_dump custom format 與 docker cp，沒有將密碼或二進位 dump 納入版本控制。

`scripts/start-reading-lab.ps1` 將該 dump 還原到獨立 PostgreSQL container `industryflow-reading-db` 的 `industry_reading`，獨立 network `industryflow-reading`。API 8013、production 網站 3013；沒有 worker、沒有外部 ingestion、沒有正式 DB 連線。API／web 使用原映像的 content ID，另保留 baseline tag。後續只重建這組容器，正式 8010／3010 服務維持原狀。

固定 reference 快照由 `scripts/reading_snapshot.py` 取得；保存筆數、事件／財報／觀測／判讀版本 fingerprints、coverage、三類更新基準（版本 ID、indicator token、candidate token）與 SQL 次數。原始本機紀錄存於忽略的 `.work/reading/`；彙總結果在本文件及效能文件更新，尚未執行的驗收不視為通過。

還原後連續兩次以 `2026-10-15T16:00:00+00:00` 為 reference，所有表筆數、四類歷史 fingerprint、coverage 與 updates JSON 完全相同。保存摘要見 [baseline JSON](reading-baseline.json)：17 環節、7 題材、95 公司、53 runtime sources、2,915 事件、147 財報、11 觀測、7 判讀版本、9 指標。固定 reference 不是文件查核日期，也不是正式來源的取得時間。

## 閱讀層驗證（2026-10-16）

typecheck、production build 通過；離線 Playwright 21/21 通過，包含中文 breadcrumb／支持程度、未知狀態、原始 URL 保留、局部 503 後研究仍可讀、鍵盤診斷與重試、來源設定限制、萬／億與原幣、精確原值、百分點、零／負值／未知值、不可比較原因及手機無橫向溢出。既有版本、完整候選、搜尋與此裝置關注流程也通過。

後端指標針對性測試 3/3 通過；只為來源投影新增 name，Decimal 比較與原始值未變。此階段仍為離線驗證，不代表技術來源已重新取得；待後續隔離 live 整合與全圖走查。

## Schema 與匯入驗證（2026-10-16）

唯一 schema 已定義 optional 關係說明、技術面向、固定文件／版本／章節、公開頁面引用及核對紀錄。舊格式、混合格式、未知發布日與同檔 assessment 論點引用均通過 full／skip-prose；驗證器 66 類失敗案例通過，包括重複 YAML 鍵、非實存下游、失效文件版本／定位、日期、來源、監測上限與 hostname。

新增六個跨市場官方入口，canonical 來源目前 41 筆；既有 adapter 設定仍可驗證。manifest 保存實際讀過的五份公開介紹／索引基準，JEDEC 受阻入口沒有被製造成已核讀文件。這些是結構與入口基準，未宣稱核讀五家所有規格。

匯入改為驗證並讀取同一份 immutable authoring copy；新增 technical-profile 不影響原 assessment semantic hash。18 項針對性 backend tests 通過，包括非法邊／文件引用／日期整次 rollback、事件與研究／版本完整比較、原三類更新基準保持一致，以及技術面向獨立修改不產生假判讀版本。文件 DB 投影、migration 與 live PostgreSQL 仍待第 7 組實作。

## 關係型別與內容

29 條既有下游邊均已補 metadata；[逐邊矩陣](industry-relation-matrix.md) 連到唯一來源檔。`datacenter:compute` 為需求回饋，其餘為供應角色；材料到載板／PCB 的直接供應尚待核實，明列具名材料與供應資格缺口。這些說明沒有被宣稱為公司交易已確認。

與 HEAD 逐檔解析比對：17 檔原有 authored 欄位及全部正文保持相同，只新增 downstream-relations。Full validator 通過。9 項 graph／map backend tests 通過：edge ID 與方向相容、segment 與 graph 同一 payload、舊格式 unreviewed、三個原案例的全部三種遍歷在有／無 metadata 時完全相同、回路路徑不重複。

連線 UI 的 typecheck／production build 通過；三項離線關係測試通過：圖上實際點線與文字清單開啟同份資料、供應／需求回饋說明、分享與返回／清除、無效關係、手機鍵盤及焦點返回、resize 保留 pan／zoom。測試發現的返回後焦點指到上一條線、手機環節讀取搶走連線焦點已修正。研究全文未被收合；原環節 URL 仍相容。完整 suite 將於交付再次執行。


2026-10-16 真實隔離網站走查：17 環節與 7 題材 × 桌機 1440×1000／手機 390×844，共 48 列。五種技術面向、鍵盤展開證據與橫向溢出檢查全部通過，pageerror 0；另確認 CMIS 固定版本與章節錨點。可保存紀錄見 [技術閱讀矩陣](technical-reading-walkthrough.json)，研究內容見 [技術研究矩陣](technical-research-matrix.md)。Git 原稿對照確認所有既有 frontmatter（扣除新增欄位）及正文完全相同；原 assessment、change_reason、原查核基準與拓樸未改動。


2026-10-16 真實隔離網站走查：17 環節與 7 題材 × 桌機 1440×1000／手機 390×844，共 48 列。五種技術面向、鍵盤展開證據與橫向溢出檢查全部通過，pageerror 0；另確認 CMIS 固定版本與章節錨點。可保存紀錄見 [技術閱讀矩陣](technical-reading-walkthrough.json)，研究內容見 [技術研究矩陣](technical-research-matrix.md)。Git 原稿對照確認所有既有 frontmatter（扣除新增欄位）及正文完全相同；原 assessment、change_reason、原查核基準與拓樸未改動。

## 執行與復原驗收

2026-10-16 的乾淨 tracked 檔案快照先經 Git index 匯出至 `.work/clean-reading-20261016-final`，不提交暫時 commit。map full、validator 66 類失敗案例、backend 全套 150 項、typecheck、production build、33 項離線 Playwright 通過；另外 2 項 PostgreSQL 測試以明確指定的 industry_empty_reading 執行並通過，未拿 skip 當通過。Linux Docker 以與 baseline 相同的 Python 直接／間接依賴及 Node 24.21.0 執行 backend 驗證，唯一新增依賴為 pypdf 6.20.1。後續的原文摘錄／年份顯示及事件來源名稱修正有對應回歸案例；事件回應只 additive 增加 source_name，source_id 保留。

7 項 live 整合測試全部通過，涵蓋桌機／手機、graph selection／viewport／history、17 環節／7 題材、快速切換與故障重試、公司與舊比較入口、事件日期／來源、coverage 與下載報告。另有 [48 列實際閱讀走查](technical-reading-walkthrough.json)，包含 24 列 coverage、固定版本章節、真實 OCP 403 下仍可讀的基準及摘錄。

隔離 Prefect 使用原有 process worker 與相同 flow，測試 deployment 沒有 schedule。兩輪實際更新選擇 TWSE 月營收、TPCA、AAON 指標、OCP 與 OIF 文件；TWSE／TPCA／AAON／OIF 均成功且新增 0，OCP 為真實 HTTP 403。兩輪的事件 2,915、財報 147、指標觀測 11、判讀版本 7、文件觀測／核對各 8 均不變，三類 token、文件內容 hash 也完全相同。每日到期分支另回 not_due，未改寫研究。

使用無服務的 localhost proxy 造成可控制的連線失敗，再恢復正常 HTTP：OIF failed → success，必要摘錄、版本、計數與 token 全部保留。這是受控網路故障測試，與 OCP 發布站的實際 403 分開記錄。PostgreSQL advisory lock 第一連線取得成功、第二連線取得失敗；文件、事件、指標沿用同一鎖。重新啟動隔離 DB、API 與 worker 後重查，資料及三類 token 不變。

在新增表／索引保留的情況，將隔離 API／web 切回 b613d53 對應 baseline image：health／map_ready 正常、七題材的三類 token 保留；再恢復新版 image，結果仍一致。未執行會刪除歷史的 downgrade。證據見 [取得、故障、重啟與回滾紀錄](reading-restart-verification.json)。

原始備份為 `backups/industry-20261015-235419.dump`，SHA256 `30F0BA37B390830331290D556AC00DA4A16805015454508DF8A9D443257CF1A0`。上述測試後停止隔離 worker／Prefect，僅重建明確命名的 industryflow-reading-db 內 industry_reading，從此備份還原，再 migration／initialize；以原快照重跑效能，避免把更新操作時間混入比較。原 industryflow 的 DB／3010／8010 服務維持原狀。


2026-10-16 預覽回饋後，一般閱讀已移除文件待核對清單及通用進階資訊；監測／核對資料仍由 API 及本機維護使用。當次 UI 驗收與後續修正請分別閱讀 [閱讀修正紀錄](reading-review-20261016.md)，舊畫面矩陣不代表修正後畫面。
