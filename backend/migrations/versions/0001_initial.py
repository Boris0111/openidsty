"""Initial application schema. Independent of Prefect's database."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('segments', sa.Column('id', sa.String(80), primary_key=True), sa.Column('layer', sa.String(40), nullable=False), sa.Column('name', sa.String(100), nullable=False), sa.Column('position', sa.Integer, nullable=False), sa.Column('data', sa.JSON, nullable=False), sa.Column('prose', sa.Text, nullable=False))
    op.create_index('ix_segments_layer', 'segments', ['layer'])
    op.create_table('themes', sa.Column('id', sa.String(80), primary_key=True), sa.Column('data', sa.JSON, nullable=False))
    op.create_table('companies', sa.Column('ticker', sa.String(40), primary_key=True), sa.Column('name', sa.String(100), nullable=False), sa.Column('aliases', sa.JSON, nullable=False), sa.Column('cik', sa.String(10)))
    op.create_table('roles', sa.Column('ticker', sa.String(40), sa.ForeignKey('companies.ticker'), primary_key=True), sa.Column('segment_id', sa.String(80), sa.ForeignKey('segments.id'), primary_key=True), sa.Column('role', sa.Text, nullable=False), sa.Column('tier', sa.Integer, nullable=False))
    op.create_table('relations', sa.Column('id', sa.String(80), primary_key=True), sa.Column('source', sa.String(40), sa.ForeignKey('companies.ticker'), nullable=False), sa.Column('target', sa.String(40), sa.ForeignKey('companies.ticker'), nullable=False), sa.Column('kind', sa.String(30), nullable=False), sa.Column('direction', sa.String(20), nullable=False), sa.Column('review_status', sa.String(20), nullable=False), sa.Column('relevance', sa.String(20), nullable=False), sa.Column('data', sa.JSON, nullable=False))
    for column in ('source', 'target'):
        op.create_index(f'ix_relations_{column}', 'relations', [column])
    op.create_table('sources', sa.Column('id', sa.String(100), primary_key=True), sa.Column('name', sa.String(150), nullable=False), sa.Column('url', sa.Text, nullable=False), sa.Column('status', sa.String(30), nullable=False), sa.Column('last_attempt', sa.DateTime(timezone=True)), sa.Column('last_success', sa.DateTime(timezone=True)), sa.Column('error', sa.Text), sa.Column('new_count', sa.Integer, nullable=False), sa.Column('data', sa.JSON, nullable=False))
    op.create_table('events', sa.Column('id', sa.Integer, primary_key=True), sa.Column('source_id', sa.String(100), sa.ForeignKey('sources.id'), nullable=False), sa.Column('external_id', sa.String(500), nullable=False), sa.Column('ticker', sa.String(40), sa.ForeignKey('companies.ticker'), nullable=False), sa.Column('title', sa.Text, nullable=False), sa.Column('body', sa.Text, nullable=False), sa.Column('kind', sa.String(30), nullable=False), sa.Column('lifecycle', sa.String(20), nullable=False), sa.Column('published_at', sa.DateTime(timezone=True), nullable=False), sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False), sa.Column('url', sa.Text, nullable=False), sa.Column('mentioned', sa.JSON, nullable=False), sa.Column('raw', sa.JSON, nullable=False), sa.UniqueConstraint('source_id','external_id'))
    for column in ('source_id', 'ticker', 'published_at'):
        op.create_index(f'ix_events_{column}', 'events', [column])
    op.create_table('financials', sa.Column('id', sa.Integer, primary_key=True), sa.Column('ticker', sa.String(40), sa.ForeignKey('companies.ticker'), nullable=False), sa.Column('source_id', sa.String(100), sa.ForeignKey('sources.id'), nullable=False), sa.Column('period', sa.String(30), nullable=False), sa.Column('period_end', sa.String(10), nullable=False), sa.Column('basis', sa.String(20), nullable=False), sa.Column('currency', sa.String(10), nullable=False), sa.Column('revenue', sa.Float), sa.Column('revenue_yoy', sa.Float), sa.Column('gross_margin', sa.Float), sa.Column('eps', sa.Float), sa.Column('published_at', sa.DateTime(timezone=True), nullable=False), sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False), sa.Column('url', sa.Text, nullable=False), sa.Column('raw', sa.JSON, nullable=False), sa.UniqueConstraint('ticker','source_id','period','basis'))
    for column in ('ticker', 'period_end'):
        op.create_index(f'ix_financials_{column}', 'financials', [column])
    op.create_table('ingestion_runs', sa.Column('id', sa.Integer, primary_key=True), sa.Column('started_at', sa.DateTime(timezone=True), nullable=False), sa.Column('finished_at', sa.DateTime(timezone=True)), sa.Column('results', sa.JSON, nullable=False))

def downgrade():
    for name in ('ingestion_runs','financials','events','sources','relations','roles','companies','themes','segments'):
        op.drop_table(name)
