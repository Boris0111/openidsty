"""Deterministic content evidence. Company roles never create direct matches."""
import re
from functools import lru_cache
import yaml
from sqlalchemy import select, delete
from .config import DATA_DIR
from .models import EventSegment, EventTheme

def term_pattern(term):
    pattern = re.escape(term).replace(r'\ ', r'[\s-]*')
    if term.isascii():
        pattern = r'(?<![A-Za-z0-9])' + pattern + r'(?![A-Za-z0-9])'
    return re.compile(pattern, re.I)

@lru_cache(maxsize=1)
def rules():
    return yaml.safe_load((DATA_DIR / 'classification-rules.yaml').read_text(encoding='utf-8'))

def matches(text, terms):
    evidence = []
    for term in terms:
        hit = term_pattern(term).search(text)
        if hit and re.search(r'(?:沒有|不涉及|無關|並非|非)\s*$',text[max(0,hit.start()-8):hit.start()]):
            continue
        if hit:
            evidence.append({'term':term, 'matched':hit[0], 'excerpt':text[max(0,hit.start()-65):hit.end()+95]})
    return evidence

def classify(title, body, kind):
    config = rules()
    text = title + '\n' + body
    context_text = re.sub(r'(?:沒有|不涉及|無關)[^\n。.!?！？;；]*','',text)
    routine = kind in ('financials','earnings_call') or (kind=='filing' and bool(re.search(r'10-[QK]|20-F',title))) or bool(matches(title, config['routine_titles']))
    result = {'segments':{}, 'themes':{}, 'routine':routine, 'version':config['version']}
    if routine or matches(title, config['software_titles']):
        return result
    relevance = 'background' if kind=='official_stats' else 'direct'
    for group in ('segments','themes'):
        for key, rule in config[group].items():
            evidence = matches(text, rule['terms'])
            if evidence and (not rule.get('context') or matches(context_text, rule['context'])):
                result[group][key] = {'relevance':relevance, 'evidence':evidence}
    return result

def classify_event(session, event):
    result = classify(event.title, event.body, event.kind)
    event.routine = result['routine']
    event.rules_version = result['version']
    for model, field, group in [(EventSegment,'segment_id','segments'),(EventTheme,'theme_id','themes')]:
        session.execute(delete(model).where(model.event_id==event.id))
        for key, evidence in result[group].items():
            session.add(model(event_id=event.id, **{field:key}, **evidence))
    return result
