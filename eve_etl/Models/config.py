from sqlalchemy import Column, Integer, String

from eve_etl.Common.Storage import base


class ConfigModel(base):
    __tablename__ = "config"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    value = Column(String(4096))


base.metadata.create_all()
