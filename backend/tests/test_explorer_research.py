from pathlib import Path
from sqlalchemy import select, func
from app.models import Theme, Segment
from app.import_map import read_doc
from app.config import MAP_DIR

def test_research_projection_preserves_full_text_and_baseline(db):
    assert db.scalar(select(func.count()).select_from(Segment)) == 17
    assert db.scalar(select(func.count()).select_from(Theme)) == 7
    for theme in db.scalars(select(Theme)):
        _, prose = read_doc(MAP_DIR / 'themes' / f'{theme.id}.md')
        assert theme.prose == prose
        assert theme.checked == '2026-10-07'
        assert 'https://' in theme.prose

def test_migration_keeps_existing_event(tmp_path):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, text
    from app.config import ROOT
    cfg = Config(str(ROOT / 'backend/alembic.ini'))
    url = f'sqlite:///{tmp_path.as_posix()}/legacy.db'
    cfg.attributes['database_url'] = url
    command.upgrade(cfg, '0001')
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO companies VALUES ('NVDA','輝達','[]',NULL)"))
        conn.execute(text("INSERT INTO sources (id,name,url,status,new_count,data) VALUES ('legacy','legacy','https://example.org','success',1,'{}')"))
        conn.execute(text("INSERT INTO events (id,source_id,external_id,ticker,title,body,kind,lifecycle,published_at,fetched_at,url,mentioned,raw) VALUES (1,'legacy','1','NVDA','原事件','保留','announcement','published','2026-10-07','2026-10-08','https://example.org','[]','{}')"))
    # PostgreSQL-only research migration has a separate isolated DB check.
    command.upgrade(cfg, '0006')
    with engine.connect() as conn:
        assert conn.execute(text('SELECT title FROM events WHERE id=1')).scalar() == '原事件'
        assert conn.execute(text('SELECT COUNT(*) FROM companies')).scalar() == 1
