"""Generates a location density plot."""

import datetime
import json

import matplotlib.pyplot as plt
import numpy
import scipy.ndimage as ndi

import hansard

with open('name_to_loc.json') as f:
    name_to_loc = json.load(f)

res = 100
heatmap = numpy.zeros((19, res, res))
sittings = []
for day in range(1, 20):
    loc_to_hits = {}
    for row in hansard.db.query(hansard.Hansard).filter_by(
                date=datetime.date(2015, 11, day)):
        loc_to_hits[tuple(name_to_loc[row.location])] = row.hits

    lats = []
    lons = []
    hits = []
    for (lat, lon), n in loc_to_hits.items():
        lats.append(lat)
        lons.append(lon)
        hits.append(n)
    if not lats:
        continue
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    hits = numpy.array(hits)

    # Rescale coordinates.
    lats -= lats.min()
    lats /= lats.max()
    lons -= lons.min()
    lons /= lons.max()

    # Generate a heatmap.
    for lat, lon, n in zip(lats, lons, hits):
        x = int(lon * (res - 1))
        y = int(lat * (res - 1))
        heatmap[day - 1, y, x] = n

    # Convolve the heatmap with a Gaussian filter.
    bw = 5
    heatmap[day - 1] = ndi.gaussian_filter(heatmap[day - 1], (bw, bw))

    # Add the day to the list of days sat.
    sittings.append(day - 1)

# Compute the average heatmap.
mean_heatmap = heatmap[sittings].mean(axis=0)
plt.pcolor(mean_heatmap, cmap='inferno')
plt.show()
