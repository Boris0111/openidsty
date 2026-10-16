"""Durable publication checkpoints and normalized request identity."""
from alembic import op
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE research.publish_jobs ADD COLUMN checkpoint jsonb NOT NULL DEFAULT '{}'::jsonb, ADD COLUMN request_payload jsonb NOT NULL DEFAULT '{}'::jsonb")


def downgrade():
    raise RuntimeError('Preserve durable publication jobs; restore an isolated backup')
