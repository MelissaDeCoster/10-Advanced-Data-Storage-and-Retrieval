import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
StationTable = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Climate Query - Hawaii")
    return (
        f"Hawaiian Climate Homepage"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/station<br/>"
        f"- List of station names (collected the data)<br/>"
        f"<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"- List of MIN/MAX/AVG temperatures when given start for all dates greater than or equal to start date, replace &ltstart&gt with date in YYYY-MM-DD format<br/>"
        f"<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
        f"- List of MIN/MAX/AVG temperatures when given start and end dates for all dates in between inclusive of the start and end dates, replace &ltstart&gt and &ltend&gt with dates in YYYY-MM-DD format<br/>"
    )  


@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366) 
    #Query  database for percipitations by date (as key)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    print("Server received request for 'precipitation' page...")
    all_precipitation = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)


@app.route("/api/v1.0/station")
def station():
    stations_data = session.query(StationTable.station, StationTable.name)
    print("Server received request for 'station' page...")
    all_stations = []
    for station, name in stations_data:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    print("Server received request for 'tobs' page...")
    all_tobs = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)



@app.route("/api/v1.0/<start>")
def start(start=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)

   
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)


if __name__ == '__main__':
    app.run(debug=True)

