#!/bin/python3

import json, sys

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

params = {"FF":"ff", "FFX":"fx", "RR":"rr", "SO":"sun" }

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

print(obs)
sys.exit()

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

#add SQL columns
sql = []
for param in params.values():
   sql.append( f"ALTER TABLE `live` ADD IF NOT EXISTS `{param}` SMALLINT(5) NULL DEFAULT NULL" )

cur.executemany(sql)

sql = []

today = DATE + td1
datum = today.strftime("%Y%m%d")
datumsec = dt.combine( today, dt.min.time() )
datumsec = int( datumsec.replace( tzinfo = tz.utc ).timestamp() )
print(datumsec)

#insert obs
for i,f in enumerate(obs):
   for param in params.values():
      for value in obs[i][param]:
         #only sunshine duration value is already correct for database storage
         if param != "sun":
            value *= 10
         #convert 'None' to 'null'
         if value == None: 
            value = "null"
         param_update = f"{param}=VALUES({param})"
         sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,{param}) VALUES ({f},{datum},{datumsec},0,'bufr',{value}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), {param_update}" )
         #add 10 mins (600 seconds) to UNIX timestamp
         datumsec += 600
print(sql)

for s in sql:
   cur.execute( s )
