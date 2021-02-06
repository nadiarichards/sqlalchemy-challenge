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
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    query = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    return jsonify(query)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    query = session.query(Measurement.station).all()
    session.close()
    return jsonify(query)


@app.route("/api/v1.0/tobs")
def tobs():

    session=Session(engine)
# Query the dates and temperature observations of the most active station for the last year of data.
    session.query(Measurement.station, func.count(Measurement.station)).group_by(
    Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station=session.query(Measurement.tobs, Measurement.date).filter(
    Measurement.station=='USC00519281').all()
# Return a JSON list of temperature observations (TOBS) for the previous year.
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    temp_last_year=session.query(Measurement.tobs).filter(Measurement.date >=last_year).all()
    session.close()
    return jsonify(most_active_station, temp_last_year)


@app.route("/api/v1.0/<start>")
def start(start):
    if start not in Measurement.date:
        print("Pick a date before 2017-08-23")
    else:
        session=Session(engine)
        sel =[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        after_start = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        start_list = list(after_start)
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
        session.close()
        return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session=Session(engine)
    sel =[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_and_end = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
    start_end_day_list = list(start_and_end)
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
    session.close()
    return jsonify(start_end_day_list)


if __name__ == '__main__':
    app.run(debug=True)
