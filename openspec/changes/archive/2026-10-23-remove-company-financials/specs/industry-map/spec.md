# Spec Delta

## MODIFIED Requirements

### Requirement: 研究投影完整且保留查核基準

網站投影 MUST 保存所有環節、題材、產品、公司與研究頁的完整已發布內容、監測定義、風險、里程碑及證據連結；題材 MUST 顯示原始狀態查核日期，匯入時間不得取代查核日。已發布 Markdown／YAML 的 Git commit MUST 為正式研究來源，網站表單只編輯待發布草稿；動態事件及指標觀測不寫入靜態監測定義。

#### Scenario: 匯入既有題材
- **WHEN** 重跑題材匯入
- **THEN** 全文與連結保留，狀態查核日期不被改為匯入日

#### Scenario: 網站與檔案編輯同一研究
- **WHEN** 兩種編輯方式各自完成發布
- **THEN** 都能由已發布內容 commit 重建相同研究投影，草稿不被誤作正式來源
