#!/bin/python3

import json, sys, os, shutil
import pandas as pd
import numpy as np

fx = {}
# KLOTEN => KLO <> FLUNTERN => SMA
stations = { "KLO" : 6670, "SMA" : 6660 }

# param_name in csv => param_name in db
params = {}

from datetime import datetime as dt, timedelta as td, timezone as tz
fmt = "%Y-%m-%d"

td1 = td(days = 1)

if len(sys.argv) == 2:
   DATE = sys.argv[1]
   DATE = dt.strptime(DATE, fmt).replace( tzinfo = tz.utc )
else:
   from datetime import date
   DATE = dt.utcnow().date() - td1

path = "SWISS/"
#create path directory if not exists
from pathlib import Path
Path(path).mkdir(parents=True, exist_ok=True)

# download latest csv to SWISS folder as "YYYYMMDDhhmm.csv" and "VQHA80.csv"
import wget
filename = "VQHA80.csv"
url = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/"

#sun = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-sonnenscheindauer-10min/ch.meteoschweiz.messwerte-sonnenscheindauer-10min_de.csv"
#rrr = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-niederschlag-10min/ch.meteoschweiz.messwerte-niederschlag-10min_de.csv"


#remove oldest tmp file
try: os.remove(path + filename)
except FileNotFoundError: print("No latest file, downloading!")
#download latest file and copy it
latest = wget.download( url + filename, out = path )
shutil.copyfile( latest, path + dt.utcnow().strftime("%Y-%m-%d@%H:%M.csv") )

# now we can work with the downloaded file (extract observations)
df = pd.read_csv(latest, sep=";")
print(df)
# select rows containing data from the 2 desired stations
df = df.loc[(df['Station/Location'].isin(("KLO","SMA")))]
print(df)
