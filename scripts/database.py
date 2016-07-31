"""Models for the data processing scripts."""

import os

import sqlalchemy as sa
import sqlalchemy.ext as ext
import sqlalchemy.ext.declarative
import sqlalchemy.orm as orm

engine = sa.create_engine(os.environ['POSTGRES_URI'])
db_session = orm.scoped_session(
        orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine))
Base = ext.declarative.declarative_base()
Base.query = db_session.query_property()

class DateHeat(Base):
    __tablename__ = 'dateheat'
    date = sa.Column(sa.Date(), primary_key=True)
    heat = sa.Column(sa.String())
    peaks = sa.Column(sa.String())
    interest = sa.Column(sa.String())

    def __init__(self, date, heat, peaks, interest):
        self.date = date
        self.heat = heat
        self.peaks = peaks
        self.interest = interest

    def __repr__(self):
        return '<DateHeat {}>'.format(self.date)


class DateLink(Base):
    __tablename__ = 'datelink'
    date = sa.Column(sa.Date(), primary_key=True)
    hid = sa.Column(sa.String())

    def __init__(self, date, hid):
        self.date = date
        self.hid = hid

    def __repr__(self):
        return '<DateLink {} - {}>'.format(self.date, self.hid)
