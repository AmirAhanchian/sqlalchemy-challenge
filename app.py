import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
import sqlite3 as sq



#Correctly generate the engine to the correct sqlite file  
#Use automap_base() and reflect the database schema  

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(autoload_with = engine)

#Correctly save references to the tables in the sqlite file (measurement and station) 

Measurment = base.classes.measurement
Station = base.classes.station

#create and binds the session between the python app and database

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

#Display the available routes on the landing page  
app = Flask(__name__)

@app.route("/")
def home():
    return(
    f"<h3>Welcome to my weather API Home page</h3>"
    f"<b>Below you can find the list of the routes you can go:</b><br>" 
    f" <br>"
    f"/api/v1.0/precipitation,<br>" 
    f" <br>"
    f"/api/v1.0/stations,<br>" 
    f" <br>"
    f"/api/v1.0/tobs,<br>" 
    f" <br>"
    f"add date in YYYY-MM-DD format to the end of the URL instead of start or start/end<br>"
    f"<br>"
    f"/api/v1.0/start,<br>" 
    f" <br>"
    f"/api/v1.0/start/end<br>")


# precipitation route that:

prevyear_data = session.query(Measurment.date,Measurment.prcp).\
    filter(Measurment.date >= '2016-08-23').all()

#Returns json with the date as the key and the value as the precipitation  
precipitation = dict((x, y) for x, y in prevyear_data)

#Only returns the jsonified precipitation data for the last year in the database  

@app.route("/api/v1.0/precipitation")
def Precipitation():
    return jsonify (precipitation)

#A stations route that:

station_names = session.query(Station.name).distinct().all()

stations_list = [row[0] for row in station_names]
#print(stations_list)

#Returns jsonified data of all of the stations in the database  

@app.route("/api/v1.0/stations")
def Stations():
    return jsonify(stations_list)

#A tobs route that:
#Only returns the jsonified data for the last year of data  

prevyear_tobs = session.query(Measurment.date,Measurment.tobs).\
    filter(Measurment.station == 'USC00519281').\
    filter(Measurment.date >= '2016-08-23').all()

#Returns jsonified data for the most active station (USC00519281)   
USC00519281_tobs = dict((x, y) for x, y in prevyear_tobs)

@app.route("/api/v1.0/tobs")
def Tobs():
    return jsonify(USC00519281_tobs)


#A start route that:

@app.route("/api/v1.0/<start>", methods=['GET'])
def temps_by_start_date(start):
#Accepts the start date as a parameter from the URL 
    sel = [func.min(Measurment.tobs),
      func.max(Measurment.tobs),
      func.avg(Measurment.tobs)]

    start = dt.datetime.strptime(start, "%Y-%m-%d").date()

    reqested_info = session.query(*sel).filter(Measurment.date >= start).all()
    list_temp_start = [row[0] for row in reqested_info]
    return jsonify(list_temp_start)

#Accepts the start and end dates as parameters from the URL 

@app.route("/api/v1.0/<start>/<end>", methods=['GET'])
def temps_by_start_end(start, end):
#Accepts the start date as a parameter from the URL 
    sel = [func.min(Measurment.tobs),
      func.max(Measurment.tobs),
      func.avg(Measurment.tobs)]

    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()

    reqested_s_e_info = session.query(*sel).\
        filter(Measurment.date >= start).\
        filter(Measurment.date <= end).all()
    list_temp_s_e = [row[0] for row in reqested_s_e_info]
    return jsonify(list_temp_s_e)


#Returns the min, max, and average temperatures calculated from the given start date to the given end date 



if __name__ == '__main__':
    app.debug = True
    app.run()