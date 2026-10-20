from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with Session() as session:
        if session.bind.dialect.name=='postgresql':
            session.connection(execution_options={'isolation_level':'REPEATABLE READ'})
            from sqlalchemy import text
            session.execute(text('SET TRANSACTION READ ONLY'))
        yield session
