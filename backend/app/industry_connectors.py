"""Free public feeds and statistical release metadata, with bounded backfill."""
import re
import calendar
import xml.etree.ElementTree as ET
from datetime import datetime, date, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from bs4 import BeautifulSoup

UTC = timezone.utc
TW = timezone(timedelta(hours=8))
MONTHS = '|'.join(calendar.month_name[1:])

def canonical_url(url, provider=''):
    parts = urlsplit(url)
    host = (parts.hostname or '').lower()
    if parts.scheme not in ('http','https') or not host:
        raise ValueError('來源連結不是 HTTP URL')
    if provider=='technews' and host in ('finance.technews.tw','cdn.technews.tw'):
        host = 'technews.tw'
    query = [(k,v) for k,v in parse_qsl(parts.query) if not k.lower().startswith('utm_') and k not in ('fbclid','gclid')]
    return urlunsplit(('https',host,parts.path.rstrip('/')+'/' if not parts.path.split('/')[-1].count('.') else parts.path,urlencode(sorted(query)),''))

def parse_date(value, tz=UTC):
    if not value:
        return None, 'unknown'
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.replace(tzinfo=parsed.tzinfo or tz), 'minute'
    except (ValueError, TypeError):
        pass
    try:
        parsed = datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.replace(tzinfo=parsed.tzinfo or tz), 'day' if len(value.strip())==10 else 'minute'
    except ValueError:
        return None, 'unknown'

def record(title,body,url,published=None,precision='unknown',kind='industry_news',raw=None,**extra):
    return dict(ticker=None, title=title, body=body[:1200], url=url, external_id=canonical_url(url),
        published_at=published, published_precision=precision, date_semantics='publication' if published else 'unknown',
        kind=kind, lifecycle='published', raw=raw or {}, **extra)

def parse_rss(xml, url):
    root = ET.fromstring(xml)
    items = root.findall('.//item')
    if not items:
        raise ValueError('RSS 沒有文章；空 feed 或格式變動')
    result = []
    for item in items:
        title = item.findtext('title','').strip()
        link = item.findtext('link','').strip()
        if not title or not link or re.search(r'VIP|會員限定|付費閱讀',title,re.I):
            continue
        description = BeautifulSoup(item.findtext('description',''),'html.parser').get_text(' ',strip=True)
        published, precision = parse_date(item.findtext('pubDate',''))
        result.append(record(title, description, link, published, precision,
            raw={'feed_url':url,'guid':item.findtext('guid'),'pubDate':item.findtext('pubDate'),'excerpt':description[:1200]}))
    return result

def parse_tpca_list(html, url):
    soup = BeautifulSoup(html,'html.parser')
    result = []
    for item in soup.select('.item-list .item'):
        anchor = item.find('a', href=re.compile(r'news_detail\.php.*news_no=\d+'))
        if not anchor:
            continue
        text = item.get_text(' ',strip=True)
        hit = re.search(r'20\d{2}-\d{2}-\d{2}',text)
        published, precision = parse_date(hit[0] if hit else '', TW)
        title = anchor.get_text(' ',strip=True)
        result.append(record(title,'',urljoin(url,anchor['href']),published,precision,
            raw={'list_url':url,'list_date':hit[0] if hit else None}))
    if not result:
        raise ValueError('TPCA 沒有公開消息清單；外殼或格式變動')
    return result

def parse_technews_list(html,url):
    """Public category excerpts; excludes member articles and never fetches paywalls."""
    soup=BeautifulSoup(html,'html.parser'); result=[]
    for article in soup.select('article.post'):
        anchor=article.select_one('.entry-title a[href]')
        header=article.select_one('.entry-header')
        excerpt=article.select_one('.moreinf')
        if not anchor or not header or not excerpt: continue
        title=anchor.get_text(' ',strip=True)
        if re.search(r'VIP|會員限定|付費閱讀',title,re.I) or article.select_one('.vip, .vip_tag, .vip-only'): continue
        hit=re.search(r'發布日期\s*(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日(?:\s*(\d{1,2}):(\d{2}))?',header.get_text(' ',strip=True))
        pub=None;precision='unknown'
        if hit:
            year,month,day,hour,minute=hit.groups()
            pub=datetime(int(year),int(month),int(day),int(hour or 0),int(minute or 0),tzinfo=TW)
            precision='minute' if hour else 'day'
        for a in excerpt.select('.more-link'): a.decompose()
        body=excerpt.get_text(' ',strip=True)
        result.append(record(title,body,urljoin(url,anchor['href']),pub,precision,
            raw={'list_url':url,'publication_label':hit[0] if hit else None,'excerpt':body[:1200]}))
    if not result: raise ValueError('科技新報分類列表沒有免費公開文章或格式變動')
    return result

def parse_tpca_detail(html):
    soup = BeautifulSoup(html,'html.parser')
    article = soup.select_one('article.html-edit')
    if not article or len(article.get_text(' ',strip=True))<40:
        raise ValueError('TPCA 文章沒有免費公開正文')
    return article.get_text(' ',strip=True)[:1200]

