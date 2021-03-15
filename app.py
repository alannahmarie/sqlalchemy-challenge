import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    # List all available api routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
        f"Enter dates in 'YYYY-DD-MM' format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results to a dictionary using date as the key and prcp as the value
    # Return the JSON representation of your dictionary

    session = Session(engine)
    
    results_prcp = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = {}
    for row in results_prcp:
        prcp_data[row[0]] = row[1]   
    
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    # Return a JSON list of stations from the dataset

    session = Session(engine)
    
    results_stations = session.query(Station.name).all()

    session.close()

    stations = list(np.ravel(results_stations))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    session = Session(engine)
    
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').all()

    session.close()

    tobs = list(np.ravel(results_tobs))

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    session = Session(engine)

    sel = func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)
    results = session.query(* sel).filter(Measurement.date >= start).first()

    session.close()
    
    start_temps = {'Lowest Temperature' : results[0],
                'Average Temperatue' : round(results[1],2),
                'Higest Temperature' : results[2]}

    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    session = Session(engine)
    
    sel = func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)
    results = session.query(* sel).filter(Measurement.date >= start).filter(Measurement.date <= end).first()

    session.close()
    
    start_end_temps = {'Lowest Temperature' : results[0],
                'Average Temperatue' : round(results[1],2),
                'Higest Temperature' : results[2]}

    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)