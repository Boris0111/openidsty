---
schema-version: research-v1
entity-id: company-4979-two
kind: company
name-zh: 華星光
aliases:
- Luxnet
- 華星光通
- 華星光通科技股份有限公司
summary: 光通訊元件與模組代工廠，主動元件及模組占營收 86%、晶粒 11%；單一客戶占 86.61%，北美占 86.96%，最大供應商（TOSA）占進貨 73.63%。
legacy-keys:
- 4979.TWO
listings:
- ticker: 4979.TWO
  market: TW
  exchange: ROCO
  share-class: unspecified
  valid-from: null
  valid-to: null
source-identifiers: []
research-depth: deep
reviewed: '2026-11-24'
financial-reporting:
  primary-source-family: tw-mops-summary
  confidence: well-supported
  reviewed: '2026-10-18'
  fiscal-year-end: 12-31
  calendar-valid-from: '2024-01-01'
  calendar-valid-to: null
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 90 頁）主要商品銷售地區，113 與 114 年度並列
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度（2024–2025 曆年）
roles:
- segment-id: segment-networking
  description: 光收發模組
  tier: 2
  baseline-path: ai-server/networking.md
claims:
- id: product-mix
  statement: 年報揭露 114 年度營業收入 4,384,846 仟元（113 年度 3,451,043 仟元），其中光通訊主動元件及模組 86.35%、晶粒 11.05%、其他 2.60%；商品包括 FP／DFB 雷射與 CW 高功率雷射晶粒、PD／APD 檢光晶粒、TO 與 OSA／BOSA 次模組、資料中心用高速平行光學引擎、相干光收發模組及代工服務。
  confidence: well-supported
  conditions:
  - 營業比重不拆分資料中心與 PON 產品
  reviewed: '2026-11-24'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 72 頁（PDF 第 73 頁）營業比重與商品項目；第 89 頁（PDF 第 90 頁）市場占有率段落
    read-scope: 重新核對商品項目、收入比重與市場占有率段落；確認公司揭露的是產品組合與代工交付，不是特定終端模組料號或具名客戶採用。
    stance: supporting
    applicable-period: 113 至 114 年度
- id: cw-laser-and-engines
  statement: 年報稱自 2019 年與策略夥伴共同開發並量產 CW DFB 雷射晶粒，已獲數家主要客戶採用，並朝 100mW CW DFB 與 100G／200G EML 發展；已完成 800G ZR 模塊與 70mW CW LD，並為雲端資料中心提供 100G–1.6T 光引擎與 CoC 封裝的 OEM／ODM 代工。
  confidence: inference
  conditions:
  - 客戶採用為公司自述，未具名；開發中產品不等於量產
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 72 頁（PDF 第 73 頁）計畫開發之新商品；第 81 頁（PDF 第 82 頁）技術及研發概況
    read-scope: 已讀新商品與研發段落
    stance: supporting
    applicable-period: 114 年度年報
- id: customer-concentration
  statement: 年報主要銷貨客戶以代號揭露，114 年度 LC01082 占 86.61%（113 年度 92.08%）、LC20188 占 10.33%；公司說明與最大客戶合作的產品成長迅速而形成銷貨集中。
  confidence: well-supported
  conditions:
  - 客戶名稱未揭露
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 93–94 頁（PDF 第 94–95 頁）主要銷貨客戶；第 107 頁（PDF 第 108 頁）銷貨集中風險
    read-scope: 已讀主要銷貨客戶表與集中風險
    stance: supporting
    applicable-period: 113 至 114 年度
- id: supplier-concentration
  statement: 年報揭露 114 年度供應商 LV221309 占進貨 73.63%（113 年度 74.20%），該供應商在主要原料表中對應次模組（TOSA）；其他原料為 PCB、上蓋、封蓋、軟板與導熱矽膠片。
  confidence: well-supported
  conditions:
  - 供應商以代號揭露；未說明是否為客戶指定料
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 93 頁（PDF 第 94 頁）主要原料之供應狀況與主要進貨廠商
    read-scope: 已讀原料與進貨表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: sales-regions
  statement: 年報揭露 114 年度銷售地區為北美 86.96%、內銷 10.81%、中國大陸 1.49%、其他 0.74%。
  confidence: well-supported
  conditions:
  - 地區依銷貨對象，不等於終端部署地點
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 89 頁（PDF 第 90 頁）主要商品之銷售地區
    read-scope: 已讀銷售地區表
    stance: supporting
    applicable-period: 113 至 114 年度
