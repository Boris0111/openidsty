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
