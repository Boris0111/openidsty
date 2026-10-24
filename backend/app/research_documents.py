"""One safe authoring representation for structured forms and Markdown imports."""
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import yaml
from markdown_it import MarkdownIt
from .research_compile import compile_archive, digest
from .research_git import safe_path, SHA, make_archive

MAX_DRAFT = 5 * 1024 * 1024
MAX_ASSET = 10 * 1024 * 1024
SCHEMA = 'research-draft-v1'
MARKDOWN = MarkdownIt('commonmark')
MAX_YAML_DEPTH, MAX_YAML_EVENTS, MAX_YAML_NODES = 32, 400_000, 400_000
# libyaml replaces scanning/parsing only; duplicate-key rules stay in the Python constructor below.
# RESEARCH_YAML_PURE=1 exists for the loader-equivalence tests, never for the service.
YAML_BASE = (yaml.SafeLoader if os.environ.get('RESEARCH_YAML_PURE') == '1'
             else getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
if YAML_BASE is yaml.SafeLoader:
    logging.getLogger(__name__).warning('libyaml is unavailable; draft YAML uses the slower pure-Python parser.')


class UniqueLoader(YAML_BASE):
    def construct_mapping(self, node, deep=False):
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in keys:
                raise ValueError('YAML 欄位名稱必須為不重複的文字。')
            keys.add(key)
        return super().construct_mapping(node, deep=deep)


def safe_yaml(value):
    # Parser events bound the document before construction; calibrated on the 3,000-relation scaled
    # manifest (97,813 events, 47,380 expanded nodes). The 5 MiB draft cap bounds every document as well.
    depth, count = 0, 0
    for event in yaml.parse(value, Loader=YAML_BASE):
        count += 1
        if isinstance(event, (yaml.MappingStartEvent, yaml.SequenceStartEvent)):
            depth += 1
        elif isinstance(event, (yaml.MappingEndEvent, yaml.SequenceEndEvent)):
            depth -= 1
        if depth > MAX_YAML_DEPTH or count > MAX_YAML_EVENTS:
            raise ValueError('YAML 結構超過深度或數量限制。')
    loaded = yaml.load(value, Loader=UniqueLoader)
    pending, visits = [(loaded, 0, frozenset())], 0
    while pending:
        item, depth, ancestors = pending.pop()
        visits += 1
        if visits > MAX_YAML_NODES or depth > MAX_YAML_DEPTH:
            raise ValueError('YAML 展開後超過深度或數量限制。')
        if isinstance(item, (dict, list)):
            if id(item) in ancestors:
                raise ValueError('YAML 不接受遞迴 alias。')
            children = item.values() if isinstance(item, dict) else item
            inner = ancestors | {id(item)}
            pending.extend((child, depth + 1, inner) for child in children)
    return loaded


def check_document(path, content):
    safe_path(path)
    if not isinstance(content, str) or '\x00' in content or len(content.encode()) > MAX_DRAFT:
        raise ValueError('研究檔案須為有效且有大小限制的 UTF-8 文字。')
    prose = content
    if path.endswith('.yaml'):
        safe_yaml(content)
        return
    if content.startswith('---\n') or content.startswith('---\r\n'):
        sections = re.split(r'^---\s*$', content, maxsplit=2, flags=re.M)
        if len(sections) != 3:
            raise ValueError('Markdown frontmatter 未結束。')
        safe_yaml(sections[1])
        prose = sections[2]
    for block in MARKDOWN.parse(prose):
        for token in [block, *(block.children or [])]:
            if token.type in ('html_inline', 'html_block'):
                raise ValueError('研究 Markdown 不接受原始 HTML。')
            if token.type == 'image':
                raise ValueError('圖解請透過研究資產 manifest 引用。')
            if token.type == 'link_open':
                url = token.attrGet('href') or ''
                if not (url.startswith(('https://', 'http://', '#', '/next?focus='))):
                    raise ValueError('研究連結格式不安全。')
    # markdown-it omits unsafe links, so inspect these before they can be hidden.
    if re.search(r'(?:javascript|vbscript|data)\s*:', prose, re.I):
        raise ValueError('研究 Markdown 不接受可執行連結。')


def check_file(path, content):
    """check_document, with the rejected file named so a 2,000-file draft points at the culprit."""
    try:
        check_document(path, content)
    except (ValueError, yaml.YAMLError, RecursionError, UnicodeError) as error:
        raise ValueError(f'{path}：{error}') from None


def normalize_payload(payload, previous=None):
    """Check a whole draft. With `previous` (a stored revision, accepted when it was saved), files whose
    text is unchanged skip check_document; the draft-wide limits always run. Validation and publishing
    never pass `previous`, so they still check every file."""
    trusted = previous['files'] if previous is not None else {}
    if not isinstance(payload, dict) or set(payload) != {'schema_version', 'files', 'assets'} or payload['schema_version'] != SCHEMA:
        raise ValueError('草稿格式版本或欄位不正確。')
    files, assets = payload['files'], payload['assets']
    if not isinstance(files, dict) or not isinstance(assets, dict) or len(files) + len(assets) > 2000:
        raise ValueError('草稿檔案清單不正確或超額。')
    if len(json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()) > MAX_DRAFT:
        raise ValueError('草稿超過 5 MiB。')
    names = set()
    for path, content in files.items():
        safe_path(path)
        if path.casefold() in names or not isinstance(content, str):
            raise ValueError('草稿檔案重複或不是文字。')
        names.add(path.casefold())
        # The schema reference itself is immutable in editor payloads.
        if path != 'industry-map/README.md' and trusted.get(path) != content:
            check_file(path, content)
    for path, sha in assets.items():
        safe_path(path, asset=True)
        if path.casefold() in names or not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise ValueError('資產路徑重複或 hash 不正確。')
        names.add(path.casefold())
    return {'schema_version': SCHEMA, 'files': dict(sorted(files.items())), 'assets': dict(sorted(assets.items()))}


def normalize_changes(previous, payload):
    """normalize_payload for a save: only added or edited files are re-checked."""
    return normalize_payload(payload, previous=previous)


def export_files(files, asset_root):
    text, assets = {}, {}
    for path, content in files.items():
        if path.startswith('industry-map/assets/'):
            sha = hashlib.sha256(content).hexdigest()
            save_asset(asset_root, sha, content)
            assets[path] = sha
        else:
            text[path] = content.decode('utf-8')
    return normalize_payload({'schema_version': SCHEMA, 'files': text, 'assets': assets})


def save_asset(root, sha, content):
    root = Path(root)
    if not SHA.fullmatch(sha) or len(content) > MAX_ASSET or hashlib.sha256(content).hexdigest() != sha:
        raise ValueError('資產大小或 hash 不正確。')
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise ValueError('資產目錄不得使用 symlink。')
    root.mkdir(parents=True, exist_ok=True)
    target = root / sha
    if target.is_symlink():
        raise ValueError('資產不得使用 symlink。')
    if target.exists():
        if target.read_bytes() != content:
            raise ValueError('既有內容定址資產不可覆寫。')
    else:
        try:
            with target.open('xb') as output:
                output.write(content)
        except FileExistsError:
            if target.read_bytes() != content:
                raise ValueError('資產內容不一致。') from None


def upload_asset(root, path, media, content):
    """Reject active/external content before it can enter the content-addressed store."""
    import re
    import xml.etree.ElementTree as ET
    from .research_git import safe_path
    safe_path(path, asset=True, write=True)
    extensions = {'image/png': ('.png',), 'image/jpeg': ('.jpg', '.jpeg'),
                  'image/webp': ('.webp',), 'image/svg+xml': ('.svg',)}
    if media not in extensions or Path(path).suffix not in extensions[media] or not 0 < len(content) <= MAX_ASSET:
        raise ValueError('資產格式或大小不正確。')
    if media == 'image/svg+xml':
        if re.search(br'<!\s*(DOCTYPE|ENTITY)', content, re.I):
            raise ValueError('SVG 不允許 DTD 或 entity。')
        try:
            tree = ET.fromstring(content)
        except ET.ParseError:
            raise ValueError('SVG 格式不正確。') from None
        if tree.tag != '{http://www.w3.org/2000/svg}svg':
            raise ValueError('內容不是 SVG。')
        for node in tree.iter():
            if node.tag.rsplit('}', 1)[-1].lower() in ('script', 'foreignobject', 'style', 'animate', 'animatetransform', 'set'):
                raise ValueError('SVG 不允許主動內容。')
            for attr, value in node.attrib.items():
                name = attr.rsplit('}', 1)[-1].lower()
                if (name.startswith('on') or name == 'style' or
                    name in ('href', 'src') and not value.startswith('#') or
                    any(not url.strip(' \t\"\'').startswith('#') for url in re.findall(r'url\s*\((.*?)\)', value, re.I))):
                    raise ValueError('SVG 不允許外部引用或事件。')
    elif not {'image/png': content.startswith(b'\x89PNG\r\n\x1a\n'),
              'image/jpeg': content.startswith(b'\xff\xd8\xff'),
              'image/webp': content.startswith(b'RIFF') and content[8:12] == b'WEBP'}[media]:
        raise ValueError('資產 media-type 與內容不符。')
    sha = hashlib.sha256(content).hexdigest()
    save_asset(root, sha, content)
    return {'path': path, 'sha256': sha, 'media_type': media, 'size': len(content)}


STORE_SYMLINK, ASSET_MISSING, ASSET_MISMATCH = '資產目錄不得使用 symlink。', '草稿引用的研究資產尚未取得。', '研究資產 hash 不符。'
# Failures caused by the asset store rather than by draft content; a fixed store must be re-validated.
ASSET_STORE_ERRORS = {STORE_SYMLINK, ASSET_MISSING, ASSET_MISMATCH}


def materialize(payload, asset_root):
    result = {path: value.encode('utf-8') for path, value in payload['files'].items()}
    root = Path(asset_root)
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise ValueError(STORE_SYMLINK)
    for name, sha in payload['assets'].items():
        path = root / sha
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ASSET:
            raise ValueError(ASSET_MISSING)
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != sha:
            raise ValueError(ASSET_MISMATCH)
        result[name] = content
    return result


def validate_payload(payload, asset_root):
    try:
        normalized = normalize_payload(payload)
        files = materialize(normalized, asset_root)
        bundle = compile_archive(make_archive(files))
        manifest = {'industry-map/' + item['path'] for item in bundle['assets'].values()}
        if manifest != set(normalized['assets']):
            raise ValueError('草稿資產與 manifest 不一致。')
        return {'valid': True, 'errors': [], 'content_hash': digest(bundle)}, bundle
    except (ValueError, yaml.YAMLError, RecursionError, UnicodeError) as error:
        return {'valid': False, 'errors': [str(error)[:12000]], 'content_hash': None}, None


def form_document(frontmatter, markdown):
    if not isinstance(frontmatter, dict) or not isinstance(markdown, str):
        raise ValueError('表單須提供 frontmatter 與 Markdown 內文。')
    # JSON round-trip rejects Python-only objects in the shared form representation.
    frontmatter = json.loads(json.dumps(frontmatter, allow_nan=False))
    return '---\n' + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).rstrip() + '\n---\n\n' + markdown