- id: named-competitors
  statement: 年報列出競爭者：收光二極體為 GCS、中國電子科技集團 13 所與 29 所、光環；10G／25G APD 為 Sifotonics、光環、中國電科 44 所、Macom；10G／25G 雷射為西安源杰、武漢敏芯、Macom、Melco 與 Broadcom；代工業務為聯鈞、眾達-KY 與 Fabrinet。
  confidence: well-supported
  conditions:
  - 競爭者依產品線列出，部分僅針對 10G／25G 世代
  reviewed: '2026-10-18'
  evidence:
  - source-id: luxnet-annual-report-2025
    url: https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&
    locator: 114 年度年報第 81 頁（PDF 第 82 頁）競爭情形
    read-scope: 已讀競爭段落
    stance: supporting
    applicable-period: 114 年度年報
- id: optical-engine-and-coherent-boundary
  statement: "華星光 114 年報商品項目列出平行光引擎、相干光收發模組及代工。800G ZR 另列為已完成開發產品，100G–1.6T 光引擎與 CoC 封裝為 OEM／ODM 服務。"
  confidence: well-supported
  conditions:
  - "光引擎或 CoC 是下游整合前交付，成品相干模組是不同產品。報告未揭露 800G ZR 量產或具名平台。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: luxnet-annual-report-2025-ir
    url: https://www.luxnetcorp.com.tw/storage/architecture/page~103/page~123/114_4.pdf
    locator: "第 72、81、83 頁（PDF 73、82、84）"
    read-scope: "已讀商品表、OEM／ODM 及 800G ZR 開發列。"
    stance: supporting
    applicable-period: "114 年度"
- id: cw-dfb-die-delivery
  statement: "華星光 114 年報自述 CW DFB 晶粒已合作開發量產及獲未具名採用，並記錄 70／100 mW CW LD 開發。公司沿革分別列 70 mW CWDM 製程面向 800G、100 mW 面向 1.6T。"
  confidence: well-supported
  conditions:
  - "兩種功率只對應公開用途與開發紀錄。量產自述限 CW DFB 家族，未證明特定功率或 200G EML 已批量出貨。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: luxnet-annual-report-2025-ir
    url: https://www.luxnetcorp.com.tw/storage/architecture/page~103/page~123/114_4.pdf
    locator: "第 72、81、83 頁（PDF 73、82、84）"
    read-scope: "已讀 CW DFB 晶粒合作、採用描述與產品研發。"
    stance: supporting
    applicable-period: "114 年度"
  - source-id: luxnet-cwdm-milestones
    url: https://www.luxnetcorp.com.tw/about-111-page179
    locator: "民國 112、113 年沿革"
    read-scope: "已讀製程開發、應用及組裝技術。"
    stance: supporting
    applicable-period: "2023／2024 里程碑，2026-11-24 查閱"
- id: optical-contract-manufacturing-comparison
  statement: "華星光年報列 OEM／ODM 光引擎與 CoC 代工；Fabrinet 官網列光封裝、主被動對準及 NPI 到量產整合。兩者可在相同工序和驗收條件下比較代工。"
  confidence: well-supported
  conditions:
  - "所讀資料未提供同一 800G 模組 BOM、良率、交期或客戶。"
  reviewed: '2026-11-24'
  evidence:
  - source-id: luxnet-annual-report-2025-ir
    url: https://www.luxnetcorp.com.tw/storage/architecture/page~103/page~123/114_4.pdf
    locator: "第 81 頁（PDF 82）競爭與技術"
    read-scope: "已讀代工服務與比較對象。"
    stance: supporting
    applicable-period: "114 年度"
  - source-id: fabrinet-optical-manufacturing-services
    url: https://fabrinet.com/markets/opticalcommunications
    locator: "Optical Communications、Capabilities、Experience"
    read-scope: "已讀對準、封裝與量產服務交付。"
    stance: supporting
    applicable-period: "2026-11-24 查閱"
gaps:
- status: not-public
  reason: 年報未揭露客戶名稱、資料中心與 PON 產品的營收拆分，也未說明最大供應商是否為客戶指定料。
---

## 供應角色

華星光通科技股份有限公司（LuxNet Corporation，4979.TWO）交付[雷射晶粒](/next?focus=product-inp-laser-chip)、光學次模組、光引擎代工及[相干收發模組](/next?focus=product-optical-transceiver)。

