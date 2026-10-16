# 環節關係核對矩陣

2026-10-16：29 條既有邊，拓樸不變。以下是供應角色與成立條件的研究投影；結構可達不證明公司交易。每條關係的缺口留在來源 frontmatter，不在上游複製。

| 起點 → 終點 | 類型 | 支持程度 | 待核對項目 |
|---|---|---|---|
| [先進封裝](../industry-map/ai-server/advanced-packaging.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 缺少指定封裝料號與整機主板、散熱模組的驗收對照，不能推定每家封裝商都供應同一 ODM。 |
| [運算晶片](../industry-map/ai-server/compute.md) → 先進封裝 | 供應角色 | 有條件推論 | 未取得各 GPU／ASIC 的 bump map、已知良品 die 測試覆蓋與封裝良率，不由晶片 roadmap 推定封裝訂單。 |
| [資料中心與雲端業者](../industry-map/ai-server/datacenter.md) → 運算晶片 | 需求回饋 | 有條件推論 | 尚未逐一拆出各雲端業者的 GPU／ASIC 採購金額、料號、交付及收入認列，不由總 capex 倒推。 |
| [EDA 工具與矽智財](../industry-map/semiconductor/eda-ip.md) → 運算晶片 | 供應角色 | 有條件推論 | 缺少指定晶片 tape-out 所用工具版本、IP 授權及認證證據；不以同環節名單推定所有工具可互替。 |
| [EDA 工具與矽智財](../industry-map/semiconductor/eda-ip.md) → 網通與光通訊 | 供應角色 | 有條件推論 | 未取得具名網路 ASIC 的 IP 授權、工具認證與矽後測試，不能由規格發布推定 IP 收入。 |
| [半導體設備](../industry-map/semiconductor/equipment.md) → 晶圓代工 | 供應角色 | 有條件推論 | 尚缺各機台在指定產線的驗收、產出及認列日期；客戶土建 capex 不能全數當設備訂單。 |
| [半導體設備](../industry-map/semiconductor/equipment.md) → 先進封裝 | 供應角色 | 有條件推論 | 未取得特定封裝路線的機台配置、節拍、良率及驗收對照；不能把 EUV 設備需求套入所有封裝。 |
| [半導體設備](../industry-map/semiconductor/equipment.md) → 測試與探針 | 供應角色 | 有條件推論 | 缺少機台料號與測試服務流程的邊界對照，本清單不證明 ATE、量測及探針卡由同一家公司供應。 |
| [半導體設備](../industry-map/semiconductor/equipment.md) → 記憶體 | 供應角色 | 有條件推論 | 未取得各記憶體廠的製程設備清單、堆疊瓶頸與擴產驗收，不能由 HBM 需求直接推定所有設備受惠。 |
| [晶圓代工](../industry-map/semiconductor/foundry.md) → 運算晶片 | 供應角色 | 有條件推論 | 缺少個別 GPU／ASIC 的良率、晶圓投入及交付份額，不能從節點名稱推定性能或訂單。 |
| [晶圓代工](../industry-map/semiconductor/foundry.md) → 網通與光通訊 | 供應角色 | 有條件推論 | 未取得具名交換器 ASIC／DSP 的代工節點、產能及良率，不把系統廠視為同一晶片設計角色。 |
| [晶圓代工](../industry-map/semiconductor/foundry.md) → 測試與探針 | 供應角色 | 有條件推論 | 缺少具名製程的 wafer map、test coverage 與測試委外合約；不由代工產能推定全部測試公司收入。 |
| [晶圓代工](../industry-map/semiconductor/foundry.md) → 功率與分離式元件 | 供應角色 | 有條件推論 | 未取得各功率產品的實際代工／IDM 比例與晶圓材料，不把先進邏輯代工視為所有功率元件供應者。 |
| [連接器、線材與滑軌](../industry-map/ai-server/interconnect.md) → 散熱 | 供應角色 | 有條件推論 | 缺少特定快接頭與冷板／歧管組合的漏率、壽命及材料相容性測試；滑軌及一般插槽不視為快接頭。 |
| [連接器、線材與滑軌](../industry-map/ai-server/interconnect.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 尚缺個別平台的線束、插槽、電力接頭及滑軌 BOM；不能把 rail 名稱直接配對到單一公司。 |
| [半導體材料](../industry-map/semiconductor/materials.md) → 晶圓代工 | 供應角色 | 有條件推論 | 缺少客戶材料清單、純度／缺陷限值與用量；不能把所有材料公司視為同種耗材供應者。 |
| [半導體材料](../industry-map/semiconductor/materials.md) → 先進封裝 | 供應角色 | 有條件推論 | 尚缺各封裝平台對矽中介層、封裝化學品及污染控制的實際用料，不能由擴產推定全清單受惠。 |
| [半導體材料](../industry-map/semiconductor/materials.md) → ABF 載板 | 供應角色 | 仍待核實 | 目前半導體材料公司清單不足以證明 ABF 膜或其他載板材料的直接供應，缺具名材料料號與供應商資格。 |
| [半導體材料](../industry-map/semiconductor/materials.md) → 印刷電路板與銅箔基板 | 供應角色 | 仍待核實 | 本材料清單不直接代表低損耗 CCL／銅箔供應商；尚缺板材配方、料號與實際供應對照。 |
| [記憶體](../industry-map/ai-server/memory.md) → 先進封裝 | 供應角色 | 有條件推論 | 未取得指定 HBM stack／base die 組合的客戶認證、測試覆蓋與封裝良率，不能由送樣推定量產。 |
| [網通與光通訊](../industry-map/ai-server/networking.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 缺少特定 ASIC／DSP／模組與 ODM 平台的互通實測與採購證據，不能由同一環節推定相同產品。 |
| [系統組裝與機櫃整合](../industry-map/ai-server/odm.md) → 資料中心與雲端業者 | 供應角色 | 有條件推論 | 未逐案取得工廠驗收、現場驗收、可用 IT 容量與收入認列的對照；出貨不必然代表已上線。 |
| [印刷電路板與銅箔基板](../industry-map/ai-server/pcb.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 缺少平台層疊、損耗預算及合格供應商清單，不能由高速升級推算各 CCL／PCB 公司份額。 |
| [電源與供電架構](../industry-map/ai-server/power.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 未取得指定平台 PSU、BBU、DC/DC 的負載規範、冗餘及保護協調驗證，不把各子系統收入直接相加。 |
| [電源與供電架構](../industry-map/ai-server/power.md) → 資料中心與雲端業者 | 供應角色 | 有條件推論 | 尚缺場址單線圖、備援時數、認證與驗收資料；功率需求成長不等於特定供應商已取得訂單。 |
| [功率與分離式元件](../industry-map/semiconductor/power-discrete.md) → 電源與供電架構 | 供應角色 | 有條件推論 | 缺少指定 PSU／DC-DC／高壓架構的元件 BOM 與認證；Si、SiC、GaN 不能僅憑材料名互替。 |
| [ABF 載板](../industry-map/ai-server/substrate.md) → 先進封裝 | 供應角色 | 有條件推論 | 未取得各封裝平台的載板設計規則、材料認證與量產良率；載板與中介層不是同層替代品。 |
| [測試與探針](../industry-map/semiconductor/test.md) → 先進封裝 | 供應角色 | 有條件推論 | 缺少具名封裝的測試覆蓋、良率分解、重測與探針／ATE 資格，不能只由封裝產量估算測試收入。 |
| [散熱](../industry-map/ai-server/thermal.md) → 系統組裝與機櫃整合 | 供應角色 | 有條件推論 | 尚缺指定冷板／CDU 與平台的熱阻、壓降、材料相容及維修驗證，不能把全部熱管理收入視為冷板收入。 |
