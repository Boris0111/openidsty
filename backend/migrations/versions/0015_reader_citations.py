"""Curated fact citations without granting readers access to raw import payloads."""
from alembic import op
revision='0015'
down_revision='0014'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('''CREATE VIEW research.financial_fact_citations WITH (security_barrier=true) AS
        SELECT f.fact_id,f.accession,f.tag,f.value,f.filed_at,f.source_url,
            f.payload->>'raw_unit' AS raw_unit,f.payload->>'normalization_multiplier' AS multiplier,
            f.payload->>'source_as_of' AS source_as_of,f.payload->'original'->>'locator' AS locator
        FROM research.financial_raw_facts f WHERE EXISTS(
            SELECT 1 FROM research.observation_provenance p JOIN research.financial_observations o USING(observation_id)
            JOIN research.financial_groups g USING(group_id) JOIN research.entity_snapshots s ON s.entity_id=g.company_id
            JOIN research.research_releases r USING(release_id)
            WHERE p.fact_id=f.fact_id AND s.kind='company' AND r.status='published')''')
    op.execute('GRANT SELECT ON research.financial_fact_citations TO research_reader,research_writer')
    op.execute('CREATE INDEX ix_research_provenance_fact ON research.observation_provenance(fact_id,observation_id)')
    op.execute('''CREATE INDEX ix_research_event_nature ON research.event_entity_links(entity_id,source_nature,relevance,event_id DESC)''')
    op.execute('''CREATE INDEX ix_events_research_date ON public.events
        (COALESCE(published_at,reported_at,'0001-01-01 00:00:00+00'::timestamptz) DESC,id DESC) WHERE lifecycle='published' ''')


def downgrade():raise RuntimeError('Preserve verified reader citation boundaries')
