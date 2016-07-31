import json

from flask import render_template

import os

from . import app
from . import models
from . import database


@app.route('/')
def index():
    #Get list of all dates we have
    available_dates = [d.date for d in database.db_session.query(models.DateHeat.date).distinct()]
    return render_template('index.html', available_dates = available_dates)

@app.route('/interesting_trends/<place_name>')
def interesting_trends(place_name):
    one_place_name = models.InterestingTrend('The crisis facing %s' % (place_name), 'There is a definitive crisis happening around the place.')
    return json.dumps({'InterestingTrends':[one_place_name.to_dict()]})


@app.route('/points_of_interest')
def points_of_interest():
    with open('govhack/points_of_interest_sample.json') as f:
        return f.read()

@app.route('/heatmap_points')
def heatmap_points():
    with open('govhack/heatmap_sample.json') as f:
        return f.read()

@app.route('/db_test')
def db_test():
    from database import db_session
    for i in db_session.query(models.DateHeat.date).distinct():
        return str(i)