華星光在[網路環節](/next?focus=segment-networking)屬[光收發模組](/next?focus=role-optical-module)，以代工方式供應光學次模組、光學引擎與[光收發模組](/next?focus=product-optical-transceiver)；同時自製雷射晶粒，屬[光通訊雷射與光電晶片](/next?focus=role-optical-chip)。

## 研究界線

重讀 114 年度年報商品、技術、開發成功品項與市場段；另對照官方沿革 70／100 mW 的應用。技術開發與完整商品採用分列。

本頁以 114 年度股東會年報為依據。客戶與供應商以代號揭露；CW 雷射獲客戶採用屬公司自述。模組與晶粒分屬兩個角色，營收也分開揭露（86.35% 與 11.05%），不合併比較。

## 產品與用途

70 mW CW LD 面向 800G，100 mW CWDM LD 製程對應 1.6T 開發，兩項功率本身不代表確定出貨。CoC、100G–1.6T 光引擎與已完成開發的 800G ZR 相干模組各有不同交付。

- **雷射與檢光晶粒**：FP、DFB、CW 高功率雷射，PD、EMPD、APD（第 72 頁）。
- **次模組**：TO、OSA、PON 用 BOSA（第 72 頁）。
- **資料中心**：高速平行光學引擎、100G–1.6T 光引擎與 CoC 封裝代工（第 72、81 頁）。
- **相干光模組**：年報列出相干光模組為主要商品，並揭露完成 800G ZR 模塊開發。800G ZR 面向資料中心互連，和[光收發模組](/next?focus=product-optical-transceiver)頁用來解釋機房內 Ethernet 的 VR8／FR／FR4 屬不同光路。年報未揭露 800G ZR 料號的出貨量或採用客戶。[114 年度年報，頁 72、81](https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=4979&year=115&mtype=F&)

## 商業模式

利用自有及合作的晶粒能力、光耦合與次模組／光引擎製程提供代工服務，完工交付可能是 chip-on-carrier、光引擎或模組，需核對委託範圍。

以研發、設計、生產與 ODM／OEM 代工為主（第 72 頁）。114 年度營收 4,384,846 仟元，較 113 年度成長約 27%。

## 客戶與供應商

年報提到 CW DFB 家族量產及未具名採用，所讀資料未揭露各 CW 功率或 800G ZR 的合格客戶、採購與出貨。TOSA 原料供應商也僅以代號揭露。

單一客戶 LC01082 占 86.61%，第二大客戶占 10.33%（第 93–94 頁）。最大供應商占進貨 73.63%，對應 TOSA 次模組（第 93 頁）。客戶與供應商名稱都未揭露。

## 競爭與替代

與 Fabrinet 可比較定制光組件封裝、主被動對準、整合及 NPI／量產服務，依同一產品工序、光耦合容限、測試責任及量產規格；Broadcom 雷射則只在相同波長、功率和晶粒交付條件下比較。

年報依產品線列出競爭者：雷射晶粒包括 [Broadcom](/next?focus=company-avgo)、Macom、源杰與敏芯；代工業務包括聯鈞、眾達-KY 與 Fabrinet（第 81 頁）。年報也說 2016 年起中國廠商的規模與技術快速提升。

## 業務曝險

主動元件及模組包含光引擎、相干模組及其他交付。若高速平台改採矽光子的 CW 架構，需求仍需按光源功率及耦合的實際選用查證。

114 年度北美銷售占 86.96%，最大客戶占 86.61%。主動元件及模組合計占 86.35%，涵蓋多種產品。評估 AI 資料中心曝險仍需產品別營收、實際出貨與終端用途的揭露，目前只能確認銷貨集中與產品應用範圍。

## 風險

營收與採購集中，且雷射及光引擎分工依賴合作、光耦合良率和客戶驗收。200G EML 仍按各次產品文件判斷採用狀態。

- **單一客戶**：最大客戶占營收八成以上。
- **單一供應商**：TOSA 供應商占進貨七成以上。
- **中國競爭**：中國光元件廠規模與技術快速提升（第 81 頁）。
- **匯率**：營收與成本多以外幣計價（第 105 頁）。

## 財務可取性

公開年報可核兩類營業占比及客戶代號。未揭露 70 mW、100 mW、200G EML、800G ZR 及各代工服務的個別營收。

- 月營收、損益與負債摘要可由櫃買中心公開資料自動取得。
- 營業現金流、資本支出需由年報合併財報人工補錄。
- 客戶名稱與資料中心營收拆分：年報未公開。
