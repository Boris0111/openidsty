"""Reindex preserved events against published stable identities; no fetching or publishing."""
import argparse,json
from collections import defaultdict
from sqlalchemy import select,text
from sqlalchemy.orm import Session
from .research_db import writer_engine
from .models import Event,Source
from .source_ingestion import company_mappings,link_events


def reindex(engine=None,after=0,limit=100000):
    engine=engine or writer_engine();last=after;count=0
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as guard:
        if not guard.execute(text('SELECT pg_try_advisory_lock(38109081)')).scalar_one():return {'status':'skipped_overlap'}
        try:
            with Session(engine) as session:
                release=session.execute(text("SELECT h.release_id FROM research.release_head h JOIN research.research_releases r USING(release_id) WHERE r.status='published'")).scalar_one_or_none()
                if not release:return {'status':'no_published_release','indexed':0}
                mapping=company_mappings(session,release)
                definitions={source.id:{**(source.data or {}),'id':source.id} for source in session.scalars(select(Source))}
                while count<limit:
                    batch=list(session.scalars(select(Event).where(Event.id>last).order_by(Event.id).limit(min(500,limit-count)).with_for_update()))
                    if not batch:break
                    grouped=defaultdict(list)
                    for event in batch:grouped[event.source_id].append(event)
                    for sid,events in grouped.items():link_events(session,definitions.get(sid,{'id':sid}),None,mapping,release,events=events)
                    last=batch[-1].id;count+=len(batch);session.commit()
                more=session.execute(select(Event.id).where(Event.id>last).limit(1)).first() is not None
                return {'status':'complete' if not more else 'partial','indexed':count,'last_id':last,'truncated':more,'mapping_release_id':str(release)}
        finally:
            try:guard.execute(text('SELECT pg_advisory_unlock(38109081)'))
            except Exception:guard.invalidate()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--after',type=int,default=0);parser.add_argument('--limit',type=int,default=100000)
    args=parser.parse_args()
    if args.after<0 or not 1<=args.limit<=100000:parser.error('after must be nonnegative and limit 1..100000')
    print(json.dumps(reindex(after=args.after,limit=args.limit)))


if __name__=='__main__':main()
