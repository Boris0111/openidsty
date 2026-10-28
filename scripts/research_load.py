"""Task 9.2 read-load benchmark against the restore drill (real or scaled data). GET only, except owner login.

python scripts/research_load.py --label real --background twse-revenue
python scripts/research_load.py --label scaled --background twse-revenue

10 closed-loop readers through the web proxy (http://127.0.0.1:3016), fixed mix profile 35% / graph 25% /
search 15% / dynamic (events, comparison) 15% / coverage 10%, 60 s warm-up then 300 s measured. A real source refresh runs during
the measured window. Writes .work/research-load/<label>.json. Targets: p95 < 500 ms, coverage p95 < 1000 ms.
"""
import argparse
import http.cookiejar
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from research_drill import env_values, running_images  # noqa: E402

WEB = 'http://127.0.0.1:3016'
MIX = [('profile', 35), ('graph', 25), ('search', 15), ('dynamic', 15), ('coverage', 10)]
TARGET = {'profile': 500, 'graph': 500, 'search': 500, 'dynamic': 500, 'coverage': 1000}
DB = 'industryflow-research-drill-db-1'


def percentile(values, q):
    ordered = sorted(values)
    return round(ordered[max(0, math.ceil(q * len(ordered)) - 1)], 1) if ordered else None


def get_json(opener, path):
    with opener.open(urllib.request.Request(WEB + path, headers={'Accept': 'application/json'}), timeout=60) as response:
        return json.load(response)


def owner_opener():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    csrf = get_json(opener, '/api/admin/session')['csrf_token']
    body = json.dumps({'password': env_values()['DRILL_OWNER_PASSWORD']}).encode()
    request = urllib.request.Request(WEB + '/api/admin/session', data=body, method='POST', headers={
        'Origin': WEB, 'X-CSRF-Token': csrf, 'Content-Type': 'application/json', 'Accept': 'application/json'})
    with opener.open(request, timeout=60) as response:
        json.load(response)
    return opener


def discover(owner):
    plain = urllib.request.build_opener()
    companies, cursor = [], None
    while True:
        page = get_json(plain, '/api/v2/companies?limit=100' + (f'&cursor={urllib.parse.quote(cursor)}' if cursor else ''))['data']
        companies += [item for item in page['items']]
        if not page.get('has_more'):
            break
        cursor = page['next_cursor']
    ids = [c['id'] for c in companies]
    others = []
    for kind in ('products', 'roles', 'applications'):
        others += [f'{kind}/{item["id"]}' for item in get_json(plain, f'/api/v2/{kind}?limit=100')['data']['items']]
    terms = sorted({c['name'][:2] for c in companies if c.get('name')} | {'TSMC', 'NVIDIA', 'cooling', '液冷', 'HBM', 'CoWoS'})
    paths = {
        'profile': [f'/api/v2/companies/{c}' for c in ids] + [f'/api/v2/{o}' for o in others],
        'graph': [f'/api/v2/graphs?root={c}&scope=company' for c in ids],
        'search': [f'/api/v2/search?q={urllib.parse.quote(t)}' for t in terms],
        'dynamic': [f'/api/v2/events?entity_id={c}' for c in ids] +
                   [f'/api/v2/compare?company_ids={a},{b}' for a, b in zip(ids[::2], ids[1::2])],
        'coverage': ['/api/admin/coverage', '/api/admin/coverage/entities', '/api/admin/coverage/entities?status=not-researched'],
    }
    return paths, {'companies': len(ids), 'other_pages': len(others), 'search_terms': len(terms)}


def sample_resources(stop, samples):
    while not stop.is_set():
        try:
            out = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{json .}}'], capture_output=True, text=True, timeout=30).stdout
            rows = [json.loads(line) for line in out.splitlines() if 'research-drill' in line]
            connections = subprocess.run(['docker', 'exec', DB, 'psql', '-U', 'industry', '-d', 'industry_research', '-At', '-c',
                                          "SELECT count(*) FROM pg_stat_activity WHERE datname='industry_research'"],
                                         capture_output=True, text=True, timeout=30).stdout.strip()
            samples.append({'t': time.time(), 'containers': {r['Name']: {'cpu': r['CPUPerc'], 'mem': r['MemUsage']} for r in rows},
                            'db_connections': int(connections or 0)})
        except Exception as error:  # noqa: BLE001
            samples.append({'t': time.time(), 'error': str(error)[:120]})
        stop.wait(10)


def db_stats():
    query = ("SELECT json_build_object('xact_commit', xact_commit, 'tup_returned', tup_returned, 'tup_fetched', tup_fetched, "
             "'blks_hit', blks_hit, 'blks_read', blks_read, 'temp_bytes', temp_bytes, 'deadlocks', deadlocks, "
             "'seq_scan', (SELECT sum(seq_scan) FROM pg_stat_user_tables), 'idx_scan', (SELECT sum(idx_scan) FROM pg_stat_user_tables)) "
             "FROM pg_stat_database WHERE datname='industry_research'")
    return json.loads(subprocess.run(['docker', 'exec', DB, 'psql', '-U', 'industry', '-d', 'industry_research', '-At', '-c', query],
                                     capture_output=True, text=True, check=True).stdout)


