from govhack import app
from flask import render_template
import models

import json

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/interesting_trends/<place_name>')
def interesting_trends(place_name):
    one_place_name = models.InterestingTrend('The crisis facing %s' % (place_name), 'lol')
    return json.dumps({'InterestingTrends':[one_place_name.to_dict()]})


@app.route('/points_of_interest')
def points_of_interest():
    with open('govhack/points_of_interest_sample.json') as f:
        return f.read()