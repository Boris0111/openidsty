-- Published versions and content-addressed bodies cannot be rewritten by the writer.
CREATE FUNCTION research.guard_immutable_row() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'immutable research row; create a new version' USING ERRCODE='23514';
END $$;
CREATE TRIGGER immutable_revision BEFORE UPDATE OR DELETE ON research.document_revisions
  FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row();
CREATE TRIGGER immutable_asset BEFORE UPDATE OR DELETE ON research.assets
  FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row();
CREATE TRIGGER immutable_entity BEFORE UPDATE OR DELETE ON research.entities
  FOR EACH ROW EXECUTE FUNCTION research.guard_immutable_row();
CREATE FUNCTION research.guard_published_release() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.status='published' THEN
    RAISE EXCEPTION 'published release is immutable' USING ERRCODE='23514';
  END IF;
  IF TG_OP='DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER immutable_release BEFORE UPDATE OR DELETE ON research.research_releases
  FOR EACH ROW EXECUTE FUNCTION research.guard_published_release();

ALTER TABLE research.financial_groups ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.financial_groups TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.financial_groups FOR SELECT TO research_reader
  USING (company_id IN (SELECT entity_id FROM research.entities));
ALTER TABLE research.financial_observations ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.financial_observations TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.financial_observations FOR SELECT TO research_reader
  USING (group_id IN (SELECT group_id FROM research.financial_groups));
ALTER TABLE research.financial_derivations ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.financial_derivations TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.financial_derivations FOR SELECT TO research_reader
  USING (observation_id IN (SELECT observation_id FROM research.financial_observations));
ALTER TABLE research.observation_provenance ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.observation_provenance TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.observation_provenance FOR SELECT TO research_reader
  USING (observation_id IN (SELECT observation_id FROM research.financial_observations));
ALTER TABLE research.event_entity_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY writer_all ON research.event_entity_links TO research_writer USING (true) WITH CHECK (true);
CREATE POLICY reader_published ON research.event_entity_links FOR SELECT TO research_reader
  USING (entity_id IN (SELECT entity_id FROM research.entities));
