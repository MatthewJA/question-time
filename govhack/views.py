import json

from flask import render_template, request, abort, jsonify

import os
import datetime
import arrow
from flask_swagger import swagger
import sklearn.neighbors
from sklearn.externals import joblib
import numpy

from sqlalchemy.sql.expression import func

from . import app
from . import models
from . import database
from . import cache

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
    description: "Gets metadata about a point of interest for a particular date."
    parameters:
        - in: query
          name: date
          required: true
          type: string
        - in: path
          name: place_name
          type: string
          required: true
    responses:
        '200':
            description: Found a point of interest for the given date.
            schema:
                id: InterestingTrends
                properties:
                    InterestingTrends:
                        type: array
                        items:
                            type: object
                            properties:
                                description:
                                    type: string
                                hansard_ids:
                                    type: array
                                    items:
                                        type: string
                                topic:
                                    type: string
                    Related:
                        type: string
                    Date:
                        type: string
    produces:
        - text/html
    """
    place_name = place_name.lower()
    date = request.args.get('date')
    date_str = date
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
                       "Related": link,
                       "Date": date_str})


@app.route('/points_of_interest')
def points_of_interest():
    """
    Gets the points of interest for a particular date.
    ---
    description: "Gets the points of interest for a particular date."
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
    description: "Gets a set of weighted heatmap latitude/longitude points."
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
    description: "Gets a list of all available dates."
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

@app.route('/random_point')
def random_point():
    """
    Gets a single Point of Interest randomly.
    ---
    description: "Gets a single Point of Interest randomly."
    produces:
        - application/json
    responses:
        '200':
            description: Found a random point of interest.
            schema:
                id: PointOfInterest
                properties:
                    lat:
                        type: number
                        format: double
                    lon:
                        type: number
                        format: double
                    name:
                        type: string
                    date:
                        type: string
    """
    #Warning: this could be done in a more performant way so try not to hit it too much
    heatmap_points = models.DateHeat.query.order_by(func.random()).limit(1).first()
    if not heatmap_points:
        return abort(501)
    peaks = json.loads(heatmap_points.peaks)
    heatmap_point_name = list(peaks.keys())[0]
    return json.dumps({
        'lat': peaks[heatmap_point_name][0],
        'lon': peaks[heatmap_point_name][1],
        'name': heatmap_point_name,
        'date': arrow.get(heatmap_points.date).format('YYYY-MM-DD')
    })

@app.route('/nearby_points')
def nearby_points():
    """
    Gets nearby points for a given longitude and latitude.
    ---
    description: "Gets five nearby point of interest pairs."
    parameters:
        - in: query
          name: latitude
          required: true
          type: string
        - in: query
          name: longitude
          required: true
          type: string
    produces:
        - application/json
    responses:
        '200':
            description: Found five nearby points of interest.
            schema:
                type: array
                items:
                    $ref: "#/definitions/PointOfInterest"
        '400':
            description: Requires longitude and latitude variables.
    """

    latitude_str = request.args.get('latitude')
    longitude_str = request.args.get('longitude')

    if not longitude_str or not longitude_str:
        abort(400)

    latitude = float(latitude_str)
    longitude = float(longitude_str)

    #Load positions
    all_dates = models.DateHeat.query.all()

    all_peaks_as_tuples = [(json.loads(date_heat.peaks), arrow.get(date_heat.date).format('YYYY-MM-DD')) for date_heat in all_dates]

    #Store coords
    peak_coords = []

    #Store list of place names
    peak_names = []

    #Store list of dates
    peak_dates = []

    #Index all data so it can be retrieved by the kdtree query result
    for peak_tuple in all_peaks_as_tuples:
        peak_dict, peak_date = peak_tuple
        for key in peak_dict:
            peak_coords.append(peak_dict[key])
            peak_names.append(key)
            peak_dates.append(peak_date)

    #Numpy the array so it's usable by KDTree
    coords = numpy.array(peak_coords)

    #Attempt to cache the tree / get tree out of cache
    import StringIO
    model_string = StringIO.StringIO()

    kdtree_cached = cache.get("kdtree_cached")

    if not kdtree_cached:
        #Add positions to tree to build cached tree
        kdtree = sklearn.neighbors.KDTree(coords)
        joblib.dump(kdtree, model_string)
        cache.set("kdtree_cached", model_string.getvalue())
    else:
        #Build tree from cache
        model_string.write(kdtree_cached)
        kdtree = joblib.load(model_string)

    #Query
    query_result = kdtree.query([[latitude, longitude]], k=5)

    _, (indices,) = query_result

    #Marshall into results
    results = [{
        'date':peak_dates[indice], 
        'name': peak_names[indice], 
        'lat': peak_coords[indice][0],
        'lon': peak_coords[indice][1],
    } for indice in indices]

    #Return as JSON
    return json.dumps(results)

@app.route('/db_test')
def db_test():
    from database import db_session
    for i in db_session.query(models.DateHeat.date).distinct():
        return str(i)

@app.route('/api_doc')
def api_doc():
    swagger_conf = swagger(app)
    # General declarations
    swagger_conf['info']['version'] = "1.0"
    swagger_conf['info']['title'] = "QuestionTime API"
    #You can change this if you don't want to use the production basepath
    swagger_conf['host'] = 'safe-oasis-74257.herokuapp.com'
    swagger_conf['schemes'] = ['https']
    return jsonify(swagger_conf)