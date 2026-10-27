"""Drop the company financial store; theme proxy revenue stays in public.financials."""
from alembic import op
revision='0017'
down_revision='0016'
branch_labels=None
depends_on=None
CONTRACT='Drops the company financial tables, view and import guard that versions before 0017 still query'

# Children before parents. DROP TABLE also removes each table's policies, triggers and indexes;
# the shared research.guard_immutable_row() stays because other research tables use it.
TABLES=('financial_derivations','observation_provenance','financial_observations','financial_raw_facts',
        'financial_import_batches','financial_groups','financial_metric_definitions')


def upgrade():
    op.execute('DROP VIEW research.financial_fact_citations')
    for table in TABLES:
        op.execute('DROP TABLE research.'+table)
    op.execute('DROP FUNCTION research.guard_financial_import()')


def downgrade():
    raise RuntimeError('Company financials were removed; restore an isolated backup to recover them')
