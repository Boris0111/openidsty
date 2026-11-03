"""The draft benchmark's statistics and report fields; the drill itself is exercised by the live run."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_draft_bench as bench


class PercentileTests(unittest.TestCase):
    def test_nearest_rank(self):
        values = list(range(1, 101))
        self.assertEqual(bench.percentile(values, 50), 50)
        self.assertEqual(bench.percentile(values, 95), 95)
        self.assertEqual(bench.percentile(values, 100), 100)
        self.assertEqual(bench.percentile([7], 95), 7)
        self.assertIsNone(bench.percentile([], 95))

    def test_unsorted_input(self):
        self.assertEqual(bench.percentile([30, 10, 20], 50), 20)


class SummaryTests(unittest.TestCase):
    def test_fields_statuses_and_error_codes(self):
        samples = [{'status': 200, 'ms': 10.0}, {'status': 200, 'ms': 30.0},
                   {'status': 422, 'ms': 5.0, 'code': 'draft-rejected'}, {'status': 409, 'ms': 4.0, 'code': 'draft-conflict'}]
        summary = bench.summarize(samples)
        self.assertEqual(set(summary), {'count', 'p50_ms', 'p95_ms', 'max_ms', 'statuses', 'error_codes'})
        self.assertEqual(summary['count'], 4)
        self.assertEqual(summary['max_ms'], 30.0)
        self.assertEqual(summary['statuses'], {'200': 2, '422': 1, '409': 1})
        self.assertEqual(summary['error_codes'], ['draft-conflict', 'draft-rejected'])

    def test_empty_sample(self):
        summary = bench.summarize([])
        self.assertEqual(summary['count'], 0)
        self.assertIsNone(summary['p95_ms'])
        self.assertIsNone(summary['max_ms'])


class ParsingTests(unittest.TestCase):
    def test_docker_memory_units(self):
        self.assertEqual(bench.memory_mib('104.2MiB / 7.46GiB'), 104.2)
        self.assertEqual(bench.memory_mib('1.5GiB / 7.46GiB'), 1536.0)
        self.assertEqual(bench.memory_mib('512KiB / 7.46GiB'), 0.5)
        self.assertIsNone(bench.memory_mib('--'))

    def test_preview_timing_lines_for_one_draft(self):
        log = ('INFO:     draft-validation computed draft=d1 revision=2\n'
               'INFO:     draft-preview timing draft=d1 revision=2 project_ms=812.5 flush_ms=640 detail_ms=40 graph_ms=9.5\n'
               'INFO:     draft-preview timing draft=other revision=7 project_ms=1 flush_ms=1 detail_ms=1 graph_ms=1\n'
               'INFO:     127.0.0.1 - "GET /api/admin/drafts/d1/preview HTTP/1.1" 200\n'
               'INFO:     draft-preview timing draft=d1 revision=2 project_ms=900 flush_ms=700 detail_ms=60 graph_ms=10.5\n')
        rows = bench.preview_timings(log, 'd1')
        self.assertEqual(rows, [{'project_ms': 812.5, 'flush_ms': 640.0, 'detail_ms': 40.0, 'graph_ms': 9.5},
                                {'project_ms': 900.0, 'flush_ms': 700.0, 'detail_ms': 60.0, 'graph_ms': 10.5}])
        self.assertEqual(bench.timing_medians(rows), {'project_ms': 856.2, 'flush_ms': 670.0, 'detail_ms': 50.0, 'graph_ms': 10.0})
        self.assertEqual(bench.timing_medians(rows[:1]), rows[0])

    def test_builds_without_the_timing_log_report_null(self):
        log = 'INFO:     draft-validation computed draft=d1 revision=2\n'
        self.assertEqual(bench.preview_timings(log, 'd1'), [])
        self.assertIsNone(bench.timing_medians([]))
        self.assertEqual(bench.preview_timings(None, 'd1'), [])


class PreviewTests(unittest.TestCase):
    def test_previews_rotate_through_fixed_pages(self):
        real = bench.preview_pages('real', 20)
        self.assertEqual(len(real), 20)
        self.assertEqual(real[:len(bench.PREVIEW_PAGES)], bench.PREVIEW_PAGES)
        self.assertEqual(set(real), set(bench.PREVIEW_PAGES))
        self.assertIn('concept-hbm-stack', real)  # the page with diagrams
        scaled = bench.preview_pages('scaled', 20)
        self.assertTrue(set(bench.SCALED_PAGES) <= set(scaled))
        self.assertFalse(set(bench.SCALED_PAGES) & set(real))

    def test_measure_reports_draft_id_preview_statistics_and_timing(self):
        calls = []

        class Owner:
            def call(self, method, path, data=None, headers=None):
                calls.append((method, path))
                if method == 'POST' and path == '/api/admin/drafts':
                    return 201, {'draft_id': 'draft-1', 'revision': 1}
                if path.endswith('/export'):
                    return 200, {'files': {'a.md': 'x'}, 'assets': {}}
                if '/document?' in path:
                    return 200, {'frontmatter': {'summary': 's'}, 'markdown': 'm'}
                if method == 'PATCH':
                    return 200, {'revision': len(calls)}
                if '/validate' in path:
                    return 200, {'valid': True}
                if '/preview' in path:
                    assets = [{'url': '/api/admin/drafts/draft-1/assets/abc'}] if 'concept-hbm-stack' in path else []
                    return 200, {'data': {'assets': assets}}
                return 200, {}

        log = 'INFO: draft-preview timing draft=draft-1 revision=3 project_ms=10 flush_ms=5 detail_ms=2 graph_ms=1\n'
        original = bench.api_log_since
        bench.api_log_since = lambda started: log
        try:
            report = bench.measure(Owner(), 'real', saves=2, previews=4)
        finally:
            bench.api_log_since = original
        self.assertEqual(report['draft_id'], 'draft-1')
        preview = report['steps']['preview']
        self.assertEqual(preview['count'], 4)
        self.assertEqual(preview['pages'], bench.PREVIEW_PAGES[:4])
        self.assertTrue({'p50_ms', 'p95_ms', 'max_ms'} <= set(preview))
        self.assertEqual(report['steps']['preview_assets']['count'], 1)  # diagrams are counted apart from previews
        self.assertEqual(report['preview_timing'], {'lines': 1, 'medians_ms': {'project_ms': 10.0, 'flush_ms': 5.0, 'detail_ms': 2.0, 'graph_ms': 1.0}})
        self.assertEqual(sum(1 for method, path in calls if '/preview' in path), 4)


class EnvFileTests(unittest.TestCase):
    def test_reads_only_the_drill_owner_password(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env.research-drill'
            path.write_text('RESEARCH_SESSION_SECRET=x\nDRILL_OWNER_PASSWORD=a=b\n', encoding='utf-8')
            self.assertEqual(bench.drill_password(path), 'a=b')
            path.write_text('RESEARCH_SESSION_SECRET=x\n', encoding='utf-8')
            with self.assertRaises(SystemExit) as missing:
                bench.drill_password(path)
            self.assertNotIn('x', str(missing.exception).replace('DRILL', '').replace('research', '').replace('first', ''))


if __name__ == '__main__':
    unittest.main()
