#!/bin/python3

import json, sys
import numpy as np

obs = {}
stations = { 5904 : 11035, 5917 : 11040, 11803 : 11320, 11804 : 11120 }

from datetime import datetime as dt, timedelta as td, timezone as tz
fmt = "%Y-%m-%d"
td1 = td(days = 1)

if len(sys.argv) == 2:
   DATE = sys.argv[1]
   DATE = dt.strptime(DATE, fmt).replace( tzinfo = tz.utc )
else:
   from datetime import date
   DATE = dt.utcnow().date() - td1

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


#DATE is yesterday by default, because we receive and save the observation on the next day
datum = DATE.strftime("%Y%m%d")

from utils import clock_iter

sql = []

#insert obs
for i,f in enumerate(obs):
   datumsec = dt.combine( DATE, dt.min.time() )
   datumsec = int( datumsec.replace( tzinfo = tz.utc ).timestamp() )
   stdmin = clock_iter("2350") # first iteration will start as "0000"
   for param in params.values():
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
