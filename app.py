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
    """List all available api routes."""
    return (
        f"Available Routes:"
        f"/api/v1.0/precipitation",
        f"/api/v1.0/stations"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    query = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    return jsonify(query)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
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


@app.route("/api/v1.0/<start>/<end>")
def date_range(start=none, end=none):

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    session=Session(engine)

    def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

    # session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(
    # Measurement.station=='USC00519281').all()


    # joined_by_station=session.query(Measurement, Station).filter(Measurement.station == Station.station)
    # for record in joined_by_station:
    #     (measurement, station) = record

    #     canonicalized = superhero.replace(" ", "").lower()
    # for character in justice_league_members:
    #     search_term = character["superhero"].replace(" ", "").lower()

    #     if search_term == canonicalized:
    #         return jsonify(character)


    session.close()

if __name__ == '__main__':
    app.run(debug=True)
