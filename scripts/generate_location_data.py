"""Dumps location data to a SQLite3 database."""

import collections
import datetime
import json

import numpy

import hansard
import sqlalchemy as sa


def generate_heatmap_data():
    """Generates all heatmap data."""
    # Fetch all dates.
    dates = list(hansard.db.query(hansard.Hansard.date).distinct())
    # Fetch all locations.
    with open('name_to_loc.json') as f:
        loc_to_pos = json.load(f)
        locations = sorted(loc_to_pos.keys())
    # Assign each location an ID based on its index.
    loc_to_id = {j:i for i, j in enumerate(locations)}
    # Generate a NumPy array of dates x locations.
    data = numpy.zeros((len(dates), len(locations)))
    # For each date and location, count Hansard items.
    for i, (date,) in enumerate(dates):
            results = hansard.Hansard.query.filter_by(
                date=date).all()
            for result in results:
                j = loc_to_id[result.location]
                data[i, j] += result.hits
    # Compute the mean heatmap.
    mean = data.mean(axis=0)
    # Divide out to normalise.
    data /= mean + 1
    # For each date, dump to a mildly horrifying JSON string. Then store in the
    # database!
    for i, date in enumerate(dates):
        # [{name, lat, lon, weight}]
        lst = []
        for j, location in enumerate(locations):
            if data[i, j] != 0:
                lat, lon = loc_to_pos[location]
                lst.append({
                    'name': location,
                    'lat': lat,
                    'lon': lon,
                    'weight': data[i, j],
                })
        print(date, lst)
        break


if __name__ == '__main__':
    generate_heatmap_data()
