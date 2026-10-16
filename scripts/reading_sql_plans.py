"""Read-only PostgreSQL plans against the fixed comparison snapshot."""
import json
from sqlalchemy import text
from app.db import engine

queries={
 'coverage-theme':"SELECT theme_id,count(DISTINCT e.id) FROM event_themes l JOIN events e ON e.id=l.event_id WHERE l.relevance='direct' AND NOT e.routine AND e.lifecycle='published' AND e.published_at BETWEEN '2026-07-17T16:00:00Z' AND '2026-10-15T16:00:00Z' GROUP BY theme_id",
 'assessment-candidates':"SELECT count(*) FROM event_themes l JOIN events e ON e.id=l.event_id WHERE l.theme_id='liquid-cooling' AND l.relevance='direct' AND NOT e.routine AND e.lifecycle='published' AND e.published_at BETWEEN '2026-10-07T16:00:00Z' AND '2026-10-15T16:00:00Z'",
 'latest-indicator':"SELECT id FROM (SELECT id,row_number() OVER(PARTITION BY identity ORDER BY revision DESC,id DESC) r FROM indicator_observations WHERE indicator_id='aaon-liquid-cooling-revenue') ranked WHERE r=1 LIMIT 12",
 'coverage-samples':"SELECT * FROM (SELECT segment_id,e.id,row_number() OVER(PARTITION BY segment_id ORDER BY published_at DESC,e.id) r FROM event_segments l JOIN events e ON e.id=l.event_id WHERE relevance='direct' AND NOT routine AND lifecycle='published' AND published_at BETWEEN '2026-07-17T16:00:00Z' AND '2026-10-15T16:00:00Z') ranked WHERE r<=3"
}
with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
    connection.execute(text('SET TRANSACTION READ ONLY'))
    result={name:connection.execute(text('EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) '+query)).scalar() for name,query in queries.items()}
print(json.dumps(result,ensure_ascii=False,default=str))
