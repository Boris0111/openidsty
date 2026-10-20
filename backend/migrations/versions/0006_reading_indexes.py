"""Cover the classification joins without loading their JSON evidence pages."""
from alembic import op
revision='0006'
down_revision='0005'
branch_labels=None
depends_on=None

def upgrade():
    op.create_index('ix_event_segments_scope_relevance','event_segments',['segment_id','relevance','event_id'])
    op.create_index('ix_event_themes_scope_relevance','event_themes',['theme_id','relevance','event_id'])

def downgrade():
    op.drop_index('ix_event_themes_scope_relevance',table_name='event_themes')
    op.drop_index('ix_event_segments_scope_relevance',table_name='event_segments')
