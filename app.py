import numpy as np
import pandas as pd

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

session=Session(engine)

joined_by_station=session.query(Measurement, Station).filter(Measurement.station == Station.station)
for record in joined_by_station:
    (measurement, station) = record
session.close()
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
    )
# session = Session(engine)
# for row in session.query(Measurement).limit(10).all():
#     print(row.station, row.date)
# session.close()

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all passenger names"""
    # Query all passengers
    #results_prcp = session.query(Measurement.prcp).all()
    #results_date = session.query(Measurement.date).all()
    query = session.query(Measurement.date, Measurement.prcp).all()
    # Convert list of tuples into normal list
    #all_prcp = {results_date : results_prcp}

    session.close()

    # all_prcp = []
    # for date, prcp in results:
    #     prcp_dict = {}
    #     prcp_dict["date"] = date
    #     prcp_dict["prcp"] = precipitation
    #     all_prcp.append(prcp_dict)

    return jsonify(query)


if __name__ == '__main__':
    app.run(debug=True)
