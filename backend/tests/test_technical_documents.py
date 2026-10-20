import copy
from pathlib import Path
import shutil
import httpx
import pytest
import yaml
from sqlalchemy import select,func
from app.models import TechnicalDocument,TechnicalObservation,TechnicalReview,Theme,ThemeAssessmentVersion,Source
from app.import_map import import_map
from app.config import MAP_DIR
from app.ingest import register_sources
from app.technical_monitor import extract_body,normalize_text,save_checked,ingest_documents,fetch_bounded,PARSER_VERSION,document_links
from app.technical_documents import import_documents
from app.theme_updates import updates_payload

def html(version='5.4',suffix='',nav='Home'):
    # Reduced test reconstruction of the official CMIS scope, not a distributed full document.
    return f'<html><title>CMIS</title><nav>{nav}</nav><main><h1>CMIS Version {version}</h1><p>Management interaction protocol. Optional functions are advertised by modules. This synthetic fixture preserves the public scope distinction and adds test-only explanatory text. {suffix}</p></main><footer>Retrieved today</footer></html>'.encode()

def pdf_fixture(text,title='test'):
    from pypdf import PdfWriter
    from pypdf.generic import NameObject,DictionaryObject,DecodedStreamObject
    import io
    writer=PdfWriter();page=writer.add_blank_page(600,800)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
    stream=DecodedStreamObject();stream.set_data(f'BT /F1 12 Tf 30 700 Td ({text}) Tj ET'.encode());page[NameObject('/Contents')]=writer._add_object(stream)
    writer.add_metadata({'/Title':title});output=io.BytesIO();writer.write(output);return output.getvalue()

def test_read_only_document_api_bounds_and_pinned_baseline(client,db):
    result=client.get('/api/technical-documents?limit=2&offset=1').json()
    assert result['total']==8 and len(result['items'])==2 and result['offset']==1
    filtered=client.get('/api/technical-documents?theme=cpo-silicon-photonics').json()
    assert any(d['id']=='oif-cmis' for d in filtered['items'])
    assert client.get('/api/technical-documents?segment=missing').json()['total']==0
    assert client.get('/api/technical-documents?limit=51').status_code==422
    assert client.get('/api/technical-documents/missing').status_code==404
    assert client.get('/api/technical-documents/missing').headers['cache-control']=='no-store'
    d=client.get('/api/technical-documents/oif-cmis?limit=1').json()
    assert d['definition']['versions'][0]['id']=='revision-5-4'
    assert len(d['history']['items'])==1 and d['history']['items'][0]['review']['status']=='adopted'
    assert client.post('/api/technical-documents/oif-cmis',json={'status':'adopted'}).status_code==405
    assert client.get('/api/themes/liquid-cooling').headers['cache-control']=='no-store'

def test_normalization_noise_login_and_versioned_changes(db):
    doc=db.get(TechnicalDocument,'oif-cmis');before=db.scalar(select(func.count()).select_from(TechnicalObservation))
    assert save_checked(db,doc,html(),'text/html',doc.data['versions'][0]['url'])
    db.commit()
    assert not save_checked(db,doc,html(nav='Changed navigation'),'text/html',doc.data['versions'][0]['url'])
    assert save_checked(db,doc,html(suffix='A meaningful new management capability.'),'text/html',doc.data['versions'][0]['url'])
    assert save_checked(db,doc,html('5.5'),'text/html',doc.data['versions'][0]['url'])
    assert db.scalar(select(func.count()).select_from(TechnicalObservation))==before+3
    with pytest.raises(ValueError,match='登入'):extract_body(b'<html><input type="password"></html>','text/html')
    with pytest.raises(ValueError):extract_body(b'<html><nav>Empty</nav></html>','text/html')
    assert normalize_text('management\n  interaction')==normalize_text('management interaction')

def test_official_index_selects_declared_family_only_and_ignores_navigation(db):
    doc=db.get(TechnicalDocument,'oif-cmis')
    body=b'<nav>Updated today</nav><a href="/wp-content/uploads/OIF-CMIS-05.4.pdf">old</a><a href="/wp-content/uploads/OIF-CMIS-05.5.pdf">new</a><a href="/unrelated.pdf">ignore</a>'
    links=document_links(body,'https://www.oiforum.com/',doc,['www.oiforum.com'])
    assert len(links)==2 and links[0].endswith('05.5.pdf')
    assert links==document_links(body.replace(b'Updated today',b'Changed menu'),'https://www.oiforum.com/',doc,['www.oiforum.com'])

def test_pdf_metadata_and_layout_noise_are_not_body_changes():
    def pdf(title,spacing):
        return pdf_fixture(f'Management interaction protocol.{spacing}Optional functions are advertised by modules. Synthetic test scope explanation keeps the body long enough for a reliable text-layer check.',title)
    a,b=pdf('first',' '),pdf('different metadata','   ')
    assert a!=b and extract_body(a,'application/pdf')==extract_body(b,'application/pdf')

def test_parser_upgrade_and_unknown_official_label(db,monkeypatch):
    import app.technical_monitor as monitor
    doc=db.get(TechnicalDocument,'oif-document-categories')
    assert save_checked(db,doc,html(),'text/html',doc.data['versions'][0]['url']);db.commit()
    monkeypatch.setattr(monitor,'PARSER_VERSION','technical-text-v2')
    assert not save_checked(db,doc,html(),'text/html',doc.data['versions'][0]['url'])
    with pytest.raises(ValueError,match='解析器版本'):save_checked(db,doc,html(suffix='Changed substantive content'),'text/html',doc.data['versions'][0]['url'])
    row=db.scalar(select(TechnicalObservation).where(TechnicalObservation.document_id==doc.id).order_by(TechnicalObservation.id.desc()))
    assert row.official_version is None

