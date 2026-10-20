# Spec Delta

## REMOVED Requirements

### Requirement: 此裝置的關注清單

**Reason**: 收藏範圍擴及公司、產品、題材與研究頁，改由 `research-watchlist` 定義；本 capability 退役。

**Migration**: 由 research-watchlist「跨研究物件的本機收藏」及「舊題材清單可遷移且儲存失敗可讀」承接；`industryflow.theme-watchlist.v1` 遷移後保留為備份。

### Requirement: 更新種類分開呈現

**Reason**: 讀者更新改為已發布研究、有效財務／指標修訂與新事件三類；未納入判讀的候選資訊屬維護佇列，移至管理端。

**Migration**: 由 research-watchlist「只追蹤讀者可見的實質更新」承接；待核對候選及處理狀態見 data-coverage 的管理 coverage。

### Requirement: 已讀基準對應實際顯示內容

**Reason**: 已讀語意擴及四類收藏目標，併入 research-watchlist。

**Migration**: 由 research-watchlist「只追蹤讀者可見的實質更新」承接首次基準、只記錄已顯示版本及移除收藏時清除基準。

### Requirement: 公開更新摘要不保存個人名單

**Reason**: 公開更新查詢改為 v2 更新查詢，不再回傳候選資訊摘要。

**Migration**: 由 research-watchlist「只追蹤讀者可見的實質更新」承接唯讀、不保存個人清單及逐項回報失效目標。
