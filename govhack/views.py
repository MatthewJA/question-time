import json

from flask import render_template, request

import os
import datetime

from . import app
from . import models
from . import database


@app.route('/')
def index():
    #Get list of all dates we have
    available_dates = [d.date for d in database.db_session.query(models.DateHeat.date).distinct()]
    available_dates.sort()
    return render_template('index.html', available_dates = available_dates)

@app.route('/interesting_trends/<place_name>')
def interesting_trends(place_name):
    place_name = place_name.lower()
    date = request.args.get('date')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')

    ##Get trends
    heatmap_points = models.DateHeat.query.filter_by(date=date).first()
    trends = json.loads(heatmap_points.interest)

    ##Get links
    docs = models.DateLink.query.filter_by(date=date).first()
    first_hid = trends[place_name]['hansard_ids'][0]
    chamber_id = first_hid.split('-')[1]

    link = ''
    list_of_docs = json.loads(docs.hid)
    for doc in list_of_docs:
        chamber_id_ = doc['event'].split('-')[1]
        if chamber_id_ == chamber_id:
            link = doc['event'] + '/' + first_hid

    return json.dumps({"InterestingTrends":[trends[place_name]],
                       "Related": link})


@app.route('/points_of_interest')
def points_of_interest():
    date = request.args.get('date')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    heatmap_points = models.DateHeat.query.filter_by(date=date).first()
    return '{"PointsOfInterest": %s}' % (heatmap_points.peaks)

@app.route('/heatmap_points')
def heatmap_points():
    date = request.args.get('date')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    heatmap_points = models.DateHeat.query.filter_by(date=date).first()
    return '{"HeatmapPoints": %s}' % (heatmap_points.heat)

@app.route('/available_dates')
def available_dates():
    available_dates = [d.date for d in database.db_session.query(models.DateHeat.date).distinct()]
    return json.dumps({"AvailableDates":available_dates})

@app.route('/db_test')
def db_test():
    from database import db_session
    for i in db_session.query(models.DateHeat.date).distinct():
        return str(i)
