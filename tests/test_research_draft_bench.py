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

    def test_preview_entity_needs_a_diagram(self):
        block = '---\nentity-id: concept-a\ndiagram-assets:\n- asset-a\n---\n'
        flow = '---\nentity-id: concept-b\ndiagram-assets: [asset-b]\n---\n'
        empty = '---\nentity-id: concept-c\ndiagram-assets: []\n---\n'
        self.assertEqual(bench.preview_entity({'industry-map/concepts/a.md': block}), 'concept-a')
        self.assertEqual(bench.preview_entity({'industry-map/concepts/b.md': flow}), 'concept-b')
        self.assertEqual(bench.preview_entity({'industry-map/concepts/c.md': empty}), 'company-auras')


if __name__ == '__main__':
    unittest.main()
