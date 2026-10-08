## MODIFIED Requirements

### Requirement: 固定模板公司頁與唯一識別
系統 MUST 以 canonical ticker 識別公司並合併跨環節角色；公司頁 MUST 採輕量模板顯示名稱、代號、各環節角色、相關事件與來源，不展示財報表格、企業關係圖或比較操作。未知公司 MUST 回傳不存在狀態，資料不足 MUST 使用單一精簡提示，不得填零或生成假內容。

#### Scenario: 跨環節公司
- **WHEN** 使用者從運算或網通開啟博通
- **THEN** 進入同一公司頁，並可看到兩個環節角色與回到環節研究的連結

## REMOVED Requirements

### Requirement: 關係圖方向與分級
**Reason**: 公司研究輕量化，不要求 UI 展示企業關係圖。
**Migration**: 既有關係資料、方向、分級及 `/api/companies/{ticker}/graph` 保留。

### Requirement: 候選與已確認關係分離
**Reason**: 公司頁移除關係圖與候選切換操作。
**Migration**: 既有 API 的 confirmed／candidate 分離及原始證據欄位保留。

### Requirement: 財報期間與來源
**Reason**: 本次入口以產業研究為主，不要求公司 UI 展示財報。
**Migration**: 財報入庫、期間、來源、幣別與累計口徑及既有 API 保留，不刪除歷史資料。
