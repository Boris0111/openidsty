-- Additive PostgreSQL 16 research model. Never rewrites public legacy tables.
CREATE SCHEMA research;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='research_reader') THEN
    CREATE ROLE research_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    CREATE ROLE research_writer NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    CREATE ROLE research_reader_login NOLOGIN IN ROLE research_reader;
    CREATE ROLE research_writer_login NOLOGIN IN ROLE research_writer;
  END IF;
END $$;
GRANT USAGE ON SCHEMA research TO research_reader, research_writer;
GRANT USAGE ON SCHEMA public TO research_reader, research_writer;

CREATE TABLE research.entities (
  entity_id text PRIMARY KEY CHECK (entity_id ~ '^(company|segment|theme|application|role|product|concept|research)-[a-z0-9]+(-[a-z0-9]+)*$'),
  kind text NOT NULL CHECK (kind IN ('company','segment','theme','application','role','product','concept','research')),
  CHECK (entity_id LIKE kind || '-%'),
  UNIQUE (entity_id, kind)
);
CREATE TABLE research.research_releases (
  release_id uuid PRIMARY KEY,
  git_commit text NOT NULL CHECK (git_commit ~ '^[0-9a-f]{40,64}$'),
  schema_version text NOT NULL,
  content_hash text NOT NULL CHECK (content_hash ~ '^[0-9a-f]{64}$'),
  status text NOT NULL CHECK (status IN ('preparing','ready','published','failed')),
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz,
  reason text NOT NULL,
  CHECK (status <> 'published' OR published_at IS NOT NULL),
  UNIQUE (git_commit, schema_version, content_hash)
);
CREATE TABLE research.release_head (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  release_id uuid NOT NULL REFERENCES research.research_releases,
  generation bigint NOT NULL CHECK (generation > 0),
  activated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE research.entity_snapshots (
  release_id uuid NOT NULL REFERENCES research.research_releases,
  entity_id text NOT NULL,
  kind text NOT NULL,
  name text NOT NULL,
  summary text NOT NULL,
  markdown text NOT NULL,
  data jsonb NOT NULL CHECK (jsonb_typeof(data)='object'),
  semantic_hash text NOT NULL CHECK (semantic_hash ~ '^[0-9a-f]{64}$'),
  reviewed date,
  PRIMARY KEY (release_id, entity_id),
  FOREIGN KEY (entity_id,kind) REFERENCES research.entities(entity_id,kind)
);
CREATE INDEX ix_research_catalog ON research.entity_snapshots(release_id,kind,entity_id);
CREATE TABLE research.entity_aliases (
  release_id uuid NOT NULL,
  entity_id text NOT NULL,
  alias text NOT NULL CHECK (length(alias)>0),
  normalized text NOT NULL,
  alias_kind text NOT NULL CHECK (alias_kind IN ('name','alias','ticker','legacy')),
  PRIMARY KEY (release_id,entity_id,alias,alias_kind),
  FOREIGN KEY (release_id,entity_id) REFERENCES research.entity_snapshots
);
CREATE INDEX ix_research_alias_exact ON research.entity_aliases(release_id,normalized text_pattern_ops);
CREATE INDEX ix_research_alias_trigram ON research.entity_aliases USING gin(normalized gin_trgm_ops);
CREATE TABLE research.listings (
  release_id uuid NOT NULL,
  listing_id text NOT NULL,
  company_id text NOT NULL CHECK (company_id LIKE 'company-%'),
  ticker text NOT NULL,
  market text NOT NULL,
  exchange text NOT NULL,
  share_class text NOT NULL,
  valid_from date,
  valid_to date,
  PRIMARY KEY (release_id,listing_id),
  UNIQUE NULLS NOT DISTINCT (release_id,market,exchange,ticker,valid_from),
  FOREIGN KEY (release_id,company_id) REFERENCES research.entity_snapshots,
  CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from)
);
CREATE INDEX ix_research_listing_resolve ON research.listings(release_id,ticker);
CREATE TABLE research.source_identifiers (
  release_id uuid NOT NULL,
  company_id text NOT NULL CHECK (company_id LIKE 'company-%'),
  provider text NOT NULL,
  value text NOT NULL,
  PRIMARY KEY (release_id,provider,value),
  FOREIGN KEY (release_id,company_id) REFERENCES research.entity_snapshots
);
CREATE TABLE research.legacy_mappings (
  release_id uuid NOT NULL,
  kind text NOT NULL,
  legacy_key text NOT NULL,
  entity_id text NOT NULL,
  PRIMARY KEY (release_id,kind,legacy_key,entity_id),
  FOREIGN KEY (release_id,entity_id) REFERENCES research.entity_snapshots
);
CREATE INDEX ix_research_legacy_resolve ON research.legacy_mappings(release_id,kind,legacy_key);
CREATE TABLE research.release_sources (
  release_id uuid NOT NULL REFERENCES research.research_releases,
  source_id text NOT NULL,
  name text NOT NULL,
  url text NOT NULL,
  data jsonb NOT NULL,
  PRIMARY KEY (release_id,source_id)
);
CREATE TABLE research.documents (
  document_id text PRIMARY KEY
);
CREATE TABLE research.document_revisions (
  revision_id text PRIMARY KEY CHECK (revision_id ~ '^[0-9a-f]{64}$'),
  document_id text NOT NULL REFERENCES research.documents,
  version_key text NOT NULL,
  title text NOT NULL,
  url text NOT NULL,
  doc_kind text NOT NULL CHECK (doc_kind IN ('formal-specification','draft','roadmap','vendor-explanation','informative')),
  data jsonb NOT NULL,
  UNIQUE (document_id,version_key,revision_id)
);
CREATE TABLE research.release_documents (
  release_id uuid NOT NULL REFERENCES research.research_releases,
  revision_id text NOT NULL REFERENCES research.document_revisions,
  PRIMARY KEY (release_id,revision_id)
);
CREATE TABLE research.assets (
  sha256 text PRIMARY KEY CHECK (sha256 ~ '^[0-9a-f]{64}$'),
  storage_key text NOT NULL,
  media_type text NOT NULL,
  byte_size bigint NOT NULL CHECK (byte_size BETWEEN 1 AND 10485760)
);
CREATE TABLE research.release_assets (
  release_id uuid NOT NULL REFERENCES research.research_releases,
  asset_id text NOT NULL,
  sha256 text NOT NULL REFERENCES research.assets,
  metadata jsonb NOT NULL,
  PRIMARY KEY (release_id,asset_id)
);
CREATE TABLE research.research_claims (
  release_id uuid NOT NULL,
  entity_id text NOT NULL,
  claim_id text NOT NULL,
  statement text NOT NULL,
  confidence text NOT NULL CHECK (confidence IN ('well-supported','inference','needs-verification')),
  conditions jsonb NOT NULL CHECK (jsonb_typeof(conditions)='array'),
  reviewed date NOT NULL,
  PRIMARY KEY (release_id,entity_id,claim_id),
  FOREIGN KEY (release_id,entity_id) REFERENCES research.entity_snapshots
);
CREATE TABLE research.claim_evidence (
  release_id uuid NOT NULL,
  entity_id text NOT NULL,
  claim_id text NOT NULL,
  ordinal integer NOT NULL CHECK (ordinal>=0),
  revision_id text NOT NULL,
  locator text NOT NULL,
  stance text NOT NULL CHECK (stance IN ('supporting','counter')),
  applicable_period text NOT NULL,
  data jsonb NOT NULL,
  PRIMARY KEY (release_id,entity_id,claim_id,ordinal),
  FOREIGN KEY (release_id,entity_id,claim_id) REFERENCES research.research_claims,
  FOREIGN KEY (release_id,revision_id) REFERENCES research.release_documents
);
CREATE TABLE research.taxonomy_links (
  release_id uuid NOT NULL,
  link_id text NOT NULL,
  parent_id text NOT NULL,
  child_id text NOT NULL,
  PRIMARY KEY (release_id,link_id),
  UNIQUE (release_id,parent_id,child_id),
  FOREIGN KEY (release_id,parent_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,child_id) REFERENCES research.entity_snapshots,
  CHECK (parent_id<>child_id)
);
CREATE INDEX ix_research_taxonomy_child ON research.taxonomy_links(release_id,child_id);
CREATE TABLE research.company_offerings (
  release_id uuid NOT NULL,
  offering_id text NOT NULL,
  company_id text NOT NULL CHECK (company_id LIKE 'company-%'),
  product_id text NOT NULL CHECK (product_id LIKE 'product-%'),
  role_id text NOT NULL CHECK (role_id LIKE 'role-%'),
  conditions jsonb NOT NULL,
  PRIMARY KEY (release_id,offering_id),
  FOREIGN KEY (release_id,company_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,product_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,role_id) REFERENCES research.entity_snapshots
);
CREATE INDEX ix_research_offering_product ON research.company_offerings(release_id,product_id,company_id);
CREATE TABLE research.offering_claims (
  release_id uuid NOT NULL,
  offering_id text NOT NULL,
  entity_id text NOT NULL,
  claim_id text NOT NULL,
  PRIMARY KEY (release_id,offering_id,entity_id,claim_id),
  FOREIGN KEY (release_id,offering_id) REFERENCES research.company_offerings,
  FOREIGN KEY (release_id,entity_id,claim_id) REFERENCES research.research_claims
);
CREATE TABLE research.relations (
  release_id uuid NOT NULL,
  relation_id text NOT NULL,
  source_id text NOT NULL,
  target_id text NOT NULL,
  kind text NOT NULL CHECK (kind IN ('capability','named-supply','partnership','competition','demand-feedback','segment-supply','segment-feedback','legacy-candidate')),
  direction text NOT NULL CHECK (direction IN ('directed','symmetric')),
  mechanism text NOT NULL,
  conditions jsonb NOT NULL,
  confidence text NOT NULL CHECK (confidence IN ('well-supported','inference','needs-verification')),
  reviewed date,
  product_id text,
  application_id text,
  data jsonb NOT NULL,
  PRIMARY KEY (release_id,relation_id),
  FOREIGN KEY (release_id,source_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,target_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,product_id) REFERENCES research.entity_snapshots,
  FOREIGN KEY (release_id,application_id) REFERENCES research.entity_snapshots,
  CHECK (direction<>'symmetric' OR (kind IN ('partnership','competition') AND source_id<target_id))
);
CREATE INDEX ix_research_relation_source ON research.relations(release_id,source_id,kind);
CREATE INDEX ix_research_relation_target ON research.relations(release_id,target_id,kind);
CREATE TABLE research.relation_claims (
  release_id uuid NOT NULL,
  relation_id text NOT NULL,
  entity_id text NOT NULL,
  claim_id text NOT NULL,
  PRIMARY KEY (release_id,relation_id,entity_id,claim_id),
  FOREIGN KEY (release_id,relation_id) REFERENCES research.relations,
  FOREIGN KEY (release_id,entity_id,claim_id) REFERENCES research.research_claims
);
CREATE TABLE research.legacy_history (
  release_id uuid NOT NULL,
  entity_id text NOT NULL,
  history_kind text NOT NULL,
  legacy_id text NOT NULL,
  content_hash text NOT NULL,
  data jsonb NOT NULL,
  PRIMARY KEY (release_id,history_kind,legacy_id),
  FOREIGN KEY (release_id,entity_id) REFERENCES research.entity_snapshots
);

