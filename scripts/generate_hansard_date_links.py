"""Generates Hansard date links in the database."""

import collections
import datetime
import json

import requests

import database

PS_URL = 'https://api.parliament.nsw.gov.au/api/hansard/search/'


def load():
    years = [2015, 2016]
    for year in years:
        tocsYear = requests.get(PS_URL + 'year/{}'.format(year)).json()
        date_to_hids = collections.defaultdict(list)
        for date_node in tocsYear:
            date = date_node['date']
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            for event in date_node['Events']:
                date_to_hids[date].append({
                    'chamber': event['Chamber'],
                    'event': event['TocDocId'],
                })

        for date in date_to_hids:
            dl = database.DateLink(date, json.dumps(date_to_hids[date]))
            database.db_session.add(dl)
            database.db_session.commit()


if __name__ == '__main__':
    load()
