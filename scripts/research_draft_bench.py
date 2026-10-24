"""Draft editing latency in the restore drill (owner flow through the web proxy, real API and PostgreSQL).

python scripts/research_draft_bench.py --label before-real
python scripts/research_draft_bench.py --label before-scaled --dataset scaled

real:   create a draft from the drill head and measure it as is.
scaled: create a draft, then import research_scale.build_tree() (300 companies, 3,000 relations) through the
        same import endpoint the CLI uses. A rejected create/import is recorded and the remaining steps continue.

Each run measures 30 company-document saves, 30 relation-manifest saves (scaled only), first and repeated
validation, the diff against the base and one preview including every diagram it references. The API
container's memory peak is sampled with docker stats. Writes .work/research-draft-bench/<label>.json.
Drafts are never published; the readers' release does not change.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
REPORTS = ROOT / '.work/research-draft-bench'
API_CONTAINER = 'industryflow-research-drill-api-1'
COMPANY = 'industry-map/companies/company-auras.md'
RELATIONS = 'industry-map/research-relations.yaml'
VALIDATION_LOG = 'draft-validation computed'


def percentile(values, q):
    """Nearest-rank percentile; None for an empty sample."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q / 100 * len(ordered)) - 1)]


def summarize(samples):
    times = [sample['ms'] for sample in samples]
    statuses = {}
    for sample in samples:
        statuses[str(sample['status'])] = statuses.get(str(sample['status']), 0) + 1
    errors = sorted({sample['code'] for sample in samples if sample.get('code')})
    return {'count': len(samples), 'p50_ms': percentile(times, 50), 'p95_ms': percentile(times, 95),
            'max_ms': max(times) if times else None, 'statuses': statuses, 'error_codes': errors}


def memory_mib(text):
    """Parse the used part of docker stats MemUsage, e.g. '104.2MiB / 7.46GiB'."""
    match = re.match(r'\s*([\d.]+)\s*([KMG]i?B)', text)
    if not match:
        return None
    scale = {'KiB': 1 / 1024, 'KB': 1 / 1024, 'MiB': 1, 'MB': 1, 'GiB': 1024, 'GB': 1024}[match[2]]
    return round(float(match[1]) * scale, 1)


class MemoryPeak:
    def __init__(self, container=API_CONTAINER, interval=2.0):
        self.container, self.interval, self.peak, self.stop = container, interval, None, threading.Event()
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def loop(self):
        while not self.stop.is_set():
            result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.MemUsage}}', self.container],
                                    capture_output=True, text=True)
            value = memory_mib(result.stdout) if result.returncode == 0 else None
            if value is not None and (self.peak is None or value > self.peak):
                self.peak = value
            self.stop.wait(self.interval)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join(timeout=30)


