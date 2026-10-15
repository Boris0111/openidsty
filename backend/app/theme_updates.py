"""Public content tokens; no personal state or operational timestamps."""
import hashlib,json
from sqlalchemy import select
from .models import Theme,Indicator,ThemeIndicator
from .assessments import assessment_payload,candidate_events
from .assessment_versions import latest_version
from .observations import latest_observations
from .indicator_api import indicators_payload


def token(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,default=str,separators=(',',':')).encode()).hexdigest()


def updates_payload(session,ids):
    items=[]
    for tid in ids:
        theme=session.get(Theme,tid)
        if not theme or not theme.active:
            items.append({'theme_id':tid,'available':False,'reason':'題材已不存在或不在目前研究範圍'});continue
        version=latest_version(session,tid);assessment=assessment_payload(session,theme)
        indicators=indicators_payload(session,theme)
        rows=[]
        for iid in session.scalars(select(ThemeIndicator.indicator_id).where(ThemeIndicator.theme_id==tid)):
            rows.extend((iid,r.identity,r.revision,r.content_hash,r.valid) for r in latest_observations(session,iid))
        candidates,unknown=candidate_events(session,theme)
        events=[(e.identity or str(e.id),e.title,e.body,e.published_at.isoformat() if e.published_at else None,e.published_precision,e.lifecycle) for e in candidates+unknown]
        warnings=assessment['source_warnings']+[{'source_id':i['source']['id'],'kind':i['source']['status'],'message':i['source']['error']} for i in indicators['indicators'] if i['source']['error']]
        items.append({'theme_id':tid,'available':True,'name':theme.data['name_zh'],'current_version_id':version.id if version else None,'version_number':version.version_number if version else None,'reviewed':theme.checked,'assessment_summary':(theme.data.get('assessment') or {}).get('summary'),'indicator_token':token(sorted(rows)),'candidate_token':token(sorted(events,key=lambda r:r[0])),'candidate_count':len(candidates),'unknown_date_count':len(unknown),'indicator_count':len(indicators['indicators']),'available_indicator_count':sum(i['latest'] is not None for i in indicators['indicators']),'indicator_summary':[{'id':i['id'],'name':i['name'],'kind':i['kind'],'period':i['latest']['original_period'] if i['latest'] else None,'revision':i['latest']['revision'] if i['latest'] else None} for i in indicators['indicators']],'source_warnings':warnings,'pending_summary':f'{len(candidates)} 則待纳入判讀；{len(unknown)} 則新收錄資訊發布日待確認（不代表新發生）'})
    return {'items':items}
