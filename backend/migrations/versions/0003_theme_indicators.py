"""Add indicator definitions and immutable observation revisions."""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('indicators',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('kind', sa.String(20), nullable=False),
        sa.Column('unit', sa.String(40), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('basis', sa.String(40), nullable=False),
        sa.Column('data', sa.JSON, nullable=False))
    op.create_table('theme_indicators',
        sa.Column('theme_id', sa.String(80), sa.ForeignKey('themes.id'), primary_key=True),
        sa.Column('indicator_id', sa.String(100), sa.ForeignKey('indicators.id'), primary_key=True))
    op.create_table('indicator_observations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('indicator_id', sa.String(100), sa.ForeignKey('indicators.id'), nullable=False),
        sa.Column('source_id', sa.String(100), sa.ForeignKey('sources.id'), nullable=False),
        sa.Column('identity', sa.String(64), nullable=False),
        sa.Column('document_identity', sa.String(500), nullable=False),
        sa.Column('dataset', sa.String(100), nullable=False),
        sa.Column('entity', sa.String(100), nullable=False),
        sa.Column('original_period', sa.String(150), nullable=False),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('basis', sa.String(40), nullable=False),
        sa.Column('scope', sa.Text, nullable=False),
        sa.Column('unit', sa.String(40), nullable=False),
        sa.Column('currency', sa.String(10)),
        sa.Column('value', sa.Numeric(28, 8), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True)),
        sa.Column('reported_at', sa.DateTime(timezone=True)),
        sa.Column('published_precision', sa.String(20), nullable=False, server_default='unknown'),
        sa.Column('date_semantics', sa.String(30), nullable=False, server_default='unknown'),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('url', sa.Text, nullable=False),
        sa.Column('raw_excerpt', sa.Text, nullable=False),
        sa.Column('raw', sa.JSON, nullable=False),
        sa.Column('revision', sa.Integer, nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('valid', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('invalid_reason', sa.Text),
        sa.UniqueConstraint('identity', 'revision', name='uq_indicator_revision'))
    for field in ('indicator_id', 'identity', 'period_end'):
        op.create_index(f'ix_indicator_observations_{field}', 'indicator_observations', [field])


def downgrade():
    raise RuntimeError('保留指標與修訂資料；請回滾應用 image，勿刪除新增表')