def parse_moea(html,url):
    soup = BeautifulSoup(html,'html.parser')
    content = soup.select_one('#div_Content')
    text = soup.get_text(' ',strip=True)
    period = re.search(r'(\d{3})年(\d{1,2})月工業生產統計',text)
    released = re.search(r'發布日期[：:]\s*(20\d{2}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?',text)
    if not content or not period or not released or '與上月比較' not in content.get_text():
        raise ValueError('經濟部未取得工業生產新聞稿正文或可靠發布日')
    pub, precision = parse_date(released[1]+('T'+released[2] if released[2] else ''),TW)
    key = f'{int(period[1])+1911}-{int(period[2]):02d}'
    return record(f'經濟部 {key} 工業生產統計',content.get_text(' ',strip=True),url,pub,precision,
        kind='official_stats',raw={'dataset':'moea-industrial-production','release_date':released[0],'excerpt':content.get_text(' ',strip=True)[:1200]},
        period=key,basis='台灣工業生產指數；總工業／製造業、年增／月增與季節調整口徑按原文，非純 AI 需求')

def parse_census(html,url):
    soup = BeautifulSoup(html,'html.parser')
    text = soup.get_text(' ',strip=True)
    release = re.search(r'FOR IMMEDIATE RELEASE:\s*\w+,\s*('+MONTHS+r')\s+(\d{1,2}),\s*(20\d{2})',text,re.I)
    content = next((x.get_text(' ',strip=True) for x in soup.select('.richtext') if 'New orders for manufactured goods' in x.get_text()), '')
    period = re.search(r'New orders for manufactured goods in ('+MONTHS+')',content,re.I)
    if not release or not content or not period:
        raise ValueError('Census M3 未取得月報新聞稿與可靠發布日')
    pub = datetime.strptime(' '.join(release.groups()),'%B %d %Y').replace(tzinfo=UTC)
    month = list(calendar.month_name).index(period[1].capitalize())
    year = pub.year - (month > pub.month)
    key = f'{year}-{month:02d}'
    return record(f'Census M3 {key} 製造業訂單／出貨／庫存',content,url,pub,'day','official_stats',
        raw={'dataset':'census-m3-full','release_date':release[0],'excerpt':content[:1200]}, period=key,
        basis='美國製造業總體；訂單、出貨、未交訂單與庫存；季節調整月增，非公司訂單或純 AI 需求')

def parse_census_archive(html,url,reference=None):
    """Archive index metadata only: never invent dates or values from PDF titles."""
    soup = BeautifulSoup(html,'html.parser'); output=[]; seen=set()
    cutoff = (reference or date.today()) - timedelta(days=150)
    for a in soup.find_all('a',href=True):
        href = urljoin(url,a['href'])
        match = re.search(r'/pressreleases/(prel|full)/(20\d{2})/([a-z]{3})\d{2}(?:prel|full)?\.pdf$',href)
        if not match or href in seen:
            continue
        seen.add(href)
        month = list(calendar.month_abbr).index(match[3].capitalize())
        year = int(match[2])
        if date(year,month,1) < cutoff:
            continue
        key = f'{year}-{month:02d}'
        label='先行報告' if match[1]=='prel' else '完整月報'
        output.append(record(f'Census M3 {key} 製造業{label}（索引）','官方歷史索引提供本期報告；發布日期及數值未從索引取得，請閱讀原始報告。',href,
            kind='official_stats',period=key,basis=f'美國製造業{label}；此筆僅索引期別，不擷取 PDF 數值或推定發布日期',
            raw={'dataset':'census-m3-'+('advance' if match[1]=='prel' else 'full'),'index_url':url,'metadata_only':True}))
    return output

def parse_eia(html,url):
    text = BeautifulSoup(html,'html.parser').get_text(' ',strip=True)
    period = re.search(r'Data for ('+MONTHS+r')\s+(20\d{2})',text,re.I)
    release = re.search(r'Release Date:\s*('+MONTHS+r')\s+(\d{1,2}),\s*(20\d{2})',text,re.I)
    if not period or not release or 'Net Generation' not in text:
        raise ValueError('EIA 電力月報缺少期別、發布日或報表內容')
    pub = datetime.strptime(' '.join(release.groups()),'%B %d %Y').replace(tzinfo=UTC)
    key = f'{period[2]}-{list(calendar.month_name).index(period[1].capitalize()):02d}'
    return record(f'EIA {key} Electric Power Monthly',f'美國電力月報資料期間 {key}。官方表格涵蓋淨發電量、燃料、售電及電價；資料集屬電力供需背景，不能等同 AI 資料中心耗電。',url,pub,'day','official_stats',
        raw={'dataset':'eia-electric-power-monthly','release_date':release[0],'data_period':period[0]},period=key,
        basis='美國電力月度統計；發電／售電與各部門口徑，非純 AI 需求；原表單位與初估／修訂見來源')

