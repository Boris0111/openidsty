# 首條液冷流程走讀

本文件保留 task 3.4 的內容與閱讀驗證。2026-10-16 已取得 Boris 實際走讀回饋，確認沿用本輪閱讀模式並繼續其他分析；task 3.4 完成。完整管理、全鏈導覽與 26 家深研仍依後續 tasks 分別交付。

## 已核讀來源

| 來源 | 實際範圍與界線 |
|---|---|
| [雙鴻 OCP Global Summit 2025](https://www.auras.com.tw/News/NewsContent/14-10/en) | 公開瀏覽器內文，2025-10-15；冷板、歧管、CDU 與研發描述。HTTP 靜態頁只有 JS 外殼，以實際 render 後內文核讀；不把舊新聞當 2026 出貨資料 |
| [Vertiv CoolChip CDU](https://www.vertiv.com/en-us/products-catalog/thermal-management/high-density-solutions/vertiv-coolchip-cdu/) | Product Family、型號表及功能；液對液／液對氣、額定能力的條件。未下載需填表的文件 |
| [Vertiv 液冷公開說明](https://www.vertiv.com/en-us/solutions/learn-about/liquid-cooling-options-for-data-centers/) | 冷板取熱、Distribution、回路及設施整合；未採用市場預測與通用節能百分比 |
| [Vertiv 公司介紹](https://www.vertiv.com/en-us/about/about-us/) | 供電、冷卻、IT 與服務的業務範圍；未把 FY2025 營收摘要轉成液冷占比 |
| [NVIDIA DSX 公開 overview](https://docs.nvidia.com/dsx/facilities-infra/reference-design-overview) | CDU 與獨立二次側回路；overview 引用 2026-08-19 指南 v2.0，未讀 NVOnline 補充文件，也未泛用參考場址的容量與條件 |

查核日皆為 2026-10-16，原來源期間與查核日分開。只保留必要短摘錄或中文整理，不散布公開文件全文。原創桌機／手機圖解由 Schema 與 hash 驗證；它是功能示意，不是公司間交易圖。

## 走讀範圍

1. 冷板的交付邊界與採用條件 → 雙鴻 → 2025 官方產品與研發證據。
2. 液對液 CDU → Vertiv → 型號／場址條件與公司整體業務的界線。
3. 兩個回路圖解、產品能力連線及文字清單，確認沒有畫成雙鴻供貨給 Vertiv。
4. URL 固定研究版本，分享、返回、快速切換與手機選擇後閱讀。

公司仍保留 basic depth，這代表本輪先核對產品範圍；完整客戶、競爭、風險與財務深研在 task 8.2，不以模板或空資料宣稱完成。其他 93 家保留既有角色索引，首輪不是全鏈交付驗收。

## 走讀與 Boris 回饋

預覽：[液冷研究](http://127.0.0.1:3014/next)。首份發布來自 `8480da4`，release `03799774-3553-5ff6-9910-13a68468af15`。桌機／手機截圖存於 `.work/first-flow-review/desktop.png`、`mobile.png`、`auras-mobile.png`。已執行 6 項真實瀏覽器走讀，產品／公司／來源、分享／返回、鍵盤、手機、慢回應與圖解故障皆通過；另修正公司章節 heading 層級與手機小圖間距。

走讀檢查這條路徑是否能辨認交付角色、找到支持判斷的原文、理解不能由產品能力推導客戶及收入的限制。技術測試與 agent 截圖不代替 Boris 的閱讀回饋。

Boris 於 2026-10-16 回覆：

> 目前頁面操作體驗尚可，可依此模式繼續其他分析產出
> 我想確認此產業研究頁籤如何與先前建立之產業地圖連結，操作邏輯與流程是怎麼走

決策：保留這一輪產品交付、角色、條件與原文並置的閱讀模式，繼續既定 change。這是首條流程的繼續指示，不擴張解讀為所有研究內容或桌機／手機各項操作均已獲使用者逐項查核。下一個操作重點是說清楚環節總覽與研究細節的關係；新舊 UI 尚未完整雙向串接，不宣稱已完成 task 6.1。

已核對 `/` 與 `/next` 均可讀；同一已發布版本中，散熱、AI 機櫃冷卻、晶片端取熱、冷板與雙鴻的相鄰節點及 `3324.TW` 身分解析正確。實際入口、現況限制與後續操作方向見 [研究與產業地圖導覽](research-navigation.md)。
