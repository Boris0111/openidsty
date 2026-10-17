"""Official HTTP adapters. Parsers are pure; fixtures never enter runtime data."""
import calendar
import csv
import hashlib
import io
import json
import math
import os
import re
import time
from datetime import datetime, date, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET
import httpx
from bs4 import BeautifulSoup
from .registry import source_definitions

UTC = timezone.utc
TAIPEI = timezone(timedelta(hours=8))

def number(value):
    try:
        result=float(str(value).replace(',','').strip().replace('%',''))
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None

def roc_date(value, clock=''):
    digits=re.sub(r'\D','',str(value or ''))
    if len(digits)==7:
        digits=f'{int(digits[:3])+1911:04d}'+digits[3:]
    if len(digits)!=8:
        raise ValueError(f'缺少有效發布日期：{value}')
    dt=datetime.strptime(digits,'%Y%m%d').replace(tzinfo=TAIPEI)
    td=re.sub(r'\D','',str(clock or '')).zfill(6)
    if len(td)==6:
        dt=dt.replace(hour=int(td[:2]),minute=int(td[2:4]),second=int(td[4:]))
    return dt

def rows_from_text(text):
    text=text.lstrip('\ufeff').strip()
    if text.startswith('['):
        rows=json.loads(text)
    elif text.startswith('<') or not text:
        raise ValueError('來源僅回傳 HTML／JavaScript 外殼，沒有資料表')
    else:
        rows=list(csv.DictReader(io.StringIO(text)))
    if not isinstance(rows,list) or not rows or not all(isinstance(r,dict) for r in rows):
        raise ValueError('官方資料格式變動或資料表為空')
    aliases={'SecuritiesCompanyCode':'公司代號','CompanyName':'公司名稱','Date':'出表日期','Year':'年度','Season':'季別','基本每股盈餘':'基本每股盈餘（元）'}
    return [{aliases.get(str(k).strip(),str(k).strip()):v for k,v in row.items()} for row in rows]

def parse_tw(text, kind, url, tracked):
    if kind not in ('announcements','revenue','financials'):
        raise ValueError('此欄位需使用新版研究財務流程，legacy 財報不支援。')
    events,financials=[],[]
    rows=rows_from_text(text)
    required={'announcements':'主旨','revenue':'資料年月','financials':'營業收入'}[kind]
    if '公司代號' not in rows[0] or required not in rows[0]:
        raise ValueError(f'官方表格缺少公司代號或 {required}')
    for r in rows:
        ticker=tracked.get(str(r.get('公司代號','')).strip().zfill(4))
        if not ticker:
            continue
        published=roc_date(r.get('發言日期') or r.get('出表日期'),r.get('發言時間',''))
        name=str(r.get('公司名稱') or ticker)
        base={'ticker':ticker,'url':url,'published_at':published,'raw':r,'lifecycle':'published'}
        if kind=='announcements':
            title=str(r.get('主旨') or '').strip()
            if not title:
                continue
            body=str(r.get('說明') or '').strip()
            # Include content digest: one issuer can file multiple items in the same second.
            digest=hashlib.sha256((title+body).encode()).hexdigest()[:16]
            events.append(dict(base,external_id=f'{ticker}:{published.isoformat()}:{digest}',title=f'{name}：{title}',body=body[:4000],kind='announcement'))
        else:
            if kind=='revenue':
                digits=re.sub(r'\D','',str(r.get('資料年月')))
                if len(digits)!=5:
                    raise ValueError('月營收資料年月格式變動')
                year,month=int(digits[:3])+1911,int(digits[3:])
                period=f'{year}-{month:02d}'
                end=f'{period}-{calendar.monthrange(year,month)[1]:02d}'
                revenue=number(r.get('營業收入-當月營收'))
                yoy=number(r.get('營業收入-去年同月增減(%)'))
                margin,eps,basis=None,None,'monthly'
                label=f'{period} 月營收'
            else:
                year=int(r['年度']); year=year+1911 if year<1911 else year
                quarter=int(r['季別'])
                if quarter not in (1,2,3,4):
                    raise ValueError('季別須為 1–4')
                month=quarter*3
                period=f'{year}-Q{quarter}'
                end=f'{year}-{month:02d}-{calendar.monthrange(year,month)[1]:02d}'
                revenue=number(r.get('營業收入'))
                gross=number(r.get('營業毛利（毛損）淨額'))
                if gross is None:
                    gross=number(r.get('營業毛利（毛損）'))
                margin=gross/revenue*100 if gross is not None and revenue not in (None,0) else None
                eps=number(r.get('基本每股盈餘（元）'))
                yoy=None
                basis='annual' if quarter==4 else 'ytd'
                label=f'{period} '+('全年財報' if quarter==4 else f'累計至第 {quarter} 季財報')
            # Zero is valid; missing fields stay missing, not fabricated.
            financials.append({k:v for k,v in dict(base,period=period,period_end=end,basis=basis,currency='TWD',revenue=revenue*1000 if revenue is not None else None,revenue_yoy=yoy,gross_margin=margin,eps=eps).items() if k!='lifecycle'})
            values=[]
            if revenue is not None:
                values.append(f'營收 {revenue*1000:,.0f} TWD')
            if yoy is not None:
                values.append(f'營收年增率 {yoy:.2f}%')
            if margin is not None:
                values.append(f'毛利率 {margin:.2f}%')
            if eps is not None:
                values.append(f'EPS {eps:.2f} TWD/股')
            basis_zh={'monthly':'單月','ytd':'年度累計','annual':'全年'}[basis]
            events.append(dict(base,external_id=f'{ticker}:{period}:{basis}',title=f'{name}：{label}',body=f'官方欄位整理；期間 {period}，口徑 {basis_zh}。'+'；'.join(values)+'。發布／出表日見來源，未提供的數值保留缺口。',kind='financials'))
    return events,financials

