---
schema-version: research-v1
entity-id: company-private-shinko
kind: company
name-zh: Shinko
aliases: ["新光電氣", "新光電氣工業", "SHINKO ELECTRIC INDUSTRIES"]
summary: "日本新光電氣工業的覆晶載板與組裝研究，現行公司承接舊 6967 業務。"
legacy-keys:
- PRIVATE:shinko
listings: []
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
roles:
- segment-id: segment-substrate
  description: 高階 ABF 載板
  tier: 1
  baseline-path: ai-server/substrate.md
claims:
- id: shinko-dll-and-dll3-delivery
  statement: "Shinko 提供 DLL／DLL3 覆晶載板，採 SAP、CO₂／UV、層間疊孔，DLL3 屬 coreless。公告另列玻璃核心 TGV 原型及載板 IATF 16949 認證。"
  confidence: well-supported
  conditions: ["IATF 對應所列據點的設計、製造範圍；不等同 AI 客戶量產。玻璃是原型，DLL 型錄未逐一揭露膜牌號。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: shinko-dll-dll3-substrate
    url: https://www.shinko.co.jp/english/product/package/substrate/dll.php
    locator: "Introduction／Features"
    read-scope: "查 DLL、DLL3、SAP 和孔結構。"
    stance: supporting
    applicable-period: "現行產品頁查核日"
  - source-id: shinko-glass-core-tgv-prototype
    url: https://www.shinko.co.jp/english/news/2026/07/b2e0e1c9fadd06989a3ba3940788615cdb6ddaf4.php
    locator: "ECTC 摘要"
    read-scope: "查玻璃核心原型與測試。"
    stance: supporting
    applicable-period: "ECTC 2025 研究"
  - source-id: shinko-iatf-substrate-certification
    url: https://www.shinko.co.jp/english/news/docs/20250716-01_en.pdf
    locator: "Scope of certification"
    read-scope: "核對 IATF 適用範圍。"
    stance: supporting
    applicable-period: "2025-07-16"
- id: shinko-current-legal-identity
  statement: "舊新光電氣 6967 股票於 2025-06-06 下市，2025-12-01 由 JICC-04 吸收合併並更名為新光電氣工業。"
  confidence: well-supported
  conditions: ["維持 Shinko 的研究 ID 與原 PRIVATE legacy key。舊 6967 只做歷史說明。"]
  reviewed: '2026-11-24'
  evidence:
  - source-id: shinko-jpx-delisting-6967
    url: https://www.jpx.co.jp/english/news/1023/20250520-11.html
    locator: "Delisting Date／Issue Name"
    read-scope: "查歷史 ticker 和日期。"
    stance: supporting
    applicable-period: "2025-05-20 JPX"
  - source-id: shinko-jicc-merger-2025
    url: https://www.shinko.co.jp/ir/kk/
    locator: "吸収合併に関する電子公告"
    read-scope: "查存續公司及法名。"
    stance: supporting
    applicable-period: "2025-12-01 生效"
  - source-id: shinko-pre-delisting-ir-archive
    url: https://www.shinko.co.jp/english/ir/
    locator: "IR Archive／IR News"
    read-scope: "查下市前財報。"
    stance: supporting
    applicable-period: "截至 2025-03 期"
gaps:
- status: not-obtained
  reason: "同封裝條件、孔規、成品良率與價格未取得。"
- status: not-public
  reason: "下市後無現行上市資料；載板專案別客戶、出貨及收入未公開。"
---

## 供應角色

新光電氣工業（SHINKO ELECTRIC INDUSTRIES）交付 DLL／DLL3 [封裝載板](/next?focus=product-abf-substrate)與組裝支援。

## 研究界線

歷史上市主體 6967 於 2025-06-06 下市，同年 12-01 由 JICC-04 吸收舊公司並更名。公司產品能力仍按當前牌號核對。

## 產品與用途

DLL 用 SAP、雷射與 stacked vias；DLL3 去除 core。玻璃 core 原型以 TGV 與熱循環等看可靠度，與有機量產分開。

## 商業模式

產品頁列載板設計、製造及 IC 組裝支援；成品載板與 assembly 有不同交付範圍。

## 客戶與供應商

用途包括伺服器、CPU、GPU、ASIC。既有力成年報具名 Shinko 原料供應，未細分到哪一載板牌號，保留該範圍。

## 競爭與替代

與 IBIDEN 同為完成載板，先對齊 core、孔型、L/S、翹曲、材料及同驗收條件；玻璃原型需另外確認切割與 TGV。

## 業務曝險

高效能伺服器可能增加大面積載板，若改用局部連接、簡化層數或換材料，效果不同。

## 風險

大面積的翹曲、玻璃切割裂紋、品質認證與量產時程皆須獨立確認。IATF 認證只涵蓋公告列出的設計與製造範圍。

## 財務可取性

公開 IR Archive 保留截至 2025-03 的歷史報告。現行實體未見同等上市披露；各產品、專案收入及合格出貨留缺口。
