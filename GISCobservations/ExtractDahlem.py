#!/bin/python3
# -*- coding:utf-8 -*-
#extracts obs data from hwerte_neu.txt file provided by ftp mira server (Freie Universit√t Berlin)

import pandas as pd
import json, sys

head = [i for i in range(0,9)]
enc  = "ISO-8859-1"
cols = [0,8,9]
name = "../ForecastProducts/hwerte_neu.txt"
eng  = "python"

df = pd.read_csv(name, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
df.columns = ["dt", "ff", "fx"]

from datetime import datetime as dt, timedelta as td, timezone as tz

today = dt.today()
today_str = today.strftime("%Y-%m-%d")

obs = {}
obs["ff"] = df.loc[df["dt"] == today_str + " 12:00"]["ff"]
obs["fx"] = df["fx"].max()

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

#add columns
sql = []
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `fx24` SMALLINT(5) NULL DEFAULT NULL")
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `ff12` SMALLINT(5) NULL DEFAULT NULL")
for s in sql: cur.execute( s )

day = today.strftime("%Y%m%d")
ts = dt.combine( today, dt.min.time() )
ts = int( ts.replace( tzinfo = tz.utc ).timestamp() )

#insert obs
try:
   FF = int( obs["ff"] * 10 )
   FX = int( obs["fx"] * 10 )
except:
   FF, FX = 'null', 'null'
   ts = dt.combine( today, dt.min.time() )

sql = []
sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts},0,'bufr',{FX}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(fx24);" )
sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff12) VALUES (10381,{day},{ts},0,'bufr',{FF}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), ff12=VALUES(ff12);")

for s in sql: cur.execute( s )