CREATE TABLE research.financial_metric_definitions (
  metric_id text PRIMARY KEY,
  label text NOT NULL,
  unit text NOT NULL,
  definition jsonb NOT NULL,
  formula_version text
);
CREATE TABLE research.financial_groups (
  group_id text PRIMARY KEY CHECK (group_id ~ '^[0-9a-f]{64}$'),
  company_id text NOT NULL REFERENCES research.entities CHECK (company_id LIKE 'company-%'),
  source_family text NOT NULL,
  metric_id text NOT NULL REFERENCES research.financial_metric_definitions,
  period_start date NOT NULL,
  period_end date NOT NULL,
  basis text NOT NULL CHECK (basis IN ('monthly','quarterly','ytd','annual','instant')),
  scope text NOT NULL,
  unit text NOT NULL,
  currency text NOT NULL DEFAULT '',
  share_class text NOT NULL DEFAULT '',
  CHECK (period_end>=period_start),
  UNIQUE (company_id,source_family,metric_id,period_start,period_end,basis,scope,unit,currency,share_class)
);
CREATE INDEX ix_research_financial_period ON research.financial_groups(company_id,metric_id,period_end DESC);
CREATE TABLE research.financial_raw_facts (
  fact_id uuid PRIMARY KEY,
  company_id text NOT NULL REFERENCES research.entities,
  source_family text NOT NULL,
  accession text NOT NULL,
  tag text NOT NULL,
  context_hash text NOT NULL,
  value numeric(38,10),
  filed_at date,
  source_url text NOT NULL,
  payload jsonb NOT NULL,
  UNIQUE (company_id,source_family,accession,tag,context_hash)
);
CREATE TABLE research.financial_observations (
  observation_id uuid PRIMARY KEY,
  group_id text NOT NULL REFERENCES research.financial_groups,
  revision integer NOT NULL CHECK (revision>0),
  value numeric(38,10) NOT NULL,
  semantic_hash text NOT NULL,
  filed_at date,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  supersedes uuid REFERENCES research.financial_observations,
  provenance_kind text NOT NULL CHECK (provenance_kind IN ('official','manual-official','derived','legacy-import')),
  limitations text NOT NULL,
  UNIQUE (group_id,revision)
);
CREATE INDEX ix_research_observation_latest ON research.financial_observations(group_id,revision DESC);
CREATE TABLE research.observation_provenance (
  observation_id uuid NOT NULL REFERENCES research.financial_observations,
  fact_id uuid NOT NULL REFERENCES research.financial_raw_facts,
  PRIMARY KEY (observation_id,fact_id)
);
CREATE TABLE research.financial_derivations (
  observation_id uuid NOT NULL REFERENCES research.financial_observations,
  input_id uuid NOT NULL REFERENCES research.financial_observations,
  formula_version text NOT NULL,
  ordinal integer NOT NULL,
  PRIMARY KEY (observation_id,ordinal),
  CHECK (observation_id<>input_id)
);
CREATE TABLE research.financial_import_batches (
  batch_id uuid PRIMARY KEY,
  payload_hash text NOT NULL UNIQUE,
  payload jsonb NOT NULL,
  status text NOT NULL CHECK (status IN ('preview','confirmed','rejected')),
  created_at timestamptz NOT NULL DEFAULT now(),
  confirmed_at timestamptz,
  confirmed_by text,
  CHECK (status<>'confirmed' OR (confirmed_at IS NOT NULL AND confirmed_by IS NOT NULL))
);
CREATE TABLE research.event_entity_links (
  event_id integer NOT NULL REFERENCES public.events,
  entity_id text NOT NULL REFERENCES research.entities,
  relevance text NOT NULL CHECK (relevance IN ('direct','background','mention')),
  source_nature text NOT NULL CHECK (source_nature IN ('official','report','rumor')),
  PRIMARY KEY (event_id,entity_id,relevance)
);
CREATE INDEX ix_research_event_entity ON research.event_entity_links(entity_id,event_id DESC);
CREATE TABLE research.source_capabilities (
  release_id uuid NOT NULL,
  source_id text NOT NULL,
  metric_id text NOT NULL,
  capability jsonb NOT NULL,
  PRIMARY KEY (release_id,source_id,metric_id),
  FOREIGN KEY (release_id,source_id) REFERENCES research.release_sources
);

