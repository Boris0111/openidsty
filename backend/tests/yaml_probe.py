"""Loader-equivalence probe: the same inputs, judged once with libyaml and once with RESEARCH_YAML_PURE=1.

python tests/yaml_probe.py <input.json> <output.json>      (run from backend/; the test drives both sides)
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT / 'scripts'))


def outcome(load, text):
    """A fingerprint of what the loader built, or 'rejected'; error messages are not compared."""
    try:
        return hashlib.sha256(repr(load(text)).encode()).hexdigest()
    except Exception:  # noqa: BLE001 - every rejection counts the same, whatever its class
        return 'rejected'


def documents(files):
    """YAML files and Markdown frontmatter, keyed by path; prose is not YAML."""
    found = {}
    for path, content in files.items():
        if path.endswith(('.yaml', '.yml')):
            found[path] = content
        elif path.endswith('.md') and content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) == 3:
                found[path] = parts[1]
    return found


def judge(spec):
    import validate_map
    from app.research_documents import UniqueLoader, safe_yaml, validate_payload
    result = {'loader': UniqueLoader.__mro__[1].__name__, 'validator_loader': validate_map.UniqueKeyLoader.__mro__[1].__name__,
              'documents': {}, 'validator_documents': {}, 'maps': {}}
    for name, text in {**spec.get('documents', {}), **spec.get('edge', {})}.items():
        result['documents'][name] = outcome(safe_yaml, text)
        result['validator_documents'][name] = outcome(validate_map.load_yaml, text)
    for map_dir in spec.get('maps', []):
        run = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/validate_map.py'), '--map-dir', map_dir],
                             capture_output=True)
        result['maps'][map_dir] = run.returncode
    if spec.get('payload') is not None:
        valid, _ = validate_payload(spec['payload'], spec['asset_root'])
        result['payload'] = {'valid': valid['valid'], 'content_hash': valid['content_hash']}
    return result


if __name__ == '__main__':
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    Path(sys.argv[2]).write_text(json.dumps(judge(spec)), encoding='utf-8')
