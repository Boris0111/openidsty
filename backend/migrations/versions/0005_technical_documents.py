"""Add document projections without rewriting research or dynamic records."""
from alembic import op
import sqlalchemy as sa
revision='0005'
down_revision='0004'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('technical_documents',
        sa.Column('id',sa.String(100),primary_key=True),
        sa.Column('source_id',sa.String(100),sa.ForeignKey('sources.id'),nullable=False),
        sa.Column('title',sa.Text,nullable=False),sa.Column('doc_kind',sa.String(40),nullable=False),
        sa.Column('active',sa.Boolean,nullable=False),sa.Column('data',sa.JSON,nullable=False))
    op.create_index('ix_technical_documents_source_id','technical_documents',['source_id'])
    op.create_table('technical_observations',
        sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('document_id',sa.String(100),sa.ForeignKey('technical_documents.id'),nullable=False),
        sa.Column('observation_key',sa.String(64),nullable=False),
        sa.Column('official_version',sa.String(200)),sa.Column('content_hash',sa.String(64),nullable=False),
        sa.Column('raw_hash',sa.String(64)),sa.Column('parser_version',sa.String(60),nullable=False),
        sa.Column('url',sa.Text,nullable=False),sa.Column('fetched_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('data',sa.JSON,nullable=False),
        sa.UniqueConstraint('document_id','observation_key',name='uq_document_observation'))
    op.create_index('ix_technical_observations_document_id','technical_observations',['document_id'])
    op.create_table('technical_reviews',
        sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('observation_id',sa.Integer,sa.ForeignKey('technical_observations.id'),nullable=False),
        sa.Column('status',sa.String(30),nullable=False),sa.Column('reviewed',sa.String(10)),
        sa.Column('reason',sa.Text),sa.Column('version_id',sa.String(100)),
        sa.UniqueConstraint('observation_id',name='uq_document_review'))
    op.create_index('ix_technical_reviews_observation_id','technical_reviews',['observation_id'])

def downgrade():
    raise RuntimeError('保留文件與核對歷史；回滾應用 image，勿刪新增資料')
