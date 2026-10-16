"""Bounded checks of explicitly declared official files; never edits research."""
import hashlib
import io
import re
import time
import unicodedata
from datetime import timedelta,timezone
from urllib.parse import urlsplit,urljoin
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from .models import Source,TechnicalDocument,TechnicalObservation,TechnicalReview,now
from .technical_documents import observation

PARSER_VERSION='technical-text-v1'

def normalize_text(text):
    text=unicodedata.normalize('NFKC',text).replace('\u00ad','')
    text=re.sub(r'(?<=\w)-\s*\n\s*(?=\w)','',text)
    return re.sub(r'\s+',' ',text).strip()

def extract_body(payload,content_type):
    if payload.startswith(b'%PDF'):
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(payload),strict=False)
        if reader.is_encrypted:raise ValueError('加密文件需人工核對')
        pages=[p.extract_text() or '' for p in reader.pages]
        if not pages or sum(map(len,pages))<100:raise ValueError('無可靠文字層，需人工核對')
        # Repeated page furniture is not substantive body content.
        lines=[p.splitlines() for p in pages];counts={}
        for page in lines:
            for line in set(normalize_text(x) for x in page[:3]+page[-3:]):
                counts[line]=counts.get(line,0)+1
        repeated={s for s,n in counts.items() if len(pages)>=3 and n>=max(3,len(pages)*.6)}
        text='\n'.join(line for page in lines for line in page if normalize_text(line) not in repeated and not re.fullmatch(r'\s*(?:Page\s*)?\d+(?:\s*(?:of|/)\s*\d+)?\s*',line,re.I))
    elif 'html' in content_type or payload.lstrip().startswith(b'<'):
        soup=BeautifulSoup(payload,'html.parser')
        if soup.select_one('input[type=password]') or re.search(r'captcha|access denied|just a moment|page not found|service unavailable',soup.title.get_text() if soup.title else '',re.I):
            raise ValueError('登入／阻擋頁，並非文件')
        for element in soup.select('script,style,nav,header,footer,aside,form'):element.decompose()
        main=soup.select_one('main,article,[role=main]')
        if main is None:raise ValueError('沒有可辨識文件主體，需人工核對')
        text=main.get_text(' ',strip=True)
    else:raise ValueError('不支援的文件格式，需人工核對')
    text=normalize_text(text)
    if len(text)<100 or re.search(r'^(?:sign in|log in|access denied)',text,re.I):raise ValueError('文件主體不足，需人工核對')
    return text

def official_version(text,definition):
    cover=text[:6000]
    if definition['id']=='oif-cmis':
        found=re.search(r'(?:CMIS\s*(?:Revision|Version)?\s*|Revision\s+)(\d+\.\d+)',cover,re.I)
        if found:return found[1]
    found=re.search(r'OIF-Co-Packaging-3\.2T-Module-\d+\.\d+',cover,re.I)
    if found:return found[0]
    for version in reversed(definition['versions']):
        label=version['label']
        if label and normalize_text(label).casefold() in text.casefold():return label
    return None

def check_url(url,hosts):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in hosts or parsed.username or parsed.password:
        raise ValueError('文件位址不在宣告的官方 HTTPS host')

def document_links(payload,base,doc,hosts):
    soup=BeautifulSoup(payload,'html.parser')
    if soup.select_one('input[type=password]'):raise ValueError('索引為登入頁')
    patterns={'oif-cmis':r'OIF-CMIS-(\d+)\.(\d+)\.pdf$',
              'oif-cpo-module':r'OIF-Co-Packaging-3\.2T-Module-(\d+)\.(\d+)\.pdf$',
              'ocp-cold-plate-requirements':r'cold-plate.*requirements.*(?:pdf|\.pdf)/?$'}
    pattern=patterns.get(doc.id)
    if not pattern:return []
    found={}
    for a in soup.select('a[href]'):
        url=urljoin(base,a['href']);match=re.search(pattern,urlsplit(url).path,re.I)
        if match:
            check_url(url,hosts)
            order=tuple(int(n) for n in match.groups()) if match.groups() else ()
            found[url]=order
    return sorted(found,key=lambda url:(found[url],url),reverse=True)

def fetch_bounded(client,url,hosts,byte_limit,timeout):
    check_url(url,hosts);started=time.monotonic()
    # Redirects are checked individually before making the next request.
    for _ in range(4):
        with client.stream('GET',url,timeout=timeout,follow_redirects=False) as response:
            if response.is_redirect:
                url=str(response.url.join(response.headers['location']));check_url(url,hosts);continue
            response.raise_for_status()
            if int(response.headers.get('content-length','0'))>byte_limit:raise ValueError('文件超過宣告大小上限')
            chunks=[];size=0
            for chunk in response.iter_bytes():
                size+=len(chunk)
                if size>byte_limit:raise ValueError('文件超過宣告大小上限')
                if time.monotonic()-started>timeout:raise TimeoutError('文件取得超過時間上限')
                chunks.append(chunk)
            return b''.join(chunks),response.headers.get('content-type',''),url
    raise ValueError('文件重新導向過多')