def parse_sec_submissions(payload,ticker,url,reference=None):
    recent=payload.get('filings',{}).get('recent')
    if not isinstance(recent,dict) or 'accessionNumber' not in recent:
        raise ValueError('SEC submissions 格式錯誤')
    output=[]
    cutoff=(reference or date.today())-timedelta(days=120)
    for i,form in enumerate(recent.get('form',[])):
        if form not in {'10-Q','10-K','20-F','6-K','8-K','10-Q/A','10-K/A','8-K/A'}:
            continue
        raw={key:values[i] for key,values in recent.items() if isinstance(values,list) and i<len(values)}
        filed=date.fromisoformat(raw['filingDate'])
        if filed<cutoff:
            continue
        acc=raw['accessionNumber']
        link=f'https://www.sec.gov/Archives/edgar/data/{int(payload["cik"])}/{acc.replace("-", "")}/{raw.get("primaryDocument", acc+"-index.htm")}'
        output.append({'ticker':ticker,'external_id':acc,'title':f'{payload.get("name",ticker)}：{form} 官方申報','body':f'表單 {form}；申報日 {filed}；報告期間 {raw.get("reportDate", "未提供")}；{raw.get("primaryDocDescription", "")}。正文請閱讀來源文件。','published_at':datetime.combine(filed,datetime.min.time(),UTC),'url':link,'kind':'filing','lifecycle':'published','raw':raw})
    return output,[]

