---
segment: thermal
name_zh: 散熱
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "3017.TW"
    name_zh: 奇鋐
    role: 均熱板與氣冷散熱模組
    tier: 1
  - ticker: "3324.TW"
    name_zh: 雙鴻
    role: 液冷冷板、歧管與冷卻液分配單元
    tier: 1
  - ticker: "2421.TW"
    name_zh: 建準
    role: 散熱風扇
    tier: 2
  - ticker: "VRT"
    name_zh: Vertiv
    role: 資料中心熱管理與冷卻液分配單元
    tier: 1
  - ticker: "PRIVATE:boyd"
    name_zh: Boyd
    role: 液冷冷板
    tier: 2
upstream: [interconnect]
downstream: [odm]
themes: [liquid-cooling]
kpis:
  - 液冷方案滲透率
  - 單機櫃散熱價值量
  - 冷板與分流單元的產能與交期
signals:
  - 機櫃世代的散熱架構轉換
  - 雲端業者新建案的液冷標案歸屬
---

## 環節定義

將晶片產生的熱移到機房可排出的地方，產品包含風扇、熱管、均熱板（VC）、冷板、歧管（manifold）與冷卻液分配單元（CDU）。氣冷與液冷同屬散熱，但冷板、歧管與 CDU 分別負責熱交換、分流與迴路管理，不能混作同一產品。本環節承載熱管理方案；快接頭及線材歸 `interconnect`，整櫃驗證與交付歸 `odm`。

## 技術變數

氣冷以風量、靜壓與 VC 擴散能力對應熱密度；direct-to-chip 液冷以冷板接觸、流量、壓降與冷卻液相容性決定可靠度。液冷伺服器仍可能保留風扇處理非液冷元件，不能把液冷滲透率當成風扇需求歸零。L2A CDU 把熱排到空氣，L2L CDU 連接設施水路；新建機房與既有機房改造的選擇不同。浸沒式與兩相冷卻另涉及介電液、材料與維修流程，不能由樣機推定取代單相冷板。

**well-supported**：雙鴻的公開產品說明區分冷板、歧管、CDU 與快接頭；系統整合商的液冷方案也區分晶片側及設施側。這支持產品邊界，不代表所有列名玩家都量產相同產品。[雙鴻產品說明](https://www.auras.com.tw/News/NewsContent/14-8)、[Supermicro 液冷方案](https://www.supermicro.com/en/solutions/liquid-cooling)。

## 玩家格局

台股的奇鋐（3017.TW）以 VC、氣冷模組及整體散熱供應能力列為主要玩家；雙鴻（3324.TW）覆蓋冷板與液冷迴路組件；建準（2421.TW）著重風扇，受惠條件取決於殘餘氣冷負載與產品升級。美股 Vertiv（VRT）偏向機房、機櫃熱管理與 CDU，與晶片冷板廠的收入邊界不同。Boyd（PRIVATE:boyd）提供冷板及液冷系統，保留非上市主體鍵以表示實際供應角色，不能把該鍵當可交易代號。`led_by: [TW]` 描述台灣在伺服器散熱零組件的供應地位，並不宣稱台灣主導所有設施冷卻設備。[Boyd 液冷迴路說明](https://cn.boydcorp.com/about-boyd/resources/technical-papers-and-guides/coolant-distribution-unit-technical-paper.html)。

## 傳導鏈

`interconnect → thermal → odm`：防漏快接頭、軟管介面與連接可靠度影響液冷系統認證，再影響 ODM 整櫃出貨。經 `liquid-cooling` 題材可跳到 `power` 與 `datacenter`；經共同下游 `odm.upstream` 可取得並列供應的 `pcb`。**inference**：熱密度上升可能同時增加冷板、電源與低損耗 PCB 的價值量，但三者不是彼此直接供貨；PCB 升級須有實際平台規格支持。設施水路未就緒也可能延後整櫃收入，即使冷板已製成。

## 監測指標

液冷滲透率必須先定義分母：AI 伺服器台數、新部署機櫃或散熱營收，三者不可混用。追蹤每櫃散熱價值量、冷板／CDU 的認證轉量產、產能利用率、交期與售後服務比重；分開確認冷板廠、CDU 廠及整合商的收入，避免重複加總。從公開資訊觀測站、公司法說會及產品文件查核；供應商示範機列 **needs verification**，須補具名客戶驗收、出貨或量化收入證據。

## 風險

漏液、腐蝕、堵塞與泵浦失效可能帶來整櫃保固責任；冷板尺寸與介面客製化造成單一平台集中。新世代設計若集中於少數客戶，認證延遲會先打擊利用率。液冷配置增加不保證單家毛利提升，因為價格議價、良率、系統責任及維護成本可能抵銷價值量成長。
