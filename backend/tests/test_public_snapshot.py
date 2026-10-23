"""Offline contracts of the public snapshot: route table, private-field stripping, asset rewriting and leak scan."""
import json
from pathlib import Path
import pytest
from app.public_snapshot import (snapshot_route, public_segment, public_theme, public_assessment, public_technical_document, public_graph,
                                 rewrite_assets, asset_hashes, leak_findings, write_json)

CASES = json.loads((Path(__file__).resolve().parents[2] / 'frontend/tests/static/route-cases.json').read_text(encoding='utf-8'))
RELEASE = CASES['release']
SHA = 'a' * 64


@pytest.mark.parametrize('key,expected', CASES['cases'])
def test_route_table_matches_shared_cases(key, expected):
    # The browser adapter reads the same cases, so both sides agree on every snapshot path.
    assert snapshot_route(key, RELEASE) == (tuple(expected) if expected else None)


def test_segment_and_theme_drop_events_only():
    payload = {'segment': 'thermal', 'prose': '全文', 'events': [{'id': 1}], 'themes_detail': []}
    assert public_segment(payload) == {'segment': 'thermal', 'prose': '全文', 'themes_detail': []}
    assert public_theme({'theme': 'hbm4', 'events': [], 'segments_detail': []}) == {'theme': 'hbm4', 'segments_detail': []}


def test_assessment_keeps_judgment_without_candidates_or_runtime():
    payload = {'available': True, 'status': 'scaling', 'checked': '2026-10-01', 'assessment': {'summary': '判讀'},
               'evidence_sources': {'s1': {'id': 's1', 'name': '官方', 'url': 'https://x', 'reachability': 'verified',
                                           'checked': '2026-10-01', 'runtime': [{'id': 's1', 'status': 'failed', 'error': 'HTTP 403'}]}},
               'source_warnings': [{'source_id': 's1', 'kind': 'unverified', 'message': '原文件可讀性尚未確認'},
                                   {'source_id': 's1', 'runtime_source_id': 's1', 'kind': 'failed', 'message': 'HTTP 403'}],
               'candidates': [{'id': 1}], 'candidate_count': 3, 'unknown_date_count': 1, 'undated_candidates': [],
               'current_version_id': 7}
    result = public_assessment(payload)
    assert set(result) == {'available', 'status', 'checked', 'assessment', 'evidence_sources', 'source_warnings'}
    assert result['evidence_sources']['s1'] == {'id': 's1', 'name': '官方', 'url': 'https://x', 'reachability': 'verified', 'checked': '2026-10-01'}
    assert result['source_warnings'] == [{'source_id': 's1', 'kind': 'unverified', 'message': '原文件可讀性尚未確認'}]


def test_technical_document_keeps_definition_without_monitoring():
    payload = {'id': 'doc', 'active': True, 'definition': {'title': '規範', 'versions': []},
               'source': {'status': 'failed', 'error': 'HTTP 403'}, 'history': {'total': 2, 'items': []}}
    assert public_technical_document(payload) == {'id': 'doc', 'definition': {'title': '規範', 'versions': []}}


def test_assets_point_to_snapshot_copy_and_reject_other_releases():
    url = f'/api/v2/assets/{SHA}?release_id={RELEASE}'
    payload = {'assets': [{'url': url}], 'note': '圖解'}
    assert asset_hashes(payload) == {SHA}
    assert rewrite_assets(payload, RELEASE, {SHA: 'svg'}) == {'assets': [{'url': f'/snapshot/{RELEASE}/assets/{SHA}.svg'}], 'note': '圖解'}
    with pytest.raises(ValueError):
        rewrite_assets({'url': f'/api/v2/assets/{SHA}?release_id=11111111-1111-4111-8111-111111111111'}, RELEASE, {SHA: 'svg'})


def test_leak_scan_reports_private_fields_paths_and_secrets(tmp_path):
    write_json(tmp_path, 'v2/companies/a.json', {'data': {'name': '公司', 'note': 'token-0123456789'}})
    write_json(tmp_path, 'legacy/segments/b.json', {'segment': 'b', 'events': []})
    write_json(tmp_path, 'legacy/themes/c.json', {'link': '/api/events?theme=c'})
    (tmp_path / 'index.html').write_text('<p>token-0123456789</p>', encoding='utf-8')
    assert leak_findings(tmp_path, ['token-0123456789', 'short']) == [
        'index.html: secret value', 'legacy/segments/b.json: forbidden field events',
        'legacy/themes/c.json: private API path', 'v2/companies/a.json: secret value']


def test_graph_drops_private_catalog_link():
    payload = {'release_id': RELEASE, 'data': {'root': 'x', 'nodes': [], 'list_url': '/api/v2/catalog?release_id=' + RELEASE}}
    assert public_graph(payload) == {'release_id': RELEASE, 'data': {'root': 'x', 'nodes': []}}


def test_candidates_leak_only_in_assessments(tmp_path):
    # An ambiguous ticker lists company candidates; only an assessment's candidates are events.
    write_json(tmp_path, 'v2/resolve.json', {'keys': {'X': {'status': 409, 'body': {'candidates': [{'id': 'company-a'}]}}}})
    write_json(tmp_path, 'legacy/themes/t/assessment.json', {'candidates': []})
    assert leak_findings(tmp_path) == ['legacy/themes/t/assessment.json: forbidden field candidates']


def test_clean_snapshot_has_no_findings(tmp_path):
    write_json(tmp_path, 'v2/manifest.json', {'release_id': RELEASE, 'data': {'published_at': '2026-10-20'}})
    assert leak_findings(tmp_path, ['token-0123456789']) == []
