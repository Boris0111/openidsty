# Spec Delta

## MODIFIED Requirements

### Requirement: 驗證後完整發布與可還原

發布 MUST 先完成全體 Schema、引用、關係一致性、資產及預覽驗證，再保存不可變的 Git 內容 commit 與完整讀取投影。只有所有必要產物備妥後才能切換正式版本。失敗 MUST 保留舊版；還原 MUST 指向先前完整版本並保留歷史，不刪除事件或指標修訂。

#### Scenario: 發布一半失敗
- **WHEN** Git 內容已保存但投影建立失敗
- **THEN** 讀者仍取得舊版，維護者可看到失敗階段並重試

#### Scenario: 還原已發布內容
- **WHEN** 維護者選擇先前完整研究版本還原
- **THEN** 地圖、公司、產品及引用一致回到該版，動態指標與事件歷史保留
