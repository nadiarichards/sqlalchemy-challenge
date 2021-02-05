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
        f"/api/v1.0/start/end<br>"
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

def to_date(date_string): 
    try:
        return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError('{} is not valid date in the format YYYY-MM-DD'.format(date_string))

@app.route("/api/v1.0/temp/<start>")

# def stats(start=None, end=None):

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


    # # Select statement
    # sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # if not end:
    #     # calculate TMIN, TAVG, TMAX for dates greater than start
    #     results = session.query(*sel).filter(Measurement.date >= start).all()
    #     # Unravel results into a 1D array and convert to a list
    #     temps = list(np.ravel(results))
    #     return jsonify(temps)
    # # calculate TMIN, TAVG, TMAX with start and stop
    # end_results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    # # Unravel results into a 1D array and convert to a list
    # end_temps = list(np.ravel(end_results))
    # return jsonify(temps=end_temps)
    
@app.route("/api/v1.0/temp/<start>/<end>")
def temperature(start=None, end=None):
    session=Session(engine)
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    # temp_last_year=session.query(Measurement.tobs).filter(Measurement.date >=last_year).all()
    #when given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive'''
    if end != None:
        temps = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    #when given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    else:
        temps = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
        #convert list of tuples into normal list
    temps_rav = list(np.ravel(temps))
    #return json representation of the list
    session.close()
    return jsonify(temps)

    # Start Day Route
@app.route("/api/v1.0/<start>")
def start_day(start):
        start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        start_day_list = list(start_day)
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
        return jsonify(start_day_list)
# Start-End Day Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
        start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        start_end_day_list = list(start_end_day)
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
        return jsonify(start_end_day_list)


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


if __name__ == '__main__':
    app.run(debug=True)