def save_checked(session,doc,payload,content_type,url):
    raw=hashlib.sha256(payload).hexdigest()
    previous=session.scalar(select(TechnicalObservation).where(TechnicalObservation.document_id==doc.id,TechnicalObservation.raw_hash==raw).limit(1))
    if previous:return False # Parser upgrades alone cannot manufacture a version.
    text=extract_body(payload,content_type);version=official_version(text,doc.data)
    content=hashlib.sha256(text.encode()).hexdigest()
    existing=session.scalar(select(TechnicalObservation).where(TechnicalObservation.document_id==doc.id,TechnicalObservation.parser_version!='authored-excerpts-v1').order_by(TechnicalObservation.id.desc()).limit(1))
    if existing and existing.parser_version!=PARSER_VERSION:raise ValueError('解析器版本變動；須先用相同原檔人工核對基準')
    known={v['label'] for v in doc.data['versions']}
    kind='official-version' if version and version not in known else 'content-change-same-version' if version else 'content-change-unversioned'
    row,created=observation(session,doc.id,version,content,PARSER_VERSION,url,{'baseline':False,'change_kind':kind,'published':None,'published_precision':'unknown','read_scope':'自動抽取文字主體；尚未核對其研究影響。','locators':[]},raw)
    return created

def ingest_documents(session,definition,client=None,force=False):
    source=session.get(Source,definition['id']);reference=now()
    try:
        interval=max(24,int(definition.get('interval-hours',24)))
        ids=definition['document-ids'];hosts=definition['allowed-hosts']
        if not isinstance(ids,list) or not ids or not all(isinstance(i,str) for i in ids):raise ValueError('document-ids 設定不合法')
        if not isinstance(hosts,list) or not hosts or not all(isinstance(i,str) for i in hosts):raise ValueError('allowed-hosts 設定不合法')
        bound=min(10,int(definition.get('max-documents',10)))
        if bound<1:raise ValueError('max-documents 須為正整數')
    except (KeyError,TypeError,ValueError) as exc:
        source.status='configuration_required';source.error=f'文件監測設定錯誤：{exc}';source.last_attempt=reference;source.new_count=0;source.data=dict(source.data,last_error_kind='configuration');session.commit()
        return {'status':source.status,'new_count':0,'error':source.error}
    if not force and source.last_attempt and reference-source.last_attempt.replace(tzinfo=source.last_attempt.tzinfo or timezone.utc)<timedelta(hours=interval):
        return {'status':'not_due','new_count':0,'error':None}
    source.last_attempt=reference;session.commit();count=0;successes=0;errors=[]
    own=client is None;client=client or httpx.Client(headers={'User-Agent':'IndustryFlow technical research contact: local-maintainer'},trust_env=True)
    if len(ids)>bound:errors.append('明列文件超過本輪上限，未讀部分需後續核對')
    try:
        indexes=[]
        # One declared source index, no recursive crawling or automatic form submissions.
        if min(2,definition.get('max-pages',2))>0:
            try:
                body,kind,final=fetch_bounded(client,definition['url'],definition['allowed-hosts'],min(2097152,definition.get('html-bytes',2097152)),min(20,definition.get('timeout-seconds',20)))
                if 'html' not in kind:raise ValueError('索引未回傳 HTML')
                indexes.append((body,final))
            except Exception as exc:errors.append(f'官方索引：{type(exc).__name__}: {exc}'[:800])
        for did in ids[:bound]:
            try:
                doc=session.get(TechnicalDocument,did)
                if not doc or doc.source_id!=source.id:raise ValueError('文件定義與來源不一致')
                url=doc.data['versions'][-1]['url']
                candidates=[link for body,base in indexes for link in document_links(body,base,doc,definition['allowed-hosts'])]
                if candidates:url=candidates[0]
                limit=min(15728640,definition.get('document-bytes',15728640))
                if not url.lower().endswith('.pdf') and '-pdf' not in url:limit=min(limit,2097152,definition.get('html-bytes',2097152))
                payload,kind,final=fetch_bounded(client,url,definition['allowed-hosts'],limit,min(20,definition.get('timeout-seconds',20)))
                if (url.lower().endswith('.pdf') or '-pdf' in url) and not payload.startswith(b'%PDF'):raise ValueError('PDF 位址未回傳 PDF；需人工核對，未建立觀測')
                created=save_checked(session,doc,payload,kind,final);session.commit();count+=int(created);successes+=1
            except Exception as exc:
                session.rollback();errors.append(f'{did}: {type(exc).__name__}: {exc}'[:800])
        source=session.get(Source,definition['id']);source.status='partial' if errors and successes else 'failed' if errors else 'success';source.error='；'.join(errors)[:2000] or None;source.new_count=count
        if successes:source.last_success=reference
        session.commit()
        return {'status':source.status,'new_count':count,'error':source.error}
    finally:
        if own:client.close()
