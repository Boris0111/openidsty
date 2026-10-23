from copy import deepcopy
from sqlalchemy import select
import yaml
import pytest
from app.config import DATA_DIR
from app.import_map import validate_research
from app.models import Company
from app.ingest import register_sources,save_records
from app.connectors import parse_tw
from pathlib import Path

@pytest.mark.parametrize('field,value',[('relevance','marketcap'),('evidence','tier'),('direction','unknown'),('source_url',''),('review_status','approved')])
def test_research_rejects_ambiguous_records(db,field,value):
    data=yaml.safe_load((DATA_DIR/'company-research.yaml').read_text(encoding='utf-8'))
    data['relations'][0][field]=value
    with pytest.raises(ValueError):
        validate_research(data,{c.ticker for c in db.scalars(select(Company))})

def test_revenue_event_detail_inference_without_company_financials(client,db):
    register_sources(db)
    fixture=(Path(__file__).parent/'fixtures/tw-revenue.json').read_text(encoding='utf-8')
    events,financials=parse_tw(fixture,'revenue','https://official.test',{'2330':'2330.TW'})
    save_records(db,'twse-revenue',events,financials,list(db.scalars(select(Company))))
    db.commit()
    assert client.get('/api/events').json()==[]
    event=client.get('/api/events?include_routine=true').json()[0]
    detail=client.get(f'/api/events/{event["id"]}').json()
    assert detail['impact']['confidence']=='inference'
    assert detail['impact']['seeds']==[]  # Company roles do not establish content relevance.
    assert detail['published_at'] is None
    assert detail['reported_at'] is not None
    assert detail['raw']['公司代號']=='2330'
    company=client.get('/api/companies/2330.TW').json()
    assert 'financials' not in company
    assert len(company['roles'])==2
