"""Bind financial confirmations to one immutable preview and durable result."""
from alembic import op
revision='0013'
down_revision='0012'
branch_labels=None
depends_on=None


def upgrade():
    op.execute('''ALTER TABLE research.financial_import_batches
        ADD COLUMN confirmation_key text UNIQUE,
        ADD COLUMN confirmation_hash text,
        ADD COLUMN result jsonb,
        ADD CONSTRAINT financial_confirmation_complete CHECK
            (status<>'confirmed' OR (confirmation_key IS NOT NULL AND confirmation_hash IS NOT NULL AND result IS NOT NULL))''')
    op.execute('''CREATE FUNCTION research.guard_financial_import() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          IF OLD.status='confirmed' OR TG_OP='DELETE' OR NEW.payload IS DISTINCT FROM OLD.payload
            OR NEW.payload_hash IS DISTINCT FROM OLD.payload_hash THEN
            RAISE EXCEPTION 'financial import preview/result is immutable' USING ERRCODE='23514';
          END IF;
          RETURN NEW;
        END $$''')
    op.execute('''CREATE TRIGGER immutable_financial_import BEFORE UPDATE OR DELETE ON research.financial_import_batches
        FOR EACH ROW EXECUTE FUNCTION research.guard_financial_import()''')


def downgrade():raise RuntimeError('Preserve official financial import audit history')
