from collections import deque
from sqlalchemy import select
from .models import Segment, Theme, Company, Relation

LAYERS = {'ai-server': 'AI 伺服器', 'semiconductor': '半導體'}

def segment_relation(source,target):
    """Topology is authoritative; absent explanation is explicitly unreviewed."""
    authored=(source.data.get('downstream-relations') or {}).get(target.id)
    detail=authored or {'summary':'此關係尚未完成技術與證據核對。','items':[],'dependencies':[],'conditions':[],
        'confidence':'needs-verification','evidence':[],'gaps':['舊格式未提供供應項目／需求機制與介面條件，需回原研究核對。'],'reviewed':None}
    return {'id':f'{source.id}:{target.id}','source':source.id,'target':target.id,'source_name':source.name,'target_name':target.name,
        'kind':authored['kind'] if authored else 'unreviewed','direction':'one_way','relation':detail}

def segment_relations(segment,neighbors):
    return [segment_relation(neighbors[sid],segment) for sid in segment.data['upstream']]+[segment_relation(segment,neighbors[sid]) for sid in segment.data['downstream']]

def industry_graph(session, layer):
    segments = {s.id:s for s in session.scalars(select(Segment))}
    inside = {s.id for s in segments.values() if s.layer == layer}
    nodes = set(inside)
    for sid in inside:
        nodes.update(segments[sid].data['upstream'] + segments[sid].data['downstream'])
    edges = []
    for sid in sorted(nodes):
        for target in segments[sid].data['downstream']:
            if target in nodes:
                edges.append(segment_relation(segments[sid],segments[target]))
    return {'layer': layer, 'nodes': [{'id':s.id,'name':s.name,'position':s.position,'external':s.id not in inside,'company_count':len(s.data['companies']),'layer':s.layer} for s in sorted((segments[n] for n in nodes), key=lambda x:(x.position,x.id))], 'edges':edges}

def impact_paths(session, seeds, max_depth=3):
    segments = {s.id:s for s in session.scalars(select(Segment))}
    themes = {t.id:t.data['segments'] for t in session.scalars(select(Theme).where(Theme.active.is_(True)))}
    results, visited = [], set(seeds)
    queue = deque((sid, [sid], 0) for sid in seeds if sid in segments)
    while queue:
        sid, path, depth = queue.popleft()
        if depth >= max_depth:
            continue
        data = segments[sid].data
        moves = [(n, 'upstream') for n in data['upstream']] + [(n,'downstream') for n in data['downstream']]
        for theme in data['themes']:
            moves.extend((n, 'theme', theme) for n in themes.get(theme, []))
        for downstream in data['downstream']:
            moves.extend((n, 'sibling', downstream) for n in segments[downstream].data['upstream'])
        # Record distinct mechanisms even when a target was already reached by another walk.
        for move in moves:
            target, kind = move[:2]
            if target == sid or target not in segments or target in path:
                continue
            item = {'segment': target, 'name':segments[target].name, 'path':path+[target], 'mechanism':kind, 'via':move[2] if len(move)>2 else None, 'confidence':'inference', 'companies':[c['ticker'] for c in segments[target].data['companies']]}
            if not any(r['segment']==target and r['mechanism']==kind for r in results):
                results.append(item)
            if target not in visited:
                visited.add(target)
                queue.append((target, path+[target], depth+1))
    return results

def company_graph(session, ticker, include_candidates=False):
    query = select(Relation)
    if not include_candidates:
        query = query.where(Relation.review_status == 'confirmed')
    relations = list(session.scalars(query))
    direct = [r for r in relations if ticker in (r.source,r.target)]
    neighbors = {ticker} | {n for r in direct for n in (r.source,r.target)}
    edges = [r for r in relations if r.source in neighbors and r.target in neighbors]
    ranking = {'unknown':0, 'low':1,'medium':2,'high':3}
    nodes = []
    for tid in sorted(neighbors):
        company = session.get(Company, tid)
        related = [r for r in direct if tid in (r.source,r.target)]
        grade = max((r.relevance for r in related), key=lambda g:ranking[g], default='unknown')
        nodes.append({'id':tid,'name':company.name,'center':tid==ticker,'relevance':grade,'size':72 if tid==ticker else {'high':62,'medium':48,'low':36,'unknown':32}[grade]})
    return {'center':ticker,'include_candidates':include_candidates,'nodes':nodes,'edges':[dict(r.data, id=r.id, color_role='partner' if r.kind=='partner' else 'upstream' if r.target==ticker else 'downstream' if r.source==ticker else 'supply') for r in edges]}
