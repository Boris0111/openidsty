import copy,shutil
from datetime import datetime,timezone
import pytest,yaml
from sqlalchemy import select,func,text,create_engine
from alembic import command
from alembic.config import Config
from app.config import MAP_DIR,ROOT
from app.models import Theme,ThemeAssessmentVersion
from app.import_map import import_map,read_doc
from app.assessment_versions import prepare_version,latest_version,diff_values


def test_semantics_baseline_revision_restore_and_reason(db):
    t=db.get(Theme,'liquid-cooling');baseline=latest_version(db,t.id)
    assert baseline.version_number==1 and baseline.reviewed=='2026-10-07'
    assert prepare_version(db,t.id,t.data,t.checked) is None
    shuffled=copy.deepcopy(t.data);shuffled['assessment']['evidence'].reverse();shuffled['assessment']['conditions'].reverse();shuffled['assessment']['change_reason']='只調整排版'
    assert prepare_version(db,t.id,shuffled,t.checked) is None
    changed=copy.deepcopy(t.data);changed['assessment']['summary']='新的有條件結論';changed['assessment']['change_reason']='新證據'
    version=prepare_version(db,t.id,changed,t.checked);db.add(version);db.commit()
    assert version.version_number==2 and version.payload['assessment']['summary']!='只調整排版'
    original=copy.deepcopy(t.data);original['assessment']['change_reason']='核對後還原'
    restore=prepare_version(db,t.id,original,t.checked);db.add(restore);db.commit()
    assert restore.version_number==3 and restore.content_hash==baseline.content_hash
    changed['assessment']['change_reason']=' '
    with pytest.raises(ValueError,match='change_reason'):prepare_version(db,t.id,changed,t.checked)


def test_invalid_import_is_atomic_and_retirement_keeps_history(db,tmp_path,client):
    root=tmp_path/'map';shutil.copytree(MAP_DIR,root)
    file=root/'themes/liquid-cooling.md';data,prose=read_doc(file)
    data['assessment']['summary']='修改結論';data['assessment']['change_reason']=''
    file.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True)+'---\n'+prose,encoding='utf-8')
    before=db.scalar(select(func.count()).select_from(ThemeAssessmentVersion))
    with pytest.raises(ValueError):import_map(db,root)
    assert db.scalar(select(func.count()).select_from(ThemeAssessmentVersion))==before
    assert db.get(Theme,'liquid-cooling').data['assessment']['summary']!='修改結論'
    # Simulate retirement projection; authored files must also remove segment refs.
    t=db.get(Theme,'liquid-cooling');t.active=False;db.commit()
    for path in ('','/assessment','/indicators'):assert client.get('/api/themes/liquid-cooling'+path).status_code==404
    assert not any(t['theme']=='liquid-cooling' for t in client.get('/api/themes').json())
    assert latest_version(db,t.id) is not None
    assert all(r['id']!='liquid-cooling' for r in client.get('/api/coverage').json()['rows'])


def test_diff_stable_ids_all_authored_fields(db):
    old=latest_version(db,'liquid-cooling').payload;new=copy.deepcopy(old)
    new['assessment']['summary']='改結論';new['status']='scaling';new['assessment']['confidence']='well-supported'
    new['assessment']['claims'][0]['statement']='改論點'
    new['assessment']['evidence'][0]['excerpt']='改摘錄'
    new['assessment']['conditions'].append('新條件');new['assessment']['gaps']=[]
    new['assessment']['milestone_reviews'][0]['state']='confirmed'
    diff=diff_values(old,new)
    assert any('claims[' in d['path'] for d in diff) and any('evidence[' in d['path'] for d in diff)
    assert any(d['path']=='assessment.conditions' and d['kind']=='added' for d in diff)
    assert any(d['path']=='assessment.gaps' and d['kind']=='removed' for d in diff)
    assert any('milestone_reviews[' in d['path'] for d in diff)


def test_0004_additive_preserves_old_theme_and_observation_tables(tmp_path):
    cfg=Config(str(ROOT/'backend/alembic.ini'));url=f'sqlite:///{tmp_path.as_posix()}/versions.db';cfg.attributes['database_url']=url
    command.upgrade(cfg,'0003');engine=create_engine(url)
    with engine.begin() as conn:conn.execute(text("INSERT INTO themes (id,data,prose,checked) VALUES ('old','{}','歷史','2026-10-07')"))
    command.upgrade(cfg,'0004')
    with engine.connect() as conn:
        row=conn.execute(text('SELECT prose,active FROM themes')).one()
        assert row.prose=='歷史' and row.active
        assert conn.execute(text('SELECT count(*) FROM indicator_observations')).scalar()==0
        assert conn.execute(text('SELECT count(*) FROM theme_assessment_versions')).scalar()==0