def parse_sec_facts(payload,ticker,url,reference=None):
    gaap=payload.get('facts',{}).get('us-gaap')
    if not isinstance(gaap,dict):
        raise ValueError('SEC companyfacts 缺少 US GAAP 資料')
    # Group by exact date range AND accession; never mix a restatement with an older filing.
    groups={}
    tags={'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'],'gross_profit':['GrossProfit'],'cost':['CostOfRevenue','CostOfGoodsAndServicesSold'],'eps':['EarningsPerShareDiluted']}
    for metric,choices in tags.items():
        for tag in choices:
            for unit,values in gaap.get(tag,{}).get('units',{}).items():
                if unit not in ('USD','USD/shares'):
                    continue
                for r in values:
                    if not all(r.get(k) for k in ('start','end','accn','filed')) or r.get('form') not in ('10-Q','10-K','10-Q/A','10-K/A'):
                        continue
                    if date.fromisoformat(r['end'])<(reference or date.today())-timedelta(days=730):
                        continue
                    g=groups.setdefault((r['start'],r['end'],r['accn']),{'values':{},'raw':{},'filed':r['filed']})
                    if metric not in g['values']:
                        g['values'][metric]=number(r['val']); g['raw'][metric]=dict(r,tag=tag,unit=unit)
    records=[]
    for (start,end,acc),g in groups.items():
        days=(date.fromisoformat(end)-date.fromisoformat(start)).days+1
        if days<70 or days>380:
            continue
        basis='quarterly' if days<=110 else 'annual' if days>=340 else 'ytd'
        values=g['values']; revenue=values.get('revenue'); gross=values.get('gross_profit')
        if gross is None and revenue is not None and values.get('cost') is not None:
            gross=revenue-values['cost']
        margin=gross/revenue*100 if gross is not None and revenue not in (None,0) else None
        if not any(v is not None for v in (revenue,margin,values.get('eps'))):
            continue
        records.append({'ticker':ticker,'period':f'{start}/{end}','period_end':end,'basis':basis,'currency':'USD','revenue':revenue,'revenue_yoy':None,'gross_margin':margin,'eps':values.get('eps'),'published_at':datetime.fromisoformat(g['filed']).replace(tzinfo=UTC),'url':f'https://www.sec.gov/Archives/edgar/data/{int(payload["cik"])}/{acc.replace("-", "")}/{acc}-index.htm','raw':{'accession':acc,'metrics':g['raw'],'period_start':start,'period_end':end}})
    # Keep the newest restatement per exact range; compare only similarly sized periods a year apart.
    latest={}
    for r in sorted(records,key=lambda r:(r['published_at'],r['revenue'] is not None,sum(r[k] is not None for k in ('revenue','gross_margin','eps')))):
        latest[(r['period'],r['basis'])]=r
    records=list(latest.values())
    for current in records:
        start,end=[date.fromisoformat(v) for v in current['period'].split('/')]
        for prior in records:
            ps,pe=[date.fromisoformat(v) for v in prior['period'].split('/')]
            if prior['basis']==current['basis'] and abs((end-pe).days-365)<=10 and abs((end-start).days-(pe-ps).days)<=10 and prior['revenue'] not in (None,0) and current['revenue'] is not None:
                current['revenue_yoy']=(current['revenue']/prior['revenue']-1)*100
                current['raw']['yoy_comparison_period']=prior['period']
                break
    return [],records

MONTH_DATE=r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})'

def english_date(text):
    m=re.search(MONTH_DATE,text,re.I)
    return datetime.strptime(' '.join(m.groups()),'%B %d %Y').replace(tzinfo=UTC) if m else None

def ir_event(ticker,title,body,published,url,raw,lifecycle='published'):
    return {'ticker':ticker,'external_id':url,'title':title,'body':body[:4000],'published_at':published,'url':url,'kind':'earnings_call','lifecycle':lifecycle,'raw':raw}

def parse_delta(html,url,reference=None):
    soup=BeautifulSoup(html,'html.parser'); output=[]
    for a in soup.find_all('a',href=True):
        href=urljoin(url,a['href'])
        if not re.search(r'(Analyst|Transcript).*\.pdf',href,re.I):
            continue
        block=a; match=None
        for _ in range(5):
            if not block.parent:
                break
            block=block.parent
            text=block.get_text(' ',strip=True)
            match=re.search(r'\b(\d{2}/\d{2}/20\d{2})\b',text)
            if match:
                break
        if not match:
            continue
        published=datetime.strptime(match[1],'%m/%d/%Y').replace(tzinfo=TAIPEI)
        if published.date()<(reference or date.today())-timedelta(days=400):
            continue
        lifecycle='preview' if published.date()>(reference or date.today()) else 'published'
        quarter=re.search(r'([1-4])Q',text,re.I)
        period=f'{published.year} 年第 {quarter[1]} 季' if quarter else published.strftime('%Y-%m-%d')
        title=f'台達電：{period}法說'+('逐字稿' if 'transcript' in href.lower() else '簡報')
        output.append(ir_event('2308.TW',title,text[:1200],published,href,{'document_url':href,'meeting_date':match[1]},lifecycle))
    if not output:
        raise ValueError('台達 IR 未取得具日期的法說文件；可能為外殼或格式變動')
    return output,[]

