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
downstream-relations:
  odm:
    kind: supply
    summary: 散熱至系統組裝與機櫃整合：散熱模組、冷板、CDU 與液路整合等不同熱管理子角色。
    items:
    - 散熱模組、冷板、CDU 與液路整合等不同熱管理子角色
    dependencies:
    - 機構接觸、水路、流量壓降與設施排熱責任
    conditions:
    - 指定熱負載、冷卻液及維修條件完成整機驗證
    confidence: inference
    evidence: []
    gaps:
    - 尚缺指定冷板／CDU 與平台的熱阻、壓降、材料相容及維修驗證，不能把全部熱管理收入視為冷板收入。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: 冷板做晶片至流體熱交換，歧管分配流量，CDU 管理技術冷卻迴路與排熱交界；設施水路是另一責任層。快接頭歸互連子角色，整櫃與場址驗收另列。
  adoption-conditions:
  - 先核對熱負載、允許溫度、流量／壓降與冷卻液；CDU、歧管及冷板必須以同一迴路驗證。
  - 材料接液相容、過濾及維修程序要符合實際安裝條件，不以單一元件型錄代替整體驗收。
  bottlenecks:
  - 壓降、流量分布、堵塞／污染與漏液會限制可用散熱能力；須核對冷板與泵浦／CDU 的共同工作點。
  - 設施側排熱與水路未完成時，冷板製成不代表整櫃已能上線。
  substitution-limits:
  - 氣冷、單相冷板、兩相與浸沒涉及不同流體、材料及維修條件，不能只依 TDP 宣稱必然替代。
  - 標準接頭外形相同不等於指定冷卻液、密封材料與壓力條件下可直接互換。
  claims:
  - id: tcs-fws-boundary
    statement: OCP 需求文件區分 TCS 與 FWS，且不涵蓋 FWS；它不是完整設計規格。
    confidence: well-supported
    evidence:
    - document-id: ocp-cold-plate-requirements
      version-id: revision-one
      locator: loop-boundary
  - id: wetted-materials
    statement: 材料相容與過濾需按實際迴路核對；不能把一般接液材料清單當相容認證。
    confidence: well-supported
    evidence:
    - document-id: ocp-cold-plate-requirements
      version-id: revision-one
      locator: materials-flow
    - document-id: ocp-cold-plate-requirements
      version-id: revision-one
      locator: serviceability
  evidence-gaps:
  - 缺少各候選供應商指定料號的熱阻／壓降曲線、冷卻液相容與壽命資料。
  - OCP PDF 本機取得 403；已讀範圍為 web 擷取章節，未完成全部條文或客戶驗收核讀。
  reviewed: '2026-10-16'
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
