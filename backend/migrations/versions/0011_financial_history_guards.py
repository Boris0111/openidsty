"""Keep financial identities and values immutable; rank by real filing date."""
from alembic import op
revision='0011'
down_revision='0010'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('''CREATE INDEX ix_research_observation_filing ON research.financial_observations
        (group_id,filed_at DESC NULLS LAST,revision DESC)''')
    op.execute('''CREATE INDEX ix_research_raw_filing ON research.financial_raw_facts
        (company_id,source_family,accession,filed_at)''')
    for table in ('financial_groups','financial_raw_facts'):
        op.execute('CREATE TRIGGER immutable_'+table+' BEFORE UPDATE OR DELETE ON research.'+table+
            ' FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row()')
    op.execute('''CREATE TRIGGER immutable_financial_values BEFORE UPDATE OF group_id,revision,value,semantic_hash,
        recorded_at,supersedes,provenance_kind,limitations ON research.financial_observations
        FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row()''')
    op.execute('''CREATE TRIGGER preserve_financial_values BEFORE DELETE ON research.financial_observations
        FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row()''')


def downgrade():
    raise RuntimeError('Preserve financial revision history; restore an isolated backup')
