"""Add research, semantic dates and content classification; keep legacy data."""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('themes') as batch:
        batch.add_column(sa.Column('prose', sa.Text, nullable=False, server_default=''))
        batch.add_column(sa.Column('checked', sa.String(10)))
    with op.batch_alter_table('events') as batch:
        batch.alter_column('ticker', existing_type=sa.String(40), nullable=True)
        batch.alter_column('published_at', existing_type=sa.DateTime(timezone=True), nullable=True)
        batch.add_column(sa.Column('published_precision', sa.String(20), nullable=False, server_default='unknown'))
        for key in ('reported_at', 'activity_at'):
            batch.add_column(sa.Column(key, sa.DateTime(timezone=True)))
        batch.add_column(sa.Column('date_semantics', sa.String(30), nullable=False, server_default='unknown'))
        batch.add_column(sa.Column('period', sa.String(80)))
        batch.add_column(sa.Column('basis', sa.Text))
        batch.add_column(sa.Column('routine', sa.Boolean, nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column('rules_version', sa.String(40)))
        batch.add_column(sa.Column('identity', sa.String(64)))
        batch.add_column(sa.Column('feeds', sa.JSON, nullable=False, server_default='[]'))
        batch.create_unique_constraint('uq_events_identity', ['identity'])
        batch.create_index('ix_events_routine', ['routine'])
    for table, key, target in [('event_segments', 'segment_id', 'segments.id'), ('event_themes', 'theme_id', 'themes.id')]:
        op.create_table(table,
            sa.Column('event_id', sa.Integer, sa.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
            sa.Column(key, sa.String(80), sa.ForeignKey(target, ondelete='CASCADE'), primary_key=True),
            sa.Column('relevance', sa.String(20), nullable=False),
            sa.Column('evidence', sa.JSON, nullable=False))

def downgrade():
    # Nullable legacy fields cannot safely be made mandatory after industry events exist.
    raise RuntimeError('此 migration 保留資料；請回滾應用 image，勿降級刪除研究及事件')
