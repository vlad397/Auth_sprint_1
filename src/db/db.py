from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import Settings

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

engine = create_engine(
    f'postgresql://{settings.pg_user}:{settings.pg_password}@{settings.host}/{settings.pg_db}',
    convert_unicode=True
)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import db.db_models as db_models
    Base.metadata.create_all(bind=engine)