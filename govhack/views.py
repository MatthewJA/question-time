import json

from flask import render_template, request, abort, jsonify

import os
import datetime
import arrow
from flask_swagger import swagger

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
    """
    Gets metadata about a point of interest for a particular date.
    ---
    description: ""
    parameters:
        - in: query
          name: date
        - in: path
          name: place_name
          type: string
    responses:
        '200':
            description: Found POI for the given date.
    """
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
    """
    Gets the points of interest for a particular date.
    ---
    description: ""
    parameters:
        - in: query
          name: date
          description: date that is to fetch the points of interest. Must be of the form YYYY-mm-dd
          required: true
          type: string
    produces:
        - text/html
    responses:
        '200':
            description: Found points of interest.
            schema:
                id: PointsOfInterest
                properties: 
                    PointsOfInterest:
                        type: object
                        additionalProperties:
                            type: array
                            items: 
                                type: number
                                format: double
        '404':
            description: Could not find points of interest for the given date.
        '405':
            description: Invalid input.
    """
    date = request.args.get('date')
    try: 
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        abort(405)
    heatmap_points = models.DateHeat.query.filter_by(date=date).first()
    if not heatmap_points:
        abort(404)
    return '{"PointsOfInterest": %s}' % (heatmap_points.peaks)

@app.route('/heatmap_points')
def heatmap_points():
    """
    Gets a set of weighted heatmap latitude/longitude points.
    ---
    description: ""
    parameters:
        - in: query
          name: date
          type: string
          description: date to be fetched.
          required: true
    produces:
        - application/json
    responses:
        '200':
            description: Found set of weighted heatmap points.
            schema:
                id: HeatmapPoints
                properties:
                    HeatmapPoints:
                        type: array
                        items:
                            schema:
                                id: HeatmapPoint
                                properties:
                                    lon:
                                        type: number
                                        format: double
                                    lat:
                                        type: number
                                        format: double
                                    weight: 
                                        type: number
                                        format: double
                                    name:
                                        type: string

    """
    date = request.args.get('date')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    heatmap_points = models.DateHeat.query.filter_by(date=date).first()
    return '{"HeatmapPoints": %s}' % (heatmap_points.heat)

@app.route('/available_dates')
def available_dates():
    """
    Gets a list of all available dates.
    ---
    description: ""
    produces:
        - application/json
    responses:
        '200':
            description: Found dates.
            schema:
                id: AvailableDates
                properties: 
                    AvailableDates:
                        type: array
                        items:
                            type: string

    """
    available_dates = [arrow.get(d.date).format('YYYY-MM-DD') for d in database.db_session.query(models.DateHeat.date).distinct()]
    return json.dumps({"AvailableDates":available_dates})

@app.route('/db_test')
def db_test():
    from database import db_session
    for i in db_session.query(models.DateHeat.date).distinct():
        return str(i)

@app.route('/api_doc')
def api_doc():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "QuestionTime API"
    return jsonify(swag)