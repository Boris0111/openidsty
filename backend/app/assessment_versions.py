"""Append-only authored history, excluding operational and formatting changes."""
import copy,hashlib,json
from sqlalchemy import select
from .models import ThemeAssessmentVersion


def normalize(value,key=''):
    if isinstance(value,dict):return {k:normalize(v,k) for k,v in sorted(value.items()) if k!='change_reason'}
    if isinstance(value,list):
        result=[normalize(v,key) for v in value]
        if all(isinstance(v,dict) and ('id' in v or 'milestone_id' in v) for v in result):return sorted(result,key=lambda v:v.get('id') or v['milestone_id'])
        if all(isinstance(v,str) for v in result):return sorted(result)
        if key=='next_checks':return sorted(result,key=lambda v:v['question'])
        return result
    return value


def semantic_payload(data,checked):
    return normalize({'assessment':data.get('assessment'),'status':data['status'],'checked':checked})


def content_hash(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def latest_version(session,theme_id):
    return session.scalar(select(ThemeAssessmentVersion).where(ThemeAssessmentVersion.theme_id==theme_id).order_by(ThemeAssessmentVersion.version_number.desc()).limit(1))


def prepare_version(session,theme_id,data,checked):
    payload=semantic_payload(data,checked);digest=content_hash(payload)
    previous=latest_version(session,theme_id)
    if previous and previous.content_hash==digest:return None
    # Legacy themes without assessments have no fabricated earlier baseline.
    if not previous and not data.get('assessment'):return None
    reason=(data.get('assessment') or {}).get('change_reason','').strip()
    if previous and not reason:raise ValueError(f'{theme_id} 判讀實質變更須有 change_reason（移除判讀仍須保留原因）')
    return ThemeAssessmentVersion(theme_id=theme_id,version_number=previous.version_number+1 if previous else 1,payload=payload,content_hash=digest,reviewed=(data.get('assessment') or {}).get('reviewed') or checked,reason=reason or '首次保存目前研究基準；無較早版本')


def version_payload(row,detail=False):
    data={'version_id':row.id,'version_number':row.version_number,'theme_id':row.theme_id,'reviewed':row.reviewed,'recorded_at':row.recorded_at,'reason':row.reason,'content_hash':row.content_hash}
    if detail:data['payload']=copy.deepcopy(row.payload)
    return data


def diff_values(before,after,path='',changes=None):
    changes=[] if changes is None else changes
    if before==after:return changes
    if isinstance(before,dict) and isinstance(after,dict):
        for key in sorted(before.keys()|after.keys()):diff_values(before.get(key),after.get(key),f'{path}.{key}'.strip('.'),changes)
    elif isinstance(before,list) and isinstance(after,list):
        if all(isinstance(v,dict) and ('id' in v or 'milestone_id' in v) for v in before+after):
            left={v.get('id') or v['milestone_id']:v for v in before};right={v.get('id') or v['milestone_id']:v for v in after}
            for key in sorted(left.keys()|right.keys()):diff_values(left.get(key),right.get(key),f'{path}[{key}]',changes)
        elif all(isinstance(v,str) for v in before+after):
            for value in sorted(set(before)-set(after)):changes.append({'path':path,'kind':'removed','before':value,'after':None})
            for value in sorted(set(after)-set(before)):changes.append({'path':path,'kind':'added','before':None,'after':value})
        else:changes.append({'path':path,'kind':'modified','before':before,'after':after})
    else:changes.append({'path':path,'kind':'added' if before is None else 'removed' if after is None else 'modified','before':before,'after':after})
    return changes
