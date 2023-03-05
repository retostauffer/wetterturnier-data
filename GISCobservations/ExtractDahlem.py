#!/bin/python3
# -*- coding:utf-8 -*-
#extracts obs data from hwerte_neu.txt file provided by ftp mira server (Freie UniversitĂt Berlin)

import pandas as pd
import json, sys

head = [i for i in range(0,9)]
enc  = "ISO-8859-1"
cols = [0,11,16]
#path to input file from FU mira FTP server
name = "../ForecastProducts/dahlem/hwerte_"
eng  = "python"

from datetime import datetime as dt, timedelta, timezone as tz
d = timedelta(days=1); fmt = "%Y-%m-%d"; Ymd = "%Y%m%d"

def dt2ts( datetime ):
   #convert today's datetime object to timestamp, we will need this later
   ts = dt.combine( datetime, dt.min.time() )
   return int( ts.replace( tzinfo = tz.utc ).timestamp() )

if len(sys.argv) == 2:
   td = dt.strptime( sys.argv[1], fmt ); yd = td - d
   name_td = name + str(sys.argv[1])
   name_yd = name + yd.strftime( fmt )
   tm = td + d
   ts_td   = dt2ts( tm )
   day     = tm.strftime( Ymd ) 
else:
   td = dt.today(); yd = td - d
   name_td = name + "neu"
   name_yd = name + yd.strftime( fmt )
   ts_td   = dt2ts( td )
   day = td.strftime( Ymd )

ts_yd = ts_td - 86400
name_td += ".txt"; name_yd += ".txt"
colnames = ["dt", "fx", "rr"]

#read the tab-seperated table with pandas and convert it to a pandas dataframe
df_td = pd.read_csv(name_td, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
df_td.columns = colnames

obs = {}

try:
   df_yd = pd.read_csv(name_yd, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
   df_yd.columns = colnames
   obs["fx_yd"] = df_yd["fx"][-2:].max()
   print("fx_yd (max):", obs["fx_yd"])
   rr24 = list( df_yd["rr"][-2:] )
except Exception as e:
   print(e); print("No obs from yesterday, setting to 0!")
   obs["fx_yd"] = 0

sys.path.append('PyModules')
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

fx = df_td["fx"]

#if file is finished
if len(fx) == 47: # take last 23 hours
   obs["fx"] = df_td["fx"][1:].max()
   # correct fx of yesterday only if higher than last hour of yesterday
   if obs["fx_yd"] > obs["fx"]:
      obs["fx"] = obs["fx_yd"]
   
   rr1x = 0
   rr24 += list( df_td["rr"][1:] )
   
   for i, rr in enumerate(rr24):
      try:               rr24[i] = float(rr)
      except ValueError: rr24[i] = 0
      try:
         rr24[i+1] = float(rr24[i+1])
      except ValueError:
         rr24[i+1] = 0
      except IndexError:
         pass
      if i+1 < len(rr24):
         max_i = sum( rr24[i:i+2] )
      rr1x = max_i if max_i > rr1x else rr1x
    
   print( rr24 )
   print( rr1x )

   obs["rr"] = rr1x

# fx is more complicated because we need the daily maximum, of the UTC-day!
print("fx (0z-23z):")
print(list(fx[2:]))
print("fx_td (max):", fx[2:].max())

#use BeautifulSoup to extract mammatus95 synopstalking page
from bs4 import BeautifulSoup
import requests

soup=BeautifulSoup(requests.get("https://userpage.fu-berlin.de/mammatus95/turm/fm12/synopsturm.php").text,features="html.parser")
# first we should find our table object:
tables = soup.find_all('table')

def find_ff( table, start_row ):
   rows = []
   
   for i, row in enumerate(table.find_all('tr')):
      rows.append([el.text.strip() for el in row.find_all('td')])
   
   synop = ""
   for row in rows[start_row:]:
      if row[0][7:9] == "12": synop = row[0]

   print(synop)

   for i in synop.split("&nbsp"):
      if i[0:4] == "555 ":
         try: return int(i[18:21])
         except Exception as e:
            print(e); return 0

obs["ff_td"] = find_ff( tables[0], 4 ); obs["ff_yd"] = find_ff( tables[1], 1 )

if obs["ff_td"]:
   print("ff @12z today:", float(obs["ff_td"]/10) )
if obs["ff_yd"]:
   print("ff @12z yesterday:", float(obs["ff_yd"]/10) )

# add columns
sql = []
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `fx24` SMALLINT(5) NULL DEFAULT NULL")
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `ff12` SMALLINT(5) NULL DEFAULT NULL")
sql.append("ALTER TABLE `live` ADD IF NOT EXISTS `rr1x` SMALLINT(5) NULL DEFAULT NULL")

if "rr" in obs.keys():
   try:    rr1x = int( obs["rr"] * 10 )
   except: rr1x = 'null'
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,rr1x) VALUES (10381,{day},{ts_td},0,'bufr',{rr1x}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(rr1x);")
if "fx" in obs.keys():
   try:    fx24 = int( obs["fx"] * 10 )
   except: fx24 = 'null'
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts_td},0,'bufr',{fx24}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), fx24=VALUES(fx24);")
if obs["ff_td"]:
   today = dt.today()
   day = today.strftime( Ymd )
   ts = dt2ts( today )
   ts += 43200
   ff12 = obs["ff_td"]
   h = 1200
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff12) VALUES (10381,{day},{ts},{h},'bufr',{ff12}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), ff12=VALUES(ff12);")
if obs["ff_yd"]:
   today = dt.today() - d
   day = today.strftime( Ymd )
   ts = dt2ts( today )
   ts += 43200
   ff12 = obs["ff_yd"]
   h = 1200
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff12) VALUES (10381,{day},{ts},{h},'bufr',{ff12}) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), ff12=VALUES(ff12);")

print(sql)

for s in sql: cur.execute( s )

db.commit()
