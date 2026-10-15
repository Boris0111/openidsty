"""Pure parsers for explicitly labeled, realized product metrics."""
import calendar,json,re
from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from .connectors import english_date

QUARTERS={'first':1,'second':2,'third':3,'fourth':4}
UTC=timezone.utc


def release_date(soup,text):
    for node in soup.find_all('script',type='application/ld+json'):
        try:
            payload=json.loads(node.string or node.get_text())
            entries=payload if isinstance(payload,list) else [payload]
            for entry in entries:
                value=entry.get('datePublished') if isinstance(entry,dict) else None
                if value:
                    day=date.fromisoformat(str(value)[:10])
                    if day.year>=2000:return datetime.combine(day,datetime.min.time(),UTC)
        except (ValueError,TypeError):pass
    match=re.search(r'Issued\s+on\s*:?\s*(20\d{2})[/-](\d{1,2})[/-](\d{1,2})',text,re.I)
    if match:return datetime(*map(int,match.groups()),tzinfo=UTC)
    return english_date(text)


def observation(indicator_id,source_id,url,year,quarter,value,unit,currency,scope,excerpt,published):
    month=quarter*3
    start=date(year,month-2,1);end=date(year,month,calendar.monthrange(year,month)[1])
    return dict(indicator_id=indicator_id,source_id=source_id,document_identity=url,dataset='aaon-liquid-cooling-sales' if source_id=='aaon-earnings-metrics' else 'tsmc-node-revenue-share',entity='AAON' if source_id=='aaon-earnings-metrics' else '2330.TW',original_period=f'{year} Q{quarter}',period_start=start,period_end=end,basis='quarterly',scope=scope,unit=unit,currency=currency,value=value,published_at=published,reported_at=None,published_precision='day' if published else 'unknown',date_semantics='publication' if published else 'unknown',url=url,raw_excerpt=excerpt,raw={'source_label':excerpt,'source_period':f'{year} Q{quarter}'})


def parse_aaon(html,url):
    soup=BeautifulSoup(html,'html.parser')
    content=soup.select_one('#hs_cos_wrapper_post_body') or soup.select_one('.post__body') or soup.find('article')
    if not content:raise ValueError('AAON 沒有可解析的公告正文')
    text=content.get_text(' ',strip=True)
    published=release_date(soup,text)
    title=(soup.title.get_text(' ',strip=True) if soup.title else '')
    title_match=re.search(r'(first|second|third|fourth)\s+quarter(?:\s+and\s+full\s+year|\s+of)?\s+(20\d{2})',title,re.I)
    if not title_match:raise ValueError('AAON 公告缺少明確季度與年度')
    quarter,year=QUARTERS[title_match[1].lower()],int(title_match[2])
    active=None;hits=[]
    heading=re.compile(r'^(first|second|third|fourth)\s+quarter(?:\s+(?:of|financial))?\s*(20\d{2})?\s*(?:financial\s+)?results$',re.I)
    money=r'(?<![A-Za-z])\$\s*(\d+(?:\.\d+)?)\s*(million|billion|thousand)'
    label=r'BASX[\s-]+branded\s+liquid\s+cooling(?:\s+product)?\s+sales'
    # Leaf strings preserve explicit annual/quarter headings in HubSpot rich text.
    visited=set()
    for leaf in content.find_all(string=True):
        # Inline emphasis may split the amount from its product label.
        block=leaf.find_parent(['p','li','h1','h2','h3','h4'])
        node=block if block and block in content.descendants else leaf
        if id(node) in visited:continue
        visited.add(id(node))
        if node.parent.name in ('script','style'):continue
        value=re.sub(r'\s+',' ',node.get_text(' ',strip=True) if block else str(node)).replace('\u2011','-').replace('\u2013','-').strip()
        section=heading.fullmatch(value)
        if section:
            active=(int(section[2] or year),QUARTERS[section[1].lower()]);continue
        if value.lower()=='segment results' and not re.search('full.year',title,re.I):
            active=(year,quarter);continue
        if re.match(r'^(?:full\s+year|nine\s+months|six\s+months).*results$',value,re.I) or re.match(r'^.*outlook$',value,re.I):
            active=None;continue
        period=re.search(r'(?:for|in)\s+the\s+(first|second|third|fourth)\s+quarter\s+of\s+(20\d{2})',value,re.I)
        if not period:period=re.search(r'(first|second|third|fourth)[\s-]+quarter\s+(?:of\s+)?(20\d{2})\s+results',value,re.I)
        if period and (int(period[2]),QUARTERS[period[1].lower()])==(year,quarter):
            active=(year,quarter)
        if active!=(year,quarter):continue
        if re.search(r'\b(?:expects?|expected|forecast|guidance|projected|year.to.date|nine.months|six.months|full.year)\b',value,re.I):continue
        if re.search(r'\b(?:CAD|EUR|TWD)\b',value,re.I):continue
        for pattern in (money+r'\s+in\s+'+label,label+r'\s+of\s+'+money):
            for match in re.finditer(pattern,value,re.I):
                amount,scale=match.groups()
                number=Decimal(amount)*{'million':10**6,'billion':10**9,'thousand':10**3}[scale.lower()]
                hits.append((number,match[0]))
    unique={number for number,_ in hits}
    if len(unique)!=1:raise ValueError('AAON 當季缺少唯一可辨識的 BASX 液冷產品數值；不使用混合收入或累計')
    value,excerpt=hits[0]
    return [observation('aaon-liquid-cooling-revenue','aaon-earnings-metrics',url,year,quarter,value,'amount','USD','BASX-branded liquid cooling sales，具名公司特定產品',excerpt,published)]


