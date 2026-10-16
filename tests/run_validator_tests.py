#!/usr/bin/env python3
"""驗證器的測試套件。

作法：以 tests/fixtures/valid 作為合法基準，複製到暫存目錄後施加「單點突變」，
每個案例只改一處，確認驗證器攔下該類錯誤並在訊息中指出具體欄位。

用法:
    python tests/run_validator_tests.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import copy
import yaml

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "fixtures" / "valid"
VALIDATOR = ROOT / "scripts" / "validate_map.py"


def run_validator(map_dir: Path, *extra: str):
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', str(VALIDATOR), "--map-dir", str(map_dir), *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def edit(rel: str, old: str, new: str, count: int = -1):
    """回傳一個突變函式：在 rel 檔案中把 old 換成 new。"""

    def mutate(map_dir: Path) -> None:
        path = map_dir / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError("突變目標不存在於 {}: {!r}".format(rel, old[:60]))
        path.write_text(text.replace(old, new, count) if count > 0 else text.replace(old, new), encoding="utf-8")

    return mutate


def add_file(rel: str, content: str):
    def mutate(map_dir: Path) -> None:
        path = map_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return mutate


def copy_as(src_rel: str, dst_rel: str):
    def mutate(map_dir: Path) -> None:
        shutil.copyfile(map_dir / src_rel, map_dir / dst_rel)

    return mutate


def strip_frontmatter(rel: str):
    def mutate(map_dir: Path) -> None:
        path = map_dir / rel
        text = path.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1]
        path.write_text(body.lstrip("\n"), encoding="utf-8")

    return mutate


ISLAND = """---
segment: island
name_zh: 孤島環節
layer: ai-server
position: 9
market_coverage:
  tw: present
  us: none
companies:
  - ticker: "1234.TW"
    name_zh: 範例公司
    role: 無連結
    tier: 3
upstream: []
downstream: []
themes: []
kpis:
  - 指標
signals:
  - 訊號
---

## 環節定義

孤島。

## 技術變數

無。

## 玩家格局

無。

## 傳導鏈

無。

## 監測指標

無。

## 風險

