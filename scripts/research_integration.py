"""Task 9.1 integration run against the restore drill (restored real data, drill-only owner credential).

python scripts/research_integration.py

Owner flow (draft -> import -> validate -> preview -> publish -> restore) while readers poll the public API,
an interrupted candidate release, anonymous/CSRF/unpublished-release/SSRF/malicious-asset probes and a
source refresh with no network. Writes .work/research-drill/integration-<UTC>.json. Never targets 3014.
"""
import http.cookiejar
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from research_lab import protected_snapshot, verify_protected  # noqa: E402
from research_drill import env_values, preview_snapshot  # noqa: E402

WEB, API = 'http://127.0.0.1:3016', 'http://127.0.0.1:8016'
ENTITY, SOURCE = 'company-auras', 'twse-revenue'
MARKER = '（演練合成修改，不代表研究內容）'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Session:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect())
        self.csrf = None

    def call(self, method, path, data=None, *, origin=WEB, csrf=True, media=None, headers=None, base=WEB):
        head = {'Accept': 'application/json', **(headers or {})}
        if origin:
            head['Origin'] = origin
        if csrf and self.csrf:
            head['X-CSRF-Token'] = self.csrf
        body = data if media or data is None else json.dumps(data, ensure_ascii=False).encode()
        if body is not None:
            head['Content-Type'] = media or 'application/json'
        request = urllib.request.Request(base + path, data=body, method=method, headers=head)
        try:
            with self.opener.open(request, timeout=120) as response:
                raw, status = response.read(), response.status
        except urllib.error.HTTPError as error:
            raw, status = error.read(), error.code
        try:
            return status, json.loads(raw)
        except ValueError:
            return status, raw[:200].decode('utf-8', 'replace')

    def login(self, password):
        self.csrf = self.call('GET', '/api/admin/session', csrf=False)[1]['csrf_token']
        status, payload = self.call('POST', '/api/admin/session', {'password': password})
        if status != 200:
            raise RuntimeError(f'drill login failed: {status}')
        self.csrf = payload['csrf_token']


