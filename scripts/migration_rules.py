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
    re.compile(r'\bDROP\s+(?:TABLE|(?:MATERIALIZED\s+)?VIEW|COLUMN|FUNCTION|TYPE|SCHEMA|POLICY|TRIGGER|CONSTRAINT|SEQUENCE'
               r'|INDEX|ROLE|EXTENSION|DEFAULT)\b', re.I),
    re.compile(r'\bALTER\s+POLICY\b', re.I),
    re.compile(r'\bRENAME\b', re.I),
    re.compile(r'\bALTER\s+(?:COLUMN\s+)?"?\w+"?\s+(?:SET\s+DATA\s+)?TYPE\b', re.I),
    re.compile(r'\bSET\s+NOT\s+NULL\b', re.I),
    re.compile(r'\bTRUNCATE\b', re.I),
    re.compile(r'\bDELETE\s+FROM\b', re.I),
    re.compile(r'\bREVOKE\b', re.I),
)
ALTER_TABLE = re.compile(r'\bALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?[\w."]+\s+', re.I)
# ADD and DROP actions of ALTER TABLE that are not about a column.
NOT_A_COLUMN = {'CONSTRAINT', 'PRIMARY', 'UNIQUE', 'CHECK', 'FOREIGN', 'EXCLUDE'}
MARKERS = ('CONTRACT', 'EXPAND_REVIEWED')


def strip_sql_comments(sql):
    return re.sub(r'--[^\n]*', ' ', re.sub(r'/\*.*?\*/', ' ', sql, flags=re.S))


def alter_table_actions(sql):
    """Each comma-separated action of every ALTER TABLE statement, up to the statement's end."""
    for match in ALTER_TABLE.finditer(sql):
        depth, start, end = 0, match.end(), match.end()
        while end < len(sql) and not (depth == 0 and sql[end] == ';'):
            if depth == 0 and sql[end] == ',':
                yield ' '.join(sql[start:end].split())
                start = end + 1
            depth += {'(': 1, ')': -1}.get(sql[end], 0)
            if depth < 0:
                break
            end += 1
        yield ' '.join(sql[start:end].split())


def action_findings(action):
    """ALTER TABLE actions that drop or add a column, whether or not they spell out COLUMN."""
    words = action.upper().split()
    if len(words) < 2 or words[1] in NOT_A_COLUMN:
        return []
    if words[0] == 'DROP' and words[1] != 'COLUMN':  # DROP COLUMN itself is an SQL_RULES match
        column = words[3] if words[1:3] == ['IF', 'EXISTS'] and len(words) > 3 else words[1]
        return [f'ALTER TABLE ... DROP {column} (a column)']
    if words[0] == 'ADD' and re.search(r'\bNOT\s+NULL\b', action, re.I) and not re.search(r'\bDEFAULT\b', action, re.I):
        return ['ADD COLUMN ... NOT NULL without DEFAULT']
    return []


def sql_findings(sql):
    sql = strip_sql_comments(sql)
    found = [' '.join(m.group(0).split()) for rule in SQL_RULES for m in rule.finditer(sql)]
    return found + [finding for action in alter_table_actions(sql) for finding in action_findings(action)]


def is_true(node, value):
    return isinstance(node, ast.Constant) and node.value is value


def call_findings(node):
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, 'id', '')
    if name.startswith('drop_') or name == 'rename_table':
        return [name + '()']
    if name == 'alter_column':
        keywords = {k.arg: k.value for k in node.keywords}
        narrowing = [key for key in ('type_', 'new_column_name') if key in keywords]
        if is_true(keywords.get('nullable'), False):
            narrowing.append('nullable=False')
        return [f'alter_column({key})' for key in narrowing]
    if name == 'add_column':
        # The previous version's INSERTs do not set a new NOT NULL column unless the server supplies a default.
        for column in [a for a in node.args if isinstance(a, ast.Call)]:
            keywords = {k.arg: k.value for k in column.keywords}
            if ((is_true(keywords.get('nullable'), False) or is_true(keywords.get('primary_key'), True))
                    and 'server_default' not in keywords):
                return ['add_column(NOT NULL without server_default)']
    return []


def reachable(tree, upgrade):
    """upgrade() plus the module-level constants it reads and the helpers it calls, recursively."""
    definitions = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name not in ('upgrade', 'downgrade'):
            definitions[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                if isinstance(target, ast.Name) and node.value is not None:
                    definitions[target.id] = node.value
    nodes, pending, seen = [], [upgrade], set()
    while pending:
        node = pending.pop()
        nodes.append(node)
        for name in {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} - seen:
            seen.add(name)
            if name in definitions:
                pending.append(definitions[name])
    return nodes


def module_constant(tree, name):
    for node in tree.body:
        if (isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets)
                and isinstance(node.value, ast.Constant)):
            return node.value.value
    return None


def parse_migration(name, source, read_sql):
    """revision, down_revision, markers and the destructive statements reachable from upgrade() (never downgrade())."""
    tree = ast.parse(source, filename=name)
    upgrade = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'upgrade'), None)
    findings = []
    for node in (child for root in (reachable(tree, upgrade) if upgrade else []) for child in ast.walk(root)):
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
