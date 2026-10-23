"""Side-by-side company research within one release; no financial values or rankings."""
import re,uuid
from fastapi import APIRouter,Depends,Query
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release,entity,envelope,summary,claims_payload,reader_gaps

router=APIRouter(prefix='/api/v2',tags=['research-compare'])


def company(session,release,identifier):
    row=entity(session,release,identifier)
    if row['kind']!='company':raise ResearchError(404,'company-not-found','找不到這家公司。')
    return row


@router.get('/compare')
def compare(company_ids:str=Query(...,max_length=850),release_id:uuid.UUID|None=None,session=Depends(get_research_session)):
    # Older shared links may still carry basis; it is ignored because no financial values are compared.
    identifiers=company_ids.split(',')
    if not 2<=len(identifiers)<=4 or len(set(identifiers))!=len(identifiers):raise ResearchError(422,'invalid-comparison','比較須選擇 2 至 4 家不同公司。')
    release=require_release(session,release_id);profiles=[company(session,release,key) for key in identifiers]
    offerings=session.execute(text('''SELECT ranked.* FROM (SELECT o.company_id,o.product_id,p.name,o.role_id,r.name AS role_name,
        o.conditions,row_number() OVER(PARTITION BY o.company_id ORDER BY o.product_id,o.role_id) AS n
        FROM research.company_offerings o JOIN research.entity_snapshots p ON p.release_id=o.release_id AND p.entity_id=o.product_id
        JOIN research.entity_snapshots r ON r.release_id=o.release_id AND r.entity_id=o.role_id
        WHERE o.release_id=:release AND o.company_id=ANY(CAST(:ids AS text[]))) ranked WHERE n<=101'''),
        {'release':release['release_id'],'ids':identifiers}).mappings().all()
    columns=[]
    for row in profiles:
        key=row['entity_id']
        sections=re.split(r'^##\s+(.+?)\s*$',row['markdown'],flags=re.M)
        prose={sections[i]:sections[i+1].strip() for i in range(1,len(sections)-1,2)}
        claims,truncated=claims_payload(session,release,key)
        products=[dict(item) for item in offerings if item['company_id']==key]
        columns.append({**summary(row),'roles':[{'segment_id':role['segment-id'],'description':role['description']} for role in row['data'].get('roles',[])[:100]],
            'products':products[:100],'risks':prose.get('風險','')[:12000] or None,'business_model':prose.get('商業模式','')[:12000] or None,
            'claims':claims,'gaps':reader_gaps(row['data'].get('gaps')),'research_depth':row['data'].get('research-depth','basic'),
            'truncated':truncated or len(products)>100 or any(len(prose.get(heading,''))>12000 for heading in ('風險','商業模式'))})
    return envelope(release,{'companies':columns})
