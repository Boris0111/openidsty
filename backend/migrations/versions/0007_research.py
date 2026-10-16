"""Add isolated, versioned research model without changing legacy primary keys."""
from pathlib import Path
from alembic import op
from sqlalchemy import text

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        raise RuntimeError('Research migration requires explicit PostgreSQL environment')
    sql = Path(__file__).parents[1] / 'sql/0007_research.sql'
    op.get_bind().execute(text(sql.read_text(encoding='utf-8')))


def downgrade():
    # A code rollback must never silently destroy published research/history.
    raise RuntimeError('Restore a verified backup to an isolated DB; destructive downgrade disabled')
