---
segment: power
name_zh: 電源與供電架構
layer: ai-server
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2308.TW"
    name_zh: 台達電
    role: 伺服器電源與供電架構
    tier: 1
  - ticker: "2301.TW"
    name_zh: 光寶科
    role: 伺服器電源
    tier: 1
  - ticker: "6282.TW"
    name_zh: 康舒
    role: 電源供應器
    tier: 2
  - ticker: "MPWR"
    name_zh: 芯源系統
    role: 電源管理晶片
    tier: 1
  - ticker: "VICR"
    name_zh: Vicor
    role: 高密度電源模組
    tier: 2
upstream: [power-discrete]
downstream: [odm, datacenter]
themes: [liquid-cooling, 800vdc, power-bottleneck]
kpis:
  - 單機櫃供電價值量
  - 高壓直流架構採用比重
  - 電源轉換效率等級
signals:
  - 供電架構世代轉換的規格定案
  - 備援電池模組規格變動
---

## 環節定義

把設施輸入電力轉成伺服器、加速器及控制電路可用的電壓，涵蓋 PSU、power shelf、DC/DC 模組與電源管理晶片。BBU（battery backup unit）在失去輸入電力或負載瞬變時提供備援與緩衝，與機房 UPS 的位置、持續時間及保護範圍不同。晶片與功率元件的底層供應歸 `power-discrete`，機櫃配置歸 `odm`，設施部署及電力取得歸 `datacenter`。

## 技術變數

既有架構常以機櫃 power shelf 供低壓直流，再於板端降至晶片電壓；800VDC 目標是把主要 AC/DC 轉換移至較集中的位置，以高壓直流分配後再就近降壓。較高電壓可降低同功率下的電流與導體損耗，但系統仍需評估隔離、電弧、觸電保護、連接器與轉換效率，不能只看電壓。BBU、電容與控制策略分別應對不同時間尺度的負載變動。

**well-supported**：NVIDIA 將原生 800VDC 機櫃的大規模部署放在後續平台 roadmap，並描述電力轉換、儲能與合作夥伴；台達的展示證明方案開發。**needs verification**：展示及生態系名單尚不能證明各廠取得量產訂單。[800VDC 架構](https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-generation-of-ai-factories/)、[儲能與供電生態系](https://developer.nvidia.com/blog/building-the-800-vdc-ecosystem-for-efficient-scalable-ai-factories/)、[台達展示](https://www.deltaww.com/en-US/press/40334)。

## 玩家格局

台達電（2308.TW）覆蓋電源供應器與系統供電方案；光寶科（2301.TW）供應伺服器電源；康舒（6282.TW）是電源供應器玩家。美股芯源系統（MPWR）偏向 PMIC 與板端電力轉換，Vicor（VICR）偏向高密度電源模組，兩者不能以整櫃 PSU 的出貨口徑直接比較。台廠的系統電源與美廠的晶片／模組是本環節不同子角色，`tier` 表示地圖中的供應重要性，不是已核實的市佔排名。

## 傳導鏈

`power-discrete → power → odm`：功率元件耐壓、導通與切換損耗影響 PSU/DC/DC 的效率和散熱，再限制可交付機櫃功率。`power → datacenter → compute` 表示設施供電改善能解除部署瓶頸並回頭形成晶片需求，並非電源廠直接向晶片設計商出售伺服器。經 `800vdc` 題材可連到 `interconnect` 的高壓連接介面；經 `liquid-cooling` 連到 `thermal`。**inference**：每櫃功率提高可增加電源價值量，但減少轉換級數也可能移轉原有 PSU 的收入位置。

## 監測指標

追蹤每櫃電源／BBU 價值量、效率曲線（包含部分負載）、功率密度、備援時間及高壓方案的認證與量產占比。從法說會區分伺服器電源、一般電源與設施電力設備收入；以具名客戶認證、定案規格、量產出貨或訂單驗證架構切換，不把總營收成長全歸給 800VDC。查核來源為公司 IR、公開申報、平台技術文件及規格組織的公開文件。

## 風險

高壓直流的安全法規、可維修性與互通性可能拖慢採用；供電故障的保固責任比單一模組更大。架構把轉換移至機櫃外，可能使設施供應商獲利而既有 PSU 產品承壓。BBU 受電池壽命、熱失控管理及供應鏈影響；客戶平台延後、功率元件交期或效率認證未過，都可能阻礙出貨。
