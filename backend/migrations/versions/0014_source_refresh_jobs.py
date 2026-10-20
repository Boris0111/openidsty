"""Durable source refresh and provider backoff, isolated from research publication."""
from alembic import op
revision='0014'
down_revision='0013'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('''CREATE TABLE research.source_refresh_jobs(
        job_id uuid PRIMARY KEY,source_id text NOT NULL REFERENCES public.sources,
        definition jsonb NOT NULL,status text NOT NULL CHECK(status IN ('queued','running','deferred','success','partial','failed')),
        budget jsonb NOT NULL DEFAULT '{}',result jsonb,failure jsonb,
        available_at timestamptz NOT NULL DEFAULT now(),dispatch_after timestamptz,
        created_at timestamptz NOT NULL DEFAULT now(),updated_at timestamptz NOT NULL DEFAULT now())''')
    op.execute("CREATE UNIQUE INDEX one_inflight_source_refresh ON research.source_refresh_jobs(source_id) WHERE status IN ('queued','running','deferred')")
    op.execute('CREATE INDEX source_jobs_due ON research.source_refresh_jobs(status,available_at,dispatch_after)')
    op.execute('CREATE INDEX source_jobs_history ON research.source_refresh_jobs(source_id,created_at DESC)')
    op.execute('''CREATE TABLE research.source_provider_backoff(
        provider text PRIMARY KEY,not_before timestamptz NOT NULL,reason text NOT NULL)''')
    op.execute('GRANT SELECT,INSERT,UPDATE ON research.source_refresh_jobs,research.source_provider_backoff TO research_writer')


def downgrade():raise RuntimeError('Preserve source refresh and retry history')
