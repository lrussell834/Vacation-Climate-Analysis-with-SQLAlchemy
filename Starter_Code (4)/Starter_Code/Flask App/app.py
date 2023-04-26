# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/'2017-08-23'<br/>"
        f"/api/v1.0/start_end/'2016-07-23'/'2017-07-23'"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation values for the last 12 months"""
    # Query all values
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Create a dictionary from the row data and append to a list of year_data
    year_data= []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
    
        year_data.append(prcp_dict)

    return jsonify(year_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation values for the last 12 months of most active station"""
    # Query all values
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Create a dictionary from the row data and append to a list of tobs_data for weather at the most active station
    tobs_data= []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
    
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


@app.route("/api/v1.0/start/<start>")
def stats_by_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Fetch the temperatures greater than or equal to the date provided and return the 
    minimum, maximum, and average temperature, or a 404 if not."""
    # Query all values
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_dates = list(np.ravel(results))
    
    start_dict = {
                'TMIN': all_dates[0], 
                'TMAX': all_dates[1],
                'TAVG': all_dates[2]
    }

    return jsonify(start_dict)

    return jsonify({"error": f"Temperature with start date {start} not found."}), 404

@app.route("/api/v1.0/start_end/<start>/<end>")
def stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Fetch the temperatures greater than or equal to the date range provided and return the 
    minimum, maximum, and average temperature"""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")

    # calculate TMIN, TAVG, TMAX for dates greater than start
    results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)
