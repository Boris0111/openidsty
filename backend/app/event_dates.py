"""Repair legacy adapter dates without substituting fetch time for publication."""
from .industry_connectors import parse_date

def normalize_dates(data, adapter):
    data = dict(data)
    if 'published_precision' in data:
        return data
    published = data.get('published_at')
    raw = data.get('raw') or {}
    data.update(published_precision='unknown', date_semantics='unknown', reported_at=None, activity_at=None)
    if adapter=='tw':
        if raw.get('發言日期'):
            data.update(published_precision='minute' if raw.get('發言時間') else 'day', date_semantics='publication')
        else:
            data.update(reported_at=published,published_at=None,date_semantics='report_date')
            # Financial report generation date is not the issuer's release date.
            if data.get('kind')=='financials':
                pieces=data.get('external_id','').split(':')
                if len(pieces)>=3: data.update(period=pieces[-2],basis=pieces[-1])
    elif adapter in ('tsmc','delta'):
        data.update(activity_at=published,published_at=None,date_semantics='activity_date')
    elif adapter in ('sec-submissions','microsoft'):
        data.update(published_precision='day',date_semantics='publication' if published else 'unknown')
    elif adapter=='nvidia':
        data.update(published_precision='minute',date_semantics='publication' if published else 'unknown')
    else:
        # The legacy column does not prove an actual release date.
        data['published_at']=None
    return data
