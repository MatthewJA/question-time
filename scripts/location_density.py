"""Generates a location density plot."""

import collections
import datetime
import json

import matplotlib.pyplot as plt
import numpy
import scipy.ndimage as ndi
import scipy.ndimage.filters
import scipy.ndimage.morphology

import hansard

with open('name_to_loc.json') as f:
    name_to_loc = json.load(f)

min_lat = min(lat for lat, _ in name_to_loc.values())
max_lat = max(lat for lat, _ in name_to_loc.values())
min_lon = min(lon for _, lon in name_to_loc.values())
max_lon = max(lon for _, lon in name_to_loc.values())

# Rescale coordinates.
for name, (lat, lon) in name_to_loc.items():
    lat -= min_lat
    lat /= max_lat - min_lat
    lon -= min_lon
    lon /= max_lon - min_lon
    name_to_loc[name] = (lat, lon)

# min_lat = -34.107
# max_lat = -33.551
# min_lon = 150.645
# max_lon = 151.403

res = 200
bw = 2


def generate_heatmap(date):
    heatmap = numpy.zeros((res, res))
    # Query for this date.
    name_to_hits = {}
    for row in hansard.db.query(hansard.Hansard).filter_by(date=date):
        if row.location in {'austral', 'tiona'}:
            continue  # ಠ_ಠ

        name_to_hits[row.location] = row.hits

    # Pull out the aggregate information into location/name/hits arrays.
    lats = []
    lons = []
    hits = []
    names = []
    for name, n in name_to_hits.items():
        lat, lon = name_to_loc[name]
        lats.append(lat)
        lons.append(lon)
        hits.append(n)
        names.append(name)
    if not lats:
        return None

    lats = numpy.array(lats)
    lons = numpy.array(lons)
    hits = numpy.array(hits)

    # Generate a heatmap.
    for lat, lon, n in zip(lats, lons, hits):
        if not 0 <= lat <= 1 or not 0 <= lon <= 1:
            continue

        x = int(lon * (res - 1))
        y = int(lat * (res - 1))
        heatmap[y, x] = n

    # Convolve the heatmap with a Gaussian filter.
    heatmap = ndi.gaussian_filter(heatmap, (bw, bw))

    return heatmap


def generate_heatpoints(date):
    # Query for this date.
    name_to_hits = {}
    for row in hansard.db.query(hansard.Hansard).filter_by(date=date):
        if row.location in {'austral', 'tiona'}:
            continue  # ಠ_ಠ

        name_to_hits[row.location] = row.hits

    # Pull out the aggregate information into location/name/hits dicts.
    objs = []
    for name, n in name_to_hits.items():
        obj = {}
        lat, lon = name_to_loc[name]
        obj['name'] = name
        obj['lat'] = lat
        obj['lon'] = lon
        obj['weight'] = n
        objs.append(obj)

    return objs


def get_all_dates():
    return list(hansard.db.query(hansard.Hansard.date).distinct())


def generate_all_heatmaps():
    dates = get_all_dates()
    n_days = len(dates)
    heatmap = numpy.zeros((n_days, res, res))

    for idx, (date,) in enumerate(dates):
        heatmap[idx] = generate_heatmap(date)
    
    return heatmap


def generate_all_heatpoints():
    dates = get_all_dates()
    n_days = len(dates)
    heatpoints = []

    for idx, (date,) in enumerate(dates):
        heatpoints.append(generate_heatpoints(date))
    
    return heatpoints


def mean_heatmap(all_heatmaps):
    # Compute the average heatmap.
    return all_heatmaps.mean(axis=0)


def mean_heatpoints(all_heatpoints):
    mean = collections.defaultdict(int)
    n = 0
    for hps in all_heatpoints:
        n += 1
        for hp in hps:
            name = hp['name']
            weight = hp['weight']
            mean[name] += weight
    for name in mean:
        mean[name] /= n

    return mean


def plot_heatmap(heatmap):
    plt.pcolor(heatmap, cmap='inferno')
    ax = plt.gca()
    for name, (lat, lon) in name_to_loc.items():
        lat *= res - 1
        lon *= res - 1
        # ax.annotate(name, xy=(lon, lat), xytext=(lon, lat), color='white',
        #             alpha=0.2)


def get_peaks(heatmap):
    # From http://stackoverflow.com/a/3689710
    neighborhood = ndi.morphology.generate_binary_structure(2, 2)
    local_max = ndi.filters.maximum_filter(heatmap,
            footprint=neighborhood) == heatmap
    background = heatmap == 0
    eroded_background = ndi.morphology.binary_erosion(
        background, structure=neighborhood, border_value=1)
    detected_peaks = (local_max - eroded_background).nonzero()
    top_5 = sorted(enumerate(heatmap[detected_peaks]), key=lambda z: z[1],
                   reverse=True)[:5]
    xs = detected_peaks[0][[i for i, _ in top_5]]
    ys = detected_peaks[1][[i for i, _ in top_5]]
    return (xs, ys)


def nearest_towns(ys, xs):
    towns = []
    for lat, lon in zip(ys, xs):
        nearest = min(name_to_loc,
                      key=lambda z: numpy.hypot(
                            name_to_loc[z][0] * (res - 1) - lat,
                            name_to_loc[z][1] * (res - 1) - lon))
        print(nearest)
        towns.append(nearest)
    return towns


def normalise_heatpoints(heatpoints, mean_hp):
    normalised = []
    for heatpoint in heatpoints:
        name = heatpoint['name']
        print(heatpoint['name'], heatpoint['weight'], mean_hp[name])
        weight = heatpoint['weight']
        normalised.append({
            'name': name,
            'weight': weight / (mean_hp[name] + 1),
            'lat': heatpoint['lat'],
            'lon': heatpoint['lon'],
        })

    return normalised


if __name__ == '__main__':
    all_heatmaps = generate_all_heatmaps()
    all_heatpoints = generate_all_heatpoints()
    mean_hm = mean_heatmap(all_heatmaps)
    mean_hp = mean_heatpoints(all_heatpoints)
    print('Date:', get_all_dates()[0])

    heatmap = all_heatmaps[0]
    heatpoints = all_heatpoints[0]

    plt.subplot(2, 2, 1)
    plt.title('Raw data')
    plt.imshow(numpy.flipud(heatmap), cmap='inferno')
    plt.subplot(2, 2, 2)
    plt.title('Normalised data')
    normalised_heatmap = heatmap / (mean_hm + 1)
    plt.imshow(numpy.flipud(normalised_heatmap), cmap='inferno')
    plt.subplot(2, 2, 3)
    plt.title('Top 5 Peaks')
    normalised_heatpoints = normalise_heatpoints(heatpoints, mean_hp)
    print(normalised_heatpoints)
    top_5 = sorted(normalised_heatpoints, key=normalised_heatpoints.get,
                   reverse=True)[:5]
    print(top_5)
    plt.imshow(numpy.flipud(normalised_heatmap), cmap='inferno')
    xs = []
    ys = []
    for name in top_5:
        lat, lon = name_to_loc[name]
        xs.append(lon * (res - 1))
        ys.append(res - lat * (res - 1))
    plt.scatter(xs, ys, color='green', s=20)
    ax = plt.gca()
    for name, lat, lon in zip(top_5, ys, xs):
        ax.annotate(name, xy=(lon, lat), xytext=(lon, lat),
                    color='white')
    plt.show()
