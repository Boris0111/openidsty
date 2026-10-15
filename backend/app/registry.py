"""The canonical registry is shared by research links and runtime adapters."""
from pathlib import Path
import yaml
from .config import MAP_DIR

def canonical_sources(path: Path = MAP_DIR / 'sources.yaml'):
    registry = yaml.safe_load(path.read_text(encoding='utf-8'))
    return [dict(entry, market=market) for market, groups in registry.items() for entries in groups.values() for entry in entries]

def source_definitions(companies, path: Path = MAP_DIR / 'sources.yaml'):
    registry = yaml.safe_load(path.read_text(encoding='utf-8'))
    definitions = []
    for market, groups in registry.items():
        for entries in groups.values():
            for entry in entries:
                config = entry.get('ingestion', {'adapter':'manual'})
                base = dict(entry, market=market, **config)
                base['registry_url'] = entry['url']
                if config.get('per_company'):
                    for company in companies:
                        if company.cik:
                            definitions.append(dict(base, id=f'{entry["id"]}-{company.ticker.lower()}',
                                name=f'{entry["name"]} {company.name}', ticker=company.ticker,
                                url=config['url'].format(cik=company.cik)))
                else:
                    definitions.append(base)
    return definitions
