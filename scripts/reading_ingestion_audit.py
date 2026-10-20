"""Content audit for the isolated restart exercise; omits credentials and raw full text."""
import json
from sqlalchemy import select,func
from app.db import Session,engine
from app.models import Event,Financial,IndicatorObservation,ThemeAssessmentVersion,TechnicalObservation,TechnicalReview,Source,Theme,now
from app.theme_updates import updates_payload
with Session() as session:
    session.connection(execution_options={'isolation_level':'REPEATABLE READ'})
    themes=list(session.scalars(select(Theme.id).where(Theme.active.is_(True)).order_by(Theme.id)))
    result={'at':now().isoformat(),'counts':{m.__tablename__:session.scalar(select(func.count()).select_from(m)) for m in (Event,Financial,IndicatorObservation,ThemeAssessmentVersion,TechnicalObservation,TechnicalReview)},'tokens':[{k:v for k,v in row.items() if k in ('theme_id','current_version_id','indicator_token','candidate_token')} for row in updates_payload(session,themes)['items']],'documents':[dict(id=o.id,document_id=o.document_id,official_version=o.official_version,hash=o.content_hash) for o in session.scalars(select(TechnicalObservation).order_by(TechnicalObservation.id))],'sources':[dict(id=s.id,status=s.status,last_success=s.last_success,error=s.error,new_count=s.new_count) for s in session.scalars(select(Source).where(Source.id.in_(['twse-revenue','ocp-cold-plate','oif-technical','tpca-news','aaon-earnings-metrics'])))]}
print(json.dumps(result,ensure_ascii=False,default=str))
