"""A real child worker dies without cleanup; another process resumes the DB job."""
import os
import subprocess
import sys
from sqlalchemy import text
from app import research_publication as publication
from test_research_auth import owner
from test_research_documents import authored
from test_research_drafts import draft_context
from test_research_publication import publishing


def test_worker_process_exit_and_fresh_process_resume(publishing):
    _, engine, base, _, _, _, key = publishing
    environment = dict(os.environ)
    assert engine.url.database == 'industry_research_test'
    environment['RESEARCH_WRITE_DATABASE_URL'] = engine.url.render_as_string(hide_password=False)
    crash = '''import os,sys
from app.research_publication import run_job
def interrupt(stage):
    if stage == 'projection':
        os._exit(77)
run_job(sys.argv[1], inject=interrupt)
'''
    child = subprocess.run([sys.executable, '-c', crash, key], env=environment, capture_output=True, timeout=120)
    assert child.returncode == 77, 'The synthetic worker must exit at its committed projection checkpoint'
    with engine.connect() as connection:
        assert publication.job(connection, key)['status'] == 'ready'
        assert str(publication.active(connection)['release_id']) == base
    resume = '''import sys
from app.research_publication import run_job
assert run_job(sys.argv[1])['status']=='published'
'''
    restarted = subprocess.run([sys.executable, '-c', resume, key], env=environment, capture_output=True, timeout=120)
    assert restarted.returncode == 0, 'A fresh worker process must resume the existing protected commit and DB job'
    with engine.connect() as connection:
        assert publication.job(connection, key)['status'] == 'published'
        assert str(publication.active(connection)['release_id']) != base
        assert connection.execute(text("SELECT count(*) FROM research.audit_log WHERE job_id=:id AND operation='publish'"), {'id':key}).scalar_one() == 1
