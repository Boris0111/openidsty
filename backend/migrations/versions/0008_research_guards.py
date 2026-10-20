"""Enforce published content immutability and hide unpublished dynamic links."""
from pathlib import Path
from alembic import op
from sqlalchemy import text

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().execute(text((Path(__file__).parents[1] / 'sql/0008_research_guards.sql').read_text(encoding='utf-8')))


def downgrade():
    raise RuntimeError('Restore a verified backup to an isolated DB; destructive downgrade disabled')
