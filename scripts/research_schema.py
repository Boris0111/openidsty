"""Research-v1 structural validation shared by CLI and release compilation."""
from datetime import date
import hashlib
from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import yaml

KINDS = {'companies': 'company', 'applications': 'application', 'roles': 'role',
         'products': 'product', 'concepts': 'concept', 'research': 'research'}
CONFIDENCES = ('well-supported', 'inference', 'needs-verification')
ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def get(mapping, key):
    return mapping.get(key) if isinstance(key, str) else None


class ResearchValidator:
    def __init__(self, root, segments, themes, errors, parse_doc, load_yaml, skip_prose):
        self.root, self.errors = root, errors
        self.parse_doc, self.load_yaml, self.skip_prose = parse_doc, load_yaml, skip_prose
        self.segments = segments
        self.legacy = {'segment-' + k: v for k, v in segments.items()}
        self.legacy.update({'theme-' + k: v for k, v in themes.items()})
        self.entities, self.assets = {}, {}

    def fail(self, path, message):
        self.errors.add(path, 'research-v1: ' + message)

    def text(self, value, path, label):
        ok = isinstance(value, str) and bool(value.strip())
        if not ok:
            self.fail(path, label + ' must be nonempty text')
        return ok

    def array(self, value, path, label, minimum=0, strings=False):
        if not isinstance(value, list):
            self.fail(path, label + ' must be an array')
            return []
        if len(value) < minimum:
            self.fail(path, label + ' needs at least ' + str(minimum) + ' item(s)')
        if strings:
            for item in value:
                self.text(item, path, label)
        return value

    def day(self, value, path, label, nullable=False):
        if value is None and nullable:
            return
        try:
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError()
        except ValueError:
            self.fail(path, label + ' must be a quoted YYYY-MM-DD')

    def identified(self, items, path, prefix='', label='id'):
        result = {}
        for item in self.array(items, path, label):
            if not isinstance(item, dict):
                self.fail(path, label + ' item must be a mapping')
                continue
            key = item.get('id')
            if not isinstance(key, str) or not ID.fullmatch(key) or not key.startswith(prefix):
                self.fail(path, label + ' invalid id')
                continue
            if key in result:
                self.fail(path, label + ' duplicate id ' + key)
            result[key] = item
        return result

    def manifest(self, filename, keys, version='research-v1'):
        path = self.root / filename
        if not path.exists():
            return {key: [] for key in keys}
        try:
            obj = self.load_yaml(path.read_text(encoding='utf-8'))
            if not isinstance(obj, dict) or obj.get('schema-version') != version:
                raise ValueError('expected ' + version + ' mapping')
            return {key: self.array(obj.get(key), path, key) for key in keys}
        except Exception as exc:
            self.fail(path, 'invalid manifest: ' + str(exc))
            return {key: [] for key in keys}

    def ref(self, value, path, label, kind=None):
        if not isinstance(value, str) or value not in {**self.legacy, **self.entities}:
            self.fail(path, label + ' unresolved entity')
            return False
        if kind and not value.startswith(kind + '-'):
            self.fail(path, label + ' wrong entity kind')
            return False
        return True

    def load(self):
        for folder, kind in KINDS.items():
            for path in sorted((self.root / folder).glob('*.md')):
                if path.is_symlink() or path.resolve().parent != (self.root / folder).resolve():
                    self.fail(path, 'symlink or path escape forbidden')
                    continue
                parsed = self.parse_doc(path, self.errors)
                if not parsed:
                    continue
                obj, body = parsed
                key = obj.get('entity-id')
                if (not isinstance(key, str) or not ID.fullmatch(key) or
                        not key.startswith(kind + '-') or key != path.stem or obj.get('kind') != kind):
                    self.fail(path, 'entity-id / kind / filename mismatch')
                    continue
                if key in self.entities:
                    self.fail(path, 'duplicate entity-id')
                if obj.get('schema-version') != 'research-v1':
                    self.fail(path, 'schema-version must be research-v1')
                for field in ('name-zh', 'summary'):
                    self.text(obj.get(field), path, field)
                self.array(obj.get('aliases'), path, 'aliases', strings=True)
                if 'reviewed' not in obj:
                    self.fail(path, 'missing reviewed')
                self.day(obj.get('reviewed'), path, 'reviewed', True)
                claims = self.identified(obj.get('claims'), path, label='claims')
                self.array(obj.get('gaps'), path, 'gaps', 0 if claims else 1, True)
                self.entities[key] = {**obj, '_body': body, '_path': path, '_claims': claims}

    def evidence(self, value, path, sources, documents):
        for item in self.array(value, path, 'evidence', 1):
            if not isinstance(item, dict):
                self.fail(path, 'evidence must be mapping')
                continue
            if item.get('stance') not in ('supporting', 'counter'):
                self.fail(path, 'evidence stance invalid')
            self.text(item.get('applicable-period'), path, 'applicable-period')
            if 'document-id' in item:
                doc = get(documents, item['document-id']) or {}
                versions = {v['id']: v for v in doc.get('versions', []) if isinstance(v, dict) and isinstance(v.get('id'), str)}
                version = get(versions, item.get('version-id')) or {}
                locators = [v.get('id') for v in version.get('locators', []) if isinstance(v, dict)]
                if not version or item.get('locator') not in locators:
                    self.fail(path, 'evidence fixed document/version/locator unresolved')
                if any(k in item for k in ('source-id', 'url', 'read-scope')):
                    self.fail(path, 'evidence mixed document and page identity')
            else:
                if get(sources, item.get('source-id')) is None:
                    self.fail(path, 'evidence source-id unresolved')
                try:
                    url = urlsplit(item.get('url', ''))
                    if url.scheme != 'https' or not url.hostname or url.username or url.password:
                        raise ValueError()
                except (ValueError, TypeError):
                    self.fail(path, 'evidence url must be credential-free HTTPS')
                for field in ('locator', 'read-scope'):
                    self.text(item.get(field), path, field)
                if 'version-id' in item:
                    self.fail(path, 'evidence version-id without document-id')

    def companies(self):
        owners, official, listings = {}, {}, {}
        for key, obj in self.entities.items():
            if obj['kind'] != 'company':
                continue
            path = obj['_path']
            for old in self.array(obj.get('legacy-keys'), path, 'legacy-keys', strings=True):
                if isinstance(old, str):
                    if old in owners:
                        self.fail(path, 'duplicate legacy-key ' + old)
                    owners[old] = key
            for ident in self.array(obj.get('source-identifiers'), path, 'source-identifiers'):
                if not isinstance(ident, dict):
                    self.fail(path, 'source identifier must be mapping')
                    continue
                if all([self.text(ident.get(f), path, f) for f in ('provider', 'value')]):
                    if ident['provider'] == 'sec-cik' and not re.fullmatch(r'\d{1,10}', ident['value']):
                        self.fail(path, 'sec-cik invalid')
                    pair = (ident['provider'], ident['value'].lstrip('0') if ident['provider'] == 'sec-cik' else ident['value'])
                    if pair in official:
                        self.fail(path, 'duplicate source identity')
                    official[pair] = key
            for listing in self.array(obj.get('listings'), path, 'listings'):
                if not isinstance(listing, dict):
                    self.fail(path, 'listing must be mapping')
                    continue
                if not all([self.text(listing.get(f), path, f) for f in ('ticker', 'exchange', 'share-class')]):
                    continue
                if listing.get('market') not in ('TW', 'US', 'KR', 'JP', 'HK', 'DE', 'NL') or listing['ticker'].startswith('PRIVATE:'):
                    self.fail(path, 'invalid listing market or private ticker')
                if not re.fullmatch(r'[A-Z0-9]{4}|UNKNOWN', listing['exchange']):
                    self.fail(path, 'exchange must be MIC or UNKNOWN')
                for field in ('valid-from', 'valid-to'):
                    if field not in listing:
                        self.fail(path, 'listing missing ' + field)
                    self.day(listing.get(field), path, field, True)
                start, end = listing.get('valid-from') or '0001-01-01', listing.get('valid-to') or '9999-12-31'
                if not isinstance(start, str) or not isinstance(end, str):
                    continue
                if start > end:
                    self.fail(path, 'listing interval reversed')
                identity = (str(listing.get('market')), listing['exchange'], listing['ticker'])
                for old_start, old_end in listings.get(identity, []):
                    if start <= old_end and old_start <= end:
                        self.fail(path, 'overlapping listing interval')
                listings.setdefault(identity, []).append((start, end))
            for role in self.array(obj.get('roles'), path, 'roles'):
                if not isinstance(role, dict):
                    self.fail(path, 'role must be mapping')
                    continue
                self.ref(role.get('segment-id'), path, 'role segment-id', 'segment')
                self.text(role.get('description'), path, 'role description')
                if type(role.get('tier')) is not int or role['tier'] not in (1, 2, 3):
                    self.fail(path, 'role tier invalid')
                segment = get(self.legacy, role.get('segment-id'))
                if segment and role.get('baseline-path') != segment['_path'].relative_to(self.root).as_posix():
                    self.fail(path, 'role baseline-path mismatch')
            if obj.get('research-depth') not in ('basic', 'deep'):
                self.fail(path, 'research-depth invalid')
        if (self.root / 'companies').exists():
            for segment in self.segments.values():
                for company in segment.get('companies', []):
                    if company.get('ticker') not in owners:
                        self.fail(segment['_path'], 'legacy company lost: ' + str(company.get('ticker')))

    def content(self):
        sources, documents = {}, {}
        try:
            groups = self.load_yaml((self.root / 'sources.yaml').read_text(encoding='utf-8'))
            for market in (groups or {}).values():
                for values in market.values() if isinstance(market, dict) else []:
                    if isinstance(values, list):
                        sources.update({s['id']: s for s in values if isinstance(s, dict) and isinstance(s.get('id'), str)})
        except (OSError, ValueError, AttributeError, yaml.YAMLError):
            pass  # Legacy validation handles invalid sources.
        for doc in self.manifest('technical-documents.yaml', ['documents'], 'technical-documents-v1')['documents']:
            if isinstance(doc, dict) and isinstance(doc.get('id'), str):
                documents[doc['id']] = doc
        for obj in self.entities.values():
            path, kind = obj['_path'], obj['kind']
            profile=obj.get('financial-reporting')
            if profile is not None:
                if kind!='company' or not isinstance(profile,dict):
                    self.fail(path,'financial-reporting must be a company mapping')
                else:
                    family=profile.get('primary-source-family')
                    if not isinstance(family,str) or not ID.fullmatch(family):self.fail(path,'financial-reporting primary-source-family invalid')
                    if profile.get('confidence') not in CONFIDENCES:self.fail(path,'financial-reporting confidence invalid')
                    self.day(profile.get('reviewed'),path,'financial-reporting reviewed')
                    self.evidence(profile.get('evidence'),path,sources,documents)
                    calendar={'fiscal-year-end','calendar-valid-from','calendar-valid-to'}
                    if calendar & profile.keys():
                        if not calendar<=profile.keys():self.fail(path,'financial calendar needs year-end and validity interval')
                        try:
                            end=profile.get('fiscal-year-end')
                            if not isinstance(end,str) or not re.fullmatch(r'\d{2}-\d{2}',end):raise ValueError()
                            date.fromisoformat('2001-'+end)
                        except ValueError:self.fail(path,'financial calendar year-end invalid')
                        self.day(profile.get('calendar-valid-from'),path,'calendar-valid-from')
                        self.day(profile.get('calendar-valid-to'),path,'calendar-valid-to',True)
                        start,finish=profile.get('calendar-valid-from'),profile.get('calendar-valid-to')
                        if isinstance(start,str) and isinstance(finish,str) and finish<start:self.fail(path,'financial calendar interval reversed')
            for claim in obj['_claims'].values():
                self.text(claim.get('statement'), path, 'claim statement')
                if claim.get('confidence') not in CONFIDENCES:
                    self.fail(path, 'claim confidence invalid')
                self.array(claim.get('conditions'), path, 'claim conditions', 1, True)
                self.day(claim.get('reviewed'), path, 'claim reviewed')
                self.evidence(claim.get('evidence'), path, sources, documents)
            headings = []
            if kind == 'company':
                headings = ['供應角色', '研究界線']
                if obj.get('research-depth') == 'deep':
                    headings += ['產品與用途', '商業模式', '客戶與供應商', '競爭與替代', '業務曝險', '風險', '財務可取性']
                    if not obj['_claims'] or obj.get('reviewed') is None:
                        self.fail(path, 'deep research needs claims and reviewed')
            elif kind in ('application', 'role', 'product'):
                headings = ['定義與用途', '採用條件與限制'] + (['供應角色與公司'] if kind == 'product' else [])
                for field in ('definition', 'purpose', 'boundary'):
                    self.text(obj.get(field), path, field)
                for field in ('adoption-conditions', 'bottlenecks', 'substitution-limits'):
                    self.array(obj.get(field), path, field, 1, True)
            elif kind in ('concept', 'research'):
                for target in self.array(obj.get('related-ids'), path, 'related-ids', 1 if kind == 'research' else 0):
                    self.ref(target, path, 'related-ids')
                if kind == 'research':
                    headings = ['研究問題', '判斷與限制']
                else:
                    headings = ['中文解釋', '圖解', '適用範圍']
                    for field in ('definition', 'scope'):
                        self.text(obj.get(field), path, field)
                    for asset in self.array(obj.get('diagram-assets'), path, 'diagram-assets', 1):
                        if get(self.assets, asset) is None:
                            self.fail(path, 'diagram-assets unresolved')
                    for comparison in self.array(obj.get('comparisons'), path, 'comparisons'):
                        if not isinstance(comparison, dict):
                            self.fail(path, 'comparison must be mapping')
                            continue
                        for field in ('left', 'right'):
                            target = comparison.get(field)
                            if self.ref(target, path, 'comparison ' + field) and not target.startswith(('product-', 'concept-')):
                                self.fail(path, 'comparison endpoints must be product/concept')
                        for field in ('conditions', 'limitations'):
                            self.array(comparison.get(field), path, 'comparison ' + field, 1, True)
            if not self.skip_prose:
                for heading in headings:
                    if not re.search(r'^## ' + re.escape(heading) + r'\s*$', obj['_body'], re.M):
                        self.fail(path, 'missing prose heading ' + heading)

    def asset_manifest(self):
        manifest_path = self.root / 'research-assets.yaml'
        for key, asset in self.identified(self.manifest('research-assets.yaml', ['assets'])['assets'], manifest_path, 'asset-').items():
            for field in ('alt', 'license', 'attribution'):
                self.text(asset.get(field), manifest_path, 'asset ' + field)
            raw = asset.get('path', '')
            relative = PurePosixPath(raw) if isinstance(raw, str) else PurePosixPath('')
            path = self.root / relative
            if (not isinstance(raw, str) or '\\' in raw or relative.is_absolute() or '..' in relative.parts or
                    not relative.parts or relative.parts[0] != 'assets' or
                    any(p.is_symlink() for p in [path, *path.parents]) or
                    not path.resolve().is_relative_to((self.root / 'assets').resolve()) or not path.is_file()):
                self.fail(manifest_path, 'asset path escape, symlink, or missing file')
                continue
            if path.stat().st_size > 10 * 1024 * 1024:
                self.fail(manifest_path, 'asset exceeds 10 MiB')
                continue
            content = path.read_bytes()
            if asset.get('sha256') != hashlib.sha256(content).hexdigest():
                self.fail(manifest_path, 'asset hash mismatch')
            media = asset.get('media-type')
            magic = {'image/png': content.startswith(b'\x89PNG\r\n\x1a\n'),
                     'image/jpeg': content.startswith(b'\xff\xd8\xff'),
                     'image/webp': content.startswith(b'RIFF') and content[8:12] == b'WEBP'}
            if media == 'image/svg+xml':
                try:
                    if re.search(br'<!\s*(DOCTYPE|ENTITY)', content, re.I):
                        raise ValueError('DTD forbidden')
                    tree = ET.fromstring(content)
                    if tree.tag != '{http://www.w3.org/2000/svg}svg':
                        raise ValueError('not SVG')
                    for node in tree.iter():
                        if node.tag.rsplit('}', 1)[-1].lower() in ('script', 'foreignobject', 'style', 'animate', 'animatetransform', 'set'):
                            raise ValueError('active SVG element')
                        for attr, value in node.attrib.items():
                            name = attr.rsplit('}', 1)[-1].lower()
                            urls = re.findall(r'url\s*\((.*?)\)', value, re.I)
                            if (name.startswith('on') or name == 'style' or
                                    (name in ('href', 'src') and not value.startswith('#')) or
                                    any(not u.strip(' \t\"\'').startswith('#') for u in urls)):
                                raise ValueError('active/external SVG reference')
                except (ET.ParseError, ValueError) as exc:
                    self.fail(manifest_path, 'unsafe SVG: ' + str(exc))
            elif not get(magic, media):
                self.fail(manifest_path, 'asset media-type / bytes mismatch')
            self.assets[key] = asset

    def relations(self):
        path = self.root / 'research-relations.yaml'
        groups = self.manifest('research-relations.yaml', ['taxonomy', 'offerings', 'relations'])
        adjacency, symmetric = {}, set()

        def claims(value, supported=False):
            for item in self.array(value, path, 'claim-refs', 1):
                if not isinstance(item, dict):
                    self.fail(path, 'claim-ref must be mapping')
                    continue
                entity = get(self.entities, item.get('entity-id')) or {}
                claim = get(entity.get('_claims', {}), item.get('claim-id'))
                if not claim:
                    self.fail(path, 'claim-ref unresolved')
                elif supported and claim.get('confidence') != 'well-supported':
                    self.fail(path, 'named-supply needs well-supported claim')

        for group, prefix in [('taxonomy', 'taxonomy-'), ('offerings', 'offering-'), ('relations', 'relation-')]:
            for key, item in self.identified(groups[group], path, prefix, group).items():
                if group == 'taxonomy':
                    parent, child = item.get('parent'), item.get('child')
                    if self.ref(parent, path, 'taxonomy parent') and self.ref(child, path, 'taxonomy child'):
                        adjacency.setdefault(parent, []).append(child)
                elif group == 'offerings':
                    for field, kind in [('company', 'company'), ('product', 'product'), ('role', 'role')]:
                        self.ref(item.get(field), path, field, kind)
                    self.array(item.get('conditions'), path, 'offering conditions', 1, True)
                    claims(item.get('claim-refs'))
                else:
                    source, target, kind = item.get('source'), item.get('target'), item.get('kind')
                    self.ref(source, path, 'relation source')
                    self.ref(target, path, 'relation target')
                    if kind not in ('capability', 'named-supply', 'partnership', 'competition', 'demand-feedback'):
                        self.fail(path, 'relation kind invalid')
                    if item.get('direction') not in ('directed', 'symmetric'):
                        self.fail(path, 'relation direction invalid')
                    if item.get('direction') == 'symmetric':
                        if kind not in ('partnership', 'competition'):
                            self.fail(path, 'only partnership/competition may be symmetric')
                        pair = (str(kind), *sorted([str(source), str(target)]))
                        if pair in symmetric:
                            self.fail(path, 'duplicate symmetric relation')
                        symmetric.add(pair)
                    if kind == 'named-supply':
                        self.ref(source, path, 'named-supply source', 'company')
                        self.ref(target, path, 'named-supply target', 'company')
                        if item.get('confidence') != 'well-supported':
                            self.fail(path, 'named-supply confidence must be well-supported')
                    if kind == 'capability':
                        self.ref(source, path, 'capability source', 'company')
                        self.ref(target, path, 'capability target', 'product')
                    for field in ('product', 'application'):
                        if field in item:
                            self.ref(item[field], path, 'relation ' + field, field)
                    self.text(item.get('mechanism'), path, 'relation mechanism')
                    self.array(item.get('conditions'), path, 'relation conditions', 1, True)
                    if item.get('confidence') not in CONFIDENCES:
                        self.fail(path, 'relation confidence invalid')
                    self.day(item.get('reviewed'), path, 'relation reviewed')
                    claims(item.get('claim-refs'), kind == 'named-supply')
        # Kahn traversal remains bounded even for deeply nested authored trees.
        from collections import deque
        indegree = {node: 0 for node in adjacency}
        for children in adjacency.values():
            for child in children:
                indegree[child] = indegree.get(child, 0) + 1
        ready = deque(node for node, degree in indegree.items() if degree == 0)
        visited = 0
        while ready:
            node = ready.popleft()
            visited += 1
            for child in adjacency.get(node, []):
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
        if visited != len(indegree):
            self.fail(path, 'taxonomy cycle')
        return groups


def validate_research(map_dir, segments, themes, errors, parse_doc, load_yaml, skip_prose=False):
    validator = ResearchValidator(map_dir, segments, themes, errors, parse_doc, load_yaml, skip_prose)
    validator.load()
    validator.companies()
    validator.asset_manifest()
    validator.content()
    relations = validator.relations()
    return {'entities': validator.entities, 'assets': validator.assets, **relations}
