import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Connect SQLite Database
# Run into internal server error alot on brach route, has to restart to fix internal server error.
# add this solve the problem, connect_args={'check_same_thread': False}
# https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa/48218213
engine = create_engine("sqlite:///hawaii.sqlite",connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Set up Flask
app = Flask(__name__)

## Root Route, Welcome:
@app.route("/")

def welcome():
    return ('''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs  
    /api/v1.0/temp/start/end
    ''')

##  Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # The query return list of tuples [('2016-08-23', 6), ('2016-08-24', 6)]
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()

    precip = {date: prcp for date, prcp in precipitation}    
    return jsonify(precip)

##  Stations Route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    # np.ravel break the list of tuple to an one-dimension array
    # list() is needed as jsonify cant convert array to jason format
    stations = list(np.ravel(results))

    # stations=stations. This formats our list into JSON (dict-like {"stations":["USC00519397","USC00513117"]}
    # otherwise just return a list. ["USC00519397","USC00513117"]
    # https://flask.palletsprojects.com/en/1.1.x/api/#flask.json.jsonify
    return jsonify(stations = stations)

##  Temperatures Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)

## Statistics Route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    # passing it as a list doesnt seem any impacts
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end == None:
        # asterisk is used to indicate there will be multiple results for our query. Needed or error        
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)