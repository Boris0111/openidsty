"""Company comparison shows research side by side and never financial values."""
from test_research_v2 import v2  # noqa: F401


def compare(client,data,ids,**params):
    return client.get('/api/v2/compare',params={'company_ids':','.join(ids),'release_id':data['release'],**params})


def test_compare_lists_research_only_and_keeps_gaps(v2):
    client,data=v2
    response=compare(client,data,data['keys'][:2])
    assert response.status_code==200,response.text
    body=response.json()['data']
    assert set(body)=={'companies'}
    first,second=body['companies']
    assert [item['product_id'] for item in first['products']]==[data['product']] and first['products'][0]['role_id']==data['role']
    # A company without offerings or a risk section shows an explicit gap, not borrowed content.
    assert second['products']==[] and second['risks'] is None and second['business_model'] is None
    assert not any(key in column for column in body['companies'] for key in ('metrics','preferred_source_family'))


def test_compare_rejects_wrong_company_counts(v2):
    client,data=v2
    for ids in (data['keys'][:1],[data['keys'][0]]*2,[data['keys'][0],data['keys'][1],'company-a','company-b','company-c']):
        response=compare(client,data,ids)
        assert response.status_code==422 and response.json()['code']=='invalid-comparison'


def test_old_links_with_basis_still_open(v2):
    client,data=v2
    plain=compare(client,data,data['keys'][:2]).json()
    assert compare(client,data,data['keys'][:2],basis='quarterly').json()==plain
