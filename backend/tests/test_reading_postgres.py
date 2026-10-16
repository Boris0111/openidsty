"""Run explicitly against the disposable empty lab DB, never the app DB."""
import os
from datetime import datetime,timezone
import pytest
from sqlalchemy import create_engine,select,delete,text
from sqlalchemy.orm import Session
from app.models import Event,EventSegment,EventTheme,TechnicalDocument,ThemeAssessmentVersion
from app.research_api import coverage
from app.import_map import import_map

@pytest.fixture
def pg_engine():
    url=os.environ.get('READING_PG_TEST_URL')
    if not url:pytest.skip('explicit disposable PostgreSQL URL required')
    engine=create_engine(url)
    if engine.url.database!='industry_empty_reading':raise RuntimeError('Only the disposable industry_empty_reading DB is allowed')
    yield engine
    engine.dispose()

def test_empty_migrated_pg_reimport_preserves_document_and_assessment_baselines(pg_engine):
    with Session(pg_engine) as session:
        before=session.scalars(select(ThemeAssessmentVersion.id)).all();docs=session.scalars(select(TechnicalDocument.id)).all()
        assert len(before)==7 and len(docs)==8
        import_map(session);import_map(session)
        assert session.scalars(select(ThemeAssessmentVersion.id)).all()==before
        assert session.scalars(select(TechnicalDocument.id)).all()==docs

def test_repeatable_read_counts_and_samples_do_not_mix_concurrent_commits(pg_engine):
    ids=[]
    try:
        with Session(pg_engine) as writer:
            def add(key):
                event=Event(source_id='oif-technical',external_id=key,title='隔離 SQL 一致性測試',body='test only',kind='industry_news',lifecycle='published',published_at=datetime.now(timezone.utc),url='https://www.oiforum.com/',mentioned=['VRT','VRT'],raw={})
                writer.add(event);writer.flush();ids.append(event.id)
                writer.add(EventTheme(event_id=event.id,theme_id='liquid-cooling',relevance='direct',evidence=[]));writer.add(EventSegment(event_id=event.id,segment_id='thermal',relevance='direct',evidence=[]));writer.commit()
            add('reading-snapshot-first')
            with pg_engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
                with Session(connection) as reader:
                    reader.execute(text('SET TRANSACTION READ ONLY'))
                    before=coverage(reader);add('reading-snapshot-second');after=coverage(reader)
                    for payload in (before,after):
                        row=next(r for r in payload['rows'] if r['id']=='thermal');assert row['direct_90d']==1 and len(row['samples'])==1 and row['company_mentions_90d']==1
            with Session(pg_engine) as reader:
                row=next(r for r in coverage(reader)['rows'] if r['id']=='thermal');assert row['direct_90d']==2 and len(row['samples'])==2 and row['company_mentions_90d']==2
    finally:
        with Session(pg_engine) as cleanup:
            for model in (EventTheme,EventSegment):cleanup.execute(delete(model).where(model.event_id.in_(ids)))
            cleanup.execute(delete(Event).where(Event.id.in_(ids)));cleanup.commit()
