"""File editing, owner HTTP retry/restore, and the real read-only role agree."""
import os
import re
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.main import app
from app.research_db import get_research_session
from app.research_cli import export_directory, import_directory
from app import research_publication as publication
from app.research_git import ManagedGit
from test_research_auth import owner
from test_research_documents import authored
from test_research_drafts import draft_context
from test_research_publication import publishing


def test_file_import_publish_http_retry_restore_and_real_reader(publishing, tmp_path, monkeypatch):
    client, engine, base, headers, url, _, _ = publishing
    reader = create_engine(os.environ['RESEARCH_PG_READER_URL'], hide_parameters=True)
    assert reader.url.database=='industry_research_test' and reader.url.username=='research_reader_login'
    def read_only():
        with Session(reader) as session:
            session.execute(text('SET TRANSACTION READ ONLY'))
            yield session
    app.dependency_overrides[get_research_session]=read_only
    try:
        previous=client.get('/api/v2/companies/company-auras').json()['data']['summary']
        profile='/api/v2/companies/company-auras'
        pinned=client.get(profile,params={'release_id':base})
        directory=tmp_path/'file-edit'
        exported=client.get(url+'/export').json()
        export_directory(exported,directory)
        path=directory/'industry-map/companies/company-auras.md'
        content=re.sub(br'^summary:.*$', 'summary: 合成檔案發布介面測試'.encode(), path.read_bytes(), flags=re.M)
        path.write_bytes(content)
        imported=import_directory(directory)
        saved=client.post(url+'/import',json=imported,headers={**headers,'If-Match':'"2"'})
        assert saved.status_code==200 and saved.json()['revision']==3
        with engine.connect() as connection:
            assert connection.execute(text('SELECT origin FROM research.draft_revisions WHERE draft_id=:id AND revision=3'),{'id':exported['draft_id']}).scalar_one()=='cli'
        preview=client.get(url+'/preview?entity_id=company-auras&revision=3').json()
        assert preview['data']['summary']=='合成檔案發布介面測試'
        assert client.get('/api/v2/companies/company-auras').json()['data']['summary']==previous
        response=client.post(url+'/publish',json={'base_release_id':base,'revision':3,'reason':'Synthetic file-interface publication'},headers={**headers,'Idempotency-Key':uuid.uuid4().hex})
        assert response.status_code==202
        key=response.json()['job_id']
        with monkeypatch.context() as patch:
            def storage_failure(*args,**kwargs):
                raise OSError('Synthetic recoverable storage outage')
            patch.setattr(ManagedGit,'prepare_job',storage_failure)
            import pytest
            with pytest.raises(OSError):
                publication.run_job(key,engine)
        assert client.post('/api/admin/jobs/'+key+'/retry',headers=headers).status_code==202
        published=publication.run_job(key,engine)
        assert published['status']=='published'
        assert client.get('/api/v2/companies/company-auras').json()['data']['summary']==preview['data']['summary']
        assert client.get(profile,params={'release_id':base},headers={'If-None-Match':pinned.headers['etag']}).status_code==304
        new_profile=client.get(profile,params={'release_id':str(published['target_release_id'])})
        assert new_profile.headers['etag']!=pinned.headers['etag']
        assert client.get('/api/v2/manifest').json()['release_id']==str(published['target_release_id'])
        restored=client.post('/api/admin/releases/'+base+'/restore',json={'base_release_id':str(published['target_release_id']),'reason':'Synthetic file-interface restoration'},headers={**headers,'Idempotency-Key':uuid.uuid4().hex})
        assert restored.status_code==202
        assert publication.run_job(restored.json()['job_id'],engine)['status']=='published'
        assert client.get('/api/v2/companies/company-auras').json()['data']['summary']==previous
        assert client.get(profile,params={'release_id':str(published['target_release_id'])},headers={'If-None-Match':new_profile.headers['etag']}).status_code==304
        assert client.get(profile,params={'release_id':base},headers={'If-None-Match':pinned.headers['etag']}).status_code==304
        client.cookies.clear()
        assert client.get('/api/admin/jobs/'+key).status_code==401
        assert client.get('/api/admin/sources').status_code==401
    finally:
        app.dependency_overrides.pop(get_research_session,None)
        reader.dispose()