def aaon_links(html,base_url):
    result={}
    for a in BeautifulSoup(html,'html.parser').find_all('a',href=True):
        url=urljoin(base_url,a['href']);parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.hostname!='investors.aaon.com' or not parsed.path.startswith('/investor-news/aaon-reports-') or 'results' not in parsed.path:continue
        match=re.search(r'(first|second|third|fourth)-quarter(?:-and-full-year|-of)?-(20\d{2})',parsed.path,re.I)
        if match:result[url.split('#')[0]]=(int(match[2]),QUARTERS[match[1].lower()])
    return sorted(result,key=lambda url:result[url],reverse=True)


def fetch_aaon(definition,http,reference=None):
    reference=reference or date.today();base=definition['url'].rstrip('/')
    backfill=definition.get('_backfill',False)
    days=definition.get('_requested_backfill_days') or definition.get('history_days',730)
    cutoff=reference-timedelta(days=days)
    max_reports=min(definition.get('max_reports',8),8) if backfill else 2
    links=[];pages=0
    for page in range(1,min(definition.get('max_pages',5),5)+1 if backfill else 2):
        response=http.get(base if page==1 else f'{base}/page/{page}')
        pages+=1
        found=aaon_links(response.text,str(response.url))
        previous=len(links);links=list(dict.fromkeys(links+found))
        if len(links)>=max_reports or len(links)==previous:break
    if not links:raise ValueError('AAON 索引沒有季度公告')
    records=[];warnings=[]
    for url in links[:max_reports]:
        try:
            response=http.get(url);rows=parse_aaon(response.text,str(response.url))
            records.extend(r for r in rows if cutoff<=r['period_end']<=reference and (not r['published_at'] or r['published_at'].date()<=reference))
        except Exception as exc:warnings.append(f'{url}: {type(exc).__name__}: {exc}')
    definition['_fetch_meta']={'requested_days':days,'pages':pages,'reports':min(len(links),max_reports),'oldest_observed':min((r['period_end'].isoformat() for r in records),default=None),'newest_observed':max((r['period_end'].isoformat() for r in records),default=None),'cutoff_reached':False,'limit':'最多 5 索引頁／8 季，僅可辨識產品欄位；不宣稱完整兩年','warnings':warnings}
    if not records:raise ValueError('AAON 未取得有效季度液冷數值；'+'；'.join(warnings))
    return records


