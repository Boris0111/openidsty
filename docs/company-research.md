# 公司識別與關係維護

`data/company-research.yaml` 保存補充 aliases、官方 CIK 與企業關係。環節／角色仍來自 `industry-map/`，不在此建立第二份地圖。修改後執行地圖匯入，驗證失敗時資料庫保留原投影。

每筆關係須有唯一 id、canonical source／target ticker、kind、direction、review_status、relevance、evidence、reason、source_url、checked。source／target 必須存在於地圖。

- supply：supplier → customer，僅 one_way。它描述供應交付方向，不描述事件影響方向。
- partner：one_way 或 two_way，依具體合作承諾記錄；雙邊合作使用 two_way。
- confirmed：官方資料明確指認兩個主體及關係；不能只因人工審核就把 inference 升格。
- candidate：待驗證，預設隱藏；保留 inference 與原始理由，圖上以虛線顯示。
- relevance：high 為該業務的關鍵直接角色，medium 為直接但影響程度未充分量化的合作，low 為有限的直接關聯，unknown 為尚無足夠判斷。`relevance_reason` 說明研究判斷；不是營收占比、市值、tier、證據強度或連結數。

初始資料刻意只列少量有官方來源的案例，不代表完整企業網路。候選「台積電—鴻海」僅由同一 AI 工廠專案共同被提及而產生，**needs verification**，不宣稱已存在直接雙邊合作。節點大小不會因其共同提及就變大。

CIK 可由 [SEC 官方 ticker mapping](https://www.sec.gov/files/company_tickers_exchange.json) 查核；aliases 中文以字串比對，ASCII 名稱採 token 邊界，以免 AMD 誤命中 AMDOCS。事件主體優先使用官方 issuer，正文提及另外保存。