def worker(index, paths, owner, deadline_warm, deadline, records):
    rng = random.Random(9200 + index)
    plain = urllib.request.build_opener()
    categories, weights = zip(*MIX)
    cursor = {c: rng.randrange(len(paths[c])) for c in categories}
    while time.time() < deadline:
        category = rng.choices(categories, weights)[0]
        path = paths[category][cursor[category] % len(paths[category])]
        cursor[category] += 1
        opener = owner if category == 'coverage' else plain
        started = time.perf_counter()
        status, size, cache = 0, 0, ''
        try:
            with opener.open(urllib.request.Request(WEB + path, headers={'Accept': 'application/json'}), timeout=60) as response:
                body = response.read()
                status, size, cache = response.status, len(body), response.headers.get('Cache-Control', '')
                json.loads(body)
        except urllib.error.HTTPError as error:
            status = error.code
        except Exception:  # noqa: BLE001 - timeouts and parse errors are errors
            status = -1
        elapsed = (time.perf_counter() - started) * 1000
        if time.time() >= deadline_warm:
            records.append((category, elapsed, status, size, cache))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--users', type=int, default=10)
    parser.add_argument('--warmup', type=int, default=60)
    parser.add_argument('--duration', type=int, default=300)
    parser.add_argument('--background', help='registered source id refreshed for real during the measured window')
    args = parser.parse_args()
    owner = owner_opener()
    paths, inventory = discover(owner)
    stats_before = db_stats()
    records, samples, stop = [], [], threading.Event()
    sampler = threading.Thread(target=sample_resources, args=(stop, samples), daemon=True)
    start = time.time()
    warm_end, end = start + args.warmup, start + args.warmup + args.duration
    threads = [threading.Thread(target=worker, args=(i, paths, owner, warm_end, end, records)) for i in range(args.users)]
    for thread in threads:
        thread.start()
    sampler.start()
    background = None
    if args.background:
        while time.time() < warm_end:
            time.sleep(1)
        begun = time.time()
        result = subprocess.run([sys.executable, 'research_drill.py', 'online-refresh', '--source', args.background], cwd=SCRIPTS,
                                capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        background = {'source': args.background, 'seconds': round(time.time() - begun, 1), 'exit': result.returncode,
                      'result': (result.stdout.strip() or result.stderr.strip())[-1500:]}
    for thread in threads:
        thread.join()
    stop.set()
    sampler.join()
    stats_after = db_stats()
    summary = {}
    for category, _ in MIX:
        rows = [r for r in records if r[0] == category]
        ok = [r[1] for r in rows if r[2] == 200]
        errors = [r for r in rows if r[2] != 200]
        summary[category] = {'samples': len(rows), 'p50_ms': percentile(ok, .5), 'p95_ms': percentile(ok, .95), 'p99_ms': percentile(ok, .99),
                             'max_ms': round(max(ok), 1) if ok else None, 'errors': len(errors),
                             'error_rate': round(len(errors) / len(rows), 4) if rows else None,
                             'error_statuses': sorted({r[2] for r in errors}), 'mean_bytes': round(sum(r[3] for r in rows) / len(rows)) if rows else None,
                             'cache_control': sorted({r[4] for r in rows}), 'target_ms': TARGET[category],
                             'meets_target': bool(ok) and percentile(ok, .95) < TARGET[category] and len(rows) >= 100 and not errors}
    docker_info = json.loads(subprocess.run(['docker', 'info', '--format', '{{json .}}'], capture_output=True, text=True).stdout)
    report = {
        'label': args.label, 'started_at': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(start)),
        'users': args.users, 'warmup_s': args.warmup, 'duration_s': args.duration, 'mix': dict(MIX),
        'path': 'load script -> web proxy 127.0.0.1:3016 -> drill API -> drill PostgreSQL',
        'inventory': inventory, 'summary': summary, 'throughput_rps': round(len(records) / args.duration, 1),
        'background_update': background, 'resources': samples, 'db_stats_delta': {k: (stats_after[k] or 0) - (stats_before[k] or 0) for k in stats_after},
        'versions': {'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
                     **running_images(),  # the images the drill actually ran, tagged by commit
                     'postgres': subprocess.run(['docker', 'exec', DB, 'postgres', '--version'], capture_output=True, text=True).stdout.strip()},
        'hardware': {'host': platform.platform(), 'host_logical_cpus': os.cpu_count(), 'docker_cpus': docker_info.get('NCPU'),
                     'docker_memory_bytes': docker_info.get('MemTotal'), 'docker_version': docker_info.get('ServerVersion')},
        'all_targets_met': all(v['meets_target'] for v in summary.values()),
    }
    folder = ROOT / '.work/research-load'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'{args.label}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('label', 'inventory', 'summary', 'throughput_rps', 'background_update', 'all_targets_met')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
