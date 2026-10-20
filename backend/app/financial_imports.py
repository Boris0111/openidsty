"""Owner-reviewed official JSON/CSV. Never fetch URLs or guess PDF tables."""
import csv,io,json,re,uuid,hashlib
from datetime import date
from dataclasses import dataclass
from urllib.parse import urlsplit
from fastapi import APIRouter,Depends,Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from .financial_core import (FinancialContext,FinancialValue,RawFact,METRICS,decimal_value,
    decimal_text,fingerprint,_json)
from .financial_store import encoded,latest,register_metrics,save_official,lock_groups
from .research_auth import require_owner,require_owner_write
from .research_db import get_admin_connection
from .research_http import ResearchError

router=APIRouter(prefix='/api/admin/financial-imports',tags=['financial-imports'])
FORMAT='official-financial-import-v1'
MAX_BYTES=1024*1024
DOC_REQUIRED={'source_id','source_family','source_url','title','accession','filed_at'}
DOC_OPTIONAL={'source_as_of'}
ROW_REQUIRED={'company_id','metric_id','period_start','period_end','basis','scope','unit','currency','raw_value','raw_unit','multiplier','tag','locator'}
ROW_OPTIONAL={'share_class','supersedes','revision_note','normalization_note'}


def words(value,name,limit=500):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or any(ord(c)<32 for c in value):
        raise ValueError(name+' 須為有效非空文字。')
    return value.strip()


def day(value,nullable=False):
    if nullable and value in (None,''):return None
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('日期須為 YYYY-MM-DD。')
    return date.fromisoformat(value)


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('JSON 欄位重複。')
        result[key]=value
    return result


@dataclass(frozen=True)
class ImportRow:
    value:FinancialValue
    fact:RawFact
    locator:str
    supersedes:uuid.UUID|None
    revision_note:str
    normalization_note:str


def decode(content,content_type):
    if len(content)>MAX_BYTES:raise ValueError('財務匯入超過 1 MiB。')
    if content_type=='text/csv':
        try:body=content.decode('utf-8-sig')
        except UnicodeDecodeError:body=content.decode('cp950')
        reader=csv.DictReader(io.StringIO(body))
        if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):raise ValueError('CSV 欄位缺少或重複。')
        data=list(reader)
        if not 1<=len(data)<=100:raise ValueError('每批需 1–100 列。')
        document=None;rows=[]
        for row in data:
            if None in row or any(value is None for value in row.values()):raise ValueError('CSV 列長與表頭不同。')
            doc={key:row.pop('document_'+key) for key in DOC_REQUIRED|DOC_OPTIONAL if 'document_'+key in row}
            if document is not None and document!=doc:raise ValueError('一批 CSV 只能引用同一份官方文件。')
            document=doc;rows.append({key:value for key,value in row.items() if value!='' or key in ROW_REQUIRED})
        return {'format':FORMAT,'document':document,'rows':rows}
    if content_type!='application/json':raise ValueError('僅接受 application/json 或 text/csv，不自動解析 PDF。')
    try:return json.loads(content,object_pairs_hook=unique,parse_float=lambda _:(_ for _ in ()).throw(ValueError('數值請用十進位字串。')),
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('不得包含非有限數。')))
    except (UnicodeError,RecursionError):raise ValueError('匯入 JSON 格式不正確。') from None


