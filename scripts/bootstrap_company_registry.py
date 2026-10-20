"""One-time, non-overwriting migration of legacy identities (not new research)."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'industry-map'
# Initial mnemonic choices are fixed in the authored files after migration.
NAMES = {'2330.TW': 'tsmc', '3324.TW': 'auras', '3017.TW': 'avc',
         '2308.TW': 'delta-electronics', '2317.TW': 'hon-hai',
         'VRT': 'vertiv', 'PRIVATE:boyd': 'boyd'}


def build_registry(map_dir, supplements):
    companies = {}
    for folder in ('ai-server', 'semiconductor'):
        for path in sorted((map_dir / folder).glob('*.md')):
            segment = yaml.safe_load(path.read_text(encoding='utf-8').split('---', 2)[1])
            for company in segment['companies']:
                ticker = company['ticker']
                if ticker not in companies:
                    extra = supplements.get(ticker, {})
                    slug = NAMES.get(ticker, re.sub('[^a-z0-9]+', '-', ticker.lower()).strip('-'))
                    listings = []
                    if not ticker.startswith('PRIVATE:'):
                        suffix = ticker.rsplit('.', 1)[-1] if '.' in ticker else 'US'
                        market, exchange = {
                            'TW': ('TW', 'XTAI'), 'TWO': ('TW', 'ROCO'),
                            'KS': ('KR', 'XKRX'), 'T': ('JP', 'XTKS'),
                            'HK': ('HK', 'XHKG'), 'DE': ('DE', 'XETR'),
                            'AS': ('NL', 'XAMS'), 'US': ('US', 'UNKNOWN'),
                        }[suffix]
                        listings.append({'ticker': ticker, 'market': market, 'exchange': exchange,
                                         'share-class': 'unspecified', 'valid-from': None, 'valid-to': None})
                    companies[ticker] = {
                        'schema-version': 'research-v1', 'entity-id': 'company-' + slug,
                        'kind': 'company', 'name-zh': company['name_zh'],
                        'aliases': list(dict.fromkeys(extra.get('aliases', []))),
                        'summary': company['name_zh'] + '的既有供應角色索引；產品與商業關係尚待逐項研究。',
                        'legacy-keys': [ticker], 'listings': listings,
                        'source-identifiers': [{'provider': 'sec-cik', 'value': extra['cik']}] if extra.get('cik') else [],
                        'research-depth': 'basic', 'reviewed': None, 'roles': [],
                        'claims': [], 'gaps': ['尚未完成公司產品、客戶、競爭與風險的獨立深研。'],
                    }
                companies[ticker]['roles'].append({
                    'segment-id': 'segment-' + segment['segment'], 'description': company['role'],
                    'tier': company['tier'], 'baseline-path': path.relative_to(map_dir).as_posix(),
                })
    return companies


def main():
    target = MAP / 'companies'
    if target.exists():
        raise SystemExit('Registry already exists; refusing to overwrite stable identities')
    supplements = yaml.safe_load((ROOT / 'data/company-research.yaml').read_text(encoding='utf-8'))['companies']
    registry = build_registry(MAP, supplements)
    if len({c['entity-id'] for c in registry.values()}) != len(registry):
        raise SystemExit('Identity collision; no files written')
    target.mkdir()
    for company in registry.values():
        roles = '\n'.join('- ' + role['description'] for role in company['roles'])
        body = '\n## 供應角色\n\n' + roles + '\n\n## 研究界線\n\n' + company['gaps'][0] + '\n'
        (target / (company['entity-id'] + '.md')).write_text(
            '---\n' + yaml.safe_dump(company, allow_unicode=True, sort_keys=False) + '---\n' + body,
            encoding='utf-8', newline='\n')
    print(f'Migrated {len(registry)} companies; no claims upgraded')


if __name__ == '__main__':
    main()
