"""Expand/contract classification of Alembic migrations; no database or Docker needed."""
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import migration_rules as rules


def migration(revision, down, upgrade='pass', header=''):
    down = repr(down)
    return (f'from alembic import op\nimport sqlalchemy as sa\n{header}\n'
            f'revision = {revision!r}\ndown_revision = {down}\n\n'
            f'def upgrade():\n    {upgrade}\n\n'
            f'def downgrade():\n    op.drop_table("anything")\n')


def base():
    return {'0001_first.py': migration('0001', None, 'op.create_table("a", sa.Column("id", sa.Integer))'),
            '0002_second.py': migration('0002', '0001', 'op.add_column("a", sa.Column("b", sa.Text))')}


def analyze(files, sql=None):
    return rules.analyze(files, lambda relative: (sql or {})[relative])


class RealMigrationsTests(unittest.TestCase):
    def test_working_tree_chain_is_clean(self):
        result = rules.analyze(*rules.load_directory())
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['head'], result['chain'][-1])
        self.assertEqual(result['chain'][:3], ['0001', '0002', '0003'])

    def test_contracts_are_0009_and_0017(self):
        self.assertEqual(rules.analyze(*rules.load_directory())['contracts'], ['0009', '0017'])

    def test_removing_the_0016_review_fails(self):
        files, read_sql = rules.load_directory()
        name = next(n for n in files if n.startswith('0016_'))
        files[name] = '\n'.join(line for line in files[name].splitlines() if not line.startswith('EXPAND_REVIEWED'))
        [error] = rules.analyze(files, read_sql)['errors']
        self.assertIn(name, error)
        self.assertIn('ALTER POLICY', error)

    def test_removing_the_0017_marker_fails(self):
        files, read_sql = rules.load_directory()
        name = next(n for n in files if n.startswith('0017_'))
        files[name] = '\n'.join(line for line in files[name].splitlines() if not line.startswith('CONTRACT'))
        result = rules.analyze(files, read_sql)
        self.assertEqual(len(result['errors']), 1)
        self.assertIn(name, result['errors'][0])
        self.assertIn('DROP TABLE', result['errors'][0])
        # Still counted as contract, so an old commit without markers is never treated as expand.
        self.assertIn('0017', result['contracts'])

    def test_committed_chain_matches_or_precedes_the_working_tree(self):
        committed = rules.commit_migrations('HEAD')
        tree = rules.analyze(*rules.load_directory())
        self.assertEqual(tree['chain'][:len(committed['chain'])], committed['chain'])


