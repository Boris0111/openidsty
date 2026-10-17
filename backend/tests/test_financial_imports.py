"""Synthetic official-import contracts; no HTTP fetch or production records."""
import csv,io,json,uuid
from copy import deepcopy
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from app.financial_imports import normalize,decode,FORMAT
from app.financial_store import save_official,register_metrics
from test_research_auth import owner,login,ORIGIN


def payload(company='company-import-synthetic',number='100',accession='synthetic-official-one',filed='2026-02-01'):
    return {'format':FORMAT,'document':{'source_id':'sec-facts','source_family':'sec',
        'source_url':'https://www.sec.gov/Archives/edgar/data/1/synthetic-test-only.htm',
        'title':'Synthetic official document for isolated testing','accession':accession,'filed_at':filed},
        'rows':[{'company_id':company,'metric_id':'revenue','period_start':'2025-01-01','period_end':'2025-12-31',
            'basis':'annual','scope':'whole-filing-entity','unit':'amount','currency':'USD',
            'raw_value':number,'raw_unit':'USD','multiplier':'1','tag':'us-gaap:Revenues','locator':'Synthetic income statement, revenue row'}]}


def csv_bytes(data):
    rows=[{**{'document_'+key:value for key,value in data['document'].items()},**row} for row in data['rows']]
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return stream.getvalue().encode('utf-8-sig')


def test_json_csv_share_normalized_content_and_decimal_units():
    data=payload(number='123.456');data['rows'][0].update(raw_unit='USD thousand',multiplier='1000')
    json_data,rows=normalize(decode(json.dumps(data).encode(),'application/json'))
    csv_data,other=normalize(decode(csv_bytes(data),'text/csv'))
    assert json_data==csv_data and rows[0].value.value==other[0].value.value==123456


@pytest.mark.parametrize('section,key',[('document','source_id'),('document','source_url'),('document','title'),
    ('rows','period_start'),('rows','currency'),('rows','locator'),('rows','raw_value')])
def test_missing_evidence_period_currency_or_value_is_rejected(section,key):
    data=payload();del (data[section] if section=='document' else data[section][0])[key]
    with pytest.raises(ValueError):normalize(data)


def test_no_pdf_float_duplicate_context_or_unknown_fields():
    with pytest.raises(ValueError):decode(b'%PDF-test','application/pdf')
    data=payload();data['rows'][0]['raw_value']=0.1
    with pytest.raises(ValueError):decode(json.dumps(data).encode(),'application/json')
    data=payload();data['rows'].append(dict(data['rows'][0]))
    with pytest.raises(ValueError):normalize(data)
    data=payload();data['rows'][0]['guessed_ai_revenue']=50
    with pytest.raises(ValueError):normalize(data)


def test_capex_negative_source_requires_explicit_sign_evidence():
    data=payload(number='-10');row=data['rows'][0];row.update(metric_id='capex',multiplier='-1')
    with pytest.raises(ValueError):normalize(data)
    row['normalization_note']='原始現金流表以負號列支出；本指標採正值購置支出。'
    assert normalize(data)[1][0].value.value==10


@pytest.mark.parametrize('supersedes',[True,{'bad':'shape'},['not-an-id'],'not-a-uuid'])
def test_malformed_correction_ids_are_validation_errors(supersedes):
    data=payload();data['rows'][0]['supersedes']=supersedes
    with pytest.raises(ValueError):normalize(data)


def test_filing_before_period_end_is_not_an_actual_financial_fact():
    with pytest.raises(ValueError):normalize(payload(filed='2025-01-01'))


@pytest.mark.parametrize('constant',['NaN','Infinity','-Infinity'])
def test_non_finite_json_constants_are_rejected(constant):
    with pytest.raises(ValueError):decode(('{"value":'+constant+'}').encode(),'application/json')


@pytest.fixture
def imports(owner):
    client,engine=owner
    identifier=uuid.uuid4();company='company-import-'+uuid.uuid4().hex
    with engine.begin() as connection:
        old=connection.execute(text('SELECT release_id FROM research.release_head')).scalar()
        connection.execute(text('''INSERT INTO research.research_releases(release_id,git_commit,schema_version,content_hash,status,reason)
            VALUES(:id,:commit,'research-v1',:hash,'preparing','Synthetic financial import baseline')'''),
            {'id':identifier,'commit':uuid.uuid4().hex+'0'*8,'hash':uuid.uuid4().hex*2})
        connection.execute(text("INSERT INTO research.entities VALUES(:id,'company')"),{'id':company})
        connection.execute(text('''INSERT INTO research.entity_snapshots(release_id,entity_id,kind,name,summary,markdown,data,semantic_hash)
            VALUES(:release,:id,'company','Synthetic company','Synthetic only','Synthetic only','{}',:hash)'''),
            {'release':identifier,'id':company,'hash':'a'*64})
        connection.execute(text('''INSERT INTO research.release_sources VALUES(:release,'sec-facts','Synthetic SEC source',
            'https://www.sec.gov/edgar/search/','{"type":"filings"}')'''),{'release':identifier})
        connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':identifier})
        connection.execute(text('''INSERT INTO research.release_head(singleton,release_id,generation) VALUES(true,:id,1)
            ON CONFLICT(singleton) DO UPDATE SET release_id=:id,generation=research.release_head.generation+1'''),{'id':identifier})
    response=login(client);assert response.status_code==200
    headers={'Origin':ORIGIN,'X-CSRF-Token':response.json()['csrf_token']}
    yield client,engine,company,headers
    with engine.begin() as connection:
        if old:connection.execute(text('UPDATE research.release_head SET release_id=:id WHERE singleton'),{'id':old})
        else:connection.execute(text('DELETE FROM research.release_head'))


