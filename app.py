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
    (Measurement, Station) = record
    print (Measurement.station)
    print (Station.station)
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
        f"Available Routes:<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all passenger names"""
    # Query all passengers
    results_prcp = session.query(prcp.Measurement).all()
    results_date = session.query(date.Measurement).all()

    # Convert list of tuples into normal list
    all_prcp = {results_date : results_prcp}

    session.close()

    return jsonify(all_prcp)





if __name__ == '__main__':
    app.run(debug=True)
