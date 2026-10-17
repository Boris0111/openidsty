# 公司、產品、術語與引用閱讀（task 6.2）

## 本輪閱讀設計

沿用已接受的白底、藍綠、Microsoft JhengHei 與產品交付—條件—證據順序：底色 `#ffffff`、文字 `#16343a`、連結 `#18647e`、主色 `#267a97`、界線 `#cbd8dc`、次要文字 `#526575`。保留現有字級與桌機兩欄／手機單欄；新增內容沿文章順序往下讀，不以新字體、通用卡片或維護數字取代研究。

```text
公司：名稱／定位 → 已知環節角色 → 有內容的研究段落 → 產品 → 主張與引用 → 研究界線
產品：名稱／交付 → 採用與替代限制 → 公司 → 主張與引用 → 完整研究 → 延伸研究
術語：解釋／適用範圍 → 圖解 → 比較條件與限制 → 主張與引用 → 延伸研究
```

公司內文仍由 Markdown 維護；完整深研的八項主題只有內容存在才顯示，不建立空白標題假裝已研究。各環節的描述與同版中文名稱並列，跨環節公司維持同一頁。公司頁內目錄只由實際研究段落產生。

產品先前沒有顯示完整 Markdown，本輪補回用途、採用條件與供應角色的解釋；既有交付／證據順序保留。術語 `comparisons` 明確呈現兩個比較對象、條件及替代限制；引用的對象與 `related-ids` 由同一 release 解析名稱，不能直接顯示 ID。比較不產生排名或宣稱無條件可替代。

圖解使用已發布、固定 hash 的資產；desktop／mobile 成對時依螢幕選圖，其餘合法圖解逐一顯示。失效圖保留說明與全文。既有兩回路走讀不重複顯示同一張圖，owner preview 使用同一 renderer。

引用直接提供原始來源、適用期間及章節／頁碼定位。「查閱這份引用」按需讀取該研究 release 中固定 document revision，顯示研究讀取範圍與合法摘錄；沒有保存全文即明說。讀取失敗保留主張及原定位，不查 latest、不改成新版本，不展示 parser 或內部維護欄位。Owner 預覽使用候選引用的內嵌資料，不透過公開 API 讀取草稿。

取證方法中的 HTTP 狀態、JavaScript 外殼或 parser 診斷不作為閱讀內容；引用保留已讀章節與未讀範圍。這是讀者呈現，不改寫保存的引用或把舊查核日期更新為今天。

## 驗收路徑

- `/next?focus=concept-liquid-cooling-loop`：保留原兩回路圖，閱讀冷板／CDU 的比較條件及互補限制；延伸研究可開公司與產品。
- `/next?focus=product-cold-plate`：除了交付與來源，現在能閱讀「定義與用途」「採用條件與限制」「供應角色與公司」的完整內文。
- `/next?focus=company-auras` 或 `company-vertiv`：查看環節角色及來源，展開「查閱這份引用」，保留同版、適用期間及引用位置。此兩頁仍是已接受的首條走讀，未宣稱已完成全套深研。
- 完整公司段落、圖解失效與固定引用失效由明示合成的離線瀏覽器情境驗證；不將其寫入 application DB。

原始公開頁面另作唯讀走查：2026-10-17，Vertiv 的[液冷說明](https://www.vertiv.com/en-us/solutions/learn-about/liquid-cooling-options-for-data-centers/)可讀直接晶片取熱及 Distribution 段落，NVIDIA 的[DSX overview](https://docs.nvidia.com/dsx/facilities-infra/reference-design-overview)可讀 CDU／secondary loop 段落。雙鴻[2025 新聞](https://www.auras.com.tw/News/NewsContent/14-10/en)於本環境 HTTP 200，但 web 文字擷取與 headless Chromium 僅得到頁首／頁尾外殼，未重新確認新聞內文；不把這輪視為新內容查核，仍保存既有研究與 2026-10-16 基準。公開來源失效或工具無法讀取，不自動刪除研究或改查其他版本。

這一階段完成內容呈現能力；全鏈新分類與 26 家深研仍由 task 8 逐項交付。財務圖表／修訂及比較屬 task 6.3，不能用此頁 renderer 或後端測試結果代替其頁面驗收。
