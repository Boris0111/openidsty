"""libyaml must judge research exactly as the pure-Python loader did: same objects, verdicts and content hash."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from app.config import ROOT
from app.research_documents import export_files
from test_research_documents import authored  # noqa: F401 - shared module fixture
import yaml_probe

BACKEND = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/valid'
# Accept/reject only; error wording differs between the two parsers and is not part of the contract.
EDGE = {
    'duplicate-key': 'a: 1\na: 2\n',
    'non-text-key': '1: a\n',
    'merge-key': 'base: &b {x: 1}\nchild:\n  <<: *b\n  y: 2\n',
    'non-bmp': 'name: "😀𠀀"\nplain: 𠀀字\n',
    'bom': '\ufeffa: 1\n',
    'tab-indent': 'a:\n\tb: 1\n',
    'tab-in-value': 'a: "x\ty"\n',
    'implicit-types': 'd: 2026-10-24\nb: yes\no: 0o17\nf: 1_000.5\nn: ~\n',
    'recursive-alias': 'a: &x [*x]\n',
    'python-tag': 'a: !!python/object:os.system {}\n',
    'unterminated': 'a: "open\n',
}


def both(tmp_path, spec):
    source = tmp_path / 'probe-in.json'
    source.write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
    target = tmp_path / 'probe-out.json'
    env = {**os.environ, 'RESEARCH_YAML_PURE': '1', 'PYTHONIOENCODING': 'utf-8'}
    subprocess.run([sys.executable, '-X', 'utf8', str(BACKEND / 'tests/yaml_probe.py'), str(source), str(target)],
                   cwd=BACKEND, env=env, check=True)
    return yaml_probe.judge(spec), json.loads(target.read_text(encoding='utf-8'))


def assert_same(fast, pure):
    assert fast['loader'] == 'CSafeLoader' and fast['validator_loader'] == 'CSafeLoader'
    assert pure['loader'] == 'SafeLoader' and pure['validator_loader'] == 'SafeLoader'
    for key in ('documents', 'validator_documents', 'maps', 'payload'):
        assert fast.get(key) == pure.get(key), key


def test_published_research_fixture_and_edge_cases_match(authored, tmp_path):  # noqa: F811
    payload, assets = authored
    fixture = {path.relative_to(FIXTURE).as_posix(): path.read_text(encoding='utf-8')
               for path in FIXTURE.rglob('*') if path.is_file() and path.suffix in ('.md', '.yaml')}
    spec = {'documents': {**yaml_probe.documents(payload['files']),
                          **{'fixture/' + name: text for name, text in yaml_probe.documents(fixture).items()}},
            'edge': EDGE, 'maps': [str(FIXTURE)], 'payload': payload, 'asset_root': str(assets)}
    fast, pure = both(tmp_path, spec)
    assert_same(fast, pure)
    assert fast['payload']['valid'] and fast['maps'][str(FIXTURE)] == 0
    for name in ('duplicate-key', 'non-text-key', 'tab-indent', 'recursive-alias', 'python-tag', 'unterminated'):
        assert fast['documents'][name] == 'rejected', name
    # Drafts already rejected merge keys before libyaml (keys are built before flattening); the map
    # validator flattens first and accepts them. Both behaviours are unchanged by the parser swap.
    assert fast['documents']['merge-key'] == 'rejected' and fast['validator_documents']['merge-key'] != 'rejected'


@pytest.mark.slow
def test_scaled_dataset_matches(scaled_tree, tmp_path):
    files = {path.relative_to(scaled_tree).as_posix(): path.read_bytes() for path in scaled_tree.rglob('*') if path.is_file()}
    assets = tmp_path / 'assets'
    payload = export_files(files, assets)
    spec = {'documents': yaml_probe.documents(payload['files']), 'maps': [str(scaled_tree / 'industry-map')],
            'payload': payload, 'asset_root': str(assets)}
    fast, pure = both(tmp_path, spec)
    assert_same(fast, pure)
    assert fast['payload']['valid'] and len(fast['documents']) > 400