def normalize(payload):
    if not isinstance(payload,dict) or set(payload)!={'format','document','rows'} or payload['format']!=FORMAT:raise ValueError('匯入格式版本不正確。')
    doc=payload['document']
    if not isinstance(doc,dict) or not DOC_REQUIRED<=doc.keys() or doc.keys()-DOC_REQUIRED-DOC_OPTIONAL:raise ValueError('官方文件來源、識別或申報日欄位不完整。')
    document={key:words(doc[key],key,2000 if key=='source_url' else 500) for key in DOC_REQUIRED-{'filed_at'}}
    document['filed_at']=day(doc['filed_at'],True)
    document['source_as_of']=day(doc.get('source_as_of'),True)
    if document['filed_at'] and document['source_as_of']:raise ValueError('公司申報日與彙整日不可混用。')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',document['source_id']):raise ValueError('來源 ID 不正確。')
    url=urlsplit(document['source_url'])
    if url.scheme!='https' or not url.hostname or url.username or url.password or url.port not in (None,443):raise ValueError('官方文件須為不含憑證的 HTTPS 位址。')
    data=payload['rows']
    if not isinstance(data,list) or not 1<=len(data)<=100:raise ValueError('每批需 1–100 列。')
    normalized=[];parsed=[];seen=set()
    for index,row in enumerate(data):
        if not isinstance(row,dict) or not ROW_REQUIRED<=row.keys() or row.keys()-ROW_REQUIRED-ROW_OPTIONAL:raise ValueError(f'第 {index+1} 列缺少必要欄位或含未知欄位。')
        clean={key:words(row[key],key,2000 if key in ('locator','revision_note','normalization_note') else 500) for key in row if key!='supersedes'}
        context=FinancialContext(clean['company_id'],document['source_family'],clean['metric_id'],
            day(clean['period_start']),day(clean['period_end']),clean['basis'],scope=clean['scope'],
            unit=clean['unit'],currency=clean['currency'],share_class=clean.get('share_class',''))
        if (document['filed_at'] or document['source_as_of']) and (document['filed_at'] or document['source_as_of'])<context.period_end:
            raise ValueError('來源日期不得早於已實現財務期間。')
        if not clean['currency']:raise ValueError('財務匯入須明列原幣。')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',context.scope):raise ValueError('會計範圍須明列穩定識別。')
        factor=decimal_value(clean['multiplier'])
        if factor<0 and (context.metric_id!='capex' or len(clean.get('normalization_note',''))<6):raise ValueError('負倍率僅能用於附符號核對說明的 capex。')
        fact=RawFact(context,document['accession'],clean['tag'],clean['raw_unit'],decimal_value(clean['raw_value']),
            document['filed_at'],document['source_url'],multiplier=factor,source_as_of=document['source_as_of'])
        value=FinancialValue(context,fact.normalized_value,uuid.uuid5(uuid.NAMESPACE_URL,'manual-value:'+str(fact.fact_id)+':'+decimal_text(fact.normalized_value)),document['accession'])
        if context.group_id in seen:raise ValueError('同一批不得有重複指標／期間／範圍群組。')
        seen.add(context.group_id)
        supersedes=uuid.UUID(words(row['supersedes'],'修正觀測 ID')) if row.get('supersedes') else None
        if supersedes and len(clean.get('revision_note',''))<6:raise ValueError('指定修正觀測須附修訂依據。')
        clean.update(raw_value=decimal_text(fact.value),multiplier=decimal_text(factor))
        if supersedes:clean['supersedes']=str(supersedes)
        normalized.append(clean)
        parsed.append(ImportRow(value,fact,clean['locator'],supersedes,clean.get('revision_note',''),clean.get('normalization_note','')))
    return {'format':FORMAT,'document':_json(document),'rows':normalized},parsed


def validate_references(connection,document,rows):
    source=connection.execute(text('''SELECT s.* FROM research.release_sources s JOIN research.release_head h USING(release_id)
        WHERE s.source_id=:id'''),{'id':document['source_id']}).mappings().first()
    if not source or source['data'].get('type') not in ('filings','earnings_call'):raise ValueError('來源須為正式研究已登錄的官方申報／公司 IR 入口。')
    known={urlsplit(source['url']).hostname}
    ingestion=source['data'].get('ingestion',{})
    known.update(urlsplit(ingestion[key]).hostname for key in ('url','fallback') if ingestion.get(key))
    if known&{'sec.gov','www.sec.gov','data.sec.gov'}:known.update(('sec.gov','www.sec.gov','data.sec.gov'))
    if urlsplit(document['source_url']).hostname not in known:raise ValueError('文件主機與登錄來源不同，請先核對並登錄官方入口。')
    if document['source_family']=='sec' and not urlsplit(document['source_url']).hostname.endswith('sec.gov'):raise ValueError('SEC 來源族須引用 SEC 官方文件。')
    for row in rows:
        exists=connection.execute(text('''SELECT 1 FROM research.entity_snapshots s JOIN research.release_head h USING(release_id)
            WHERE s.entity_id=:id AND s.kind='company' '''),{'id':row.value.context.company_id}).scalar()
        if not exists:raise ValueError('匯入公司不在目前已發布研究中。')
        if row.supersedes:
            group=connection.execute(text('SELECT group_id FROM research.financial_observations WHERE observation_id=:id'),{'id':row.supersedes}).scalar()
            if group!=row.value.context.group_id:raise ValueError('指定修正的觀測不存在或口徑不同。')


