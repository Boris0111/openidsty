"""Shared, bounded results for immutable draft inputs: one computation per key, even under concurrency."""
import threading
import time
import pytest
import app.research_drafts as drafts
from app.research_documents import ASSET_MISSING, export_files
from app.research_git import ManagedGit
from app.research_http import ResearchError
from test_research_documents import tiny_git, COMPANY  # noqa: F401 - shared fixture


@pytest.fixture(autouse=True)
def empty_caches():
    drafts.BASE_EXPORTS.clear(); drafts.VALIDATIONS.clear()
    yield
    drafts.BASE_EXPORTS.clear(); drafts.VALIDATIONS.clear()


def counter(value='result', delay=0.0, error=None):
    calls = []
    def compute():
        calls.append(1)
        time.sleep(delay)
        if error:
            raise error
        return value
    return calls, compute


def test_same_key_computes_once():
    cache, (calls, compute) = drafts.SharedResults(2), counter()
    assert cache.get('a', compute) == cache.get('a', compute) == 'result' and len(calls) == 1


def test_concurrent_misses_share_one_computation():
    cache, (calls, compute) = drafts.SharedResults(2), counter(value=object(), delay=0.3)
    results, start = [], threading.Barrier(8)
    def worker():
        start.wait()
        results.append(cache.get('a', compute))
    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    assert len(calls) == 1 and len(results) == 8 and len({id(result) for result in results}) == 1


def test_failure_reaches_every_waiter_and_is_not_kept():
    cache, (calls, compute) = drafts.SharedResults(2), counter(delay=0.3, error=RuntimeError('boom'))
    errors, start = [], threading.Barrier(4)
    def worker():
        start.wait()
        try:
            cache.get('a', compute)
        except RuntimeError as error:
            errors.append(error)
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    assert len(calls) == 1 and len(errors) == 4
    _, recovered = counter('fixed')
    assert cache.get('a', recovered) == 'fixed'  # The failure was not cached.


def test_waiter_times_out_with_retryable_503():
    cache, (_, slow) = drafts.SharedResults(2, wait=0.1), counter(delay=0.6)
    owner = threading.Thread(target=cache.get, args=('a', slow))
    owner.start(); time.sleep(0.05)
    with pytest.raises(ResearchError) as busy:
        cache.get('a', slow)
    owner.join()
    assert busy.value.status == 503 and busy.value.retryable


def test_rejected_results_are_not_kept_and_lru_evicts_oldest():
    cache = drafts.SharedResults(2)
    calls, compute = counter('skip')
    cache.get('a', compute, keep=lambda value: False); cache.get('a', compute, keep=lambda value: False)
    assert len(calls) == 2
    for key in ('x', 'y'):
        cache.get(key, lambda key=key: key)
    cache.get('x', lambda: pytest.fail('x is still cached'))  # x becomes most recent
    cache.get('z', lambda: 'z')                               # evicts y
    assert list(cache.values) == ['x', 'z']


def test_base_export_archives_each_commit_once(tiny_git, monkeypatch, tmp_path):  # noqa: F811
    managed, head, _ = tiny_git
    monkeypatch.setenv('RESEARCH_GIT_ROOT', str(managed.root))
    monkeypatch.setenv('RESEARCH_ASSET_ROOT', str(tmp_path / 'assets'))
    expected = export_files(managed.files(head), tmp_path / 'assets')
    calls, original = [], ManagedGit.files
    monkeypatch.setattr(ManagedGit, 'files', lambda self, commit: (calls.append(commit), original(self, commit))[1])
    assert drafts.base_export(head) == drafts.base_export(head) == expected and calls == [head]


def test_validation_is_shared_per_content_hash_but_asset_store_errors_retry(monkeypatch):
    calls = []
    def fake(payload, root):
        calls.append(payload['marker'])
        if payload['marker'] == 'missing-asset':
            return {'valid': False, 'errors': [ASSET_MISSING], 'content_hash': None}, None
        return {'valid': payload['marker'] == 'ok', 'errors': [] if payload['marker'] == 'ok' else ['內容錯誤'], 'content_hash': 'h'}, {}
    monkeypatch.setattr(drafts, 'validate_payload', fake)
    revision = lambda marker, digest: {'draft_id': 'd', 'revision': 1, 'payload_hash': digest, 'payload': {'marker': marker}}
    for marker, digest in [('ok', 'h1'), ('ok', 'h1'), ('bad', 'h2'), ('bad', 'h2'), ('missing-asset', 'h3'), ('missing-asset', 'h3')]:
        drafts.validated(revision(marker, digest))
    assert calls == ['ok', 'bad', 'missing-asset', 'missing-asset']
