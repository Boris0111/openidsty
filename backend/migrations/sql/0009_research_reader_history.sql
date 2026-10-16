-- Maintenance observations/reviews remain preserved but are not reader content.
DROP POLICY reader_published ON research.legacy_history;
CREATE POLICY reader_published ON research.legacy_history FOR SELECT TO research_reader
  USING (history_kind IN ('assessment','indicator-definition','indicator-observation')
    AND release_id IN (SELECT release_id FROM research.research_releases WHERE status='published'));