def validations_since(started):
    """Count full validations the API logged since `started` (only builds that log them)."""
    result = subprocess.run(['docker', 'logs', '--since', started, API_CONTAINER], capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    return (result.stdout + result.stderr).count(VALIDATION_LOG) if result.returncode == 0 else None


def timed(owner, method, path, data=None, headers=None):
    started = time.perf_counter()
    status, payload = owner.call(method, path, data, headers=headers)
    sample = {'status': status, 'ms': round((time.perf_counter() - started) * 1000, 1)}
    if status >= 400 and isinstance(payload, dict):
        sample['code'] = payload.get('code')
    return sample, payload


def scaled_files(exported):
    import research_scale
    research_scale.build_tree()
    files = dict(exported['files'])
    for path in research_scale.TREE.rglob('*'):
        name = path.relative_to(research_scale.TREE).as_posix()
        if path.is_file() and not name.startswith('industry-map/assets/') and name != 'industry-map/README.md':
            files[name] = path.read_text(encoding='utf-8')
    return files


def preview_entity(files):
    """A company or concept page that references at least one diagram, so asset requests are measured."""
    for path, content in sorted(files.items()):
        if path.endswith('.md') and re.search(r'^diagram-assets:[ \t]*(\[[ \t]*[\w-]|\n[ \t]*-[ \t]*[\w-])', content, re.M):
            found = re.search(r'^entity-id:\s*(\S+)', content, re.M)
            if found:
                return found[1]
    return 'company-auras'


def measure(owner, dataset, saves):
    report = {'dataset': dataset, 'steps': {}}
    steps = report['steps']
    sample, created = timed(owner, 'POST', '/api/admin/drafts', {})
    steps['create'] = summarize([sample])
    if sample['status'] != 201:
        return report
    draft = created['draft_id']
    url = '/api/admin/drafts/' + draft
    revision = created['revision']
    sample, exported = timed(owner, 'GET', url + '/export')
    files = exported['files']
    if dataset == 'scaled':
        files = scaled_files(exported)
        report['payload_bytes'] = len(json.dumps(files, ensure_ascii=False).encode())
        sample, imported = timed(owner, 'POST', url + '/import', {**exported, 'files': files},
                                 headers={'If-Match': f'"{revision}"'})
        steps['import'] = summarize([sample])
        if sample['status'] != 200:
            report['import_error'] = imported.get('message', '')[:300] if isinstance(imported, dict) else str(imported)[:300]
            return report
        revision = imported['revision']
    report['files'] = len(files)

    status, parts = owner.call('GET', url + '/document?path=' + COMPANY)
    samples = []
    for index in range(saves):
        fields = dict(parts['frontmatter'])
        fields['summary'] = parts['frontmatter']['summary'] + f'（量測 {index}）'
        sample, saved = timed(owner, 'PATCH', url, {'changes': [{'path': COMPANY, 'frontmatter': fields, 'markdown': parts['markdown']}]},
                              headers={'If-Match': f'"{revision}"'})
        samples.append(sample)
        if sample['status'] == 200:
            revision = saved['revision']
    steps['save_company'] = summarize(samples)

    if dataset == 'scaled':
        samples, manifest = [], files[RELATIONS]
        for index in range(saves):
            sample, saved = timed(owner, 'PATCH', url, {'changes': [{'path': RELATIONS, 'content': manifest + f'# 量測 {index}\n'}]},
                                  headers={'If-Match': f'"{revision}"'})
            samples.append(sample)
            if sample['status'] == 200:
                revision = saved['revision']
        steps['save_relations'] = summarize(samples)

    sample, first = timed(owner, 'POST', f'{url}/validate?revision={revision}')
    steps['validate_first'] = summarize([sample])
    report['valid'] = first.get('valid') if isinstance(first, dict) else None
    sample, _ = timed(owner, 'POST', f'{url}/validate?revision={revision}')
    steps['validate_repeat'] = summarize([sample])
    sample, _ = timed(owner, 'GET', url + '/diff')
    steps['diff'] = summarize([sample])

    entity = preview_entity(files)
    started_log = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    began = time.perf_counter()
    sample, preview = timed(owner, 'GET', f'{url}/preview?entity_id={entity}&revision={revision}')
    assets = [asset['url'] for asset in preview.get('data', {}).get('assets', [])] if sample['status'] == 200 else []
    with ThreadPoolExecutor(max_workers=6) as pool:  # browsers fetch a page's images in parallel
        asset_samples = list(pool.map(lambda path: timed(owner, 'GET', path)[0], assets))
    steps['preview'] = summarize([sample])
    steps['preview_assets'] = summarize(asset_samples)
    steps['preview_total'] = {'ms': round((time.perf_counter() - began) * 1000, 1), 'entity': entity, 'assets': len(assets),
                              'validations_logged': validations_since(started_log)}
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--label', required=True, help='report name, e.g. before-real')
    parser.add_argument('--dataset', choices=['real', 'scaled'], default='real')
    parser.add_argument('--saves', type=int, default=30)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(SCRIPTS))
    from research_drill import env_values
    from research_integration import Session
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    owner = Session()
    owner.login(env_values()['DRILL_OWNER_PASSWORD'])
    try:
        with MemoryPeak() as memory:
            report = measure(owner, args.dataset, args.saves)
    finally:
        owner.call('DELETE', '/api/admin/session')
    report.update(label=args.label, commit=commit, measured_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  api_memory_peak_mib=memory.peak)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f'{args.label}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
