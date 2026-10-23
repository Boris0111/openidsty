"""A persisted request budget shared by HTTP, process restarts and Prefect."""
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
from email.utils import parsedate_to_datetime
import hashlib,random,time,ipaddress,socket
from urllib.parse import urlsplit,urljoin
import httpx
from sqlalchemy import text
from .connectors import OfficialHttp
from .payloads import encoded
from .sec_http import request_gate,is_sec,user_agent,validate_sec_url

UTC=timezone.utc


class SourceDeferred(Exception):
    def __init__(self,until,status=429):
        self.until,self.status=until,status
        super().__init__('提供者暫停存取，已保存稍後重試時間。')


class RetryExhausted(ValueError):pass


def provider_key(url):return 'sec' if is_sec(url) else urlsplit(url).hostname


def retry_after(value,now):
    try:
        seconds=max(1,int(value))
        try:return now+timedelta(seconds=seconds)
        except OverflowError:return datetime.max.replace(tzinfo=UTC)
    except (ValueError,TypeError):
        try:result=parsedate_to_datetime(value);return max(result.replace(tzinfo=result.tzinfo or UTC),now+timedelta(seconds=1))
        except (TypeError,ValueError,OverflowError):return now+timedelta(minutes=15)


class RequestBudget:
    def __init__(self,engine,job_id):self.engine,self.job_id=engine,job_id

    def reserve(self,url):
        key=hashlib.sha256(url.encode()).hexdigest();provider=provider_key(url)
        with self.engine.begin() as connection:
            now=connection.execute(text('SELECT clock_timestamp()')).scalar_one()
            backoff=connection.execute(text('SELECT not_before FROM research.source_provider_backoff WHERE provider=:provider'),{'provider':provider}).scalar()
            if backoff and backoff>now:raise SourceDeferred(backoff)
            budget=dict(connection.execute(text('SELECT budget FROM research.source_refresh_jobs WHERE job_id=:id FOR UPDATE'),{'id':self.job_id}).scalar_one())
            item=budget.get(key,{'attempts':0,'url':url})
            if item.get('not_before') and datetime.fromisoformat(item['not_before'])>now:raise SourceDeferred(datetime.fromisoformat(item['not_before']),503)
            if item['attempts']>=4:raise RetryExhausted('此來源請求已用完首次加三次重試，重啟不會重設預算。')
            if sum(row['attempts'] for row in budget.values())>=800:raise RetryExhausted('此來源作業超過 800 次總請求上限。')
            item={**item,'attempts':item['attempts']+1};budget[key]=item
            connection.execute(text("UPDATE research.source_refresh_jobs SET budget=CAST(:budget AS jsonb),dispatch_after=now()+interval '2 minutes',updated_at=now() WHERE job_id=:id"),{'budget':encoded(budget),'id':self.job_id})
        return item['attempts']

    def delay(self,url,until,*,provider=False):
        key=hashlib.sha256(url.encode()).hexdigest()
        with self.engine.begin() as connection:
            budget=dict(connection.execute(text('SELECT budget FROM research.source_refresh_jobs WHERE job_id=:id FOR UPDATE'),{'id':self.job_id}).scalar_one())
            budget[key]={**budget[key],'not_before':until.isoformat()}
            connection.execute(text('UPDATE research.source_refresh_jobs SET budget=CAST(:budget AS jsonb),updated_at=now() WHERE job_id=:id'),{'budget':encoded(budget),'id':self.job_id})
            if provider:connection.execute(text('''INSERT INTO research.source_provider_backoff VALUES(:provider,:until,'HTTP 429')
                ON CONFLICT(provider) DO UPDATE SET not_before=GREATEST(research.source_provider_backoff.not_before,EXCLUDED.not_before)'''),
                {'provider':provider_key(url),'until':until})


def check_host(url,hosts):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None,443):
        raise ValueError('擷取 URL 不在已登錄的官方／公開來源主機。')
    return parsed


def check_url(url,hosts,resolve=socket.getaddrinfo):
    parsed=check_host(url,hosts)
    addresses={row[4][0] for row in resolve(parsed.hostname,443,type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(value).is_global for value in addresses):
        raise ValueError('擷取來源解析至非公開網路，已拒絕。')


class SourceHttp(OfficialHttp):
    def __init__(self,budget,hosts,*,client=None,resolve=socket.getaddrinfo,sleep=time.sleep):
        super().__init__();self.budget,self.hosts,self.resolve,self.sleep=budget,set(hosts),resolve,sleep
        if client is not None:self.client.close();self.client=client
        self.deferred=None;self.last_status=None;self.error_kind=None

    def get(self,url,sec=False):
        sec_chain=sec
        for _ in range(4):
            check_host(url,self.hosts)
            sec_chain=sec_chain or is_sec(url)
            if sec_chain:validate_sec_url(url);ua=user_agent()
            while True:
                try:attempt=self.budget.reserve(url)
                except SourceDeferred as error:self.deferred=error.until;raise
                try:
                    check_url(url,self.hosts,self.resolve)
                    if not sec_chain:
                        self.sleep(max(0,.25-(time.monotonic()-self.last_request)))
                        self.last_request=time.monotonic()
                    started=time.monotonic()
                    gate=request_gate(self.budget.engine) if sec_chain else null_gate()
                    with gate:
                        with self.client.stream('GET',url,headers={'User-Agent':ua} if sec_chain else None,follow_redirects=False,timeout=20) as response:
                            self.last_status=response.status_code;self.error_kind=None
                            if response.status_code==429:
                                self.error_kind='http'
                                until=retry_after(response.headers.get('Retry-After'),datetime.now(UTC))
                                self.budget.delay(url,until,provider=True);self.deferred=until
                                raise SourceDeferred(until)
                            response.raise_for_status() if not response.is_redirect else None
                            chunks=[];size=0
                            for chunk in response.iter_bytes():
                                size+=len(chunk)
                                if size>25*1024*1024 or time.monotonic()-started>20:raise ValueError('來源回應超過大小或時間界線。')
                                chunks.append(chunk)
                            headers={key:value for key,value in response.headers.items() if key not in ('content-encoding','content-length','transfer-encoding')}
                            result=httpx.Response(response.status_code,headers=headers,content=b''.join(chunks),request=response.request)
                    break
                except (httpx.TimeoutException,httpx.NetworkError,httpx.RemoteProtocolError,httpx.HTTPStatusError,socket.gaierror) as error:
                    status=error.response.status_code if isinstance(error,httpx.HTTPStatusError) else None
                    self.last_status=status;self.error_kind='http' if status else 'timeout' if isinstance(error,httpx.TimeoutException) else 'network'
                    if status is not None and status<500 or attempt>=4:raise
                    seconds=(1,4,16)[attempt-1]+random.uniform(0,.25)
                    until=datetime.now(UTC)+timedelta(seconds=seconds)
                    self.budget.delay(url,until)
                    self.sleep(seconds)
            if not result.is_redirect:return result
            if not result.headers.get('location'):raise ValueError('來源重新導向缺少目標。')
            url=urljoin(url,result.headers['location'])
        raise ValueError('來源重新導向超過界線。')

    @contextmanager
    def stream(self,method,url,**kwargs):
        if method!='GET':raise ValueError('來源擷取只允許 GET。')
        response=self.get(url)
        try:yield response
        finally:response.close()


@contextmanager
def null_gate():yield
