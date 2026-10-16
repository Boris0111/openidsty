"""Read-only HTTP benchmark; production proxy, fixed endpoint mix, no fixtures.

python scripts/reading_load.py --origin http://127.0.0.1:3013 --output .work/reading/baseline.json
"""
import argparse
import concurrent.futures
import json
import math
import platform
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def get(origin, path, category=None):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(origin + path, timeout=30) as response:
            raw = response.read()
            value = json.loads(raw)
            if not isinstance(value, (list, dict)):
                raise ValueError('Unexpected JSON response')
            if category:
                valid={
                    'graph':lambda:isinstance(value.get('nodes'),list) and isinstance(value.get('edges'),list) and bool(value['nodes']),
                    'segment':lambda:value.get('segment')==path.rsplit('/',1)[-1] and isinstance(value.get('prose'),str),
                    'theme':lambda:value.get('theme')==path.rsplit('/',1)[-1] and isinstance(value.get('prose'),str),
                    'assessment':lambda:isinstance(value.get('available'),bool) and isinstance(value.get('candidate_count'),int),
                    'indicators':lambda:isinstance(value.get('indicators'),list),
                    'updates':lambda:isinstance(value.get('items'),list) and len(value['items'])==len(urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)['ids'][0].split(',')),
                    'coverage':lambda:isinstance(value.get('rows'),list) and bool(value.get('as_of')),
                    'documents':lambda:isinstance(value.get('items'),list) and isinstance(value.get('total'),int),
                    'document-detail':lambda:isinstance(value.get('definition'),dict) and isinstance(value.get('history'),dict) and isinstance(value['history'].get('total'),int),
                }[category]
                if not isinstance(value,dict) or not valid():raise ValueError(f'Unexpected {category} content')
            return value, {'ms': (time.perf_counter()-start)*1000, 'bytes': len(raw), 'status': response.status, 'error': None}
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        return None, {'ms': (time.perf_counter()-start)*1000, 'bytes': 0, 'status': getattr(exc, 'code', None), 'error': str(exc)}


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)] if values else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--warmup', type=int, default=60)
    parser.add_argument('--seconds', type=int, default=300)
    parser.add_argument('--readers', type=int, default=10)
    parser.add_argument('--documents', action='store_true', help='Benchmark new document resources separately')
    args = parser.parse_args()
    segments, first = get(args.origin, '/api/segments')
    themes, second = get(args.origin, '/api/themes')
    if first['error'] or second['error']:
        raise SystemExit(f'Cannot discover actual resources: {first} {second}')
    theme_ids = [t['theme'] for t in themes]
    workload = [
        ('graph', '/api/industries/ai-server/graph'),
        ('graph', '/api/industries/semiconductor/graph'),
        *[('segment', '/api/segments/'+s['id']) for s in segments],
        *[(category, '/api/themes/'+tid+suffix) for tid in theme_ids for category, suffix in
          [('theme', ''), ('assessment', '/assessment'), ('indicators', '/indicators')]],
        ('updates', '/api/theme-updates?'+urllib.parse.urlencode({'ids': ','.join(theme_ids)})),
        ('coverage', '/api/coverage'),
    ]
    if args.documents:
        documents,discovery=get(args.origin,'/api/technical-documents?limit=50&offset=0','documents')
        if discovery['error']:raise SystemExit(discovery['error'])
        workload = [('documents', '/api/technical-documents?limit=20&offset=0'),*[('document-detail','/api/technical-documents/'+d['id']+'?limit=10&offset=0') for d in documents['items']]]
    cold = []
    for category, path in workload:
        _, result = get(args.origin, path, category)
        cold.append(dict(category=category, path=path, **result))
    samples, lock = [], threading.Lock()
    sample_counts = {category:0 for category,_ in workload}

    def phase(seconds, record):
        deadline = time.perf_counter()+seconds
        def reader(reader_id):
            index = reader_id * len(workload)//args.readers
            while time.perf_counter() < deadline or (record and any(n<100 for n in sample_counts.values())):
                category, path = workload[index % len(workload)]
                _, result = get(args.origin, path, category)
                if record:
                    with lock:
                        samples.append(dict(category=category, path=path, **result))
                        sample_counts[category] += 1
                index += 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.readers) as pool:
            list(pool.map(reader, range(args.readers)))

    print(f'Discovered {len(segments)} segments / {len(themes)} themes; warmup {args.warmup}s', flush=True)
    phase(args.warmup, False)
    print(f'Measuring {args.readers} readers for {args.seconds}s', flush=True)
    started = time.perf_counter()
    phase(args.seconds, True)
    elapsed = time.perf_counter()-started
    grouped = defaultdict(list)
    for row in samples:
        grouped[row['category']].append(row)
    summary = {}
    for category, rows in grouped.items():
        latencies = [row['ms'] for row in rows]
        target = 1000 if category == 'coverage' else 500
        summary[category] = dict(samples=len(rows), errors=sum(bool(row['error']) for row in rows),
            p50_ms=percentile(latencies, .5), p95_ms=percentile(latencies, .95), p99_ms=percentile(latencies, .99),
            throughput=len(rows)/elapsed, mean_bytes=sum(row['bytes'] for row in rows)/len(rows), target_ms=target,
            passed=len(rows)>=100 and not any(row['error'] for row in rows) and percentile(latencies, .95)<target)
    result = dict(as_of=datetime.now(timezone.utc).isoformat(), origin=args.origin, host=platform.platform(),
        readers=args.readers, warmup_seconds=args.warmup, measured_seconds=elapsed, requested_seconds=args.seconds,
        acceptance_run=args.readers==10 and args.warmup>=60 and args.seconds>=300,
        segment_ids=[s['id'] for s in segments], theme_ids=theme_ids, workload=workload, cold=cold,
        summary=summary, samples=samples, new_document_baseline='N/A' if not args.documents else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k in ('summary','acceptance_run','measured_seconds')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
