"""Mutation tests for identity preservation, typed evidence and graph boundaries."""
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_map as legacy
from research_schema import validate_research
from bootstrap_company_registry import build_registry


class ResearchSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.segments = {'thermal': {'_path': self.root / 'ai-server/thermal.md', 'companies': []}}
        self.company = {
            'schema-version': 'research-v1', 'entity-id': 'company-example', 'kind': 'company',
            'name-zh': '範例公司', 'summary': '結構測試，非真實公司研究。', 'aliases': ['範例'],
            'reviewed': None, 'claims': [], 'gaps': ['未研究'], 'legacy-keys': ['1234.TW'],
            'source-identifiers': [], 'listings': [], 'roles': [], 'research-depth': 'basic',
        }
        self.write(self.company)

    def write(self, obj, body='\n## 供應角色\n\n測試\n\n## 研究界線\n\n未研究\n'):
        folders = {'company': 'companies', 'product': 'products', 'role': 'roles', 'concept': 'concepts'}
        path = self.root / folders[obj['kind']] / (obj['entity-id'] + '.md')
        path.parent.mkdir(exist_ok=True)
        path.write_text('---\n' + yaml.safe_dump(obj, allow_unicode=True, sort_keys=False) + '---\n' + body, encoding='utf-8')

    def check(self, expected=None):
        errors = legacy.Errors()
        value = validate_research(self.root, self.segments, {}, errors, legacy.parse_doc, legacy.load_yaml)
        messages = '\n'.join(m for _, m in errors.items)
        if expected:
            self.assertIn(expected, messages)
        else:
            self.assertEqual(messages, '')
        return value

    def relations(self, **groups):
        obj = {'schema-version': 'research-v1', 'taxonomy': [], 'offerings': [], 'relations': [], **groups}
        (self.root / 'research-relations.yaml').write_text(yaml.safe_dump(obj), encoding='utf-8')

    def claim(self, confidence='well-supported'):
        (self.root / 'sources.yaml').write_text('tw:\n  filings:\n    - id: example-official\n', encoding='utf-8')
        return {'id': 'example', 'statement': '測試主張', 'confidence': confidence,
                'conditions': ['僅測試'], 'reviewed': '2026-10-16', 'evidence': [{
                    'source-id': 'example-official', 'url': 'https://example.org/product',
                    'locator': '產品', 'read-scope': '公開介紹', 'stance': 'supporting',
                    'applicable-period': '測試期間'}]}

    def test_all_95_identities_and_100_roles_preserved(self):
        map_dir = ROOT / 'industry-map'
        old = build_registry(map_dir, yaml.safe_load((ROOT / 'data/company-research.yaml').read_text(encoding='utf-8'))['companies'])
        docs = [legacy.parse_doc(p, legacy.Errors())[0] for p in (map_dir / 'companies').glob('*.md')]
        by_key = {key: obj for obj in docs for key in obj['legacy-keys']}
        self.assertEqual(set(by_key), set(old))
        self.assertEqual(len({d['entity-id'] for d in docs}), 95)
        self.assertEqual(sum(len(d['roles']) for d in docs), 100)
        for key, expected in old.items():
            self.assertEqual(by_key[key]['roles'], expected['roles'])
            self.assertLessEqual(set(expected['aliases']), set(by_key[key]['aliases']))
            self.assertEqual(by_key[key]['source-identifiers'], expected['source-identifiers'])
        self.assertEqual(by_key['PRIVATE:boyd']['listings'], [])

    def test_cross_market_listings_share_one_identity_after_rename(self):
        # Synthetic securities, not a claim about an actual company.
        self.company['listings'] = [
            {'ticker': '1234.TW', 'market': 'TW', 'exchange': 'XTAI', 'share-class': 'ordinary', 'valid-from': None, 'valid-to': None},
            {'ticker': 'EXMP', 'market': 'US', 'exchange': 'XNYS', 'share-class': 'adr', 'valid-from': None, 'valid-to': None}]
        self.company['name-zh'] = '新名稱'
        self.write(self.company)
        result = self.check()
        self.assertEqual(list(result['entities']), ['company-example'])
        self.assertEqual(len(result['entities']['company-example']['listings']), 2)

    def test_same_alias_does_not_merge_parent_and_subsidiary(self):
        child = copy.deepcopy(self.company)
        child['entity-id'], child['legacy-keys'] = 'company-subsidiary', []
        self.write(child)
        self.assertEqual(len(self.check()['entities']), 2)

    def test_duplicate_legacy_key_rejected(self):
        child = {**self.company, 'entity-id': 'company-second'}
        self.write(child)
        self.check('duplicate legacy-key')

    def test_missing_legacy_company_rejected(self):
        self.segments['thermal']['companies'] = [{'ticker': '5678.TW'}]
        self.check('legacy company lost')

    def test_overlapping_listing_rejected(self):
        listing = {'ticker': 'EXMP', 'market': 'US', 'exchange': 'XNYS', 'share-class': 'ordinary', 'valid-from': None, 'valid-to': None}
        self.company['listings'] = [listing, listing]
        self.write(self.company)
        self.check('overlapping listing')

    def test_official_identity_cannot_be_shared(self):
        self.company['source-identifiers'] = [{'provider': 'sec-cik', 'value': '001234'}]
        self.write(self.company)
        self.write({**self.company, 'entity-id': 'company-second', 'legacy-keys': [],
                    'source-identifiers': [{'provider': 'sec-cik', 'value': '1234'}]})
        self.check('duplicate source identity')

    def test_taxonomy_cycle_rejected(self):
        self.relations(taxonomy=[{'id': 'taxonomy-a', 'parent': 'segment-thermal', 'child': 'company-example'},
                                 {'id': 'taxonomy-b', 'parent': 'company-example', 'child': 'segment-thermal'}])
        self.check('taxonomy cycle')

    def test_supply_feedback_cycle_allowed(self):
        self.company['claims'] = [self.claim()]
        self.write(self.company)
        common = {'conditions': ['結構測試'], 'confidence': 'inference', 'reviewed': '2026-10-16',
                  'mechanism': '需求回饋測試', 'direction': 'directed', 'kind': 'demand-feedback',
                  'claim-refs': [{'entity-id': 'company-example', 'claim-id': 'example'}]}
        self.relations(relations=[{**common, 'id': 'relation-a', 'source': 'company-example', 'target': 'segment-thermal'},
                                  {**common, 'id': 'relation-b', 'source': 'segment-thermal', 'target': 'company-example'}])
        self.check()

    def test_named_supply_cannot_use_inference(self):
        self.company['claims'] = [self.claim('inference')]
        self.write(self.company)
        self.write({**self.company, 'entity-id': 'company-second', 'legacy-keys': []})
        self.relations(relations=[{'id': 'relation-customer', 'source': 'company-example', 'target': 'company-second',
            'kind': 'named-supply', 'direction': 'directed', 'mechanism': '結構測試', 'conditions': ['測試'],
            'confidence': 'inference', 'reviewed': '2026-10-16',
            'claim-refs': [{'entity-id': 'company-example', 'claim-id': 'example'}]}])
        self.check('named-supply needs well-supported claim')

    def test_unresolved_claim_rejected(self):
        self.relations(offerings=[{'id': 'offering-a', 'company': 'company-example', 'product': 'product-unknown',
            'role': 'role-unknown', 'conditions': ['測試'], 'claim-refs': [{'entity-id': 'company-example', 'claim-id': 'unknown'}]}])
        self.check('claim-ref unresolved')

    def test_fixed_document_cannot_resolve_latest(self):
        claim = self.claim()
        claim['evidence'] = [{'document-id': 'missing', 'version-id': 'latest', 'locator': 'one',
                              'stance': 'supporting', 'applicable-period': '未知'}]
        self.write({**self.company, 'claims': [claim]})
        self.check('fixed document/version/locator unresolved')

    def asset(self, content, path='assets/diagram.svg', digest=None):
        target = self.root / 'assets/diagram.svg'
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(content)
        manifest = {'schema-version': 'research-v1', 'assets': [{'id': 'asset-example', 'path': path,
            'sha256': digest or hashlib.sha256(content).hexdigest(), 'media-type': 'image/svg+xml',
            'alt': '測試示意', 'license': 'original', 'attribution': 'test'}]}
        (self.root / 'research-assets.yaml').write_text(yaml.safe_dump(manifest), encoding='utf-8')

    def test_original_svg_allowed(self):
        self.asset(b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>')
        self.check()

    def test_active_svg_rejected(self):
        for fragment in ('<script/>', '<foreignObject/>', '<image href="https://example.org/a"/>',
                         '<rect onclick="alert(1)"/>', '<style/>'):
            with self.subTest(fragment=fragment):
                self.asset(('<svg xmlns="http://www.w3.org/2000/svg">' + fragment + '</svg>').encode())
                self.check('unsafe SVG')

    def test_asset_escape_rejected(self):
        self.asset(b'<svg/>', '../secrets.svg')
        self.check('asset path escape')

    def test_asset_hash_rejected(self):
        self.asset(b'<svg xmlns="http://www.w3.org/2000/svg"/>', digest='0' * 64)
        self.check('asset hash mismatch')

    def test_malformed_references_report_errors(self):
        self.relations(taxonomy=[{'id': 'taxonomy-malformed', 'parent': {}, 'child': []}])
        self.check('unresolved entity')

    def test_duplicate_yaml_key_rejected(self):
        path = self.root / 'companies/company-example.md'
        path.write_text(path.read_text(encoding='utf-8').replace('kind: company', 'kind: company\nkind: product'), encoding='utf-8')
        self.check('重複 YAML 鍵')

    def financial_profile(self):
        (self.root/'sources.yaml').write_text(yaml.safe_dump({'tw':{'filings':[{'id':'test-financial-source'}]}}),encoding='utf-8')
        return {'primary-source-family':'tw-mops-summary','confidence':'well-supported','reviewed':'2026-10-17',
            'fiscal-year-end':'12-31','calendar-valid-from':'2024-01-01','calendar-valid-to':None,
            'evidence':[{'source-id':'test-financial-source','url':'https://official.example/annual',
                'locator':'年度報表實際期間','read-scope':'合成格式測試，非真實財年研究。','applicable-period':'測試期間','stance':'supporting'}]}

    def test_financial_calendar_is_optional_but_evidence_and_dates_are_required(self):
        self.company['financial-reporting']=self.financial_profile();self.write(self.company);self.check()
        self.company['financial-reporting']['evidence']=[];self.write(self.company);self.check('evidence needs at least')

    def test_financial_calendar_invalid_and_reversed_intervals_rejected(self):
        self.company['financial-reporting']=self.financial_profile()
        self.company['financial-reporting']['fiscal-year-end']='02-30';self.write(self.company);self.check('year-end invalid')
        self.company['financial-reporting']['fiscal-year-end']='12-31'
        self.company['financial-reporting']['calendar-valid-to']='2023-12-31';self.write(self.company);self.check('interval reversed')


if __name__ == '__main__':
    unittest.main()