def test_import_retains_version_identity_and_retired_history(db):
    doc=db.get(TechnicalDocument,'oif-document-categories');definition=copy.deepcopy(doc.data)
    definition['versions'][0]['url']='https://www.oiforum.com/new-document'
    with pytest.raises(ValueError,match='固定文件版本'):import_documents(db,{'documents':[definition]},[])
    db.rollback()
    import_documents(db,{'documents':[]},[]);db.commit()
    assert not db.get(TechnicalDocument,doc.id).active
    assert db.scalar(select(func.count()).select_from(TechnicalObservation).where(TechnicalObservation.document_id==doc.id))==1

def test_manual_parser_rebaseline_uses_same_bytes_without_a_new_official_version(db):
    import hashlib
    doc=db.get(TechnicalDocument,'oif-cmis');definition=copy.deepcopy(doc.data);version=definition['versions'][0]
    original_version=version['id'];version['parser-version']='technical-text-v2';version['content-hash']=hashlib.sha256(b'test normalized representation v2').hexdigest();version['normalization-note']='核對相同 raw-hash 原檔，僅更新解析基準，非官方新版。'
    import_documents(db,{'documents':[definition]},[]);db.commit()
    assert len(db.get(TechnicalDocument,doc.id).data['versions'])==1
    rows=list(db.scalars(select(TechnicalObservation).where(TechnicalObservation.document_id==doc.id)))
    assert len(rows)==2 and len({r.official_version for r in rows})==1
    assert all(db.scalar(select(TechnicalReview).where(TechnicalReview.observation_id==r.id)).status=='adopted' for r in rows)

def test_monitor_isolation_due_limits_failure_and_tokens(db):
    defs=register_sources(db);d=next(d for d in defs if d['id']=='oif-technical')
    before=updates_payload(db,['cpo-silicon-photonics'])
    def response(request):
        if 'CMIS' in str(request.url):return httpx.Response(403,request=request)
        if request.url.path.endswith('.pdf'):return httpx.Response(200,content=pdf_fixture('OIF-Co-Packaging-3.2T-Module-01.0 Thermal Interface Material. Synthetic test reconstruction of scope, thermal considerations and management interface boundaries.'),headers={'content-type':'application/pdf'},request=request)
        return httpx.Response(200,content=html(),headers={'content-type':'text/html'},request=request)
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        first=ingest_documents(db,d,client,force=True);assert first['status']=='partial' and first['new_count']==1
        assert ingest_documents(db,d,client)['status']=='not_due'
        second=ingest_documents(db,d,client,force=True);assert second['new_count']==0
        short=dict(d,**{'document-bytes':100});assert ingest_documents(db,short,client,force=True)['status']=='failed'
        with pytest.raises(ValueError,match='官方'):fetch_bounded(client,'https://example.com/document',['www.oiforum.com'],100,20)
    def timeout(request):raise httpx.ReadTimeout('controlled timeout',request=request)
    with httpx.Client(transport=httpx.MockTransport(timeout)) as client:
        result=ingest_documents(db,d,client,force=True);assert result['status']=='failed' and 'ReadTimeout' in result['error']
    after=updates_payload(db,['cpo-silicon-photonics'])
    for field in ('current_version_id','indicator_token','candidate_token'):assert before['items'][0][field]==after['items'][0][field]
    assert db.get(TechnicalDocument,'oif-cmis').data['versions']
    malformed={k:v for k,v in d.items() if k!='document-ids'}
    assert ingest_documents(db,malformed,force=True)['status']=='configuration_required'

@pytest.mark.parametrize('disposition',['adopted','no-impact'])
def test_import_review_atomic_and_removed_definition_preserved(db,tmp_path,disposition):
    root=tmp_path/'map';shutil.copytree(MAP_DIR,root)
    doc=db.get(TechnicalDocument,'oif-cmis');save_checked(db,doc,html(suffix='Reviewed change'),'text/html',doc.data['versions'][0]['url']);db.commit()
    observation=db.scalar(select(TechnicalObservation).where(TechnicalObservation.document_id==doc.id).order_by(TechnicalObservation.id.desc()))
    path=root/'technical-documents.yaml';manifest=yaml.safe_load(path.read_text(encoding='utf-8'));entry=next(d for d in manifest['documents'] if d['id']==doc.id)
    entry['reviews']=[{'content-hash':observation.content_hash,'official-version':observation.official_version,'disposition':disposition,'reviewed':'2026-10-16','reason':'核讀管理介面說明，未改變原採用與收入判斷。'}]
    if disposition=='adopted':
        version=copy.deepcopy(entry['versions'][0]);version.update({'id':'revision-5-4-reviewed-change','content-hash':observation.content_hash,'raw-hash':observation.raw_hash,'parser-version':PARSER_VERSION,'published':None,'published-precision':'unknown'})
        entry['versions'].append(version);entry['reviews'][0]['version-id']=version['id']
    path.write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8');import_map(db,root)
    review=db.scalar(select(TechnicalReview).where(TechnicalReview.observation_id==observation.id));assert review.status==disposition
    count=db.scalar(select(func.count()).select_from(ThemeAssessmentVersion));import_map(db,root);assert db.scalar(select(func.count()).select_from(ThemeAssessmentVersion))==count
    entry['reviews'][0]['content-hash']='a'*64;path.write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
    with pytest.raises(ValueError,match='無對應觀測'):import_map(db,root)
    assert db.get(TechnicalReview,review.id).status==disposition
