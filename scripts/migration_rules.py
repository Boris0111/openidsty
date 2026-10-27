"""Classify Alembic migrations as expand or contract, for the working tree or any Git commit.

A migration whose upgrade() drops, renames, narrows or deletes must declare at module level either
CONTRACT = '<why the previous version breaks>' or EXPAND_REVIEWED = '<why the previous version is unaffected>'.
The chain must stay linear with one head, and each 4-digit revision must equal its file name prefix.

python scripts/migration_rules.py                 # lint the working tree; exit 1 with findings
python scripts/migration_rules.py --commit <sha>  # chain, head and contract revisions of one commit
"""
import argparse
import ast
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = 'backend/migrations'
FILE_NAME = re.compile(r'(\d{4})_[a-z0-9_]+\.py')
SQL_FILE = re.compile(r'sql/[A-Za-z0-9_.-]+\.sql')
# Word boundaries keep identifiers such as revoked_at or dropped_count out.
SQL_RULES = (
    re.compile(r'\bDROP\s+(?:TABLE|(?:MATERIALIZED\s+)?VIEW|COLUMN|FUNCTION|TYPE|SCHEMA|POLICY|TRIGGER|CONSTRAINT|SEQUENCE)\b', re.I),
    re.compile(r'\bRENAME\b', re.I),
    re.compile(r'\bALTER\s+(?:COLUMN\s+)?"?\w+"?\s+(?:SET\s+DATA\s+)?TYPE\b', re.I),
    re.compile(r'\bSET\s+NOT\s+NULL\b', re.I),
    re.compile(r'\bTRUNCATE\b', re.I),
    re.compile(r'\bDELETE\s+FROM\b', re.I),
    re.compile(r'\bREVOKE\b', re.I),
)
ADD_COLUMN = re.compile(r'\bADD\s+COLUMN\b', re.I)
MARKERS = ('CONTRACT', 'EXPAND_REVIEWED')


def strip_sql_comments(sql):
    return re.sub(r'--[^\n]*', ' ', re.sub(r'/\*.*?\*/', ' ', sql, flags=re.S))


def add_column_clauses(sql):
    """Each ADD COLUMN clause up to the next top-level comma or semicolon."""
    for match in ADD_COLUMN.finditer(sql):
        depth, end = 0, match.end()
        while end < len(sql) and not (depth == 0 and sql[end] in ',;'):
            depth += {'(': 1, ')': -1}.get(sql[end], 0)
            if depth < 0:
                break
            end += 1
        yield sql[match.start():end]


def sql_findings(sql):
    sql = strip_sql_comments(sql)
    found = [' '.join(m.group(0).split()) for rule in SQL_RULES for m in rule.finditer(sql)]
    found += ['ADD COLUMN ... NOT NULL without DEFAULT' for clause in add_column_clauses(sql)
              if re.search(r'\bNOT\s+NULL\b', clause, re.I) and not re.search(r'\bDEFAULT\b', clause, re.I)]
    return found


def call_findings(node):
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, 'id', '')
    if name.startswith('drop_') or name == 'rename_table':
        return [name + '()']
    if name == 'alter_column':
        keywords = {k.arg: k.value for k in node.keywords}
        narrowing = [key for key in ('type_', 'new_column_name') if key in keywords]
        if isinstance(keywords.get('nullable'), ast.Constant) and keywords['nullable'].value is False:
            narrowing.append('nullable=False')
        return [f'alter_column({key})' for key in narrowing]
    return []


def module_constant(tree, name):
    for node in tree.body:
        if (isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets)
                and isinstance(node.value, ast.Constant)):
            return node.value.value
    return None


def parse_migration(name, source, read_sql):
    """revision, down_revision, markers and the destructive statements of upgrade() only."""
    tree = ast.parse(source, filename=name)
    upgrade = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'upgrade'), None)
    findings = []
    for node in ast.walk(upgrade) if upgrade else ():
        if isinstance(node, ast.Call):
            findings += call_findings(node)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if SQL_FILE.fullmatch(node.value):
                findings += [f'{finding} in {node.value}' for finding in sql_findings(read_sql(node.value))]
            else:
                findings += sql_findings(node.value)
    return {'file': name, 'revision': module_constant(tree, 'revision'),
            'down_revision': module_constant(tree, 'down_revision'), 'findings': findings,
            **{marker.lower(): module_constant(tree, marker) for marker in MARKERS}}