def parse_tsmc(html,url,reference=None):
    soup=BeautifulSoup(html,'html.parser')
    # Ignore bogus 1970 datePublished in the site's JSON-LD.
    content=soup.select_one('main') or soup
    text=content.get_text(' ',strip=True)
    date_node=soup.select_one('[class*=phase3-description]')
    published=english_date(date_node.get_text(' ',strip=True) if date_node else text)
    links=[urljoin(url,a['href']) for a in content.find_all('a',href=True) if re.search(r'\.pdf(?:$|\?)',a['href'],re.I)]
    if not published:
        raise ValueError('TSMC IR 未取得可靠的法說發布日期')
    future=published.date()>(reference or date.today())
    if not future and not links:
        raise ValueError('TSMC IR 只見活動文字，沒有已發布文件')
    canonical=soup.find('link',rel='canonical')
    link=canonical['href'] if canonical else url
    title_node=soup.find('meta',property='og:title')
    title=title_node['content'] if title_node else '台積電季度法說'
    return [ir_event('2330.TW',title,text[text.find('Earnings Conference'):][:2000],published,link,{'documents':links,'event_date':published.isoformat(),'date_semantics':'conference_date'},'preview' if future else 'published')],[]

def parse_nvidia_rss(xml,url,reference=None):
    root=ET.fromstring(xml); output=[]
    for item in root.findall('.//item'):
        title=item.findtext('title',''); link=item.findtext('link','')
        if not re.search(r'earnings|financial results',title,re.I) or not link:
            continue
        published=parsedate_to_datetime(item.findtext('pubDate',''))
        if published.tzinfo is None:
            published=published.replace(tzinfo=UTC)
        body=BeautifulSoup(item.findtext('description',''),'html.parser').get_text(' ',strip=True)
        upcoming=bool(re.search(r'upcoming|will be held|will host|scheduled to',title+' '+body,re.I))
        lifecycle='preview' if published.date()>(reference or date.today()) or upcoming else 'published'
        output.append(ir_event('NVDA',title,body,published,link,{'rss_item':ET.tostring(item,encoding='unicode'),'date_semantics':'feed_date'},lifecycle))
    if not output:
        raise ValueError('NVIDIA 活動來源沒有具日期的財報活動資料')
    return output,[]

def parse_microsoft(html,url,reference=None):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style','nav','header','footer']):
        tag.decompose()
    text=soup.get_text(' ',strip=True)
    start=text.find('REDMOND, Wash.')
    if start<0:
        raise ValueError('Microsoft IR 未取得財報新聞稿正文')
    text=text[start:]
    published=english_date(text[:300])
    if not published or published.date()>(reference or date.today()):
        raise ValueError('Microsoft IR 財報尚未發布或日期缺少')
    title=soup.title.get_text(' ',strip=True) if soup.title else '微軟季度財報及 webcast'
    return [ir_event('MSFT',title,text[:4000],published,url,{'excerpt':text[:4000],'document_url':url})],[]

class OfficialHttp:
    def __init__(self,sec_gate=None):
        self.client=httpx.Client(timeout=httpx.Timeout(20,connect=10),follow_redirects=True,headers={'User-Agent':'IndustryFlow/0.1 (public official-information research)','Accept':'application/json,text/html,text/csv,application/xml;q=0.9,*/*;q=0.5'})
        self.last_request=0.0
        self.sec_gate=sec_gate

    def _request(self,url,sec=False):
        from .sec_http import request_gate,validate_sec_url,is_sec,user_agent
        gate=self.sec_gate or request_gate
        sec_chain=sec
        for _ in range(4):
            sec_chain=sec_chain or is_sec(url)
            if sec_chain:
                validate_sec_url(url)
                ua=user_agent()
                with gate():
                    response=self.client.get(url,headers={'User-Agent':ua},follow_redirects=False)
            else:
                response=self.client.get(url,follow_redirects=False)
            if not response.is_redirect:return response
            if not response.headers.get('location'):raise ValueError('來源重新導向沒有目標位址。')
            url=urljoin(url,response.headers.get('location',''))
        raise ValueError('來源重新導向超過限制。')

    def get(self,url,sec=False):
        from .sec_http import is_sec,user_agent,validate_sec_url
        sec=sec or is_sec(url)
        if sec:user_agent()
        if sec:validate_sec_url(url)
        error=None
        for attempt in range(2):
            time.sleep(max(0,0.25-(time.monotonic()-self.last_request)))
            self.last_request=time.monotonic()
            try:
                r=self._request(url,sec)
                r.raise_for_status()
                if len(r.content)>20_000_000:
                    raise ValueError('來源超過 20 MB 上限')
                return r
            except httpx.HTTPError as exc:
                error=exc
                if isinstance(exc,httpx.HTTPStatusError) and exc.response.status_code not in (429,500,502,503,504):
                    break
                if attempt==0:
                    time.sleep(1)
        status=getattr(getattr(error,'response',None),'status_code','')
        detail=str(error)[:300] if not status else f'HTTP {status}'
        raise ValueError(f'HTTP 擷取失敗：{type(error).__name__} {detail}') from error

    def close(self):
        self.client.close()

