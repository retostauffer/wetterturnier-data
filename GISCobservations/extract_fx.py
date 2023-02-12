#!/bin/python3

import json, sys

fx = {}
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

with open( path + DATE.strftime(fmt) + ".json", "r" ) as f:
   d = json.load(f)
   for f in d["features"]:
      p = f["properties"]
      try:
         fx[stations[int(p["station"])]] = p["parameters"]["vvmax"]["data"][0]
      except:
         fx[stations[int(p["station"])]] = None
         none_counter += 1

if none_counter == len(stations.keys()):
    sys.exit("NO DATA!")

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

#add column
sql = "ALTER TABLE `live` ADD IF NOT EXISTS `fx24` SMALLINT(5) NULL DEFAULT NULL"
cur.execute(sql)

sql = []

today = DATE + td1
datum = today.strftime("%Y%m%d")
datumsec = dt.combine( today, dt.min.time() )
datumsec = int( datumsec.replace( tzinfo = tz.utc ).timestamp() )
print(datumsec)

#insert obs
for i,f in enumerate(fx):
   try:
      FX = int(fx[f]*10)
   except:
      FX = 'null'
   sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES ({f},{datum},{datumsec},0,'bufr',{FX}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(fx24);" )

print(sql)

for s in sql:
   cur.execute( s )
