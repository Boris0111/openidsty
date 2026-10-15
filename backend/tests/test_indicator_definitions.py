import copy
from pathlib import Path
import pytest
import yaml
from app.indicator_definitions import read_definitions,import_definitions
from app.models import Indicator,ThemeIndicator


def test_fixed_catalog_covers_every_theme_and_reimports(db):
    definitions=read_definitions()
    assert len(definitions)==9 and sum(d['kind']=='direct' for d in definitions)==2
    assert {t for d in definitions for t in d['themes']}=={'liquid-cooling','hbm4','cpo-silicon-photonics','advanced-node-2nm','custom-asic-vs-gpu','800vdc','power-bottleneck'}
    assert import_definitions(db)==import_definitions(db)
    assert db.query(Indicator).count()==9 and db.query(ThemeIndicator).count()==9


@pytest.mark.parametrize('mutation',[
    lambda ds:ds.append(copy.deepcopy(ds[0])),
    lambda ds:ds[0].update(source_id='missing'),
    lambda ds:ds[0].update(themes=['missing']),
    lambda ds:ds[0].update(kind='score'),
    lambda ds:ds[0].update(unit='unknown'),
    lambda ds:ds[0].update(value=123),
    lambda ds:ds[0].update(frequency='annual'),
])
def test_invalid_definitions_do_not_change_projection(db,tmp_path,mutation):
    import_definitions(db);db.commit()
    definitions=read_definitions();mutation(definitions)
    file=tmp_path/'indicators.yaml';file.write_text(yaml.safe_dump({'version':'test','indicators':definitions},allow_unicode=True),encoding='utf-8')
    with pytest.raises(ValueError):import_definitions(db,file)
    assert db.query(Indicator).count()==9 and db.query(ThemeIndicator).count()==9
