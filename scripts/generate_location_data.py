"""Dumps location data to a SQLite3 database."""

import collections
import datetime
import json
import operator

import nltk
import numpy
from RAKE import rake
import sqlalchemy as sa

import database
import hansard


N_PEAKS = 5


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

    # Get the top n peaks for each date.
    all_peaks = numpy.argsort(data, axis=1)[:, -N_PEAKS:]

    # For each date, dump to a mildly horrifying JSON string. Then store in the
    # database!
    for i, (date,) in enumerate(dates):
        # [{name, lat, lon, weight}]
        heat = []
        # {location: [lat, lon]}
        peaks = {}
        # {location: {title, description}}
        topics = {}
        for j, location in enumerate(locations):
            if data[i, j] != 0:
                lat, lon = loc_to_pos[location]
                heat.append({
                    'name': location,
                    'lat': lat,
                    'lon': lon,
                    'weight': data[i, j],
                })

        for location_idx in all_peaks[i]:
            location = locations[location_idx]
            lat, lon = loc_to_pos[location]
            peaks[location] = (lat, lon)

            h = hansard.Hansard.query.filter_by(
                    date=date, location=location).first()
            text = h.text.decode('utf-8')
            # From github.com/aneesha/RAKE.
            sentence_list = rake.split_sentences(text)
            stop_path = 'RAKE/SmartStoplist.txt'
            stopword_pattern = rake.build_stop_word_regex(stop_path)
            phrase_list = rake.generate_candidate_keywords(
                    sentence_list, stopword_pattern)
            word_scores = rake.calculate_word_scores(phrase_list)
            keyword_candidates = rake.generate_candidate_keyword_scores(
                    phrase_list, word_scores)
            sorted_keywords = sorted(
                    keyword_candidates.items(),
                    key=operator.itemgetter(1),
                    reverse=True)
            r = rake.Rake(stop_path)
            keywords = r.run(text)
            topic = keywords[0][0]
            # Grab a description. We'll use the longest text that includes the
            # topic.
            subtexts = text.split('|')
            best_desc = ''
            for subtext in subtexts:
                if len(subtext) <= len(best_desc):
                    continue

                assert type(topic) == type(subtext)

                if topic.lower() in subtext.lower():
                    best_desc = subtext

            topics[location] = {
                'topic': topic,
                'description': best_desc,
                'hansard_ids': h.hids.split('|'),
            }

        heat = json.dumps(heat)
        peaks = json.dumps(peaks)
        topics = json.dumps(topics)

        dh = database.DateHeat(date, heat, peaks, topics)
        database.db_session.add(dh)
        database.db_session.commit()

def generate_heatmap_data_no_db():
    """Generates all heatmap data without touching the database."""
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

    # Get the top n peaks for each date.
    all_peaks = numpy.argsort(data, axis=1)[:, -N_PEAKS:]

    for i, (date,) in enumerate(dates):
        # Have a gander at the top peak.
        peak = all_peaks[i, 0]
        location = locations[peak]
        h = hansard.Hansard.query.filter_by(
                date=date, location=location).first()
        text = h.text

        # From github.com/aneesha/RAKE.
        sentence_list = rake.split_sentences(text)
        stop_path = 'RAKE/SmartStoplist.txt'
        stopword_pattern = rake.build_stop_word_regex(stop_path)
        phrase_list = rake.generate_candidate_keywords(
                sentence_list, stopword_pattern)
        word_scores = rake.calculate_word_scores(phrase_list)
        keyword_candidates = rake.generate_candidate_keyword_scores(
                phrase_list, word_scores)
        sorted_keywords = sorted(
                keyword_candidates.items(),
                key=operator.itemgetter(1),
                reverse=True)
        r = rake.Rake(stop_path)
        keywords = r.run(text)
        print(keywords[0][0])


if __name__ == '__main__':
    generate_heatmap_data()
