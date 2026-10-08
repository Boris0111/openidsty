---
segment: interconnect
name_zh: 連接器、線材與滑軌
layer: ai-server
position: 2
market_coverage:
  tw: present
  us: present
companies:
  - ticker: "3533.TW"
    name_zh: 嘉澤
    role: 處理器插槽與高速連接器
    tier: 1
  - ticker: "3665.TW"
    name_zh: 貿聯
    role: 高速線材與線束
    tier: 1
  - ticker: "3023.TW"
    name_zh: 信邦
    role: 線材與連接組件
    tier: 2
  - ticker: "APH"
    name_zh: 安費諾
    role: 高速連接器與液冷快接頭
    tier: 1
  - ticker: "2059.TW"
    name_zh: 川湖
    role: 伺服器滑軌與理線機構
    tier: 2
upstream: []
downstream: [thermal, odm]
themes: [800vdc]
kpis:
  - 單機櫃連接器與線材價值量
  - 高速規格世代佔比
  - 銅纜與光纖的方案比重
signals:
  - 機櫃內互連規格世代轉換
  - 銅纜方案延伸或被光學取代的進展
---

## 環節定義

涵蓋伺服器與機櫃之間的電氣、流體及維修介面：處理器插槽、高速連接器、線束、液冷快接頭，以及 rail（機構滑軌）。滑軌負責承重、抽換與理線，與輸送電力的 busbar／power rail 不同；供應商角色應分開比較。此處把滑軌作為機櫃介面群組的子角色，不表示滑軌可替代連接器。高速訊號的 ASIC、DSP 與光模組歸 `networking`，本環節側重實體介面及組裝。

## 技術變數

高速電氣介面看插入損耗、串音、阻抗、接點可靠度與銅纜長度；銅纜轉光纖取決於距離、功耗及維修成本，不能把所有短距連接都視為將被 CPO 取代。800VDC 的介面需要耐壓、爬電距離、電弧管理與插拔保護；液冷快接頭看漏率、流量及插拔壽命。機構滑軌看承重、可抽換空間、免工具安裝、線材／液路彎曲半徑及理線臂干涉。[貿聯 800VDC 介面方案](https://www.bizlinktech.com/de/news/bizlink-advances-800-vdc-power-solutions-for-ai-infrastructure-with-nvidia)、[川湖滑軌與理線產品](https://www.kingslide.com/products_cloud/?___store=default)。

**well-supported**：安費諾公開產品列有 UQD／UQDB 液冷快接頭，故在公司角色中明列此項；其他台廠是否供應同類快接頭不能由「連接器」大類推定。[安費諾液冷連接產品](https://www.amphenol.com/products/connectors?pagenumber=62)。

## 玩家格局

嘉澤（3533.TW）以處理器插槽與高速連接器為主要角色；貿聯（3665.TW）覆蓋高速線材、線束與電力連接方案；信邦（3023.TW）提供線材與連接組件。美股安費諾（APH）供應高速連接器並具廣泛介面產品布局。川湖（2059.TW）是伺服器滑軌及理線機構玩家，已有公開 MGX 合作及產品證據。列入本環節不代表每家公司都供應液冷快接頭或高壓直流產品，個別料號與客戶認證仍須查核。[川湖 MGX 合作說明](https://www.kingslide.com/blog/post/news/identifier/company-news-018/)。

## 傳導鏈

`interconnect → thermal`：流體連接及插拔可靠度影響液冷迴路；`interconnect → odm`：高速線束、插槽、電力介面與滑軌影響整機配置、組裝及維修驗證。透過 `800vdc` 題材取得 `power` 與 `datacenter`，表示新供電架構會同時改變電源與連接要求。**inference**：機櫃更重、液路更多，可能增加滑軌與理線價值量，但需平台機構圖及訂單支持；不由液冷新聞直接推論所有連接器公司受惠。

## 監測指標

追蹤每櫃連接器／線材價值量、高速世代組合、銅與光方案比重、設計導入至量產時間，以及滑軌承重與維修規格變動。公開申報及公司法說會用來確認營收組合，產品型錄與客戶認證用來確認供應角色。**needs verification**：若消息只寫「rail」，先辨認是滑軌、電力母排還是電壓軌；缺少料號時不直接配對公司。

## 風險

標準化介面可能降低差異化，高速規格轉換則可能使既有銅纜產品失去位置。高壓安全及漏液責任提高驗證成本；單一平台的客製模具或滑軌若延後部署，產能與庫存會受影響。連接器、滑軌及光學方案的價值量不可直接相加為一家供應商的可取得市場。