class DestructiveStatementTests(unittest.TestCase):
    def assert_fails(self, upgrade, *expected, sql=None):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', upgrade)
        result = analyze(files, sql)
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertIn('0003_change.py', result['errors'][0])
        for text in expected:
            self.assertIn(text, result['errors'][0])
        self.assertEqual(result['contracts'], ['0003'])

    def test_unmarked_drop_table(self):
        self.assert_fails('op.drop_table("a")', 'drop_table()')

    def test_drop_column_in_referenced_sql(self):
        upgrade = 'op.execute((Path(__file__).parents[1] / "sql/0003_change.sql").read_text())'
        sql = {'sql/0003_change.sql': '-- DROP TABLE in a comment is ignored\nALTER TABLE a DROP COLUMN b;\n'}
        self.assert_fails(upgrade, 'DROP COLUMN in sql/0003_change.sql', sql=sql)

    def test_alter_column_type(self):
        self.assert_fails('op.alter_column("a", "b", type_=sa.Integer)', 'alter_column(type_)')

    def test_alter_column_not_null_and_rename(self):
        self.assert_fails('op.alter_column("a", "b", nullable=False, new_column_name="c")',
                          'alter_column(new_column_name)', 'alter_column(nullable=False)')

    def test_add_not_null_column_without_default(self):
        self.assert_fails('op.execute("ALTER TABLE a ADD COLUMN c text NOT NULL, ADD COLUMN d int")',
                          'ADD COLUMN ... NOT NULL without DEFAULT')

    def test_sql_keywords(self):
        for statement, expected in [('ALTER TABLE a RENAME TO b', 'RENAME'),
                                    ('ALTER TABLE a ALTER COLUMN b SET DATA TYPE bigint', 'ALTER COLUMN b SET DATA TYPE'),
                                    ('ALTER TABLE a ALTER COLUMN b SET NOT NULL', 'SET NOT NULL'),
                                    ('TRUNCATE a', 'TRUNCATE'), ('DELETE FROM a', 'DELETE FROM'),
                                    ('REVOKE SELECT ON a FROM reader', 'REVOKE'),
                                    ('DROP POLICY p ON a', 'DROP POLICY'),
                                    ('ALTER TABLE a DROP b', 'ALTER TABLE ... DROP B (a column)'),
                                    ('ALTER TABLE ONLY a DROP IF EXISTS b CASCADE', 'ALTER TABLE ... DROP B (a column)'),
                                    ('ALTER TABLE a ADD c int NOT NULL', 'ADD COLUMN ... NOT NULL without DEFAULT'),
                                    ('ALTER TABLE a ADD COLUMN c int NOT NULL', 'ADD COLUMN ... NOT NULL without DEFAULT'),
                                    ('ALTER TABLE a ALTER COLUMN b DROP DEFAULT', 'DROP DEFAULT'),
                                    ('DROP INDEX research.one_inflight_source_refresh', 'DROP INDEX'),
                                    ('DROP ROLE research_reader_login', 'DROP ROLE'),
                                    ('DROP EXTENSION pgcrypto', 'DROP EXTENSION'),
                                    ('ALTER POLICY reader_published ON a USING (false)', 'ALTER POLICY')]:
            with self.subTest(statement=statement):
                self.assert_fails(f'op.execute({statement!r})', expected)

    def test_additive_statements_pass(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.execute("ALTER TABLE a ADD COLUMN revoked_at timestamptz, '
                                            "ADD COLUMN c jsonb NOT NULL DEFAULT '{}'::jsonb, "
                                            'ADD CONSTRAINT c_ok CHECK (revoked_at IS NOT NULL OR c IS NOT NULL)")')
        result = analyze(files)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['contracts'], [])

    def test_alter_table_constraint_actions_are_not_columns(self):
        # One finding for DROP CONSTRAINT, none for adding a constraint or relaxing NOT NULL.
        self.assert_fails('op.execute("ALTER TABLE a DROP CONSTRAINT c_ok, ADD CONSTRAINT c_new CHECK (b IS NOT NULL), '
                          'ALTER COLUMN b DROP NOT NULL")', 'DROP CONSTRAINT')

    def test_add_column_not_null_without_server_default(self):
        self.assert_fails('op.add_column("a", sa.Column("c", sa.Text, nullable=False))', 'add_column(NOT NULL without server_default)')
        self.assert_fails('op.add_column("a", sa.Column("id2", sa.Integer, primary_key=True))', 'add_column(NOT NULL without server_default)')

    def test_add_column_with_server_default_passes(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.add_column("a", sa.Column("c", sa.Text, nullable=False, server_default=""))')
        self.assertEqual(analyze(files)['errors'], [])

    def test_module_constant_read_by_upgrade(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'for statement in STATEMENTS: op.execute(statement)',
                                            header="STATEMENTS = ['DROP TABLE research.old_rows']")
        result = analyze(files)
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('DROP TABLE', result['errors'][0])

    def test_helper_called_by_upgrade(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'retire("a")',
                                            header='def retire(table):\n    clean(table)\n\ndef clean(table):\n    op.drop_table(table)\n')
        self.assertIn('drop_table()', analyze(files)['errors'][0])

    def test_helper_used_only_by_downgrade_is_ignored(self):
        files = base()
        source = migration('0003', '0002', 'op.create_table("b", sa.Column("id", sa.Integer))',
                           header='UNDO = "DROP TABLE b"\n\ndef undo():\n    op.execute(UNDO)\n')
        files['0003_change.py'] = source.replace('op.drop_table("anything")', 'undo()')
        self.assertEqual(analyze(files)['errors'], [])

    def test_revoked_at_is_not_revoke(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.execute("UPDATE a SET revoked_at = now() WHERE revoked_at IS NULL")')
        self.assertEqual(analyze(files)['errors'], [])

    def test_only_upgrade_is_classified(self):
        # base() migrations all drop a table in downgrade().
        self.assertEqual(analyze(base())['errors'], [])


class MarkerTests(unittest.TestCase):
    def test_expand_reviewed_passes_and_is_not_a_boundary(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.drop_index("ix_a_b")',
                                            header="EXPAND_REVIEWED = 'Dropping an index never breaks the previous version'")
        result = analyze(files)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['contracts'], [])

    def test_contract_marker_passes_and_is_a_boundary(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.drop_table("a")',
                                            header="CONTRACT = 'Removes table a; the previous version still reads it'")
        result = analyze(files)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['contracts'], ['0003'])

    def test_contract_without_destructive_statement_is_allowed(self):
        # Semantic breaks the lint cannot see are declared by hand.
        files = base()
        files['0003_change.py'] = migration('0003', '0002', 'op.execute("CREATE TRIGGER t BEFORE INSERT ON a EXECUTE FUNCTION f()")',
                                            header="CONTRACT = 'New trigger rejects writes from the previous version'")
        self.assertEqual(analyze(files)['contracts'], ['0003'])

    def test_both_markers_or_empty_reason_fail(self):
        for header in ("CONTRACT = 'x'\nEXPAND_REVIEWED = 'y'", "CONTRACT = ''"):
            files = base()
            files['0003_change.py'] = migration('0003', '0002', 'op.drop_table("a")', header=header)
            with self.subTest(header=header):
                self.assertTrue(any('0003_change.py' in error for error in analyze(files)['errors']))