def baseline(connection,rows):
    result={};items=[]
    for row in rows:
        context=row.value.context;current=latest(connection,context.group_id)
        result[context.group_id]=str(current['observation_id']) if current else None
        items.append({'company_id':context.company_id,'metric_id':context.metric_id,'label':METRICS[context.metric_id][0],
            'period_start':context.period_start.isoformat(),'period_end':context.period_end.isoformat(),'basis':context.basis,
            'currency':context.currency,'scope':context.scope,'unit':context.unit,'share_class':context.share_class,
            'raw_value':decimal_text(row.fact.value),'raw_unit':row.fact.raw_unit,'multiplier':decimal_text(row.fact.multiplier),
            'value':decimal_text(row.value.value),'previous_value':decimal_text(current['value']) if current else None,
            'changed':current is None or current['semantic_hash']!=row.value.semantic_hash,'locator':row.locator,
            'supersedes':str(row.supersedes) if row.supersedes else None,'revision_note':row.revision_note})
    return result,items


def batch(connection,batch_id,lock=False):
    row=connection.execute(text('SELECT * FROM research.financial_import_batches WHERE batch_id=:id'+(' FOR UPDATE' if lock else '')),
        {'id':batch_id}).mappings().first()
    if not row:raise ResearchError(404,'financial-import-not-found','找不到這份財務預覽。')
    return row


def representation(row):
    return {'batch_id':str(row['batch_id']),'payload_hash':row['payload_hash'],'status':row['status'],
        'document':row['payload']['input']['document'],'items':row['payload']['items'],'result':row['result'],
        'upload_sha256':row['payload']['upload_sha256'],'confirmed_at':row['confirmed_at'].isoformat() if row['confirmed_at'] else None}


def create_preview(connection,content,content_type):
    try:
        data,rows=normalize(decode(content,content_type))
        validate_references(connection,data['document'],rows)
        heads,items=baseline(connection,rows)
    except (ValueError,TypeError,KeyError,RecursionError) as error:
        raise ResearchError(422,'financial-import-invalid',str(error)) from None
    payload={'input':data,'baseline':heads,'items':items,'upload_sha256':hashlib.sha256(content).hexdigest()}
    hashed=fingerprint({'input':data,'baseline':heads})
    identifier=uuid.uuid5(uuid.NAMESPACE_URL,'financial-import:'+hashed)
    connection.execute(text('''INSERT INTO research.financial_import_batches(batch_id,payload_hash,payload,status)
        VALUES(:id,:hash,CAST(:payload AS jsonb),'preview') ON CONFLICT(payload_hash) DO NOTHING'''),
        {'id':identifier,'hash':hashed,'payload':encoded(payload)})
    return representation(batch(connection,identifier))