def fetch_industry(definition,http,backfill_days=90):
    adapter=definition['adapter']; url=definition['url']
    cutoff = datetime.now(UTC) - timedelta(days=backfill_days)
    output=[]; errors=[]; seen=set(); seen_pages=set(); pages=0; oldest=None; boundary=False
    maximum=definition.get('max_pages',1) if definition.get('_backfill',True) else 1
    if adapter in ('rss','tpca'):
        for page in range(1,maximum+1):
            page_url=url
            tech_list=adapter=='rss' and definition.get('provider')=='technews' and page>1
            if tech_list:
                page_url=url.rsplit('/feed/',1)[0]+f'/page/{page}/'
            elif page>1:
                parts=urlsplit(url); params=dict(parse_qsl(parts.query)); params['paged' if adapter=='rss' else 'PageNum']=str(page)
                page_url=urlunsplit(parts._replace(query=urlencode(params)))
            try:
                r=http.get(page_url); pages+=1
                rows=parse_technews_list(r.text,str(r.url)) if tech_list else parse_rss(r.text,str(r.url)) if adapter=='rss' else parse_tpca_list(r.text,str(r.url))
                fingerprint=tuple(sorted(canonical_url(e['url'],definition['provider']) for e in rows))
                if fingerprint in seen_pages:
                    errors.append('來源重複回傳同一頁，已停止歷史分頁'); break
                seen_pages.add(fingerprint)
                fresh=[e for e in rows if canonical_url(e['url'],definition['provider']) not in seen]
                seen.update(canonical_url(e['url'],definition['provider']) for e in fresh)
                dates=[e['published_at'] for e in rows if e['published_at']]
                if dates: oldest=min(dates+[oldest] if oldest else dates)
                if any(dt<cutoff for dt in dates): boundary=True
                for e in fresh:
                    if e['published_at'] and e['published_at'] < cutoff:
                        boundary=True; continue
                    if adapter=='tpca':
                        try:
                            detail=http.get(e['url']); e['body']=parse_tpca_detail(detail.text)
                            e['raw']['excerpt']=e['body']
                        except ValueError as exc:
                            errors.append(str(exc)); continue
                    output.append(e)
                if boundary or (adapter=='rss' and not definition.get('paged')): break
            except Exception as exc:
                errors.append(str(exc)); break
    else:
        r=http.get(url); pages=1
        if adapter=='moea':
            soup=BeautifulSoup(r.text,'html.parser')
            links=list(dict.fromkeys(urljoin(url,a['href']) for a in soup.find_all('a',href=True) if re.search(r'bull_id=\d+',a['href']) and '工業生產統計' in a.get_text()))
            for link in links[:6 if definition.get('_backfill',True) else 1]:
                try:
                    detail=http.get(link); pages+=1; e=parse_moea(detail.text,str(detail.url))
                    if e['published_at']<cutoff: boundary=True; break
                    output.append(e)
                except Exception as exc: errors.append(str(exc))
        elif adapter=='census':
            output=[parse_census(r.text,str(r.url))]
            if definition.get('_backfill',True):
                try:
                    archive=http.get('https://www.census.gov/manufacturing/m3/historical_data/index.html'); pages+=1
                    # Current release has a known date; it takes precedence over metadata-only index.
                    output+= [e for e in parse_census_archive(archive.text,str(archive.url)) if e['period']!=output[0]['period']]
                except Exception as exc: errors.append(str(exc))
        elif adapter=='eia': output=[parse_eia(r.text,str(r.url))]
        else: raise ValueError('未知產業 connector')
    if not output:
        raise ValueError('；'.join(errors) or '來源沒有可用公開內容')
    if errors:
        for e in output: e['raw']['adapter_warnings']=errors
    dated=[e['published_at'] for e in output if e['published_at']]
    if adapter in ('rss','tpca') and definition.get('_backfill',True) and not boundary and pages>=maximum:
        errors.append(f'達到 {maximum} 頁回補上限，尚未觸及 {backfill_days} 日邊界；保留歷史缺口')
        for e in output: e['raw']['adapter_warnings']=errors
    limits={'rss':'以公開 RSS／分類列表可取範圍為限；付費文章不擷取',
        'tpca':'以公開消息列表及免費正文可取範圍為限',
        'moea':'以官方列表最近六期發布為限；保留工業生產口徑',
        'census':'目前完整月報有發布日；歷史索引僅有期別，不推定發布日或 PDF 數值',
        'eia':'本輪僅最新公開月報；未取得歷史發布快照，保留回補缺口'}
    definition['_fetch_meta']={'requested_days':backfill_days,'pages':pages,'cutoff_reached':boundary,
        'oldest_observed':oldest.isoformat() if oldest else min(dated).isoformat() if dated else None,
        'newest_observed':max(dated).isoformat() if dated else None,
        'limit':limits[adapter],
        'warnings':errors}
    return output,[]
