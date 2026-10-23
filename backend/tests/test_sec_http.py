from contextlib import contextmanager
import os
import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from app.connectors import OfficialHttp
from app.sec_http import request_gate


@pytest.fixture
def writer_url():
    url=os.getenv('RESEARCH_PG_WRITER_URL')
    if not url:pytest.skip('The shared SEC gate requires disposable PostgreSQL')
    if make_url(url).database!='industry_research_test':raise RuntimeError('Disposable research test DB required')
    return url


def test_missing_contact_fails_before_network_or_database(monkeypatch):
    monkeypatch.delenv('SEC_USER_AGENT',raising=False)
    http=OfficialHttp(sec_gate=lambda:pytest.fail('no request gate before configuration'))
    http.client=httpx.Client(transport=httpx.MockTransport(lambda _:pytest.fail('no network before configuration')))
    with pytest.raises(ValueError,match='SEC_USER_AGENT'):http.get('https://data.sec.gov/test')
    http.close()


def test_redirects_each_pass_gate_and_foreign_redirect_never_receives_contact(monkeypatch):
    monkeypatch.setenv('SEC_USER_AGENT','SyntheticOfflineTest contact@example.invalid')
    requests=[];gates=[]
    @contextmanager
    def gate():
        gates.append(True);yield
    def transport(request):
        requests.append(request)
        if len(requests)==1:return httpx.Response(302,headers={'Location':'https://www.sec.gov/official'})
        return httpx.Response(302,headers={'Location':'https://untrusted.invalid/contact-leak'})
    http=OfficialHttp(sec_gate=gate);http.client.close()
    http.client=httpx.Client(transport=httpx.MockTransport(transport))
    with pytest.raises(ValueError,match='官方 HTTPS'):http.get('https://data.sec.gov/test')
    assert len(requests)==len(gates)==2
    assert all(request.headers['user-agent']=='SyntheticOfflineTest contact@example.invalid' for request in requests)
    http.close()


def test_retry_is_also_gated(monkeypatch):
    monkeypatch.setenv('SEC_USER_AGENT','SyntheticOfflineTest contact@example.invalid')
    monkeypatch.setattr('app.connectors.time.sleep',lambda _:None)
    gates=[]
    @contextmanager
    def gate():gates.append(True);yield
    http=OfficialHttp(sec_gate=gate);http.client.close()
    http.client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(503)))
    with pytest.raises(ValueError,match='503'):http.get('https://data.sec.gov/test')
    assert len(gates)==2
    http.close()


def test_non_sec_page_redirecting_to_sec_also_requires_gate_and_contact(monkeypatch):
    monkeypatch.setenv('SEC_USER_AGENT','SyntheticOfflineTest contact@example.invalid')
    gates=[];requests=[]
    @contextmanager
    def gate():gates.append(True);yield
    def transport(request):
        requests.append(request)
        return httpx.Response(302,headers={'Location':'https://www.sec.gov/official'}) if len(requests)==1 else httpx.Response(200,json={})
    http=OfficialHttp(sec_gate=gate);http.client.close()
    http.client=httpx.Client(transport=httpx.MockTransport(transport))
    assert http.get('https://issuer.example.invalid/filing').status_code==200
    assert len(requests)==2 and len(gates)==1
    assert 'contact@example.invalid' not in requests[0].headers['user-agent']
    assert 'contact@example.invalid' in requests[1].headers['user-agent']
    http.close()


def test_database_gate_is_shared_across_independent_processes(writer_url):
    # Separate real processes/connections, with no external HTTP requests.
    import subprocess,sys,json
    code='''import os,json
from sqlalchemy import create_engine,text
from app.sec_http import request_gate
engine=create_engine(os.environ['RESEARCH_PG_WRITER_URL'])
with request_gate(engine):
    with engine.connect() as c:
        stamp=c.execute(text('SELECT extract(epoch FROM clock_timestamp())')).scalar_one()
    print(json.dumps(float(stamp)),flush=True)
engine.dispose()
'''
    processes=[subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(3)]
    stamps=[]
    try:
        for process in processes:
            stdout,stderr=process.communicate(timeout=30)
            assert process.returncode==0,stderr
            stamps.append(json.loads(stdout))
    finally:
        for process in processes:
            if process.poll() is None:process.kill();process.wait()
    stamps.sort()
    assert all(right-left>=0.49 for left,right in zip(stamps,stamps[1:]))
    # A failed HTTP operation releases the session lock, permitting later work.
    engine=create_engine(writer_url,hide_parameters=True)
    try:
        with pytest.raises(RuntimeError):
            with request_gate(engine):raise RuntimeError('synthetic network interruption')
        with request_gate(engine):pass
    finally:
        engine.dispose()