CREATE TABLE research.editor_drafts (
  draft_id uuid PRIMARY KEY,
  base_release_id uuid REFERENCES research.research_releases,
  current_revision integer NOT NULL CHECK (current_revision>0),
  status text NOT NULL CHECK (status IN ('editing','published','abandoned')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE research.draft_revisions (
  draft_id uuid NOT NULL REFERENCES research.editor_drafts,
  revision integer NOT NULL CHECK (revision>0),
  origin text NOT NULL CHECK (origin IN ('web','cli')),
  payload jsonb NOT NULL,
  payload_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (draft_id,revision)
);
ALTER TABLE research.editor_drafts ADD CONSTRAINT fk_research_current_revision
  FOREIGN KEY (draft_id,current_revision) REFERENCES research.draft_revisions DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE research.publish_jobs (
  job_id uuid PRIMARY KEY,
  draft_id uuid,
  draft_revision integer,
  operation text NOT NULL CHECK (operation IN ('publish','restore','sync-ref')),
  base_release_id uuid REFERENCES research.research_releases,
  target_release_id uuid REFERENCES research.research_releases,
  idempotency_key text NOT NULL UNIQUE,
  payload_hash text NOT NULL,
  status text NOT NULL CHECK (status IN ('queued','preparing','ready','published','failed')),
  stage text NOT NULL,
  attempts integer NOT NULL DEFAULT 0,
  available_at timestamptz NOT NULL DEFAULT now(),
  lease_until timestamptz,
  prefect_run_id uuid,
  failure jsonb,
  reason text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (draft_id,draft_revision) REFERENCES research.draft_revisions,
  CHECK ((draft_id IS NULL)=(draft_revision IS NULL))
);
CREATE INDEX ix_research_jobs_due ON research.publish_jobs(status,available_at,lease_until);
CREATE TABLE research.audit_log (
  audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  actor text NOT NULL,
  operation text NOT NULL,
  job_id uuid REFERENCES research.publish_jobs,
  release_id uuid REFERENCES research.research_releases,
  detail jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE research.admin_owner (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  password_hash text NOT NULL,
  credential_version integer NOT NULL CHECK (credential_version>0),
  changed_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE research.admin_sessions (
  token_hash text PRIMARY KEY CHECK (token_hash ~ '^[0-9a-f]{64}$'),
  csrf_hash text NOT NULL,
  credential_version integer NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL,
  absolute_expires_at timestamptz NOT NULL,
  revoked_at timestamptz
);
CREATE INDEX ix_research_sessions_expiry ON research.admin_sessions(absolute_expires_at);
CREATE TABLE research.login_attempts (
  bucket_hash text PRIMARY KEY,
  attempts integer NOT NULL,
  window_start timestamptz NOT NULL,
  blocked_until timestamptz
);

-- Writer is an application role, never schema owner or superuser.
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA research TO research_writer;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA research TO research_writer;
-- Reader receives no grant for drafts, sessions, audit, jobs, imports or raw payloads.
GRANT SELECT ON research.entities, research.release_head, research.financial_metric_definitions,
  research.financial_groups, research.financial_observations, research.financial_derivations,
  research.observation_provenance, research.event_entity_links TO research_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO research_reader;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO research_writer;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO research_writer;
ALTER ROLE research_reader_login SET default_transaction_read_only=on;
DO $$ DECLARE t text; BEGIN
  FOREACH t IN ARRAY ARRAY['research_releases','entity_snapshots','entity_aliases','listings','source_identifiers',
    'legacy_mappings','release_sources','release_documents','release_assets','research_claims','claim_evidence',
    'taxonomy_links','company_offerings','offering_claims','relations','relation_claims','legacy_history','source_capabilities'] LOOP
    EXECUTE format('ALTER TABLE research.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('GRANT SELECT ON research.%I TO research_reader', t);
    EXECUTE format('CREATE POLICY writer_all ON research.%I TO research_writer USING (true) WITH CHECK (true)', t);
    IF t='research_releases' THEN
      EXECUTE 'CREATE POLICY reader_published ON research.research_releases FOR SELECT TO research_reader USING (status=''published'')';
    ELSE
      EXECUTE format('CREATE POLICY reader_published ON research.%I FOR SELECT TO research_reader USING (release_id IN (SELECT release_id FROM research.research_releases WHERE status=''published''))',t);
    END IF;
  END LOOP;
END $$;
-- Immutable document/asset bodies are visible only when a published release cites them.
ALTER TABLE research.document_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE research.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE research.assets ENABLE ROW LEVEL SECURITY;
GRANT SELECT ON research.document_revisions,research.documents,research.assets TO research_reader;
CREATE POLICY writer_all ON research.document_revisions TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY writer_all ON research.documents TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY writer_all ON research.assets TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.document_revisions FOR SELECT TO research_reader
  USING (revision_id IN (SELECT revision_id FROM research.release_documents));
CREATE POLICY reader_published ON research.documents FOR SELECT TO research_reader
  USING (document_id IN (SELECT document_id FROM research.document_revisions));
CREATE POLICY reader_published ON research.assets FOR SELECT TO research_reader
  USING (sha256 IN (SELECT sha256 FROM research.release_assets));

ALTER TABLE research.entities ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.entities TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.entities FOR SELECT TO research_reader
  USING (entity_id IN (SELECT entity_id FROM research.entity_snapshots));

CREATE FUNCTION research.require_published_head() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM research.research_releases WHERE release_id=NEW.release_id AND status='published') THEN
    RAISE EXCEPTION 'release head requires published release' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER require_published_head AFTER INSERT OR UPDATE ON research.release_head
  DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research.require_published_head();

CREATE FUNCTION research.guard_published_snapshot() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE old_release uuid; new_release uuid;
BEGIN
  IF TG_OP<>'INSERT' THEN old_release:=OLD.release_id; END IF;
  IF TG_OP<>'DELETE' THEN new_release:=NEW.release_id; END IF;
  IF EXISTS (SELECT 1 FROM research.research_releases WHERE release_id IN (old_release,new_release) AND status='published') THEN
    RAISE EXCEPTION 'published research is immutable' USING ERRCODE='23514';
  END IF;
  IF TG_OP='DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
  FOREACH t IN ARRAY ARRAY['entity_snapshots','entity_aliases','listings','source_identifiers','legacy_mappings',
    'release_sources','release_documents','release_assets','research_claims','claim_evidence','taxonomy_links',
    'company_offerings','offering_claims','relations','relation_claims','legacy_history','source_capabilities'] LOOP
    EXECUTE format('CREATE TRIGGER immutable_published BEFORE INSERT OR UPDATE OR DELETE ON research.%I FOR EACH ROW EXECUTE FUNCTION research.guard_published_snapshot()',t);
  END LOOP;
END $$;