def preview(client,headers,data,csv=False):
    result=client.post('/api/admin/financial-imports',content=csv_bytes(data) if csv else json.dumps(data).encode(),
        headers={**headers,'Content-Type':'text/csv' if csv else 'application/json'})
    assert result.status_code==201,result.text
    return result.json()


def confirm(client,headers,batch,key=None,reason='已核對合成測試官方文件與列定位。',**changes):
    return client.post('/api/admin/financial-imports/'+batch['batch_id']+'/confirm',
        json={'payload_hash':batch['payload_hash'],'reason':reason,'confirmed_official_source':True,**changes},
        headers={**headers,'Idempotency-Key':key or 'financial-confirm-'+batch['batch_id']})


def test_preview_csv_json_then_confirm_retry_and_audit(imports):
    client,engine,company,headers=imports
    one=preview(client,headers,payload(company));same=preview(client,headers,payload(company),True)
    assert one['batch_id']==same['batch_id'] and one['items'][0]['value']=='100' and one['status']=='preview'
    with engine.connect() as connection:
        assert connection.execute(text('SELECT count(*) FROM research.financial_groups WHERE company_id=:id'),{'id':company}).scalar_one()==0
    assert confirm(client,headers,one,confirmed_official_source=False).status_code==422
    assert confirm(client,headers,one,payload_hash='0'*64).status_code==409
    result=confirm(client,headers,one)
    assert result.status_code==200,result.text
    assert result.json()['result']['new_revisions']==1
    assert confirm(client,headers,one).json()==result.json()
    assert confirm(client,headers,one,reason='Different confirmed reason').status_code==409
    other=preview(client,headers,payload(company,'110','synthetic-official-two','2026-03-01'))
    assert confirm(client,headers,other,key='financial-confirm-'+one['batch_id']).status_code==409
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM research.audit_log WHERE operation='financial-import-confirm' AND detail->>'batch_id'=:id"),{'id':one['batch_id']}).scalar_one()==1
        fact=connection.execute(text('''SELECT f.payload FROM research.financial_raw_facts f WHERE f.company_id=:id'''),{'id':company}).scalar_one()
        assert fact['original']['locator']=='Synthetic income statement, revenue row'
        with pytest.raises(DBAPIError):
            with connection.begin_nested():connection.execute(text("UPDATE research.financial_import_batches SET result='{}' WHERE batch_id=:id"),{'id':one['batch_id']})
    client.cookies.clear()
    assert client.get('/api/admin/financial-imports/'+one['batch_id']).status_code==401
    assert confirm(client,headers,one).status_code==401


def test_stale_preview_and_untrusted_url_cannot_write(imports):
    client,engine,company,headers=imports
    data=payload(company);one=preview(client,headers,data)
    invalid=deepcopy(data);invalid['document']['source_url']='https://untrusted.invalid/number'
    rejected=client.post('/api/admin/financial-imports',json=invalid,headers=headers)
    assert rejected.status_code==422
    _,rows=normalize(payload(company,'110','synthetic-external-new','2026-04-01'))
    with engine.begin() as connection:
        register_metrics(connection);save_official(connection,rows[0].value,(rows[0].fact,))
    assert confirm(client,headers,one).status_code==409
    fresh=preview(client,headers,data)
    assert fresh['batch_id']!=one['batch_id'] and fresh['items'][0]['previous_value']=='110'


def test_same_day_bad_value_is_atomic_and_explicit_correction_keeps_history(imports):
    client,engine,company,headers=imports
    first=preview(client,headers,payload(company));response=confirm(client,headers,first)
    assert response.status_code==200,response.text
    saved=response.json()
    existing=saved['result']['items'][0]['observation_id']
    bad=payload(company,'999','synthetic-correction')
    extra=dict(bad['rows'][0],metric_id='gross-profit',raw_value='40',tag='us-gaap:GrossProfit')
    bad['rows'].append(extra)
    pending=preview(client,headers,bad)
    assert confirm(client,headers,pending,key='financial-confirm-bad-'+pending['batch_id']).status_code==409
    with engine.connect() as connection:
        values=connection.execute(text('''SELECT g.metric_id,o.value FROM research.financial_groups g
            JOIN research.financial_observations o USING(group_id) WHERE g.company_id=:id'''),{'id':company}).all()
        assert [(metric,str(value.normalize())) for metric,value in values]==[('revenue','1E+2')]
    corrected=payload(company,'110','synthetic-corrected-filing')
    corrected['rows'][0].update(supersedes=existing,revision_note='已核對同日官方修正文件的報表列與版本。')
    verified=preview(client,headers,corrected)
    result=confirm(client,headers,verified,key='financial-confirm-corrected-'+verified['batch_id'])
    assert result.status_code==200,result.text
    assert result.json()['result']['new_revisions']==1
    with engine.connect() as connection:
        values=connection.execute(text('''SELECT o.value,o.supersedes FROM research.financial_groups g
            JOIN research.financial_observations o USING(group_id) WHERE g.company_id=:id ORDER BY revision'''),{'id':company}).all()
        assert len(values)==2 and values[0].value==100 and values[1].value==110 and str(values[1].supersedes)==existing
