"""Reader financial policies check each visible row by key instead of hashing every published row."""
from alembic import op
revision='0016'
down_revision='0015'
branch_labels=None
depends_on=None

# Same visibility as 0008: a row is readable only when its parent row is readable under the parent's own policy.
ROW_LOOKUPS={
    'financial_observations':'EXISTS(SELECT 1 FROM research.financial_groups g WHERE g.group_id=financial_observations.group_id)',
    'financial_derivations':'EXISTS(SELECT 1 FROM research.financial_observations o WHERE o.observation_id=financial_derivations.observation_id)',
    'observation_provenance':'EXISTS(SELECT 1 FROM research.financial_observations o WHERE o.observation_id=observation_provenance.observation_id)'}
SET_LOOKUPS={
    'financial_observations':'group_id IN (SELECT group_id FROM research.financial_groups)',
    'financial_derivations':'observation_id IN (SELECT observation_id FROM research.financial_observations)',
    'observation_provenance':'observation_id IN (SELECT observation_id FROM research.financial_observations)'}


def upgrade():
    for table,check in ROW_LOOKUPS.items():
        op.execute(f'ALTER POLICY reader_published ON research.{table} USING ({check})')
    # Reader queries are short keyed lookups; JIT compilation cost seconds per request once RLS plans grew with the data.
    op.execute('ALTER ROLE research_reader_login SET jit=off')


def downgrade():
    for table,check in SET_LOOKUPS.items():
        op.execute(f'ALTER POLICY reader_published ON research.{table} USING ({check})')
    op.execute('ALTER ROLE research_reader_login RESET jit')