def official_page_links(html,base_url,hostname,path_pattern):
    """Match the URL path, never a share/mailto query containing a release URL."""
    links=set()
    for a in BeautifulSoup(html,'html.parser').find_all('a',href=True):
        parsed=urlsplit(urljoin(base_url,a['href']))
        if parsed.scheme=='https' and parsed.hostname==hostname and re.fullmatch(path_pattern,parsed.path,re.I):
            links.add(parsed._replace(path=parsed.path.lower(),query='',fragment='').geturl())
    return links

def fetch_source(definition,http,tracked):
    adapter=definition['adapter']; url=definition['url']
    if adapter in ('rss','tpca','moea','census','eia'):
        from .industry_connectors import fetch_industry
        return fetch_industry(definition,http,definition.get('_backfill_days',90))
    if adapter=='tw':
        try:
            r=http.get(url)
            return parse_tw(r.text,definition['kind'],str(r.url),tracked)
        except ValueError:
            if not definition.get('fallback'):
                raise
            r=http.get(definition['fallback'])
            return parse_tw(r.text,definition['kind'],str(r.url),tracked)
    if adapter.startswith('sec-'):
        r=http.get(url,sec=True)
        return (parse_sec_submissions if adapter=='sec-submissions' else parse_sec_facts)(r.json(),definition['ticker'],url)
    r=http.get(url)
    if adapter=='delta':
        return parse_delta(r.text,str(r.url))
    if adapter=='nvidia':
        soup=BeautifulSoup(r.text,'html.parser')
        rss=soup.find('a',href=re.compile(r'/rss/Event',re.I))
        if not rss:
            raise ValueError('NVIDIA IR 外殼沒有可解析的活動 feed')
        feed=http.get(urljoin(url,rss['href']))
        return parse_nvidia_rss(feed.text,str(feed.url))
    if adapter=='microsoft':
        # Follow the newest release linked by the shared investor navigation.
        links=official_page_links(r.text,url,'www.microsoft.com',r'/en-us/investor/earnings/fy-\d{4}-q[1-4]/press-release-webcast/?')
        newest=max(links,key=lambda v:re.search(r'fy-(\d{4})-q([1-4])',v,re.I).groups(),default=url)
        if newest.lower()!=url.lower():
            r=http.get(newest)
        return parse_microsoft(r.text,str(r.url))
    if adapter=='tsmc':
        output=[]; errors=[]
        soup=BeautifulSoup(r.text,'html.parser')
        paths=official_page_links(r.text,url,'investor.tsmc.com',r'/english/quarterly-results/20\d{2}/q[1-4]')
        try:
            output.extend(parse_tsmc(r.text,str(r.url))[0])
        except ValueError as e:
            errors.append(str(e))
        current=soup.find('link',rel='canonical')
        if current:
            paths.discard(current['href'])
        for path in sorted(paths,reverse=True)[:2]:
            try:
                detail=http.get(path)
                output.extend(parse_tsmc(detail.text,str(detail.url))[0])
            except ValueError as e:
                errors.append(str(e))
        if not output:
            raise ValueError('; '.join(errors) or 'TSMC IR 沒有資料')
        # Partial adapters surface warnings as raw metadata, ingester reports partial status.
        for e in output:
            e['raw']['adapter_warnings']=errors
        return output,[]
    raise ValueError('未知 connector')
