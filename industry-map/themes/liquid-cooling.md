---
theme: liquid-cooling
name_zh: 液冷散熱
status: scaling
segments: [thermal, odm, datacenter, power]
beneficiaries:
  - "3017.TW"
  - "3324.TW"
  - "VRT"
  - "2308.TW"
milestones:
  - date: 2026-Q1
    event: 核對具名高密度平台的液冷配置與交付
    evidence: 平台正式規格、客戶交付或 ODM 法說會區分液冷機櫃出貨；不把單一平台配置擴大為全市場預設
  - date: 2026
    event: 核對冷板與 CDU 的商業出貨、收入及產能利用
    evidence: 供應商財報明確量化液冷產品收入，並與產能爬坡／客戶訂單交叉核對；月營收總額不能代替液冷收入
  - date: 2027
    event: 待比較新建案與改造案的 L2L／L2A 方案組合
    evidence: 同口徑的具名機房採購規格及熱管理供應商產品收入；沒有完整樣本時不宣稱一種方案已超越另一種
---

## 題材範圍

以 direct-to-chip 冷板、歧管與 CDU 為主要追蹤範圍，同時觀察設施水路改造及其他冷卻路線。冷板、機櫃 CDU 與機房側設備是不同收入層次，液冷滲透率須說明分母。高密度 AI 平台的採用不表示一般伺服器已全部轉液冷。[Supermicro 液冷方案](https://www.supermicro.com/en/solutions/liquid-cooling)。

## 傳導與受惠條件

題材橫向連接 `thermal / odm / datacenter / power`，透過 ODM 的共同上游再取得 PCB 與連接介面。3017.TW、3324.TW 是散熱零組件候選，VRT 偏熱管理系統，2308.TW 同時有供電／冷卻方案。**inference**：液冷配置可能增加每櫃價值量，但個別受惠須看實際採購項目；`beneficiaries` 不代表已核實每家的液冷收入或保證毛利上升。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`，以產業商業出貨及已實現液冷設備收入為依據。**well-supported**：AAON 的 2025 Q3 公開財報單獨量化 BASX 液冷產品銷售，證據不是示範機或未來市場預估；2025 Q4 財報亦確認冷卻設備訂單與出貨增長。[液冷產品收入證據](https://www.sec.gov/Archives/edgar/data/824142/000082414225000197/aaonq32025pressreleaseexs.htm)、[後續財報佐證](https://www.sec.gov/Archives/edgar/data/824142/000082414226000003/liveaaonpressreleaseexs.htm)。這是題材狀態的業界證據，不能替代上述四個候選公司的各自財報；冷板廠收入占比與 L2L／L2A 分配仍需另查。尚未達到全市場標準配置，故不採 `mature`。
