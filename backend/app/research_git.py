"""Isolated managed Git storage. HTTP input never selects a repository or command."""
import argparse
from contextlib import contextmanager
import io
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import uuid

TEXT_DIRS = {'ai-server', 'semiconductor', 'themes', 'companies', 'applications',
             'roles', 'products', 'concepts', 'research'}
YAML_FILES = {'sources.yaml', 'technical-documents.yaml', 'research-relations.yaml', 'research-assets.yaml'}
DATA_FILES = {'data/company-research.yaml', 'data/theme-indicators.yaml'}
COMMIT = re.compile(r'^[0-9a-f]{40,64}$')
SHA = re.compile(r'^[0-9a-f]{64}$')


class MissingResearchFile(ValueError):
    """The commit is valid but does not contain the requested research file."""


def safe_path(value, *, asset=False, write=False):
    if not isinstance(value, str) or len(value) > 240 or '\\' in value or ':' in value:
        raise ValueError('研究路徑格式不正確。')
    parts = PurePosixPath(value).parts
    if not parts or value != '/'.join(parts) or any(part in ('.', '..') or part.startswith('.') for part in parts):
        raise ValueError('研究路徑不得越界或使用隱藏檔案。')
    if asset:
        valid = (len(parts) >= 3 and parts[:2] == ('industry-map', 'assets')
                 and PurePosixPath(value).suffix in ('.png', '.jpg', '.jpeg', '.webp', '.svg')
                 and all(re.fullmatch('[a-z0-9][a-z0-9._-]*', part) for part in parts[2:]))
    else:
        valid = (value in DATA_FILES or value == 'industry-map/README.md' and not write
            or len(parts) == 2 and parts[0] == 'industry-map' and parts[1] in YAML_FILES
            or len(parts) == 3 and parts[0] == 'industry-map' and parts[1] in TEXT_DIRS
               and re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*[.]md', parts[2]))
    if not valid:
        raise ValueError('此路徑不在允許的研究範圍。')
    return value


def research_path(value):
    return safe_path(value, asset=value.startswith('industry-map/assets/'))


def read_archive(data):
    if len(data) > 100 * 1024 * 1024:
        raise ValueError('研究 archive 超過大小限制。')
    result, names, total = {}, set(), 0
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        for member in archive:
            if member.isdir():
                continue
            research_path(member.name)
            key = member.name.casefold()
            if not member.isfile() or member.mode & 0o111 or key in names:
                raise ValueError('研究內容不得包含 symlink、可執行檔或重複路徑。')
            total += member.size
            if member.size > 10 * 1024 * 1024 or total > 100 * 1024 * 1024 or len(names) >= 2000:
                raise ValueError('研究內容超過大小或檔案數限制。')
            result[member.name] = archive.extractfile(member).read()
            names.add(key)
    return result


def make_archive(files):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for name, content in sorted(files.items()):
            research_path(name)
            item = tarfile.TarInfo(name)
            item.mode, item.size = 0o644, len(content)
            archive.addfile(item, io.BytesIO(content))
    return stream.getvalue()


class ManagedGit:
    def __init__(self, root=None):
        self.root = Path(root or os.getenv('RESEARCH_GIT_ROOT', '/home/app/research-git')).absolute()
        if any(item.is_symlink() for item in (self.root, *self.root.parents)):
            raise ValueError('Managed Git root 不得使用 symlink。')
        self.repo = self.root / 'repository.git'

    def command(self, *args, directory=None, check=True):
        env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0',
                   GIT_ALLOW_PROTOCOL='file', GIT_NO_REPLACE_OBJECTS='1')
        command = ['git', '-c', 'core.hooksPath=' + os.devnull, '-c', 'core.autocrlf=false',
                   '-c', 'core.quotePath=false', '-C', str(directory or self.repo), *args]
        result = subprocess.run(command, env=env, capture_output=True, timeout=90)
        if result.returncode and check:
            raise ValueError('Managed Git 操作失敗：' + args[0])
        return result.stdout

    def verify(self, commit):
        if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
            raise ValueError('必須指定完整內容 commit。')
        if not self.repo.is_dir() or self.repo.is_symlink():
            raise ValueError('請先由本機初始化 managed Git。')
        found = self.command('rev-parse', '--verify', commit + '^{commit}').decode().strip()
        if found != commit:
            raise ValueError('內容 commit 不正確。')
        return commit

    def files(self, commit):
        self.verify(commit)
        data = self.command('archive', '--format=tar', commit, 'industry-map', *sorted(DATA_FILES))
        return read_archive(data)

    def file(self, commit, path):
        """One research file at an immutable commit, without archiving the whole tree."""
        self.verify(commit)
        research_path(path)
        if self.command('cat-file', '-t', commit + ':' + path, check=False).strip() != b'blob':
            raise MissingResearchFile('基準版本沒有這份研究檔案。')
        content = self.command('cat-file', 'blob', commit + ':' + path)
        if len(content) > 10 * 1024 * 1024:  # Same per-file bound as read_archive.
            raise ValueError('研究內容超過大小或檔案數限制。')
        return content

    def seed(self, bundle, commit):
        if not COMMIT.fullmatch(commit) or len(bundle) > 100 * 1024 * 1024:
            raise ValueError('初始化 bundle 或 commit 不正確。')
        self.root.mkdir(parents=True, exist_ok=True)
        if self.repo.exists():
            self.verify(commit)
            return  # Never overwrite an existing repository or refs.
        with tempfile.TemporaryDirectory(prefix='seed-', dir=self.root) as temporary:
            incoming = Path(temporary) / 'research.bundle'
            incoming.write_bytes(bundle)
            clone = Path(temporary) / 'candidate.git'
            self.command('clone', '--bare', str(incoming), str(clone), directory=self.root)
            self.command('rev-parse', '--verify', commit + '^{commit}', directory=clone)
            clone.rename(self.repo)
        self.files(commit)  # Verify research paths and file modes before use.

    def protect_release(self, release_id, commit):
        release = str(uuid.UUID(str(release_id)))
        self.verify(commit)
        ref = 'refs/research/releases/' + release
        existing = subprocess.run(['git', '-C', str(self.repo), 'rev-parse', '--verify', ref], capture_output=True)
        if existing.returncode == 0 and existing.stdout.decode().strip() != commit:
            raise ValueError('Release ref 不可改寫為其他 commit。')
        self.command('update-ref', ref, commit, commit if existing.returncode == 0 else '0' * len(commit))

    @contextmanager
    def worktree(self, base):
        self.verify(base)
        folder = self.root / 'worktrees' / uuid.uuid4().hex
        folder.parent.mkdir(parents=True, exist_ok=True)
        if folder.parent.is_symlink() or folder.parent.resolve() != self.root.resolve() / 'worktrees':
            raise ValueError('Managed worktree 路徑越界。')
        self.command('worktree', 'add', '--detach', str(folder), base)
        try:
            yield folder
        finally:
            if folder.is_symlink() or not folder.resolve().is_relative_to((self.root / 'worktrees').resolve()):
                raise ValueError('拒絕移除越界 worktree。')
            self.command('worktree', 'remove', '--force', str(folder))

    def commit_files(self, base, files, protect_ref=None):
        from .research_compile import compile_archive
        bundle = compile_archive(make_archive(files))
        expected_assets = {'industry-map/' + asset['path'] for asset in bundle['assets'].values()}
        if {name for name in files if name.startswith('industry-map/assets/')} != expected_assets:
            raise ValueError('所有研究資產皆須登錄於 manifest。')
        baseline = self.files(base)
        names = set(baseline) | set(files)
        for name in names:
            if baseline.get(name) != files.get(name):
                safe_path(name, asset=name.startswith('industry-map/assets/'), write=True)
        # All research changes are written in a disposable managed worktree.
        with self.worktree(base) as folder:
            for name in names:
                if baseline.get(name) == files.get(name):
                    continue
                target = folder / PurePosixPath(name)
                if any(path.is_symlink() for path in (target, *target.parents)):
                    raise ValueError('研究檔案不得使用 symlink。')
                if name not in files:
                    target.unlink(missing_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(files[name])
            self.command('add', '--', 'industry-map', *sorted(DATA_FILES), directory=folder)
            changed = self.command('diff', '--cached', '--name-only', '-z', directory=folder)
            for name in filter(None, changed.decode().split('\0')):
                safe_path(name, asset=name.startswith('industry-map/assets/'), write=True)
            if not changed:
                if protect_ref:
                    self.command('update-ref', protect_ref, base)
                return base
            self.command('-c', 'user.name=IndustryFlow owner', '-c', 'user.email=owner@localhost',
                         'commit', '--no-gpg-sign', '-m', 'Update validated research content', directory=folder)
            commit = self.command('rev-parse', 'HEAD', directory=folder).decode().strip()
            if protect_ref:
                self.command('update-ref', protect_ref, commit)
            return commit

    def prepare_job(self, job_id, base, files):
        ref = 'refs/research/jobs/' + str(uuid.UUID(str(job_id)))
        try:
            existing = self.command('rev-parse', '--verify', ref).decode().strip()
        except ValueError:
            existing = None
        if existing:
            if self.files(existing) != files:
                raise ValueError('發布作業既有 commit 與草稿不一致。')
            return existing
        return self.commit_files(base, files, protect_ref=ref)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['seed'])
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    managed = ManagedGit()
    managed.seed(sys.stdin.buffer.read(100 * 1024 * 1024 + 1), args.commit)
    from sqlalchemy import text
    from .research_db import writer_engine
    with writer_engine().connect() as connection:
        for release in connection.execute(text("SELECT release_id,git_commit FROM research.research_releases WHERE status='published'")):
            managed.protect_release(release.release_id, release.git_commit)
    print('Managed research Git initialized; development index unchanged')


if __name__ == '__main__':
    main()
