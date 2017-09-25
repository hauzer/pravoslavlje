import os

from sqlalchemy import MetaData, create_engine, Table, Column, ForeignKey, Integer, Date, Text
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Issue(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    number = Column(Text, unique=True, nullable=False)
    date = Column(Date, unique=True, nullable=False)


engine = create_engine('sqlite:///' + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3'))
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)
