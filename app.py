import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
# List all available api routes.
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/2017-08-23<br>"
        f"/api/v1.0/2016-06-20/2016-06-30<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=last_year).all()
    session.close()
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    query = session.query(Measurement.station).group_by(
    Measurement.station).all()
    session.close()
    return jsonify(query)


@app.route("/api/v1.0/tobs")
def tobs():

    session=Session(engine)
# Query the dates and temperature observations of the most active station for the last year of data.
    session.query(Measurement.station, func.count(Measurement.station)).group_by(
    Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    most_active_station=session.query(Measurement.tobs, Measurement.date).filter(
    Measurement.station=='USC00519281').filter(Measurement.date >=last_year).all()
# Return a JSON list of temperature observations (TOBS) for the previous year.
    previous_year=dt.date(2017,8,23)-dt.timedelta(days=365*2)
    most_active_station_previous_year=session.query(Measurement.tobs, Measurement.date).filter(
    Measurement.station=='USC00519281').filter(Measurement.date >=previous_year).all()
    session.close()
    return jsonify(most_active_station_previous_year)


@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    sel =[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    after_start = session.query(*sel).filter(Measurement.date >= start).all()
    # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
    session.close()
    return jsonify(after_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session=Session(engine)
    sel =[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_and_end = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
    session.close()
    return jsonify(start_and_end)


if __name__ == '__main__':
    app.run(debug=True)
