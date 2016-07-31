"""Initialises the (temporary) SQLite3 database to dump location data into."""

import sqlalchemy as sa
import sqlalchemy.ext as ext
import sqlalchemy.ext.declarative
import sqlalchemy.orm as orm

engine = sa.create_engine('sqlite:///hansard_processed.db')
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

    def __init__(self, date, heat):
        self.date = date
        self.heat = heat

    def __repr__(self):
        return '<DateHeat {}>'.format(self.date)

Base.metadata.create_all(bind=engine)