def parse_tsmc_metric(html,url):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup(['script','style','nav']):
        if node.name!='script' or node.get('type')!='application/ld+json':node.decompose()
    text=soup.get_text(' ',strip=True)
    period=re.search(r'(?:for\s+the\s+)?(first|second|third|fourth)\s+quarter\s+ended\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})',text,re.I)
    if not period:raise ValueError('TSMC 缺少明確當季起迄依據')
    quarter=QUARTERS[period[1].lower()]
    end=datetime.strptime(' '.join(period.groups()[1:]),'%B %d %Y').date()
    if end.month!=quarter*3 or end.day!=calendar.monthrange(end.year,end.month)[1]:raise ValueError('TSMC 季別與期末不一致')
    # Require the realized shipment denominator, not an outlook/table forecast.
    match=re.search(r'shipments\s+of\s+2[\s-]*nanometer\s+accounted\s+for\s+(\d+(?:\.\d+)?)\s*%\s+of\s+total\s+wafer\s+revenue',text,re.I)
    if not match:raise ValueError('TSMC 未揭露可辨識的當季 2nm 晶圓營收占比')
    preceding=text[max(0,match.start()-180):match.start()]
    if re.search(r'expect|forecast|outlook|projected',preceding,re.I):raise ValueError('TSMC 預估不能當已實現占比')
    value=Decimal(match[1])
    if not Decimal(0)<=value<=Decimal(100):raise ValueError('TSMC 占比超出有效範圍')
    published=release_date(soup,text)
    return [observation('tsmc-2nm-wafer-revenue-share','tsmc-node-metrics',url,end.year,quarter,value,'percent',None,'當季已實現 2nm 收入占晶圓營收的比例',match[0],published)]


def tsmc_links(html,base_url):
    quarter_pages={};releases=set()
    for a in BeautifulSoup(html,'html.parser').find_all('a',href=True):
        url=urljoin(base_url,a['href']);parsed=urlsplit(url)
        if parsed.scheme!='https':continue
        match=re.fullmatch(r'/english/quarterly-results/(20\d{2})/q([1-4])/?',parsed.path,re.I)
        if parsed.hostname=='investor.tsmc.com' and match:quarter_pages[url]=(int(match[1]),int(match[2]))
        elif parsed.hostname=='pr.tsmc.com' and re.fullmatch(r'/(?:english|japanese)/news/\d+/?',parsed.path):releases.add(url)
    return sorted(quarter_pages,key=lambda url:quarter_pages[url],reverse=True),sorted(releases)


def fetch_tsmc_metric(definition,http,reference=None):
    reference=reference or date.today();backfill=definition.get('_backfill',False)
    days=definition.get('_requested_backfill_days') or definition.get('history_days',730)
    cutoff=reference-timedelta(days=days);maximum=min(definition.get('max_reports',8),8) if backfill else 2
    response=http.get(definition['url']);pages=1
    quarters,releases=tsmc_links(response.text,str(response.url))
    warnings=[];errors=[]
    for url in quarters[:min(maximum,definition.get('max_pages',8))]:
        try:
            detail=http.get(url);pages+=1
            _,found=tsmc_links(detail.text,str(detail.url));releases+=found
        except Exception as exc:errors.append(exc);warnings.append(f'{url}: {type(exc).__name__}: {exc}')
    records=[]
    for url in list(dict.fromkeys(releases))[:maximum]:
        try:
            detail=http.get(url);pages+=1
            records.extend(r for r in parse_tsmc_metric(detail.text,str(detail.url)) if cutoff<=r['period_end']<=reference and (not r['published_at'] or r['published_at'].date()<=reference))
        except Exception as exc:errors.append(exc);warnings.append(f'{url}: {type(exc).__name__}: {exc}')
    definition['_fetch_meta']={'requested_days':days,'pages':pages,'reports':min(len(set(releases)),maximum),'oldest_observed':min((r['period_end'].isoformat() for r in records),default=None),'newest_observed':max((r['period_end'].isoformat() for r in records),default=None),'cutoff_reached':False,'limit':'近兩年、最多 8 季官方新聞稿；只取可辨識當季占比','warnings':warnings}
    if not records:
        raise ValueError('TSMC 未取得有效當季 2nm 占比；'+'；'.join(warnings)) from (errors[-1] if errors else None)
    return records


def fetch_metrics(definition,http):
    if definition['adapter']=='aaon-metrics':return fetch_aaon(definition,http)
    if definition['adapter']=='tsmc-metrics':return fetch_tsmc_metric(definition,http)
    raise ValueError('未知指標來源 adapter')
