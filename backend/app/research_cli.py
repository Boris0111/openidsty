"""Interactive owner draft exchange; passwords and session cookies never enter files."""
import argparse
import getpass
import http.cookiejar
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from .research_documents import MAX_DRAFT, normalize_payload
from .research_git import safe_path


class Client:
    def __init__(self, base):
        parsed = urllib.parse.urlsplit(base)
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
            raise ValueError('請提供不含帳密、路徑或 query 的管理網站網址。')
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '[::1]', '::1')):
            raise ValueError('HTTP 僅允許本機；遠端管理必須使用 HTTPS。')
        self.base = base.rstrip('/')
        self.csrf = None
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect())

    def request(self, path, method='GET', data=None, revision=None, media=None, idempotency_key=None):
        headers = {'Origin': self.base, 'Accept': 'application/json'}
        if self.csrf:
            headers['X-CSRF-Token'] = self.csrf
        if revision is not None:
            headers['If-Match'] = '"' + str(revision) + '"'
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        content = data if media else json.dumps(data, ensure_ascii=False).encode() if data is not None else None
        if content is not None:
            headers['Content-Type'] = media or 'application/json'
            if len(content) > (10 * 1024 * 1024 if media else MAX_DRAFT):
                raise ValueError('資料超過大小限制。')
        request = urllib.request.Request(self.base + '/api/admin/' + path, data=content, method=method, headers=headers)
        try:
            with self.opener.open(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            try:
                message = json.loads(error.read(MAX_DRAFT)).get('message', '操作未完成。')
            except (ValueError, AttributeError):
                message = '操作未完成。'
            raise ValueError(str(error.code) + ': ' + message) from None

    def login(self):
        if not sys.stdin.isatty():
            raise ValueError('請在互動終端登入；密碼不可由參數、環境變數或管線傳入。')
        self.csrf = self.request('session')['csrf_token']
        password = getpass.getpass('維護者密碼：')
        try:
            self.csrf = self.request('session', 'POST', {'password': password})['csrf_token']
        finally:
            password = None

    def logout(self):
        self.request('session', 'DELETE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, *args, **kwargs):
        raise ValueError('管理 CLI 不跟隨重新導向，請核對網站網址。')


def exchange_path(root, name):
    safe_path(name)
    root = Path(root).absolute()
    target = root / name
    if any(path.is_symlink() for path in (target, *target.parents)) or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('交換資料夾不得使用 symlink 或越界路徑。')
    return target


def export_directory(data, directory):
    root = Path(directory).absolute()
    # A fresh directory prevents accidental replacement of a development checkout.
    if root.exists():
        raise ValueError('匯出資料夾必須尚未存在。')
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise ValueError('交換資料夾不得使用 symlink。')
    normalize_payload({key: data[key] for key in ('schema_version', 'files', 'assets')})
    root.mkdir(parents=True)
    for name, content in data['files'].items():
        target = exchange_path(root, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8', newline='')
    metadata = {key: value for key, value in data.items() if key != 'files'}
    (root / 'draft.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')


def import_directory(directory):
    root = Path(directory).absolute()
    metadata = root / 'draft.json'
    if any(path.is_symlink() for path in (metadata, *metadata.parents)) or metadata.stat().st_size > MAX_DRAFT:
        raise ValueError('交換中繼資料不正確。')
    data = json.loads(metadata.read_text(encoding='utf-8'))
    files, total = {}, metadata.stat().st_size
    for target in root.rglob('*'):
        if target.is_symlink():
            raise ValueError('交換資料夾不得使用 symlink。')
        if target.is_dir() or target == metadata:
            continue
        name = target.relative_to(root).as_posix()
        exchange_path(root, name)
        total += target.stat().st_size
        if total > MAX_DRAFT or len(files) >= 2000:
            raise ValueError('交換資料夾超過大小或檔案數限制。')
        # Preserve source bytes: universal-newline decoding creates fake revisions
        # for a CRLF checkout even when the owner changed nothing.
        files[name] = target.read_bytes().decode('utf-8')
    data['files'] = files
    normalize_payload({key: data[key] for key in ('schema_version', 'files', 'assets')})
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:3010')
    parser.add_argument('action', choices=['create', 'export', 'import', 'validate', 'preview', 'upload-asset', 'publish', 'status'])
    parser.add_argument('--draft')
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--entity')
    parser.add_argument('--file', type=Path)
    parser.add_argument('--asset-path')
    parser.add_argument('--media-type')
    parser.add_argument('--reason')
    parser.add_argument('--idempotency-key')
    parser.add_argument('--job')
    args = parser.parse_args()
    client = Client(args.base_url)
    if args.action not in ('create', 'upload-asset', 'status') and not args.draft:
        parser.error('--draft is required')
    key = str(uuid.UUID(args.draft)) if args.draft else None
    if args.action in ('export', 'import', 'publish') and args.directory is None:
        parser.error('--directory is required')
    if args.action == 'preview' and not args.entity:
        parser.error('--entity is required')
    if args.action == 'upload-asset' and not all((args.file, args.asset_path, args.media_type)):
        parser.error('--file, --asset-path and --media-type are required')
    if args.action == 'publish' and not all((args.reason, args.idempotency_key)):
        parser.error('--reason and --idempotency-key are required')
    if args.action == 'status' and not args.job:
        parser.error('--job is required')
    client.login()
    try:
        path = 'drafts/' + key if key else 'drafts'
        if args.action == 'status':
            print(json.dumps(client.request('jobs/' + str(uuid.UUID(args.job))), ensure_ascii=False, indent=2))
        elif args.action == 'publish':
            data = import_directory(args.directory)
            if data['draft_id'] != key:
                raise ValueError('檔案不屬於指定草稿。')
            result = client.request(path + '/publish', 'POST',
                {'base_release_id':data['base_release_id'], 'revision':data['revision'], 'reason':args.reason},
                idempotency_key=args.idempotency_key)
            print('發布作業 ' + result['job_id'] + '，狀態 ' + result['status'])
        elif args.action == 'upload-asset':
            safe_path(args.asset_path, asset=True, write=True)
            if args.file.is_symlink() or args.file.stat().st_size > 10 * 1024 * 1024:
                raise ValueError('資產不得使用 symlink 或超過 10 MiB。')
            result = client.request('drafts/asset-upload?path=' + urllib.parse.quote(args.asset_path),
                                    'POST', args.file.read_bytes(), media=args.media_type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.action == 'create':
            result = client.request(path, 'POST', {})
            print('草稿 ' + result['draft_id'] + '，修訂 ' + str(result['revision']))
        elif args.action == 'export':
            export_directory(client.request(path + '/export'), args.directory)
            print('已匯出研究檔案；資產以既有內容 hash 引用，匯出不包含密碼或 session。')
        elif args.action == 'import':
            data = import_directory(args.directory)
            result = client.request(path + '/import', 'POST', data, data['revision'])
            print('已匯入修訂 ' + str(result['revision']) + '；再次編輯前請匯出新修訂。')
        elif args.action == 'validate':
            result = client.request(path + '/validate', 'POST')
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if not result['valid']:
                raise SystemExit(1)
        else:
            result = client.request(path + '/preview?entity_id=' + urllib.parse.quote(args.entity))
            print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        client.logout()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
