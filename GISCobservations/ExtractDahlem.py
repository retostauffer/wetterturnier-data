#!/bin/python3
# -*- coding:utf-8 -*-
#extracts obs data from hwerte_neu.txt file provided by ftp mira server (Freie UniversitÃt Berlin)

import pandas as pd
import json, sys

head = [i for i in range(0,9)]
enc  = "ISO-8859-1"
cols = [0,8,9]
name = "../ForecastProducts/dahlem/hwerte_neu.txt"
eng  = "python"

df = pd.read_csv(name, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
df.columns = ["dt", "ff", "fx"]

from datetime import datetime as dt, timedelta as td, timezone as tz

today = dt.today()
today_str = today.strftime("%Y-%m-%d")

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

obs = {}
# for ff we use the 13 MET (12 UTC) obs
obs["ff"] = df.loc[df["dt"] == today_str + " 13:00"]["ff"]
print("ff (12z):", float(obs["ff"]))

# fx is more complicated because we need the daily maximum, of the UTC-day!
fx = df["fx"]
print("fx (0z-23z):")
print(list(fx[2:]))
print("fx (max):", fx[2:].max())

# save day and timestamp (ts) variables
day = today.strftime("%Y%m%d")
ts = dt.combine( today, dt.min.time() )
ts = int( ts.replace( tzinfo = tz.utc ).timestamp() )


if len(fx) == 48: # take last 23 hours
   obs["fx"] = df["fx"][2:].max()
elif len(fx) == 2: # just take first hour
   # correct fx of yesterday only if higher than current fx of yesterday
   obs["fx_yd"] = df["fx"].max()
   print("fx_yd (max):", obs["fx_yd"])

   # find out if it's higher... if not skip, nothing to save here!

   from datetime import timedelta as td
   
   # yesterday
   yd = day - td(days=1)
   # timestamp of yesterday
   ts_yd -= 86400
   sql = "SELECT fx24 FROM live WHERE statnr=10381, datum={yd}, datumsec={ts_yd}, stdmin=0, msgtyp='bufr'"
   cur.execute( sql )
   try:
      fx_yd = cur.fetchone()[0] / 10
      print("fx_yd (old):", fx_yd)
   except:
      print("ERROR, no fx saved for yesterday! Setting it to 0.")
      fx_yd = 0
   if obs["fx_yd"] > fx_yd:
      overwrite = True
      print("fx_yd (new):", obs["fx_yd"])
   else: overwrite = False
   

# add columns
sql = []
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `fx24` SMALLINT(5) NULL DEFAULT NULL")
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `ff12` SMALLINT(5) NULL DEFAULT NULL")
for s in sql: cur.execute( s )


# insert obs
try:
   FF = int( obs["ff"] * 10 )
except:
   FF = 'null'
   ts = dt.combine( today, dt.min.time() )

sql = []
if "fx" in obs.keys():
   try:
      FX = int( obs["fx"] * 10 )
   except:
      FX = 'null'
   sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts},0,'bufr',{FX}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(fx24);" )
elif "fx_yd" in obs.keys() and overwrite == True:
   FX = int( obs["fx_yd"] * 10 )
   sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{yd},{ts_yd},0,'bufr',{FX}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(fx24);" )
if "ff" in obs.keys():
   sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff12) VALUES (10381,{day},{ts},0,'bufr',{FF}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), ff12=VALUES(ff12);")

for s in sql: cur.execute( s )
