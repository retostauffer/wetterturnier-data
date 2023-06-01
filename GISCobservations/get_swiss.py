#!/bin/python3

import json, sys, os, shutil
from glob import glob
import pandas as pd
import numpy as np

fx = {}
# KLOTEN => KLO <> FLUNTERN => SMA
stations = { 6670 : "KLO", 6660 : "SMA" }

# param_name in csv => param_name in db
params = { "rrr10":"rre150z0", "sun10":"sre000z0" }

from datetime import datetime as dt, timedelta as td, timezone as tz
fmt  = "%Y-%m-%d@%H:%M"
fmt2 = "%Y%m%d%H%M"
latest_name = "VQHA80"
C = ".csv"
path = "SWISS/"
#create path directory if not exists
from pathlib import Path
Path(path).mkdir(parents=True, exist_ok=True)

if len(sys.argv) == 2:
   if sys.argv[1] == "-a":
      #take all .csv
      outfiles = glob(path + "*.csv")
      print(outfiles)
   else:
      outfiles = [path + sys.argv[1] + C]
else:
   # download latest csv to SWISS folder as "YYYY-MM-DD@hh:mm.csv" and "VQHA80.csv"
   import wget
   filename = latest_name + C
   url = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/"
   #sun = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-sonnenscheindauer-10min/ch.meteoschweiz.messwerte-sonnenscheindauer-10min_de.csv"
   #rrr = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-niederschlag-10min/ch.meteoschweiz.messwerte-niederschlag-10min_de.csv"

   #remove oldest tmp file
   try: os.remove(path + filename)
   except FileNotFoundError: print("No latest file, downloading new!")
   #download latest file and copy it
   outfiles = [wget.download( url + filename, out = path )]
   shutil.copyfile( outfiles[0], path + dt.utcnow().strftime(fmt + C) )


for outfile in outfiles:

   # now we can work with the downloaded file (extract observations)
   df = pd.read_csv(outfile, sep=";")

   # connect to database
   sys.path.append('PyModules')
   from readconfig import readconfig
   config = readconfig("config.conf")

   from database import database
   db = database(config)
   cur = db.cursor()

   #add SQL columns
   sql = "ALTER TABLE `live` ADD IF NOT EXISTS %s SMALLINT(5) NULL DEFAULT NULL"
   for p in list(params.keys()): cur.execute( sql % p )

   sql = []

   for s in stations:
      obs = df.loc[df['Station/Location'] == stations[s]]
      for p in params:
         try:
            value = float(obs[params[p]])
            # to save sunshine duration in the same format as for ZAMG stations, multiply by 60
            if p == "sun10": value *= 60
            # RR needs to be multiplied by 10 in order to match DB format (integer 1/10 mm)
            else: value *= 10
            value = int(np.round(value))
         except ValueError:
            value = 'null'
         Date = str(int(obs["Date"]))
         datum = int( Date[:8] )
         stdmin = int( Date[8:] )
         datumsec = int( dt.strptime(Date, fmt2).replace(tzinfo=tz.utc).timestamp() )
         param_update = f"{p}=VALUES({p})"
         sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,{p}) VALUES ({s},{datum},{datumsec},{stdmin},'bufr',{value}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), {param_update}" )

   for s in sql:
      print(s); cur.execute( s )

   # commit and close db
   db.commit(); db.close()
