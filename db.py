import os

from sqlalchemy import MetaData, create_engine, Table, Column, ForeignKey, Integer, Date, Text
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base

from babel.dates import format_date

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Issue(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    number = Column(Text, unique=True, nullable=False)
    date = Column(Date, unique=True, nullable=False)

    @property
    def month_name(self):
        return format_date(self.date, 'MMMM', locale='sr')

    @property
    def pdf_path(self):
        return 'issues/{0}/{1}/{1}.pdf'.format(self.date.year, self.number)

    @property
    def cover_path(self):
        return 'issues/{}/{}/cover.png'.format(self.date.year, self.number)


engine = create_engine('sqlite:///' + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3'))
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)
