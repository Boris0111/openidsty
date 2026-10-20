---
segment: test
name_zh: 測試與探針
layer: semiconductor
position: 3
market_coverage:
  tw: present
  us: present
  led_by: [TW]
companies:
  - ticker: "2449.TW"
    name_zh: 京元電
    role: 晶圓測試與成品測試
    tier: 1
  - ticker: "3264.TWO"
    name_zh: 欣銓
    role: 晶圓測試
    tier: 2
  - ticker: "6515.TW"
    name_zh: 穎崴
    role: 測試座
    tier: 1
  - ticker: "6223.TWO"
    name_zh: 旺矽
    role: 探針卡與測試設備
    tier: 1
  - ticker: "TER"
    name_zh: 泰瑞達
    role: 測試機台
    tier: 1
  - ticker: "6857.T"
    name_zh: 愛德萬測試
    role: 測試機台
    tier: 1
upstream: [equipment, foundry]
downstream: [advanced-packaging]
themes: []
kpis:
  - 測試機台與測試座出貨量
  - 高速測試營收佔比
  - 稼動率與測試工時
signals:
  - 高階加速器測試時間拉長帶動的設備需求
  - 探針卡規格世代轉換
downstream-relations:
  advanced-packaging:
    kind: supply
    summary: 測試與探針至先進封裝：晶圓／已知良品 die、封裝後與系統相關測試服務及介面。
    items:
    - 晶圓／已知良品 die、封裝後與系統相關測試服務及介面
    dependencies:
    - 測試程式、探針／socket、功耗散熱與良品判準
    conditions:
    - 測試涵蓋封裝失效風險且治具與目標產品相容
    confidence: inference
    evidence: []
    gaps:
    - 缺少具名封裝的測試覆蓋、良率分解、重測與探針／ATE 資格，不能只由封裝產量估算測試收入。
    reviewed: '2026-10-16'
technical-profile:
  product-boundary: wafer sort、final test、SLT、ATE 與探針／socket 各有角色；測試服務、設備及接觸介面採不同收入單位。
  adoption-conditions:
  - 按目標失效機制、電力／溫控、接觸介面與測試程式核對覆蓋及誤判率。
  bottlenecks:
  - 測試時間、並行度、接觸壽命與熱控可能限制產能；工時延長不一定等比例增加收入。
  substitution-limits:
  - SLT 補充系統環境驗證，不能直接替代全部 ATE 或封裝前 KGD 篩選。
  claims:
  - id: slt-complement
    statement: Teradyne 公開文章將 SLT 與 ATE 視為互補，並列供電、熱、互連及韌體失效範圍；不構成全產業份額證據。
    confidence: well-supported
    evidence:
    - source-id: teradyne-slt-technical
      url: https://www.teradyne.com/2026/08/24/slt-in-the-ai-era-validating-reliability-at-scale/
      locator: Why System-Level Test Matters Now／SLT as a Complement
      read-scope: 已讀指定公開說明；沒有取得客戶完整設計、測試或認證檔
  evidence-gaps:
  - 未取得指定 chiplet／HBM 產品的測試覆蓋、重測、良率分解與治具資格。
  reviewed: '2026-10-16'
---

## 環節定義

以 wafer sort、final test 與 system-level test（SLT）確認晶片及模組符合功能、電氣、溫度與可靠度要求，涵蓋測試服務、ATE、探針卡及測試座。服務按工時／測試量收費，設備與介面按機台及耗材收費，不能把不同收入口徑當成同一市場。本圖 `test → advanced-packaging` 主要表示封裝前良品篩選的重要性，不表示封裝後沒有測試。

## 技術變數

高 pin count、高速介面、功耗及熱密度提高接觸、訊號與溫控要求；chiplet／HBM 的昂貴整合使 known good die 更重要。SLT 在接近實際工作負載的環境找出 ATE 不易重現的失效，是互補驗證，不能直接取代所有晶圓與成品測試。**well-supported**：設備供應商說明 AI 封裝的系統測試要求；其產品宣稱仍需客戶使用證據支持商業份額。[Teradyne SLT 說明](https://www.teradyne.com/2026/08/24/slt-in-the-ai-era-validating-reliability-at-scale/)。

## 玩家格局

台股京元電（2449.TW）及欣銓（3264.TWO）主要提供測試服務；穎崴（6515.TW）提供測試座，旺矽（6223.TWO）提供探針卡與相關設備。美股泰瑞達（TER）與日股愛德萬測試（6857.T）提供 ATE 等測試系統。台灣服務／接觸介面供應鏈與美日機台供應鏈互補；`led_by: [TW]` 指本圖關注的服務及介面地位，不表示台灣主導所有 ATE。

## 傳導鏈

`equipment / foundry → test → advanced-packaging`：製造良率與測試能力影響可供封裝的良品，測試不足可能讓昂貴的多晶片模組報廢。CoWoS 擴產可從 `advanced-packaging.upstream` 反查測試服務與探針玩家。**inference**：測試時間拉長，在機台產能與收費不變時增加工時需求，但也可能成為產線瓶頸；需查並行測試、程式最佳化和報價，不能假定收入等比例增加。

## 監測指標

追蹤測試工時、稼動率、機台驗收、探針卡／測試座出貨及使用壽命，高速／高功率應用收入與設備 capex。優先看各公司法說會、年報、月營收及官方產品文件。收入成長須區分新機台、服務單價與耗材更換；未具名的 AI 客戶認證列 **needs verification**，不從某平台上市自動配對測試供應商。

## 風險

設備投資先於收入，平台延後與利用率下降會壓縮回收；接觸介面磨耗、熱控不良或程式錯誤可能造成良品誤判。客戶內製測試、並行度提高及測試最佳化可能降低外包工時。封裝更複雜既創造測試需求，也提高技術與保固責任。
