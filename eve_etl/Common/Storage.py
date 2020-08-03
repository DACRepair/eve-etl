from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from eve_etl.Common import config


engine = create_engine(config.get("Storage", "uri"))
base = declarative_base(bind=engine)


def session(bind=engine):
    sesmkr = sessionmaker(bind=bind)
    if str(bind.url).lower().startswith("sqlite"):
        return sesmkr()
    else:
        return scoped_session(sesmkr)()