無。
"""

MID = "ai-server/mid-part.md"
END = "ai-server/end-part.md"
THEME = "themes/sample-theme.md"
SOURCES = "sources.yaml"

# (案例名稱, 突變, 預期訊息片段, 是否也該在 --skip-prose 模式下被攔下)
CASES = [
    ('來源 ID 重複', edit(SOURCES, 'id: sample-media', 'id: sample-filings'), '來源識別碼重複', True),
    ('來源 ID 缺少', edit(SOURCES, 'id: sample-media\n      ', ''), '缺少必填欄位: id', True),
    ('自動設定錯誤', edit(SOURCES, 'id: sample-media', 'ingestion: {adapter: nope}\n      id: sample-media'), 'adapter 不合法', True),
    ('來源題材無法解析', edit(SOURCES, 'id: sample-media', 'themes: [nope]\n      id: sample-media'), '引用不存在的題材', True),
    ("缺少必填欄位", edit(MID, "kpis:\n  - 出貨量\n  - 毛利率\n", ""), "缺少必填欄位: kpis", True),
    ("環節識別碼重複", copy_as(MID, "ai-server/dup.md"), "識別碼重複", True),
    ("上下游引用無法解析", edit(MID, "downstream: [end-part]", "downstream: [nonexistent]"), "引用不存在的環節: nonexistent", True),
    ("單向上下游關係", edit(MID, "downstream: [end-part]", "downstream: []"), "單向關係", True),
    ("代號格式錯誤", edit(MID, 'ticker: "2330.TW"', 'ticker: "2330.TWX"'), "代號格式不符規範", True),
    ("市場覆蓋與公司清單矛盾", edit(MID, "  tw: present", "  tw: none"), "宣告 none，但 companies 含 TW", True),
    ("led_by 無對應公司", edit(MID, "  us: present\ncompanies:", "  us: present\n  led_by: [KR]\ncompanies:"), "led_by 列出 KR", True),
    ("position 超出範圍", edit(MID, "position: 2", "position: 0"), "position 須為 1–99", True),
    ("tier 超出範圍", edit(MID, "    tier: 3", "    tier: 5"), "tier 須為 1–3", True),
    ("layer 與目錄不符", edit(MID, "layer: ai-server", "layer: semiconductor"), "與所在目錄", True),
    ("缺少 frontmatter", strip_frontmatter(MID), "缺少 YAML frontmatter", True),
    ("孤島環節", add_file("ai-server/island.md", ISLAND), "孤島環節", True),
    ("題材狀態非法", edit(THEME, "status: scaling", "status: hot"), "status 須為", True),
    ("題材與環節單向關聯", edit(MID, "themes: [sample-theme]", "themes: []"), "單向關聯", True),
    ("受惠公司不在任何環節", edit(THEME, '  - "2330.TW"', '  - "9999.TW"'), "未出現在任何環節", True),
    ("里程碑缺少證據", edit(THEME, "    evidence: 法說會訂單指引與月營收\n", ""), "缺少必填欄位: evidence", True),
    ("里程碑日期格式錯誤", edit(THEME, "date: 2026-Q1", "date: 26Q1"), "須為 YYYY、YYYY-Qn 或 YYYY-MM", True),
    ("缺少散文段落", edit(MID, "## 風險\n\n客戶集中度偏高。\n", ""), "缺少必要段落: ## 風險", False),
    (
        "散文段落順序錯誤",
        edit(
            MID,
            "## 監測指標\n\n月營收與出貨量。\n\n## 風險\n\n客戶集中度偏高。\n",
            "## 風險\n\n客戶集中度偏高。\n\n## 監測指標\n\n月營收與出貨量。\n",
        ),
        "段落順序須為",
        False,
    ),
    ("付費來源混入", edit(SOURCES, "access: free", "access: paid", count=1), "僅限免費公開來源", True),
    ("來源缺少必填欄位", edit(SOURCES, "      checked: '2026-10-07'\n      segments: [mid-part]\n", "      segments: [mid-part]\n"), "缺少必填欄位: checked", True),
    ("來源引用不存在的環節", edit(SOURCES, "segments: [mid-part]", "segments: [nope]"), "引用不存在的環節: nope", True),
    ("來源回補頁數超限", edit(SOURCES, "      segments: [mid-part]", "      ingestion: {adapter: rss, max_pages: 201}\n      segments: [mid-part]", count=1), "max_pages 須為 1–200", True),
]


ASSESSMENT = {
    'summary': '具來源的條件式判讀', 'confidence': 'inference', 'reviewed': '2026-10-07',
    'conditions': ['需有實際採購'], 'gaps': ['尚未取得反向證據'],
    'next_checks': [{'question': '是否交付', 'evidence_required': '具名客戶紀錄'}],
    'evidence': [{'id': 'source-one', 'source_id': 'sample-filings', 'url': 'https://example.invalid/filing', 'excerpt': '測試摘錄', 'period': '2026-Q1', 'published': None}],
    'claims': [{'id': 'claim-one', 'stance': 'supporting', 'confidence': 'well-supported', 'statement': '只限來源揭露對象', 'evidence_ids': ['source-one']}],
    'paths': [
        {'id': 'upstream-path', 'steps': [{'from': 'mid-part', 'to': 'support-part', 'type': 'upstream'}], 'mechanism': '採購', 'direction': 'positive', 'conditions': ['實際下單'], 'claim_ids': ['claim-one']},
        {'id': 'theme-path', 'steps': [{'from': 'mid-part', 'to': 'support-part', 'type': 'theme', 'via': 'sample-theme'}], 'mechanism': '題材橫向', 'direction': 'mixed', 'conditions': ['規格相符'], 'claim_ids': ['claim-one']},
        {'id': 'sibling-path', 'steps': [{'from': 'upstream-part', 'to': 'support-part', 'type': 'sibling', 'via': 'mid-part'}], 'mechanism': '共同採購', 'direction': 'unknown', 'conditions': ['共同客戶'], 'claim_ids': ['claim-one']},
    ],
    'milestone_reviews': [{'milestone_id': 'first-delivery', 'state': 'unconfirmed', 'reviewed': '2026-10-07', 'note': '尚未確認', 'evidence_ids': []}],
}


def assessment_fixture(map_dir, mutate=None):
    path = map_dir / THEME
    _, header, body = path.read_text(encoding='utf-8').split('---', 2)
    data = yaml.safe_load(header)
    data['segments'].append('support-part')
    data['milestones'][0]['id'] = 'first-delivery'
    data['assessment'] = copy.deepcopy(ASSESSMENT)
    if mutate: mutate(data)
    path.write_text('---\n' + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + '---\n' + body + '\n查核日期：2026-10-07\n', encoding='utf-8')
    support = map_dir / 'semiconductor/support-part.md'
    support.write_text(support.read_text(encoding='utf-8').replace('themes: []', 'themes: [sample-theme]'), encoding='utf-8')


def assessment_mutation(mutate):
    return lambda map_dir: assessment_fixture(map_dir, mutate)


CASES += [
    ('判讀重複識別', assessment_mutation(lambda d: d['assessment']['evidence'].append(dict(d['assessment']['evidence'][0]))), '識別碼重複', True),
    ('里程碑重複識別', assessment_mutation(lambda d: d['milestones'].append(dict(d['milestones'][0]))), '里程碑識別碼重複', True),
    ('失效來源引用', assessment_mutation(lambda d: d['assessment']['evidence'][0].update(source_id='nope')), 'source_id 引用不存在', True),
    ('失效證據引用', assessment_mutation(lambda d: d['assessment']['claims'][0].update(evidence_ids=['nope'])), 'evidence_ids 引用不存在', True),
    ('失效論點引用', assessment_mutation(lambda d: d['assessment']['paths'][0].update(claim_ids=['nope'])), 'claim_ids 引用不存在', True),
    ('失效里程碑引用', assessment_mutation(lambda d: d['assessment']['milestone_reviews'][0].update(milestone_id='nope')), 'milestone_id 無法解析', True),
    ('查核日期錯誤', assessment_mutation(lambda d: d['assessment'].update(reviewed='2026-02-30')), '有效 YYYY-MM-DD', True),
    ('原查核基準不一致', assessment_mutation(lambda d: d['assessment'].update(reviewed='2026-10-08')), '與散文查核日期不一致', False),
    ('判讀支持程度錯誤', assessment_mutation(lambda d: d['assessment'].update(confidence=['unsupported'])), 'confidence 不合法', True),
    ('證據 URL 不合法', assessment_mutation(lambda d: d['assessment']['evidence'][0].update(url='http://example.invalid')), '完整 HTTPS', True),
    ('缺少證據期間', assessment_mutation(lambda d: d['assessment']['evidence'][0].update(period='')), 'period 須為非空文字', True),
    ('影響方向錯誤', assessment_mutation(lambda d: d['assessment']['paths'][0].update(direction='profit')), 'direction 不合法', True),
    ('非法線性步驟', assessment_mutation(lambda d: d['assessment']['paths'][0]['steps'][0].update(to='end-part')), '傳導步驟不符合', True),
    ('非法題材步驟', assessment_mutation(lambda d: d['assessment']['paths'][1]['steps'][0].update(via='missing-theme')), '傳導步驟不符合', True),
    ('非法手足步驟', assessment_mutation(lambda d: d['assessment']['paths'][2]['steps'][0].update(via='end-part')), '傳導步驟不符合', True),
    ('已確認卻沒有證據', assessment_mutation(lambda d: d['assessment']['milestone_reviews'][0].update(state='confirmed')), 'evidence_ids 須為陣列且至少 1 筆', True),
]


def technical_fixture(map_dir, mutate=None):
    """Synthetic schema examples only; never used by runtime ingestion."""
    assessment_fixture(map_dir)
    path=map_dir/MID
    _,header,body=path.read_text(encoding='utf-8').split('---',2)
    data=yaml.safe_load(header)
    reference={'document-id':'sample-document','version-id':'public-overview','locator':'boundary'}
    data['downstream-relations']={'end-part':{'kind':'supply','summary':'測試整合關係，不代表客戶交易','items':['測試元件'],'dependencies':['測試介面'],'conditions':['實際驗證'],'confidence':'inference','evidence':[reference],'gaps':['無客戶料號'],'reviewed':'2026-10-16'}}
    data['technical-profile']={'product-boundary':'測試產品責任','adoption-conditions':['測試整合'],'bottlenecks':['測試限制'],'substitution-limits':['非同料號不能推定替代'],'claims':[{'id':'interface-scope','statement':'測試技術範圍','confidence':'well-supported','evidence':[reference]}],'evidence-gaps':['未取得測試客戶採用'],'reviewed':'2026-10-16'}
    doc={'id':'sample-document','source-id':'sample-technical','title':'Synthetic schema fixture','publisher':'測試機構','doc-kind':'informative','segments':['mid-part'],'themes':['sample-theme'],'versions':[{'id':'public-overview','label':None,'url':'https://example.invalid/technical','published':None,'published-precision':'unknown','reviewed':'2026-10-16','read-scope':'僅測試介紹','access-limitations':'測試，未讀全文','scope':'不能推定採用','locators':[{'id':'boundary','section':'產品邊界','excerpt':'Synthetic test excerpt.'}]}],'reviews':[]}
    manifest={'schema-version':'technical-documents-v1','documents':[doc]}
    source={'id':'sample-technical','name':'測試技術入口','url':'https://example.invalid/technical','type':'technical-documents','access':'free','reachability':'verified','checked':'2026-10-16','segments':['mid-part'],'ingestion':{'adapter':'technical-documents','document-ids':['sample-document'],'allowed-hosts':['example.invalid']}}
    if mutate:mutate(data,manifest,source)
    path.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False)+'---'+body,encoding='utf-8')
    (map_dir/'technical-documents.yaml').write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
    sources=yaml.safe_load((map_dir/SOURCES).read_text(encoding='utf-8'));sources['global']={'technical-documents':[source]}
    (map_dir/SOURCES).write_text(yaml.safe_dump(sources,allow_unicode=True,sort_keys=False),encoding='utf-8')
    theme_path=map_dir/THEME
    _,theme_header,theme_body=theme_path.read_text(encoding='utf-8').split('---',2)
    theme=yaml.safe_load(theme_header)
    theme['technical-profile']=dict(data['technical-profile'],claims=[],**{'assessment-claim-ids':['claim-one']})
    theme_path.write_text('---\n'+yaml.safe_dump(theme,allow_unicode=True,sort_keys=False)+'---'+theme_body,encoding='utf-8')


def technical_mutation(mutate):
    return lambda map_dir:technical_fixture(map_dir,mutate)


CASES += [
    ('關係型別錯誤',technical_mutation(lambda d,m,s:d['downstream-relations']['end-part'].update(kind='partner')),'kind 不合法',True),
    ('不存在的下游說明',technical_mutation(lambda d,m,s:d['downstream-relations'].update({'upstream-part':d['downstream-relations']['end-part']})),'非實存下游邊',True),
    ('關係缺少條件',technical_mutation(lambda d,m,s:d['downstream-relations']['end-part'].update(conditions=[])),'conditions 須為陣列且至少 1 筆',True),
    ('關係無證據缺口',technical_mutation(lambda d,m,s:d['downstream-relations']['end-part'].update(evidence=[],gaps=[])),'至少需要證據或具體缺口',True),
    ('關係無效查核日',technical_mutation(lambda d,m,s:d['downstream-relations']['end-part'].update(reviewed='2026-02-30')),'reviewed 須為有效',True),
    ('技術來源失效',technical_mutation(lambda d,m,s:d['technical-profile']['claims'][0].update(evidence=[{'source-id':'missing','url':'https://example.invalid','locator':'介紹','read-scope':'摘要'}])),'source-id 引用不存在來源',True),
    ('技術文件失效',technical_mutation(lambda d,m,s:d['technical-profile']['claims'][0]['evidence'][0].update(**{'document-id':'missing'})),'引用不存在文件版本',True),
    ('技術版本失效',technical_mutation(lambda d,m,s:d['technical-profile']['claims'][0]['evidence'][0].update(**{'version-id':'latest'})),'引用不存在文件版本',True),
    ('技術定位失效',technical_mutation(lambda d,m,s:d['technical-profile']['claims'][0]['evidence'][0].update(locator='missing')),'locator 引用不存在定位',True),
    ('技術引用混填',technical_mutation(lambda d,m,s:d['technical-profile']['claims'][0]['evidence'][0].update(**{'source-id':'sample-technical'})),'不能混填來源身分',True),
    ('技術論述重複',technical_mutation(lambda d,m,s:d['technical-profile']['claims'].append(copy.deepcopy(d['technical-profile']['claims'][0]))),'claims 識別碼重複',True),
    ('技術日期錯誤',technical_mutation(lambda d,m,s:d['technical-profile'].update(reviewed='2026-13-01')),'reviewed 須為有效',True),
    ('文件來源失效',technical_mutation(lambda d,m,s:m['documents'][0].update(**{'source-id':'missing'})),'source-id 引用不存在來源',True),
    ('文件版本重複',technical_mutation(lambda d,m,s:m['documents'][0]['versions'].append(copy.deepcopy(m['documents'][0]['versions'][0]))),'versions 識別碼重複',True),
    ('文件定位重複',technical_mutation(lambda d,m,s:m['documents'][0]['versions'][0]['locators'].append(copy.deepcopy(m['documents'][0]['versions'][0]['locators'][0]))),'locators 識別碼重複',True),
    ('文件未知日偽造',technical_mutation(lambda d,m,s:m['documents'][0]['versions'][0].update(published='2026-10-16')),'未知精度必須 null',True),
    ('文件發布月份錯誤',technical_mutation(lambda d,m,s:m['documents'][0]['versions'][0].update(published='2026-13',**{'published-precision':'month'})),'published 與精度不一致',True),
    ('文件性質錯誤',technical_mutation(lambda d,m,s:m['documents'][0].update(**{'doc-kind':'commercial-proof'})),'doc-kind 不合法',True),
    ('文件監測超量',technical_mutation(lambda d,m,s:s['ingestion'].update(**{'max-documents':11})),'max-documents 須為 1–10',True),
    ('文件監測非明列',technical_mutation(lambda d,m,s:s['ingestion'].update(**{'document-ids':['missing']})),'document-ids 引用不存在',True),
    ('文件監測非官方hostname',technical_mutation(lambda d,m,s:s['ingestion'].update(**{'allowed-hosts':['elsewhere.invalid']})),'allowed-hosts 未包含',True),
    ('核對無採納版本',technical_mutation(lambda d,m,s:m['documents'][0]['reviews'].append({'content-hash':'a'*64,'official-version':None,'disposition':'adopted','reviewed':'2026-10-16','reason':'測試'})),'version-id 引用不存在版本',True),
    ('技術重複YAML鍵',edit(MID,'downstream: [end-part]','downstream: [end-part]\ndownstream: [end-part]'),'重複 YAML 鍵',True),
]


def main() -> int:
    if not BASELINE.is_dir():
        print("找不到基準 fixture: {}".format(BASELINE), file=sys.stderr)
        return 2

    failures = []

    # 合法案例：完整模式與骨架模式都必須通過。
    for extra, label in (((), "full"), (("--skip-prose",), "skip-prose")):
        code, output = run_validator(BASELINE, *extra)
        if code != 0:
            failures.append("合法基準在 {} 模式下未通過（exit {}）:\n{}".format(label, code, output))
            print("  FAIL  合法基準（{}）".format(label))
        else:
            print("  ok    合法基準（{}）".format(label))

    with tempfile.TemporaryDirectory() as tmp:
        map_dir = Path(tmp) / 'industry-map'
        shutil.copytree(BASELINE, map_dir)
        assessment_fixture(map_dir)
        code, output = run_validator(map_dir)
        if code:
            failures.append(f'合法判讀基準未通過: {output}')
        else:
            print('  ok    合法判讀（含三種傳導與未知日期）')

    # 失敗案例：每個突變都必須被攔下，且訊息需指出具體問題。
    with tempfile.TemporaryDirectory() as tmp:
        map_dir=Path(tmp)/'industry-map';shutil.copytree(BASELINE,map_dir)
        technical_fixture(map_dir)
        for extra in [(),('--skip-prose',)]:
            code,output=run_validator(map_dir,*extra)
            if code:failures.append(f'合法技術擴充未通過: {output}')
            else:print(f'  ok    合法技術擴充（固定版本／未知日／global／原判讀引用；{extra or "full"}）')
    for name, mutate, expected, caught_in_skip_prose in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            map_dir = Path(tmp) / "industry-map"
            shutil.copytree(BASELINE, map_dir)
            try:
                mutate(map_dir)
            except AssertionError as exc:
                failures.append("{}: 突變無法施加 — {}".format(name, exc))
                print("  FAIL  {} （突變失敗）".format(name))
                continue

            code, output = run_validator(map_dir)
            if code == 0:
                failures.append("{}: 驗證器未攔下（exit 0）".format(name))
                print("  FAIL  {} （未攔下）".format(name))
                continue
            if expected not in output:
                failures.append("{}: 訊息未包含 {!r}\n{}".format(name, expected, output))
                print("  FAIL  {} （訊息不符）".format(name))
                continue

            # 骨架模式下，結構類錯誤仍須被攔下；散文類錯誤則應被略過。
            skip_code, _ = run_validator(map_dir, "--skip-prose")
            if caught_in_skip_prose and skip_code == 0:
                failures.append("{}: 結構錯誤在 --skip-prose 模式下被漏放".format(name))
                print("  FAIL  {} （--skip-prose 漏放）".format(name))
                continue
            if not caught_in_skip_prose and skip_code != 0:
                failures.append("{}: 散文錯誤不該在 --skip-prose 模式下被攔".format(name))
                print("  FAIL  {} （--skip-prose 誤攔）".format(name))
                continue

            print("  ok    {}".format(name))

    print()
    if failures:
        print("{} 個測試失敗：\n".format(len(failures)), file=sys.stderr)
        for item in failures:
            print("  - {}".format(item), file=sys.stderr)
        return 1

    print("全部通過：1 個合法基準（2 種模式）、{} 類失敗案例".format(len(CASES)))
    # Keep the documented validator command authoritative for the new schema too.
    import unittest
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_research_schema.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
