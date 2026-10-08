"""Read-only source probe; saved responses are QA inputs, never runtime data."""
from pathlib import Path
import sys
import concurrent.futures
import httpx
from bs4 import BeautifulSoup

DEST = Path(__file__).resolve().parents[1] / '.work' / 'source-probes'
URLS = {
    'tech-semiconductor': 'https://technews.tw/category/semiconductor/feed/',
    'tech-components': 'https://technews.tw/category/component/feed/',
    'tech-server': 'https://technews.tw/category/pcnotebook/伺服器/feed/',
    'tech-energy': 'https://technews.tw/category/能源科技/feed/',
    'semiengineering': 'https://semiengineering.com/feed/',
    'tpca': 'https://www.tpca.org.tw/web/list_news.php?menu_no=182&mod_no=5',
    'moea': 'https://www.moea.gov.tw/Mns/dos/bulletin/Bulletin.aspx?kind=6&html=1&menu_id=6725',
    'census': 'https://www.census.gov/manufacturing/m3/current/index.html',
    'eia': 'https://www.eia.gov/electricity/monthly/',
    'tpca-detail': 'https://www.tpca.org.tw/web/news_detail.php?menu_no=182&mod_no=5&news_no=500440',
}
def probe(item):
    key, url = item
    try:
        r = httpx.get(url, timeout=25, follow_redirects=True, headers={'User-Agent':'IndustryFlow/0.2 public research'})
        DEST.mkdir(parents=True, exist_ok=True)
        (DEST / f'{key}.txt').write_text(r.text, encoding='utf-8')
        soup = BeautifulSoup(r.text, 'html.parser')
        print(key, r.status_code, str(r.url), len(r.content), soup.get_text(' ', strip=True)[:400], flush=True)
        if key in ('moea','tpca','census','eia'):
            links = [(a.get_text(' ',strip=True)[:100],a['href']) for a in soup.find_all('a',href=True)]
            (DEST / f'{key}-links.txt').write_text('\n'.join(str(l) for l in links), encoding='utf-8')
    except Exception as e:
        print(key, type(e).__name__, str(e)[:200], flush=True)
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(probe, URLS.items()))
