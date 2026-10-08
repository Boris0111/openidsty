---
theme: custom-asic-vs-gpu
name_zh: 客製 ASIC 與通用 GPU 的路線競爭
status: scaling
segments: [compute, eda-ip, networking]
beneficiaries:
  - "AVGO"
  - "MRVL"
  - "3661.TW"
  - "3443.TW"
milestones:
  - date: 2026
    event: 核對客製加速器的商業收入及客戶部署
    evidence: Broadcom FY2026 Q3 財報量化 AI 半導體收入並說明客製加速器需求；自研部署占比另需雲端客戶揭露
  - date: 2026-Q2
    event: 待核實設計服務廠的新案歸屬與 tape-out
    evidence: 具名專案公告、客戶確認及 NRE／量產收入；供應鏈傳聞與設計洽談不足以確認得標
  - date: 2027
    event: 比較特定工作負載下 GPU／ASIC 的採購與總成本
    evidence: 同工作負載、軟體及利用率口徑的性能／能耗與具名採購組合；供應商毛利率不能代替客戶 TCO
---

## 題材範圍

比較可程式化 GPU 與為特定工作負載設計的 ASIC 在性能、軟體、生產規模及總成本上的分工。客製晶片不必然取代通用 GPU；需求成長時兩者可同時擴張，train／inference 也不是兩種硬體的絕對界線。

## 傳導與受惠條件

題材連接 `compute / eda-ip / networking`：專案先帶來設計服務及 IP 授權，量產再傳到製造、封裝與網路。AVGO、MRVL 是客製與連接方案候選，3661.TW、3443.TW 是設計服務候選。**inference**：案件增多不等於每家都得標，`beneficiaries` 需逐案確認客戶、NRE 與量產收入；總 AI 網路收入不能全算 ASIC 收入。

## 狀態判定依據

查核日期：2026-10-07。採 `scaling`。**well-supported**：Broadcom FY2026 Q3 財報量化已實現 AI 半導體收入，並明確把需求與客製加速器及網路業務連結，支持商業採購與出貨，不再只是設計提案。[Broadcom FY2026 Q3 財報](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial)。財務口徑包含網路，未將全額稱為純 ASIC 收入；各雲端自研比重與台灣設計服務廠得標仍列 **needs verification**。若專案取消、量產延後或成本優勢消失，需重新校準狀態。
