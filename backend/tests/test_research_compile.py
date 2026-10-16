import io
from pathlib import Path
import subprocess
import tarfile
import pytest
from app.config import ROOT
from app.research_compile import compile_archive, digest, normalize


def archive_item(name, content=b'x', symlink=False):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        info = tarfile.TarInfo(name)
        if symlink:
            info.type, info.linkname = tarfile.SYMTYPE, '/etc/passwd'
        else:
            info.size = len(content)
        archive.addfile(info, None if symlink else io.BytesIO(content))
    return stream.getvalue()


@pytest.mark.parametrize('path,link', [('../secret', False), ('backend/app/main.py', False),
                                      ('industry-map/companies/company-test.md', True)])
def test_archive_rejects_nonresearch_paths_and_links(path, link):
    with pytest.raises(ValueError, match='Unsafe archive path|Non-research path|links/duplicates'):
        compile_archive(archive_item(path, symlink=link))


def test_same_git_commit_rebuild_retains_content_dates_and_evidence():
    if not (ROOT / '.git').exists():
        pytest.skip('Git archive reconstruction is verified through research_lab in containers')
    archive = subprocess.check_output(['git', 'archive', '--format=tar', 'HEAD', 'industry-map',
        'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
    first, second = compile_archive(archive), compile_archive(archive)
    assert first == second and digest(first) == digest(second)
    counts = {kind: sum(s['kind'] == kind for s in first['snapshots']) for kind in ('company', 'segment', 'theme')}
    assert counts == {'company': 95, 'segment': 17, 'theme': 7}
    themes = [s for s in first['snapshots'] if s['kind'] == 'theme']
    assert all(t['reviewed'] == '2026-10-07' for t in themes)
    assert all(t['data']['assessment']['evidence'] for t in themes)
    assert all('https://' in t['markdown'] for t in themes)
    assert len(first['documents']) == 8
    assert sum(c['review_status'] == 'candidate' for c in first['legacy_relations']) == 1
    assert len(first['indicator_definitions']['indicators']) == 9


def test_alias_normalization_preserves_entity_identity():
    assert normalize('臺積電') == normalize('台積電')
    assert normalize('  ＮＶＩＤＩＡ  ') == 'nvidia'
    assert normalize('AMD') != normalize('AMDOCS')
