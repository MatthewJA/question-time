"""Reads the PSMA locations and converts them into town/location pairs."""

import csv
import json
import re
import sys

import numpy

csv.field_size_limit(sys.maxsize)

name_to_loc = {}  # Maps names to location tuples.
loc_regex = re.compile(r'-?\d+\.\d+ -?\d+\.\d+')
with open('suburb_locality_nsw.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['nsw_loca_2']
        geom = [[float(j) for j in i.split()]
                for i in loc_regex.findall(row['geom'])]
        loc = tuple(numpy.array(geom).mean(axis=0))
        name_to_loc[name.lower()] = loc

with open('name_to_loc.json', 'w') as f:
    json.dump(name_to_loc, f)
