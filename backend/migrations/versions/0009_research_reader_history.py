"""Keep legacy technical maintenance queues outside the reader role."""
from pathlib import Path
from alembic import op
from sqlalchemy import text
revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().execute(text((Path(__file__).parents[1] / 'sql/0009_research_reader_history.sql').read_text(encoding='utf-8')))


def downgrade():
    raise RuntimeError('Restore an isolated backup; reader isolation is not downgraded')
