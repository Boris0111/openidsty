"""Draft editing latency in the restore drill (owner flow through the web proxy, real API and PostgreSQL).

python scripts/research_draft_bench.py --label before-real
python scripts/research_draft_bench.py --label before-scaled --dataset scaled

real:   create a draft from the drill head and measure it as is.
scaled: create a draft, then import research_scale.build_tree() (300 companies, 3,000 relations) through the
        same import endpoint the CLI uses. A rejected create/import is recorded and the remaining steps continue.

Each run measures 30 company-document saves, 30 relation-manifest saves (scaled only), first and repeated
validation, the diff against the base and --previews reading previews (default 20) that rotate through a fixed
list of pages. Diagram requests of a previewed page are recorded separately, not in the preview time. The API's
`draft-preview timing` log lines (builds that write them) give the per-stage medians; older builds report null.
The API container's memory peak is sampled with docker stats. Writes .work/research-draft-bench/<label>.json,
including draft_id, which scripts/research_editor_latency.cjs opens. Drafts are never published; the readers'
release does not change.
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
TIMING_LOG = 'draft-preview timing'
TIMING_FIELDS = ('project_ms', 'flush_ms', 'detail_ms', 'graph_ms')
# Pages previewed in turn: a concept with diagrams, a company, segments and themes; the scaled tree adds
# synthetic companies whose relations exist only there.
PREVIEW_PAGES = ['concept-hbm-stack', 'company-auras', 'segment-thermal', 'segment-pcb', 'theme-liquid-cooling',
                 'segment-compute', 'theme-hbm4']
SCALED_PAGES = ['company-synth-001', 'company-synth-150']


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


def api_log_since(started):
    """The drill API's log since `started`, or None when docker cannot read it."""
    result = subprocess.run(['docker', 'logs', '--since', started, API_CONTAINER], capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    return result.stdout + result.stderr if result.returncode == 0 else None


def preview_timings(log, draft_id):
    """The numeric fields of every `draft-preview timing` line for this draft, in log order."""
    rows = []
    for line in (log or '').splitlines():
        if TIMING_LOG not in line or f'draft={draft_id}' not in line:
            continue
        fields = dict(re.findall(r'(\w+)=([0-9.]+)', line.split(TIMING_LOG, 1)[1]))
        rows.append({key: float(fields[key]) for key in TIMING_FIELDS if key in fields})
    return rows


def timing_medians(rows):
    """Median of each stage over the logged previews; None when the build logs no timing (before the change)."""
    if not rows:
        return None
    medians = {}
    for key in TIMING_FIELDS:
        values = sorted(row[key] for row in rows if key in row)
        if values:
            middle = len(values) // 2
            medians[key] = values[middle] if len(values) % 2 else round((values[middle - 1] + values[middle]) / 2, 1)
    return medians


def preview_pages(dataset, count):
    """`count` previews rotating through the fixed page list."""
    pages = PREVIEW_PAGES + (SCALED_PAGES if dataset == 'scaled' else [])
    return [pages[index % len(pages)] for index in range(count)]


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


def measure(owner, dataset, saves, previews=20):
    report = {'dataset': dataset, 'steps': {}}
    steps = report['steps']
    sample, created = timed(owner, 'POST', '/api/admin/drafts', {})
    steps['create'] = summarize([sample])
    if sample['status'] != 201:
        return report
    draft = created['draft_id']
    report['draft_id'] = draft
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

    started_log = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    samples, asset_samples, pages = [], [], preview_pages(dataset, previews)
    for entity in pages:
        sample, preview = timed(owner, 'GET', f'{url}/preview?entity_id={entity}&revision={revision}')
        samples.append({**sample, 'entity': entity})
        assets = [asset['url'] for asset in preview.get('data', {}).get('assets', [])] if sample['status'] == 200 else []
        with ThreadPoolExecutor(max_workers=6) as pool:  # browsers fetch a page's images in parallel
            asset_samples += list(pool.map(lambda path: timed(owner, 'GET', path)[0], assets))
    steps['preview'] = {**summarize(samples), 'pages': pages}
    steps['preview_assets'] = summarize(asset_samples)  # diagrams are not part of the preview time
    log = api_log_since(started_log)
    rows = preview_timings(log, draft)
    report['preview_timing'] = {'lines': None if log is None else len(rows), 'medians_ms': timing_medians(rows)}
    report['preview_validations_logged'] = None if log is None else log.count(VALIDATION_LOG)
    return report


def drill_password(env_file):
    """DRILL_OWNER_PASSWORD from the drill env file; the value is never printed or stored in a report."""
    for line in Path(env_file).read_text(encoding='utf-8').splitlines():
        if line.startswith('DRILL_OWNER_PASSWORD='):
            return line.split('=', 1)[1]
    raise SystemExit('drill env file has no DRILL_OWNER_PASSWORD; run research_drill.py setup and owner first')


def default_env_file():
    """The drill secrets every drill script reads (INDUSTRYFLOW_DRILL_HOME), whichever checkout runs this."""
    sys.path.insert(0, str(SCRIPTS))
    from research_drill import ENV_FILE
    return ENV_FILE


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--label', required=True, help='report name, e.g. before-real')
    parser.add_argument('--dataset', choices=['real', 'scaled'], default='real')
    parser.add_argument('--saves', type=int, default=30)
    parser.add_argument('--previews', type=int, default=20, help='reading previews after validation (default 20)')
    parser.add_argument('--env-file', type=Path, default=default_env_file(),
                        help='drill secrets; default from INDUSTRYFLOW_DRILL_HOME, shared by every checkout and worktree')
    args = parser.parse_args(argv)
    sys.path.insert(0, str(SCRIPTS))
    from research_integration import Session
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    # The measured code is the drill API's image, not this script's checkout.
    image = subprocess.run(['docker', 'inspect', '--format', '{{.Image}}', API_CONTAINER], capture_output=True, text=True).stdout.strip()
    owner = Session()
    owner.login(drill_password(args.env_file))
    try:
        with MemoryPeak() as memory:
            report = measure(owner, args.dataset, args.saves, args.previews)
    finally:
        owner.call('DELETE', '/api/admin/session')
    report.update(label=args.label, commit=commit, api_image=image, measured_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  api_memory_peak_mib=memory.peak)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f'{args.label}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
