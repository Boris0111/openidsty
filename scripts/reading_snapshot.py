"""Run inside the isolated API container, not against the application DB.

docker cp scripts/reading_snapshot.py industryflow-reading-api:/tmp/reading_snapshot.py
docker exec industryflow-reading-api python /tmp/reading_snapshot.py --reference 2026-10-15T16:00:00+00:00
"""
import argparse
import hashlib
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path.cwd()))
from sqlalchemy import event, func, select, text
from app.db import Session, engine
from app import models
from app.research_api import coverage
from app.theme_updates import updates_payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True)
    args = parser.parse_args()
    reference = datetime.fromisoformat(args.reference)
    class ReferenceDate(date):
        @classmethod
        def today(cls):
            return reference.date()
    statements = []
    @event.listens_for(engine, 'before_cursor_execute')
    def before(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    result = {'reference': reference.isoformat(), 'counts': {}, 'fingerprints': {}, 'queries': {}}
    with Session() as session, patch('app.assessments.now', lambda: reference), patch('app.indicator_api.date', ReferenceDate):
        session.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        for table in models.Base.metadata.sorted_tables:
            result['counts'][table.name] = session.scalar(select(func.count()).select_from(table))
        for model in (models.Event, models.Financial, models.IndicatorObservation, models.ThemeAssessmentVersion):
            rows = [dict(row) for row in session.execute(select(model.__table__).order_by(*model.__table__.primary_key.columns)).mappings()]
            result['fingerprints'][model.__tablename__] = hashlib.sha256(json.dumps(rows, default=str, sort_keys=True).encode()).hexdigest()
        result['segments'] = [{'id':s.id,'name':s.name} for s in session.scalars(select(models.Segment).order_by(models.Segment.id))]
        result['themes'] = [{'id':t.id,'name':t.data['name_zh']} for t in session.scalars(select(models.Theme).where(models.Theme.active.is_(True)).order_by(models.Theme.id))]
        for name, read in [('coverage', lambda:coverage(session, reference)), ('updates', lambda:updates_payload(session,[t['id'] for t in result['themes']]))]:
            start_queries = len(statements)
            started = time.perf_counter()
            result[name] = read()
            result['queries'][name] = {'sql_count':len(statements)-start_queries,'ms':(time.perf_counter()-started)*1000}
    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
