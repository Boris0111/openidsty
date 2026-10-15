from pathlib import Path
from decimal import Decimal
import pytest
from app.metric_connectors import parse_aaon,aaon_links,parse_tsmc_metric,tsmc_links

F=Path(__file__).parent/'fixtures/metrics'


@pytest.mark.parametrize('file,value,end,published',[
    ('aaon-q4-2025.html','75300000','2025-12-31','2026-03-02'),
    ('aaon-q1-2026.html','93200000','2026-03-31','2026-05-07'),
])
def test_real_aaon_liquid_sales_not_mixed_business(file,value,end,published):
    row=parse_aaon((F/file).read_text(encoding='utf-8'),'https://investors.aaon.com/investor-news/quarter')[0]
    assert row['value']==Decimal(value) and row['currency']=='USD'
    assert row['period_end'].isoformat()==end and row['published_at'].date().isoformat()==published
    assert row['basis']=='quarterly' and 'liquid cooling' in row['raw_excerpt']


@pytest.mark.parametrize('body',[
    '<strong>Full Year 2025 Results</strong><p>$200 million in BASX-branded liquid cooling sales</p>',
    '<strong>Fourth Quarter 2025 Results</strong><p>BASX total sales of $102.6 million</p>',
    '<strong>2026 Outlook</strong><p>BASX-branded liquid cooling sales of $100 million</p>',
    '<strong>Fourth Quarter 2025 Results</strong><p>BASX-branded liquid cooling sales increased 198.7%</p>',
    '<strong>Fourth Quarter 2025 Results</strong><p>Expected BASX-branded liquid cooling sales of $100 million</p>',
    '<strong>Fourth Quarter 2025 Results</strong><p>Nine months BASX-branded liquid cooling sales of $100 million</p>',
    '<strong>Fourth Quarter 2025 Results</strong><p>BASX-branded liquid cooling sales of C$100 million</p>',
])
def test_aaon_annual_mixed_forecast_and_unquantified_are_not_observations(body):
    with pytest.raises(ValueError):parse_aaon(f'<title>AAON Reports Fourth Quarter 2025 Results</title><article>{body}</article>','https://official.test')


def test_aaon_discovery_keeps_only_official_quarterly_links():
    good='https://investors.aaon.com/investor-news/aaon-reports-first-quarter-2026-results'
    assert aaon_links(f'<a href="{good}">quarter</a><a href="https://example.org/investor-news/aaon-reports-second-quarter-2026-results">external</a><a href="mailto:?body={good}">share</a>',good)==[good]
    assert not aaon_links('<a href="/investor-news/aaon-announces-first-quarter-2026-conference-call-and-webcast">call</a>',good)


def test_quarterly_segment_results_and_inline_amount_are_realized():
    html='<title>AAON Reports Second Quarter 2026 Results</title><article><p>2026 Outlook</p><p>Expected BASX-branded liquid cooling sales of $900 million</p><p>Segment Results</p><p>BASX-branded liquid cooling sales of <strong>$126.6 million</strong>, up 208.4% during the period.</p></article>'
    assert parse_aaon(html,'https://official.test')[0]['value']==Decimal('126600000')


def test_quarter_context_returns_after_outlook_without_using_forecast_or_mixed_sales():
    html='<title>AAON Reports First Quarter 2026 Results</title><article><strong><span>First Quarter</span><span>2026 Results</span></strong><strong>2026 Outlook</strong><p>Expected BASX-branded liquid cooling sales of $900 million</p><p>First‑quarter 2026 results included actual segment sales.</p><p>BASX mixed sales of $120 million. BASX-branded liquid cooling sales of $90 million.</p></article>'
    assert parse_aaon(html,'https://official.test')[0]['value']==Decimal('90000000')


def test_real_tsmc_node_share_has_wafer_denominator_and_quarter():
    row=parse_tsmc_metric((F/'tsmc-q2-2026.html').read_text(encoding='utf-8'),'https://pr.tsmc.com/japanese/news/3326')[0]
    assert row['value']==Decimal('3') and row['unit']=='percent' and row['currency'] is None
    assert row['period_start'].isoformat()=='2026-04-01' and row['period_end'].isoformat()=='2026-06-30'
    assert row['published_at'].date().isoformat()=='2026-07-16' and row['basis']=='quarterly'


@pytest.mark.parametrize('body',[
    '2-nanometer expected to generate 3% of revenue',
    'Outlook: shipments of 2-nanometer accounted for 3% of total wafer revenue',
    'shipments of 2-nanometer accounted for 3% of total company revenue',
    'shipments of 3-nanometer accounted for 30% of total wafer revenue',
])
def test_tsmc_forecast_wrong_denominator_or_no_disclosure_is_gap(body):
    with pytest.raises(ValueError):parse_tsmc_metric(f'<article>second quarter ended June 30, 2026<p>{body}</p></article>','https://official.test')


def test_tsmc_discovery_requires_official_hosts_and_html_releases():
    html='<a href="/english/quarterly-results/2026/q2">Q2</a><a href="https://pr.tsmc.com/japanese/news/3326">Press</a><a href="https://example.org/english/news/123">external</a>'
    quarters,releases=tsmc_links(html,'https://investor.tsmc.com/english/quarterly-results')
    assert quarters==['https://investor.tsmc.com/english/quarterly-results/2026/q2']
    assert releases==['https://pr.tsmc.com/japanese/news/3326']
