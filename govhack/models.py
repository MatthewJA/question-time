import sqlalchemy as sa
import sqlalchemy.ext as ext
import sqlalchemy.ext.declarative
import sqlalchemy.orm as orm
from database import Base


class InterestingTrend():
    def __init__(self, title, description):
        self.title = title
        self.description = description

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description
        }
        
    @staticmethod
    def from_dict(dct):
        return InterestingTrend(dct['title'], dct['description'])

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