def drill(*args):
    output = subprocess.run([sys.executable, 'research_drill.py', *args], cwd=SCRIPTS, capture_output=True,
                            text=True, encoding='utf-8', check=True, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    return json.loads(output.stdout)


def db(sql):
    return subprocess.run(['docker', 'exec', 'industryflow-research-drill-db-1', 'psql', '-U', 'industry', '-d',
                           'industry_research', '-At', '-c', sql], capture_output=True, text=True, check=True).stdout.strip()


class Readers:
    """Poll the public company page through the web proxy and the API; every answer must be one release."""
    def __init__(self, workers=4):
        self.samples, self.errors, self.stop = [], [], threading.Event()
        self.threads = [threading.Thread(target=self.loop, args=(i,), daemon=True) for i in range(workers)]

    def loop(self, index):
        base = WEB if index % 2 == 0 else API
        while not self.stop.is_set():
            try:
                with urllib.request.urlopen(base + '/api/v2/companies/' + ENTITY, timeout=30) as response:
                    payload = json.load(response)
                self.samples.append((payload['release_id'], payload['data']['summary']))
            except Exception as error:  # noqa: BLE001 - every failure is a finding
                self.errors.append(f'{base}: {type(error).__name__}: {str(error)[:120]}')
            time.sleep(0.05)

    def __enter__(self):
        for thread in self.threads:
            thread.start()
        return self

    def __exit__(self, *exc):
        self.stop.set()
        for thread in self.threads:
            thread.join()

    def verdict(self, expected):
        mixed = [s for s in self.samples if expected.get(s[0]) != s[1]]
        return {'samples': len(self.samples), 'errors': self.errors[:10], 'error_count': len(self.errors),
                'by_release': {r: sum(1 for s in self.samples if s[0] == r) for r in expected},
                'mixed_or_unknown': len(mixed)}


def owner_flow(owner, report):
    status, active = owner.call('GET', '/api/admin/releases')
    old = active['active_release_id']
    with urllib.request.urlopen(API + '/api/v2/companies/' + ENTITY) as response:
        old_summary = json.load(response)['data']['summary']
    status, created = owner.call('POST', '/api/admin/drafts', {})
    draft = created['draft_id']
    status, exported = owner.call('GET', f'/api/admin/drafts/{draft}/export')
    path = f'industry-map/companies/{ENTITY}.md'
    exported['files'][path] = exported['files'][path].replace('summary: ' + old_summary, 'summary: ' + old_summary + MARKER, 1)
    if MARKER not in exported['files'][path]:
        raise RuntimeError('synthetic summary change did not apply')
    status, imported = owner.call('POST', f'/api/admin/drafts/{draft}/import', exported,
                                  headers={'If-Match': f'"{exported["revision"]}"'})
    revision = imported['revision']
    stale, _ = owner.call('POST', f'/api/admin/drafts/{draft}/import', exported, headers={'If-Match': f'"{exported["revision"]}"'})
    valid = owner.call('POST', f'/api/admin/drafts/{draft}/validate')[1]
    preview_status, preview = owner.call('GET', f'/api/admin/drafts/{draft}/preview?entity_id={ENTITY}')
    diff_status, _ = owner.call('GET', f'/api/admin/drafts/{draft}/diff?against=active')
    key = str(uuid.uuid4())
    body = {'base_release_id': old, 'revision': revision, 'reason': '演練：發布期間閱讀'}
    publish_status, job = owner.call('POST', f'/api/admin/drafts/{draft}/publish', body, headers={'Idempotency-Key': key})
    replay_status, replay = owner.call('POST', f'/api/admin/drafts/{draft}/publish', body, headers={'Idempotency-Key': key})
    conflict_status, _ = owner.call('POST', f'/api/admin/drafts/{draft}/publish', {**body, 'reason': '不同內容'},
                                    headers={'Idempotency-Key': key})
    with Readers() as readers:
        time.sleep(3)
        started = time.time()
        result = drill('run-job', '--job', job['job_id'])
        publish_seconds = time.time() - started
        time.sleep(3)
    new = result['target_release_id']
    publish = readers.verdict({old: old_summary, new: old_summary + MARKER})
    with Readers() as readers:
        time.sleep(3)
        status, restore = owner.call('POST', f'/api/admin/releases/{old}/restore',
                                     {'base_release_id': new, 'reason': '演練：還原期間閱讀'}, headers={'Idempotency-Key': str(uuid.uuid4())})
        started = time.time()
        restored = drill('run-job', '--job', restore['job_id'])
        restore_seconds = time.time() - started
        time.sleep(3)
    restored_id = restored['target_release_id']
    rollback = readers.verdict({new: old_summary + MARKER, restored_id: old_summary, old: old_summary})
    with urllib.request.urlopen(API + '/api/v2/manifest') as response:
        manifest = json.load(response)
    report['owner_flow'] = {
        'draft_import_ok': bool(revision), 'stale_import_status': stale, 'validate_valid': valid.get('valid'),
        'preview_status': preview_status, 'diff_status': diff_status, 'publish_status': publish_status,
        'idempotent_replay': [replay_status, replay.get('job_id') == job['job_id']], 'idempotency_conflict_status': conflict_status,
        'publish_job': result, 'publish_seconds': round(publish_seconds, 1), 'reads_during_publish': publish,
        'restore_job': restored, 'restore_seconds': round(restore_seconds, 1), 'reads_during_restore': rollback,
        'restored_release_id': restored_id, 'restored_content_matches_old': db(
            f"SELECT (SELECT content_hash FROM research.research_releases WHERE release_id='{restored_id}') = "
            f"(SELECT content_hash FROM research.research_releases WHERE release_id='{old}')") == 't',
        'manifest_after': manifest}
    return draft


def interrupted_candidate(owner, report):
    status, created = owner.call('POST', '/api/admin/drafts', {})
    draft = created['draft_id']
    exported = owner.call('GET', f'/api/admin/drafts/{draft}/export')[1]
    path = f'industry-map/companies/{ENTITY}.md'
    exported['files'][path] = exported['files'][path].replace('\nsummary: ', '\nsummary: 未發布候選測試；', 1)
    revision = owner.call('POST', f'/api/admin/drafts/{draft}/import', exported, headers={'If-Match': f'"{exported["revision"]}"'})[1]['revision']
    base = owner.call('GET', '/api/admin/releases')[1]['active_release_id']
    head_before = db("SELECT release_id || ':' || generation FROM research.release_head")
    job = owner.call('POST', f'/api/admin/drafts/{draft}/publish', {'base_release_id': base, 'revision': revision, 'reason': '演練：中斷候選'},
                     headers={'Idempotency-Key': str(uuid.uuid4())})[1]
    stopped = drill('run-job', '--job', job['job_id'], '--stop-at', 'before-activation')
    candidate = db(f"SELECT target_release_id FROM research.publish_jobs WHERE job_id='{job['job_id']}'")
    statuses = db(f"SELECT status FROM research.research_releases WHERE release_id='{candidate}'") if candidate else ''
    probes = {}
    for label, path in [('catalog', f'/api/v2/catalog?release_id={candidate}'),
                        ('company', f'/api/v2/companies/{ENTITY}?release_id={candidate}'),
                        ('random-release', f'/api/v2/catalog?release_id={uuid.uuid4()}')]:
        for target in (API, WEB):
            probes[f'{label}@{target[-4:]}'] = Session().call('GET', path, base=target, origin=None)[0]
    head_after = db("SELECT release_id || ':' || generation FROM research.release_head")
    report['unpublished_candidate'] = {'job': stopped, 'candidate_release': candidate, 'candidate_status': statuses,
                                       'reader_status': probes, 'head_before': head_before, 'head_after': head_after,
                                       'active_unchanged': head_before == head_after and head_before.startswith(base)}


def security(owner, report, draft):
    anonymous = Session()
    anonymous.csrf = anonymous.call('GET', '/api/admin/session', csrf=False)[1]['csrf_token']
    report['anonymous'] = {
        'drafts_list': anonymous.call('GET', '/api/admin/drafts')[0],
        'coverage': anonymous.call('GET', '/api/admin/coverage')[0],
        'draft_export': anonymous.call('GET', f'/api/admin/drafts/{draft}/export')[0],
        'create_draft': anonymous.call('POST', '/api/admin/drafts', {})[0],
        'restore': anonymous.call('POST', f'/api/admin/releases/{uuid.uuid4()}/restore', {'base_release_id': str(uuid.uuid4()), 'reason': 'x'})[0],
        'api_direct_drafts': anonymous.call('GET', '/api/admin/drafts', base=API, origin=None)[0],
        'reader_post': Session().call('POST', '/api/v2/catalog', {}, base=API, origin=None)[0],
        'reader_delete': Session().call('DELETE', f'/api/v2/companies/{ENTITY}', base=API, origin=None)[0]}
    token = owner.csrf
    owner.csrf = None
    no_token = owner.call('POST', '/api/admin/drafts', {})[0]
    owner.csrf = 'wrong-token'
    wrong_token = owner.call('POST', '/api/admin/drafts', {})[0]
    owner.csrf = token
    report['csrf'] = {'missing_token': no_token, 'wrong_token': wrong_token,
                      'cross_origin': owner.call('POST', '/api/admin/drafts', {}, origin='https://evil.example')[0],
                      'no_origin': owner.call('POST', '/api/admin/drafts', {}, origin=None)[0],
                      'foreign_host_api': owner.call('GET', '/api/admin/drafts', base=API, origin=None,
                                                     headers={'Host': 'evil.example'})[0]}
    count_assets = lambda: int(subprocess.run(['docker', 'exec', 'industryflow-research-drill-api-1', 'sh', '-c',
                                               'ls /home/app/research-assets | wc -l'], capture_output=True, text=True).stdout)
    before = count_assets()
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
    cases = {
        'svg_script': ('industry-map/assets/drill-a.svg', 'image/svg+xml', b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'),
        'svg_event': ('industry-map/assets/drill-b.svg', 'image/svg+xml', b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>'),
        'svg_external_href': ('industry-map/assets/drill-c.svg', 'image/svg+xml',
                              b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://evil.example/x.png"/></svg>'),
        'svg_entity': ('industry-map/assets/drill-d.svg', 'image/svg+xml',
                       b'<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg xmlns="http://www.w3.org/2000/svg">&x;</svg>'),
        'path_traversal': ('industry-map/assets/../../backend/app/drill.svg', 'image/svg+xml', svg),
        'outside_assets': ('industry-map/companies/drill.svg', 'image/svg+xml', svg),
        'type_mismatch': ('industry-map/assets/drill-e.png', 'image/png', svg),
        'oversize': ('industry-map/assets/drill-f.svg', 'image/svg+xml', svg + b' ' * (11 * 1024 * 1024)),
    }
    uploads = {name: owner.call('POST', '/api/admin/drafts/asset-upload?path=' + urllib.parse.quote(path), body, media=media)[0]
               for name, (path, media, body) in cases.items()}
    exported = owner.call('GET', f'/api/admin/drafts/{draft}/export')[1]
    revision = exported['revision']
    imports = {}
    for name, change in {
        'path_escape': lambda f: f.update({'industry-map/../escape.md': '# x\n'}),
        'code_file': lambda f: f.update({'backend/app/evil.py': 'import os\n'}),
        'schema_readme': lambda f: f.update({'industry-map/README.md': f['industry-map/README.md'] + '\nx\n'}),
        'script_link': lambda f: f.update({f'industry-map/companies/{ENTITY}.md': f[f'industry-map/companies/{ENTITY}.md'] + '\n[x](javascript:alert(1))\n'}),
        'oversize_draft': lambda f: f.update({f'industry-map/companies/{ENTITY}.md': f[f'industry-map/companies/{ENTITY}.md'] + 'x' * (6 * 1024 * 1024)}),
    }.items():
        files = dict(exported['files'])
        change(files)
        imports[name] = owner.call('POST', f'/api/admin/drafts/{draft}/import', {**exported, 'files': files},
                                   headers={'If-Match': f'"{revision}"'})[0]
    unchanged = owner.call('GET', f'/api/admin/drafts/{draft}/export')[1]['revision'] == revision
    ssrf = {'url_as_source_id': owner.call('POST', '/api/admin/sources/' + urllib.parse.quote('http://169.254.169.254/latest', safe='') + '/refresh')[0],
            'unregistered_source': owner.call('POST', '/api/admin/sources/not-a-registered-source/refresh')[0],
            'manual_source': owner.call('POST', '/api/admin/sources/mops-manual/refresh')[0]}
    report['malicious_assets'] = {'uploads': uploads, 'asset_files_before': before, 'asset_files_after': count_assets()}
    report['malicious_drafts'] = {'imports': imports, 'revision_unchanged': unchanged}
    report['ssrf'] = ssrf


def source_failure(owner, report):
    # Revenue rows only feed theme proxy indicators; a failed refresh must leave both untouched.
    def state():
        return {'revenue_rows': db(f"SELECT count(*) FROM public.financials WHERE source_id='{SOURCE}'"),
                'indicator_observations': db('SELECT count(*) FROM public.indicator_observations'),
                'release': db('SELECT release_id FROM research.release_head')}
    before = state()
    result = drill('offline-refresh', '--source', SOURCE)
    source = owner.call('GET', f'/api/admin/sources/{SOURCE}')[1]
    after = state()
    report['source_failure'] = {'refresh_result': result, 'source_status': source.get('status'),
                                'source_error_present': bool(source.get('error')), 'last_job_status': (source.get('last_job') or {}).get('status'),
                                'last_success_kept': source.get('last_success'),
                                'revenue_rows_unchanged': before['revenue_rows'] == after['revenue_rows'],
                                'indicator_observations_unchanged': before['indicator_observations'] == after['indicator_observations'],
                                'release_unchanged': before['release'] == after['release']}


def main():
    protected, preview = protected_snapshot(), preview_snapshot()
    report = {'started_at': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), 'target': WEB}
    owner = Session()
    owner.login(env_values()['DRILL_OWNER_PASSWORD'])
    draft = owner_flow(owner, report)
    interrupted_candidate(owner, report)
    security(owner, report, draft)
    source_failure(owner, report)
    owner.call('DELETE', '/api/admin/session')
    report['logout_then_drafts'] = owner.call('GET', '/api/admin/drafts')[0]
    verify_protected(protected)
    report['protected_services_unchanged'] = True
    report['preview_unchanged'] = preview_snapshot() == preview
    folder = ROOT / '.work/research-drill'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'integration-{report["started_at"]}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
