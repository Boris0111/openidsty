"""Provider snapshot dates are not company filing dates."""
from alembic import op
revision='0012'
down_revision='0011'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('ALTER TABLE research.financial_observations ADD COLUMN source_as_of date')
    op.execute('''CREATE INDEX ix_research_observation_effective_date ON research.financial_observations
        (group_id,(COALESCE(filed_at,source_as_of)) DESC NULLS LAST,revision DESC)''')


def downgrade():
    raise RuntimeError('Preserve filing versus snapshot date semantics')
