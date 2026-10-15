"""Project existing official Financial values; never fetch a source again."""
import calendar,json
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from .models import Financial,Indicator,ThemeIndicator
from .observations import save_observation


def runtime_source_id(definition):
    sid=definition['source_id']
    return f'{sid}-{definition["entity"].lower()}' if sid=='sec-facts' else sid


def financial_observation(row,definition):
    if row.basis!=definition['basis'] or row.revenue is None:return None
    end=date.fromisoformat(row.period_end)
    if row.basis=='monthly':
        if row.period!=end.strftime('%Y-%m') or end.day!=calendar.monthrange(end.year,end.month)[1]:return None
        start=end.replace(day=1)
    elif row.basis=='quarterly':
        # SEC exact fiscal ranges; never synthesize a calendar quarter from FY labels.
        try:start,period_end=map(date.fromisoformat,row.period.split('/'))
        except (ValueError,TypeError):return None
        if period_end!=end or not 70<=(end-start).days+1<=110:return None
    else:return None
    if row.currency!=definition['currency']:return None
    raw=row.raw or {}
    original_period=raw.get('original_period') or row.period
    return dict(indicator_id=definition['id'],source_id=row.source_id,document_identity=f'financial:{row.ticker}:{row.period}:{row.basis}',dataset=definition['dataset'],entity=row.ticker,original_period=original_period,period_start=start,period_end=end,basis=row.basis,scope=definition['scope'],unit=definition['unit'],currency=row.currency,value=Decimal(str(row.revenue)),published_at=row.published_at if row.source_id.startswith('sec-') else None,reported_at=None if row.source_id.startswith('sec-') else row.published_at,published_precision='day' if row.source_id.startswith('sec-') else 'unknown',date_semantics='publication' if row.source_id.startswith('sec-') else 'report_release',fetched_at=row.fetched_at,url=row.url,raw_excerpt=json.dumps(raw.get('metrics',{}).get('revenue') or {k:raw[k] for k in ('資料年月','年度','季別','營業收入-當月營收') if k in raw},ensure_ascii=False),raw={'financial_id':row.id,'official_raw':raw})


def project_financials(session):
    count=0
    for indicator in session.scalars(select(Indicator).where(Indicator.kind=='proxy',Indicator.id.in_(select(ThemeIndicator.indicator_id)))):
        d=indicator.data
        if d['measure']!='revenue':continue
        for row in session.scalars(select(Financial).where(Financial.ticker==d['entity'],Financial.source_id==runtime_source_id(d),Financial.basis==d['basis']).order_by(Financial.period_end,Financial.id)):
            observation=financial_observation(row,d)
            if observation:count+=save_observation(session,observation)
    session.flush()
    return count


if __name__=='__main__':
    from .db import Session,engine
    from .ingest import ingestion_lock
    from .indicator_definitions import import_definitions
    with ingestion_lock(engine) as acquired:
        if not acquired:print({'status':'skipped_overlap'})
        else:
            with Session() as session:
                print(dict(import_definitions(session),new_observations=project_financials(session)));session.commit()
