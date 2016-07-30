"""Loads data from the Hansard."""

import collections
import datetime
import json
import logging
import re

from bs4 import BeautifulSoup
import requests
import sqlalchemy as sa
from sqlalchemy import ext
from sqlalchemy import orm
import sqlalchemy.ext.declarative

PS_URL = 'https://api.parliament.nsw.gov.au/api/hansard/search/'

locations = []
with open('name_to_loc.json') as f:
    f = json.load(f)
    for name in f:
        locations.append(name)


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True


def init_db():
    engine = sa.create_engine('sqlite:///hansard.db')
    db_session = orm.scoped_session(
            orm.sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine))
    Base = ext.declarative.declarative_base()
    Base.query = db_session.query_property()
    Base.metadata.drop_all(bind=engine)
    return db_session, Base, engine


db, Base, engine = init_db()

class Hansard(Base):
    __tablename__ = 'hansard'
    id = sa.Column(sa.Integer(), primary_key=True)
    location = sa.Column(sa.String())
    date = sa.Column(sa.Date())
    hits = sa.Column(sa.Integer())
    hids = sa.Column(sa.String())
    text = sa.Column(sa.String())

    def __init__(self, location, date, hits, hids, text):
        self.location = location
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d')
        self.text = ' | '.join(text)
        self.hids = '|'.join(hids)

Base.metadata.create_all(bind=engine)


def load_year(year, session):
    # Fetch the table of contents for a year.
    tocsYear = requests.get(PS_URL + 'year/{}'.format(year))
    for i in tocsYear.json():
        date = i['date']
        # Maps places to [number of hits, {documents}, [text blocks]].
        hits = collections.defaultdict(lambda: [0, set(), []])
        for j in i['Events']:
            # Grab the table of contents.
            tocDocId = j['TocDocId']
            # Fetch the metadata for that sitting.
            metadata = requests.post(PS_URL + 'daily/tableofcontentsbydate/' +
                                     tocDocId)
            metadata = json.loads(metadata.json())
            # DFS over the metadata to find doc IDs.
            docIds = []
            stack = metadata[:]
            while stack:
                x = stack.pop()
                if isinstance(x, str) or isinstance(x, bool):
                    continue

                if 'docid' in x:
                    docIds.append(x['docid'])

                try:
                    for child in x.values():
                        stack.append(child)
                except AttributeError:
                    for child in x:
                        stack.append(child)

            logging.info('Found %d documents for %s.', len(docIds), date)

            # Request all of the documents.
            for upto, docId in enumerate(docIds):
                logging.debug('Requesting document: %s (%.2f%%)', docId,
                              (upto + 1) / len(docIds))
                r = requests.get(PS_URL + '/daily/fragment/' + docId)
                soup = BeautifulSoup(r.text, 'html.parser')
                texts = soup.findAll(text=True)
                visible_texts = filter(visible, texts)
                for text in visible_texts:
                    for location in locations:
                        if location in text.lower():
                            hits[location][0] += 1
                            hits[location][1].add(docId)
                            hits[location][2].append(text)

        # Dump everything for this date.
        for location, (n_hits, hids, texts) in hits.items():
            logging.debug('Inserting %s (%s)', location, n_hits)
            h = Hansard(location, date, n_hits, hids, texts)
            db.add(h)
        db.commit()

if __name__ == '__main__':
    logging.root.setLevel(logging.DEBUG)
    load_year(2015, db)