def confirm(connection,batch_id,data,key):
    if not re.fullmatch(r'[A-Za-z0-9._:-]{8,128}',key or ''):raise ResearchError(422,'invalid-idempotency-key','確認需提供有效 Idempotency-Key。')
    if not isinstance(data,dict) or set(data)!={'payload_hash','reason','confirmed_official_source'} or data['confirmed_official_source'] is not True:
        raise ResearchError(422,'financial-confirmation-required','請明確確認已核對官方原文與定位。')
    try:reason=words(data['reason'],'確認理由',2000)
    except ValueError as error:raise ResearchError(422,'financial-confirmation-required',str(error)) from None
    connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,38109078))'),{'key':key})
    row=batch(connection,batch_id,True)
    if data['payload_hash']!=row['payload_hash']:raise ResearchError(409,'financial-import-hash-mismatch','預覽內容不同，請重新核對。')
    confirmation_hash=fingerprint({'batch_id':str(batch_id),**data})
    previous=connection.execute(text('SELECT batch_id FROM research.financial_import_batches WHERE confirmation_key=:key'),{'key':key}).scalar()
    if previous and previous!=batch_id:raise ResearchError(409,'financial-confirmation-conflict','此確認 key 已用於其他預覽。')
    if row['status']=='confirmed':
        if row['confirmation_key']!=key or row['confirmation_hash']!=confirmation_hash:raise ResearchError(409,'financial-confirmation-conflict','這份預覽已由另一個確認內容完成。')
        return representation(row)
    if row['status']!='preview':raise ResearchError(409,'financial-import-closed','這份預覽已結束。')
    try:
        normalized,rows=normalize(row['payload']['input'])
        validate_references(connection,normalized['document'],rows)
        lock_groups(connection,[entry.value.context.group_id for entry in rows])
        heads,_=baseline(connection,rows)
        if heads!=row['payload']['baseline']:raise ResearchError(409,'financial-import-stale','財務已有新修訂，請重新匯入並核對差異。')
        register_metrics(connection);saved=[]
        for entry in sorted(rows,key=lambda item:item.value.context.group_id):
            result=save_official(connection,entry.value,(entry.fact,),kind='manual-official',expected_supersedes=entry.supersedes,
                limitations='人工核對官方文件；'+entry.normalization_note,
                payloads={str(entry.fact.fact_id):{'document':normalized['document'],'locator':entry.locator,
                    'revision_note':entry.revision_note,'normalization_note':entry.normalization_note}})
            if result['status']!='saved':raise ResearchError(409,'financial-value-needs-review','同日／未知日期不同值須附指定觀測及修訂依據，原值未被更動。')
            saved.append({**result,'observation_id':str(result['observation_id'])})
    except (ValueError,TypeError,KeyError) as error:raise ResearchError(422,'financial-import-invalid',str(error)) from None
    result={'new_revisions':sum(item['new_revision'] for item in saved),'active_changes':sum(item['active_changed'] for item in saved),'items':saved}
    connection.execute(text('''UPDATE research.financial_import_batches SET status='confirmed',confirmed_at=now(),confirmed_by='owner',
        confirmation_key=:key,confirmation_hash=:hash,result=CAST(:result AS jsonb) WHERE batch_id=:id'''),
        {'key':key,'hash':confirmation_hash,'result':encoded(result),'id':batch_id})
    connection.execute(text('''INSERT INTO research.audit_log(actor,operation,detail) VALUES('owner','financial-import-confirm',CAST(:detail AS jsonb))'''),
        {'detail':encoded({'batch_id':str(batch_id),'payload_hash':row['payload_hash'],'reason':reason,'source_id':normalized['document']['source_id'],
            'rows':len(rows),'new_revisions':result['new_revisions']})})
    return representation(batch(connection,batch_id))


async def bounded_body(request):
    content=bytearray()
    async for part in request.stream():
        content.extend(part)
        if len(content)>MAX_BYTES:raise ResearchError(413,'financial-import-too-large','財務匯入超過 1 MiB。')
    return bytes(content)


@router.post('')
async def preview(request:Request,owner=Depends(require_owner_write),connection=Depends(get_admin_connection)):
    content=await bounded_body(request)
    result=await run_in_threadpool(create_preview,connection,content,request.headers.get('content-type','').split(';')[0])
    return JSONResponse(result,status_code=201,headers={'Cache-Control':'no-store'})


@router.get('/{batch_id}')
def get_preview(batch_id:uuid.UUID,owner=Depends(require_owner),connection=Depends(get_admin_connection)):
    return JSONResponse(representation(batch(connection,batch_id)),headers={'Cache-Control':'no-store'})


@router.post('/{batch_id}/confirm')
async def confirm_preview(batch_id:uuid.UUID,request:Request,owner=Depends(require_owner_write),connection=Depends(get_admin_connection)):
    try:data=decode(await bounded_body(request),'application/json')
    except ValueError as error:raise ResearchError(422,'financial-confirmation-required',str(error)) from None
    result=await run_in_threadpool(confirm,connection,batch_id,data,request.headers.get('Idempotency-Key'))
    return JSONResponse(result,headers={'Cache-Control':'no-store'})
