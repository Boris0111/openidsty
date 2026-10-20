# 公司識別與關係維護

新版公司的穩定身分、aliases、listing 及官方識別只維護 `industry-map/companies/`；格式唯一規範在 [Schema](../industry-map/README.md)。目前 95 家基本索引保留原 100 筆角色與舊 ticker／PRIVATE 映射，不把遷移當新一輪研究。改名或換代號時保留 entity-id，未上市公司 listings 為空。

`data/company-research.yaml` 暫留為舊 API 匯入相容輸入與舊企業關係來源。不要在兩處各自維護新研究；新投影依 registry 身分解析，既有關係仍保留原證據與狀態。以下說明舊關係欄位，並非新版另一份 Schema。

每筆關係須有唯一 id、canonical source／target ticker、kind、direction、review_status、relevance、evidence、reason、source_url、checked。source／target 必須存在於地圖。

- supply：supplier → customer，僅 one_way。它描述供應交付方向，不描述事件影響方向。
- partner：one_way 或 two_way，依具體合作承諾記錄；雙邊合作使用 two_way。
- confirmed：官方資料明確指認兩個主體及關係；不能只因人工審核就把 inference 升格。
- candidate：待驗證，預設隱藏；保留 inference 與原始理由，圖上以虛線顯示。
- relevance：high 為該業務的關鍵直接角色，medium 為直接但影響程度未充分量化的合作，low 為有限的直接關聯，unknown 為尚無足夠判斷。`relevance_reason` 說明研究判斷；不是營收占比、市值、tier、證據強度或連結數。

初始資料刻意只列少量有官方來源的案例，不代表完整企業網路。候選「台積電—鴻海」僅由同一 AI 工廠專案共同被提及而產生，**needs verification**，不宣稱已存在直接雙邊合作。節點大小不會因其共同提及就變大。

CIK 可由 [SEC 官方 ticker mapping](https://www.sec.gov/files/company_tickers_exchange.json) 查核；aliases 中文以字串比對，ASCII 名稱採 token 邊界，以免 AMD 誤命中 AMDOCS。事件主體優先使用官方 issuer，正文提及另外保存。
