import os
os.environ['DATABASE_URL'] = 'sqlite://'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base, get_session
from app.main import app
from app.import_map import import_map

@pytest.fixture
def db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(engine, expire_on_commit=False)() as session:
        import_map(session)
        yield session
    engine.dispose()

@pytest.fixture
def client(db):
    app.dependency_overrides[get_session] = lambda:db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: builds the 3,000-relation scaled dataset; CI still runs it')

@pytest.fixture(scope='session')
def scaled_tree(tmp_path_factory):
    """research_scale's 300-company / 3,000-relation tree, written to a temporary folder."""
    import sys
    from app.config import ROOT
    # The API image ships only the validator scripts, so the PostgreSQL run inside it (research_drill.py
    # pg-check) skips this offline test; CI runs it from the checkout.
    if not (ROOT / 'scripts' / 'research_scale.py').exists():
        pytest.skip('scripts/research_scale.py is not in the API image; CI runs this test from the checkout')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import research_scale
    research_scale.TREE = tmp_path_factory.mktemp('scaled') / 'tree'
    research_scale.build_tree()
    return research_scale.TREE
