from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import ROOT
from app.models import Indicator, IndicatorObservation


def test_0003_preserves_legacy_rows_and_decimal_metadata(tmp_path):
    cfg=Config(str(ROOT/'backend/alembic.ini'))
    url=f'sqlite:///{tmp_path.as_posix()}/indicators.db';cfg.attributes['database_url']=url
    command.upgrade(cfg,'0002')
    engine=create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO companies VALUES ('NVDA','輝達','[]',NULL)"))
        conn.execute(text("INSERT INTO themes (id,data,prose,checked) VALUES ('legacy','{}','保留研究','2026-10-07')"))
        conn.execute(text("INSERT INTO sources (id,name,url,status,new_count,data) VALUES ('legacy','來源','https://example.org','success',0,'{}')"))
        conn.execute(text("INSERT INTO events (id,source_id,external_id,title,body,kind,lifecycle,fetched_at,url,mentioned,raw) VALUES (1,'legacy','1','保留事件','摘錄','industry_news','published','2026-10-07','https://example.org','[]','{}')"))
        conn.execute(text("INSERT INTO financials (id,ticker,source_id,period,period_end,basis,currency,revenue,published_at,fetched_at,url,raw) VALUES (1,'NVDA','legacy','2026-Q2','2026-06-30','quarterly','USD',123,'2026-07-29','2026-07-29','https://example.org','{}')"))
    command.upgrade(cfg,'0003')
    with Session(engine) as session:
        session.add(Indicator(id='sample',name='測試指標',kind='proxy',unit='amount',frequency='quarterly',basis='quarterly',data={}))
        session.flush()
        session.add(IndicatorObservation(indicator_id='sample',source_id='legacy',identity='a'*64,document_identity='report',dataset='sample',entity='NVDA',original_period='FY2026 Q2',period_start=date(2026,4,1),period_end=date(2026,6,30),basis='quarterly',scope='公司整體',unit='amount',currency='USD',value=Decimal('123.45678901'),published_at=None,reported_at=datetime(2026,7,29,tzinfo=timezone.utc),url='https://example.org',raw_excerpt='原始數值',raw={},revision=1,content_hash='b'*64))
        session.commit()
        row=session.query(IndicatorObservation).one()
        assert row.value==Decimal('123.45678901') and row.published_at is None
        assert row.original_period=='FY2026 Q2' and row.period_end==date(2026,6,30)
        assert row.reported_at is not None and row.valid
    with engine.connect() as conn:
        assert conn.execute(text('SELECT title FROM events')).scalar()=='保留事件'
        assert conn.execute(text('SELECT revenue FROM financials')).scalar()==123
        assert conn.execute(text('SELECT prose FROM themes')).scalar()=='保留研究'
        assert conn.execute(text('SELECT count(*) FROM companies')).scalar()==1
    engine.dispose()
