#!/bin/python3

import json, sys
import numpy as np

obs = {}
stations = { 5904 : 11035, 5917 : 11040, 11803 : 11320, 11804 : 11120 }

from datetime import datetime as dt, timedelta as td, timezone as tz
sys.path.append('PyModules')
from utils import clock_iter, dt2ts, str2dt
fmt = "%Y-%m-%d"
Ymd = "%Y%m%d"
td1 = td(days = 1)

if len(sys.argv) == 2:
   print("CUSTOM DAY")
   DATE = sys.argv[1]
   DATE = str2dt( DATE, fmt, tzinfo = tz.utc )
else: # default is yesterday
   print("YESTERDAY")
   from datetime import date
   DATE = dt.utcnow().date()

DATE_yd = DATE - td1
datum = DATE.strftime( Ymd )

path = "ZAMG/"
none_counter = 0
params = {"FF":"ff10", "FFX":"ffx10", "RR":"rrr10", "SO":"sun10" }

with open( path + DATE.strftime(fmt) + ".test.json", "r" ) as f:
   d = json.load(f)
   for f in d["features"]:
      p = f["properties"]
      obs[stations[int(p["station"])]] = {}
      none_counter = 0
      for param in list(params.keys()):
         try:
            obs[stations[int(p["station"])]][params[param]] = p["parameters"][param]["data"]
         except:
            obs[stations[int(p["station"])]][params[param]] = None
            none_counter += 1

      if none_counter == len(params.keys()):
         print("MISSING DATA!")

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

#add SQL columns
sql = "ALTER TABLE `live` ADD IF NOT EXISTS %s SMALLINT(5) NULL DEFAULT NULL"
for p in list(params.values()): cur.execute( sql % p )

sql = []

#insert obs
for i,f in enumerate(obs):
   for param in list(params.values()):
      datumsec = dt2ts( DATE_yd, Ymd, 1 )
      stdmin = clock_iter("2350") # first iteration will start as "0000"
      for value in obs[f][param]:
         #convert 'None' to 'null' to match SQL format
         if value == None: value = "null"
         else:
            #all params except sun10 need to be *10 for database storage
            if param != "sun10": value *= 10
            value = int(value)
         param_update = f"{param}=VALUES({param})"
         sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,{param}) VALUES ({f},{datum},{datumsec},{next(stdmin)},'bufr',{value}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), {param_update}" )
         #add 10 mins (600 seconds) to UNIX timestamp
         datumsec += 600

for s in sql:
   cur.execute( s )

db.commit(); db.close()
