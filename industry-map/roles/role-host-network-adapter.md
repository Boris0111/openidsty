---
schema-version: research-v1
entity-id: role-host-network-adapter
kind: role
name-zh: "主機網路介面卡"
aliases:
- "host network adapter"
summary: "交付可裝入主機的 NIC，讓系統連接外部網路。"
definition: "設計或整合主機用 Ethernet 或 InfiniBand 介面卡。"
purpose: "按主機插槽與網路埠提供封包傳輸及指定卸載功能。"
boundary: "不含單獨控制器、PCIe retimer、線纜及交換器 ASIC／成品。"
adoption-conditions:
- "以主機卡型、韌體與網路協定判斷交付。"
bottlenecks:
- "主機可用 PCIe lane、散熱與協定互通。"
substitution-limits:
- "卡型及介面相同時仍須核對實際網路部署與驅動。"
reviewed: "2026-11-24"
claims: []
gaps:
- status: not-applicable
  reason: "角色頁列出交付分類，成卡與來源見產品及公司。"
---

## 定義與用途

為伺服器供應[資料中心主機網路介面卡](/next?focus=product-datacenter-network-adapter)，介於主機 PCIe 與交換系統之間。[博通](/next?focus=company-avgo)與[輝達](/next?focus=company-nvda)具公開成卡料號。

## 採用條件與限制

比較同一網路協定、相同埠配置與主機插槽的卡。Ethernet 與 InfiniBand 須按各自拓樸與端點。單獨的 controller 不能據此被視為成卡供應。
