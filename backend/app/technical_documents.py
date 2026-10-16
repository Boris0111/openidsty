"""Authored baselines, append-only observations and locally imported reviews."""
import hashlib
import json
from sqlalchemy import select,func,update,exists
from fastapi import HTTPException
from .models import TechnicalDocument,TechnicalObservation,TechnicalReview,Source,now

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def observation(session,doc,version,content_hash,parser,url,data,raw_hash=None):
    key=digest([doc,version,content_hash])
    existing=session.scalar(select(TechnicalObservation).where(TechnicalObservation.document_id==doc,TechnicalObservation.observation_key==key))
    if existing:return existing,False
    row=TechnicalObservation(document_id=doc,observation_key=key,official_version=version,content_hash=content_hash,raw_hash=raw_hash,parser_version=parser,url=url,data=data)
    session.add(row);session.flush()
    session.add(TechnicalReview(observation_id=row.id,status='pending'))
    session.flush()
    return row,True

def import_documents(session,manifest,sources):
    # Source identities come from the same validated authoring snapshot. Runtime state survives.
    for entry in sources:
        sid=entry['id'];row=session.get(Source,sid)
        config=entry.get('ingestion',{'adapter':'manual'})
        if not row:
            row=Source(id=sid,name=entry['name'],url=entry['url'],status='manual' if config['adapter']=='manual' else 'not_run',new_count=0,data=dict(entry,**config))
            session.add(row)
        else:
            runtime={k:v for k,v in (row.data or {}).items() if k in ('fetch_meta','backfill_meta','backfill_completed_at','last_error_kind','last_http_status')}
            row.name=entry['name'];row.url=entry['url'];row.data=dict(entry,**config,**runtime)
    session.flush()
    ids=[]
    for d in manifest['documents']:
        previous=session.get(TechnicalDocument,d['id'])
        if previous:
            versions={v['id']:v for v in d['versions']}
            for old in previous.data['versions']:
                new=versions.get(old['id'])
                if not new:raise ValueError(f"已保存文件版本不得刪除：{d['id']}/{old['id']}")
                for key in ('url','label','content-hash'):
                    rebaseline=key=='content-hash' and old.get('raw-hash') and old['raw-hash']==new.get('raw-hash') and old.get('parser-version')!=new.get('parser-version') and new.get('normalization-note')
                    if old.get(key) is not None and old.get(key)!=new.get(key) and not rebaseline:raise ValueError(f"固定文件版本不可改指向其他內容：{d['id']}/{old['id']}；請新增版本識別碼")
        ids.append(d['id']);session.merge(TechnicalDocument(id=d['id'],source_id=d['source-id'],title=d['title'],doc_kind=d['doc-kind'],active=True,data=d))
        session.flush()
        for version in d['versions']:
            # A partial, manually read baseline is distinct from a complete normalized observation.
            content=version.get('content-hash') or digest([d['id'],version['id'],version['locators']])
            parser=version.get('parser-version') or 'authored-excerpts-v1'
            row,_=observation(session,d['id'],version['label'],content,parser,version['url'],{'baseline':True,'version_id':version['id'],'published':version['published'],'published_precision':version['published-precision'],'locators':version['locators'],'read_scope':version['read-scope']},version.get('raw-hash'))
            review=session.scalar(select(TechnicalReview).where(TechnicalReview.observation_id==row.id))
            review.status='adopted';review.reviewed=version['reviewed'];review.reason=version.get('normalization-note') or '匯入已核對基準；已讀範圍依 manifest。';review.version_id=version['id']
        for decision in d.get('reviews',[]):
            matches=list(session.scalars(select(TechnicalObservation).where(TechnicalObservation.document_id==d['id'],TechnicalObservation.content_hash==decision['content-hash'],TechnicalObservation.official_version==decision['official-version'])))
            if not matches:raise ValueError(f"文件核對紀錄無對應觀測：{d['id']}")
            for row in matches:
                review=session.scalar(select(TechnicalReview).where(TechnicalReview.observation_id==row.id))
                review.status=decision['disposition'];review.reviewed=decision['reviewed'];review.reason=decision['reason'];review.version_id=decision.get('version-id')
    session.execute(update(TechnicalDocument).where(TechnicalDocument.id.not_in(ids)).values(active=False))
    session.flush()

def summary_map(session,documents=None):
    documents=list(session.scalars(select(TechnicalDocument).order_by(TechnicalDocument.id))) if documents is None else documents
    counts=dict(session.execute(select(TechnicalObservation.document_id,func.count()).join(TechnicalReview).where(TechnicalReview.status=='pending',TechnicalObservation.document_id.in_([d.id for d in documents])).group_by(TechnicalObservation.document_id)).all())
    return [{'id':d.id,'title':d.title,'source_id':d.source_id,'doc_kind':d.doc_kind,'active':d.active,'segments':d.data['segments'],'themes':d.data['themes'],'versions':len(d.data['versions']),'pending_count':counts.get(d.id,0)} for d in documents]

def list_documents(session,limit=20,offset=0,segment=None,theme=None):
    query=select(TechnicalDocument).where(TechnicalDocument.active.is_(True))
    for field,value in [('segments',segment),('themes',theme)]:
        if value:
            each=(func.json_array_elements_text(TechnicalDocument.data[field]).table_valued('value') if session.bind.dialect.name=='postgresql' else func.json_each(TechnicalDocument.data[field]).table_valued('value')).alias('document_scope_'+field)
            query=query.where(exists(select(1).select_from(each).where(each.c.value==value)))
    total=session.scalar(select(func.count()).select_from(query.subquery()))
    documents=list(session.scalars(query.order_by(TechnicalDocument.id).limit(limit).offset(offset)))
    return {'as_of':now(),'items':summary_map(session,documents),'total':total,'limit':limit,'offset':offset}

def document_detail(session,did,limit=10,offset=0):
    doc=session.get(TechnicalDocument,did)
    if not doc:raise HTTPException(404,'找不到技術文件')
    q=select(TechnicalObservation,TechnicalReview).join(TechnicalReview).where(TechnicalObservation.document_id==did)
    total=session.scalar(select(func.count()).select_from(TechnicalObservation).where(TechnicalObservation.document_id==did))
    rows=session.execute(q.order_by(TechnicalObservation.id.desc()).limit(limit).offset(offset))
    source=session.get(Source,doc.source_id)
    return {'id':did,'active':doc.active,'definition':doc.data,'source':{'id':source.id,'name':source.name,'status':source.status,'last_attempt':source.last_attempt,'last_success':source.last_success,'error':source.error},'history':{'total':total,'limit':limit,'offset':offset,'items':[{'id':o.id,'official_version':o.official_version,'content_hash':o.content_hash,'parser_version':o.parser_version,'url':o.url,'fetched_at':o.fetched_at,'data':o.data,'review':{'status':r.status,'reviewed':r.reviewed,'reason':r.reason,'version_id':r.version_id}} for o,r in rows]}}
