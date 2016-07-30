"""Loads data from the Hansard."""

import collections
import json
import re

from bs4 import BeautifulSoup
import requests

PS_URL = 'https://api.parliament.nsw.gov.au/api/hansard/search/'

locations = ['Wollondilly']


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def load_year(year):
    # Fetch the table of contents for a year.
    tocsYear = requests.get(PS_URL + 'year/{}'.format(year))
    # Map places to dates to [n hits, {documents}].
    hits = collections.defaultdict(lambda: 
            collections.defaultdict(lambda: [0, set()]))
    for i in tocsYear.json():
        date = i['date']
        for j in i['Events']:
            # Grab the table of contents.
            tocDocId = j['TocDocId']
            # Fetch the metadata for that sitting.
            metadata = requests.post(PS_URL + 'daily/tableofcontentsbydate/' + tocDocId)
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

            # Request all of the documents.
            for docId in docIds:
                r = requests.get(PS_URL + '/daily/fragment/' + docId)
                soup = BeautifulSoup(r.text, 'html.parser')
                texts = soup.findAll(text=True)
                visible_texts = filter(visible, texts)
                for text in visible_texts:
                    for location in locations:
                        if location in text.lower():
                            hits[location][date][0] += 1
                            hits[location][date][1].add(docId)
                print(hits)
                break
            break
        break

load_year(2015)