class ChainTests(unittest.TestCase):
    def test_fork_fails(self):
        files = base()
        files['0003_left.py'] = migration('0003', '0002')
        files['0004_right.py'] = migration('0004', '0002')
        result = analyze(files)
        self.assertTrue(any('forks the chain' in e and '0002' in e for e in result['errors']), result['errors'])
        self.assertTrue(any('exactly one head' in e for e in result['errors']))
        self.assertIsNone(result['head'])

    def test_file_name_mismatch_fails(self):
        files = base()
        files['0003_change.py'] = migration('0004', '0002')
        result = analyze(files)
        self.assertTrue(any('0003_change.py' in e and 'file name prefix' in e for e in result['errors']), result['errors'])

    def test_missing_parent_fails(self):
        files = base()
        files['0003_change.py'] = migration('0003', '0099')
        self.assertTrue(any('0099 does not exist' in e for e in analyze(files)['errors']))

    def test_broken_commit_chain_is_refused(self):
        files = base()
        files['0003_left.py'] = migration('0003', '0002')
        files['0004_right.py'] = migration('0004', '0002')
        with mock.patch.object(rules, 'load_commit', return_value=(files, lambda r: '')):
            with self.assertRaisesRegex(ValueError, 'broken'):
                rules.commit_migrations('abc')


class ContractsBetweenTests(unittest.TestCase):
    chain = ['0001', '0002', '0003', '0004', '0005']

    def test_half_open_interval(self):
        self.assertEqual(rules.contracts_between(self.chain, ['0003', '0005'], '0003', '0005'), ['0005'])
        self.assertEqual(rules.contracts_between(self.chain, ['0003', '0005'], '0002', '0004'), ['0003'])
        self.assertEqual(rules.contracts_between(self.chain, ['0003'], '0003', '0003'), [])
        self.assertEqual(rules.contracts_between(self.chain, ['0001'], None, '0002'), ['0001'])

    def test_unknown_or_reversed_revisions_fail(self):
        with self.assertRaisesRegex(ValueError, '0009'):
            rules.contracts_between(self.chain, [], '0002', '0009')
        with self.assertRaisesRegex(ValueError, 'newer'):
            rules.contracts_between(self.chain, [], '0004', '0002')


if __name__ == '__main__':
    unittest.main()
