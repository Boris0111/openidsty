"""Preserve authored assessment versions and retired themes."""
from alembic import op
import sqlalchemy as sa
revision='0004'
down_revision='0003'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('themes',sa.Column('active',sa.Boolean,nullable=False,server_default=sa.true()))
    op.create_table('theme_assessment_versions',
        sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('theme_id',sa.String(80),sa.ForeignKey('themes.id'),nullable=False),
        sa.Column('version_number',sa.Integer,nullable=False),
        sa.Column('payload',sa.JSON,nullable=False),
        sa.Column('content_hash',sa.String(64),nullable=False),
        sa.Column('reviewed',sa.String(10)),
        sa.Column('recorded_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('reason',sa.Text,nullable=False),
        sa.UniqueConstraint('theme_id','version_number',name='uq_theme_version'))
    op.create_index('ix_theme_assessment_versions_theme_id','theme_assessment_versions',['theme_id'])

def downgrade():
    raise RuntimeError('保留題材與版本；回滾應用 image，勿刪新增資料')