def analyze(files, read_sql):
    """files: {file name: source}. Returns the ordered chain, head, contract revisions and every finding.
    An unmarked destructive migration counts as contract (commits older than the markers stay safe)
    and is also a lint error; chain errors are structural and make the result unusable."""
    migrations, errors, structural = [], [], []
    for name in sorted(files):
        if not name.endswith('.py'):
            continue
        prefix = FILE_NAME.fullmatch(name)
        info = parse_migration(name, files[name], read_sql)
        if not prefix or info['revision'] != prefix.group(1):
            structural.append(f'{name}: revision {info["revision"]!r} must equal the 4-digit file name prefix')
        migrations.append(info)
    by_revision, children = {}, {}
    for info in migrations:
        if info['revision'] in by_revision:
            structural.append(f'{info["file"]}: revision {info["revision"]} also declared by {by_revision[info["revision"]]["file"]}')
        by_revision[info['revision']] = info
        if info['down_revision'] in children:
            structural.append(f'{info["file"]}: forks the chain; {children[info["down_revision"]]["file"]} '
                              f'also follows {info["down_revision"]}')
        children[info['down_revision']] = info
    for info in migrations:
        if info['down_revision'] is not None and info['down_revision'] not in by_revision:
            structural.append(f'{info["file"]}: down_revision {info["down_revision"]} does not exist')
    heads = sorted(r for r in by_revision if r not in children)
    if migrations and len(heads) != 1:
        structural.append('Expected exactly one head, found ' + (', '.join(heads) or 'none'))
    chain, current = [], children.get(None)
    while current and current['revision'] not in chain:
        chain.append(current['revision'])
        current = children.get(current['revision'])
    if not structural and len(chain) != len(migrations):
        structural.append('Migrations not reachable from the root: ' +
                          ', '.join(sorted(set(by_revision) - set(chain))))
    contracts, unmarked = [], []
    for info in migrations:
        if info['contract'] is not None and info['expand_reviewed'] is not None:
            errors.append(f'{info["file"]}: declare either CONTRACT or EXPAND_REVIEWED, not both')
        if any(info[m.lower()] is not None and not (isinstance(info[m.lower()], str) and info[m.lower()].strip())
               for m in MARKERS):
            errors.append(f'{info["file"]}: CONTRACT / EXPAND_REVIEWED must give a non-empty reason')
        if info['contract'] is not None:
            contracts.append(info['revision'])
        elif info['findings'] and info['expand_reviewed'] is None:
            unmarked.append(info['revision'])
            contracts.append(info['revision'])
            errors.append(f'{info["file"]}: destructive statements without CONTRACT or EXPAND_REVIEWED: '
                          + '; '.join(info['findings']))
    order = {revision: index for index, revision in enumerate(chain)}
    return {'chain': chain, 'head': heads[0] if len(heads) == 1 else None,
            'contracts': sorted(contracts, key=lambda r: order.get(r, len(order))),
            'unmarked': unmarked, 'errors': structural + errors, 'structural_errors': structural}


def load_directory(root=ROOT):
    folder = Path(root) / MIGRATIONS
    files = {path.name: path.read_text(encoding='utf-8') for path in (folder / 'versions').glob('*.py')}
    return files, lambda relative: (folder / relative).read_text(encoding='utf-8')


def load_commit(commit, root=ROOT):
    """Migration sources exactly as committed: one git archive, no line-ending conversion."""
    archive = subprocess.run(['git', '-c', 'core.autocrlf=false', 'archive', '--format=tar', commit, MIGRATIONS],
                             cwd=root, capture_output=True, check=True).stdout
    contents = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            if member.isfile():
                contents[member.name[len(MIGRATIONS) + 1:]] = tar.extractfile(member).read().decode('utf-8')
    files = {name.split('/', 1)[1]: text for name, text in contents.items() if name.startswith('versions/')}
    return files, lambda relative: contents[relative]


def commit_migrations(commit, root=ROOT):
    """Chain, head and contract revisions of one commit; refuses a commit whose chain is broken."""
    result = analyze(*load_commit(commit, root))
    if result['structural_errors']:
        raise ValueError(f'Migration chain of {commit} is broken: ' + '; '.join(result['structural_errors']))
    return {key: result[key] for key in ('chain', 'head', 'contracts', 'unmarked')}


def contracts_between(chain, contracts, lower, upper):
    """Contract revisions in (lower, upper] along chain. lower None means before the first migration."""
    if upper not in chain or (lower is not None and lower not in chain):
        raise ValueError(f'Revision {lower if upper in chain else upper} is not on the known migration chain')
    start = chain.index(lower) + 1 if lower is not None else 0
    if start > chain.index(upper) + 1:
        raise ValueError(f'Revision {lower} is newer than {upper}')
    return [revision for revision in chain[start:chain.index(upper) + 1] if revision in contracts]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--commit', help='inspect a commit instead of linting the working tree')
    args = parser.parse_args()
    result = analyze(*(load_commit(args.commit) if args.commit else load_directory()))
    print(json.dumps({key: result[key] for key in ('chain', 'head', 'contracts', 'errors')}, indent=2))
    sys.exit(1 if result['errors'] else 0)


if __name__ == '__main__':
    main()
