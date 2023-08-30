#!/bin/python3
# -*- coding:utf-8 -*-
#extracts obs data from hwerte_neu.txt file provided by ftp mira server (Freie Universit√t Berlin)

import pandas as pd
import numpy as np
import json, sys
sys.path.append('PyModules')

head = [i for i in range(0,8)]
enc  = "ISO-8859-1"
cols = [0,11,16,18]
#path to input files from FU mira FTP server
path = "../ForecastProducts/dahlem"
#Heizwerte table
name = path + "/hwerte_"
#RR 10 mins values
rr10 = path + "/Berlin-Dahlem_rr10min-Werte_"
eng  = "python"

from datetime import datetime as dt, timedelta, timezone as tz
d = timedelta(days=1); fmt = "%Y-%m-%d"; Ymd = "%Y%m%d"


from utils import dt2ts, str2dt, hhmm_str

if len(sys.argv) == 2:
   td = dt.strptime( sys.argv[1], fmt )
   name_td = name + str(sys.argv[1])
   print("name_td: ", name_td)
   day     = td.strftime( Ymd ) 
else:
   td = dt.today()
   name_td = name + "neu"
   print("name_td: ",name_td)
   day = td.strftime( Ymd )

ts_td = dt2ts( td, 1 )
yd = td - d
today     = td.strftime( Ymd )
yesterday = yd.strftime( Ymd )
name_yd = name + yd.strftime( fmt )
print("name_yd: ", name_yd)

# load config and connect to DB
from readconfig import readconfig
config = readconfig("config.conf")

from database import database
db = database(config)
cur = db.cursor()

#Extract RR 10mins values from Dahlem
name_rr = rr10 + td.strftime( fmt ) + ".csv"
print("name_rr: " + name_rr)
df_rr = pd.read_csv( name_rr, sep=";", encoding=enc, engine=eng)

sql = []
datumsec = dt2ts(yd, 1)

for index, row in df_rr.iterrows():
   value = int( row["rr-Menge 10min in mm"] * 10 )
   datetime_str = row["zeit"]
   datetime = str2dt(datetime_str, "%Y-%m-%d %X") - timedelta(hours=1)
   hh = hhmm_str(datetime.hour)
   mm = hhmm_str(datetime.minute)
   stdmin = hh + mm
   datumsec = dt2ts(datetime)
   sql.append( f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,rrr10) VALUES (10381,{today},{datumsec},{stdmin},'bufr',{value}) ON DUPLICATE KEY UPDATE rrr10=VALUES(rrr10)" )

for s in sql:
   try: cur.execute( s )
   except: pass

db.commit()

ts_yd = ts_td - 86400
name_td += ".txt"; name_yd += ".txt"
colnames = ["dt", "fx", "rr", "sd"]

#get date of file (DOF)
with open(name_td, "r", encoding=enc) as f:
   lines    = f.readlines()
   date_ger = lines[2][-11:]
   date_ger = date_ger[:10]
   DOF = dt.strptime( date_ger, "%d.%m.%Y" )

#read the tab-seperated table with pandas and convert it to a pandas dataframe
df_td = pd.read_csv(name_td, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
df_td.columns = colnames
df_td = df_td.replace(".", 0)
df_td["sd"] = df_td["sd"].astype(float)


obs = {}

try:
   print(name_yd)
   df_yd = pd.read_csv(name_yd, sep="\t", encoding=enc, skiprows=head, skipfooter=4, engine=eng, usecols=cols)
   df_yd.columns = colnames
   df_yd = df_yd.replace(".",0)
   df_yd["sd"] = df_yd["sd"].astype(float)
   fx_yd = list(df_yd["fx"])[2:]
   rr24 = list(df_yd["rr"])[2:]
except Exception as e:
   print(e); print(f"No obs from {yesterday}, setting fx and sd to 0!")
   fx_yd = 0
   obs["sd_yd"] = 0


fx = df_td["fx"]
print(list(df_td["sd"][23:25]))
if len(df_td["sd"][23:25]) == 2:
   obs["sd1"] = df_td["sd"][23:25].sum()
   print("sd1:", obs["sd1"])
else:
   if len(sys.argv) == 2:
      print(f"no Sd1 @12z for {today}")
   else: print("no Sd1 @12z for today (yet)")

#if file is finished
if len(sys.argv) == 2 or len(fx) == 47:
   # take last 23 hours for Sd - sun doesnt shine at night usually ;)

   obs["sd24"] = df_td["sd"][:-2].sum()
   print("sd24:", obs["sd24"])

if len(sys.argv) == 2 or len(fx) == 2:
   
   fx_td = list(df_td["fx"])[:2]
   print(f"FX24 {today}:", fx_td)
   obs["fx_yd"] = max(list(fx_yd) + list(fx_td))
   print(f"FX24 {yesterday}:", obs["fx_yd"])

   rr1x = 0
   rr24 += list( df_td["rr"][:2] )

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

   print( f"RR24 {yesterday}:", max(rr24) )
   print( f"RR1X {yesterday}:", rr1x )
   obs["rr1x"] = rr1x 


#use BeautifulSoup to extract schroetej31 formerly (mammatus95 synopstalking) page
from bs4 import BeautifulSoup
import requests

soup=BeautifulSoup(requests.get("http://userpage.fu-berlin.de/schroetej31/turm/fm12/synops").text,features="html.parser")
# first we should find our table object:
tables = soup.find_all('table')


def find_ff_fx( table, start_row ):
   rows = []
   
   for i, row in enumerate(table.find_all('tr')):
      rows.append([el.text.strip() for el in row.find_all('td')])
   
   synop_12, synop_6 = "", ""
   for row in rows[start_row:]:
      hour_synop = row[0][7:9]
      if hour_synop == "12": synop_12 = row[0]
      elif hour_synop == "6 ": synop_6 = row[0]

   res = []

   for i in synop_12.split("&nbsp"):
      if i[0:4] == "555 ":
         try: res.append( int(i[18:21]) )
         except Exception as e:
            continue

   if len(res) == 0: res.append(None)

   for i in synop_6.split("&nbsp"):
      if "BOT" in i and "80000" in i:
         i = i.split("80000 ")
         try: res.append( int(i[-1][14:17]) )
         except Exception as e:
            continue

   if len(res) == 1: res.append(None)
   
   if res[0] is not None and res[1] is not None:
      return res
   elif res[0] is None and res[1] is not None:
      return None, res[1]
   elif res[0] is not None and res[1] is None:
      return res[0], None
   else: return None, None


try:     obs["ff_td"], obs["fx_yd"] = find_ff_fx( tables[0], 1 )
except Exception as e: print(e)
try:     obs["ff_yd"], obs["fx_2d"] = find_ff_fx( tables[1], 1 )
except:  pass
try:     obs["ff_2d"], obs["fx_3d"] = find_ff_fx( tables[2], 1 )
except:  print("Error while reading data! schroetej31 userpage down?")


if "ff_td" in obs.keys() and obs["ff_td"] is not None:
   print("ff @12z today:", float(obs["ff_td"]/10) )
else: print("no ff obs @12z today (yet)!")

if "ff_yd" in obs.keys() and obs["ff_yd"] is not None:
   print("ff @12z yesterday:", float(obs["ff_yd"]/10) )
else: print("no ff obs @12z yesterday!")

if "ff_2d" in obs.keys() and obs["ff_2d"] is not None:
   print("ff @12z the day before yesterday:", float(obs["ff_2d"]/10) )
else: print("no ff obs @12z the day before yesterday!")

if "fx_yd" in obs.keys() and obs["fx_yd"] is not None:
   print("fx @6z today (for yesterday):", float(obs["fx_yd"]/10) )
else: print("no fx obs @6z today!")

if "fx_2d" in obs.keys() and obs["fx_2d"] is not None:
   print("fx @6z yesterday (for day before yesterday):", float(obs["fx_2d"]/10) )
else: print("no fx obs @6z yesterday!")

if "fx_3d" in obs.keys() and obs["fx_3d"] is not None:
   print("fx @6z the day before yesterday (for previous day):", float(obs["fx_3d"]/10) )
else: print("no fx obs @6z the day before yesterday!")


# add columns
sql = []
for param in ("fx24","ff12","rr1x","sun","sunday"):
   sql.append(f"ALTER TABLE `live` ADD IF NOT EXISTS `{param}` SMALLINT(5) NULL DEFAULT NULL")

hour = dt.utcnow().hour

if len(sys.argv) == 2:
   dk = " ON DUPLICATE KEY UPDATE ucount=ucount+1, sun=VALUES(sun)"
else: dk = ""

if "sd1" in obs.keys() and hour >= 12 and hour <= 14:
   try:    sd1 = int( np.round( obs["sd1"] ) )
   except: pass
   else:
      day = DOF.strftime( Ymd )
      ts  = dt2ts( DOF )
      ts += 42600
      print(day)
      print(ts)
      print("SD1 (min):", sd1)
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,sun) VALUES (10381,{day},{ts},1150,'bufr',{sd1}){dk};")

if len(sys.argv) == 2:
   dk = " ON DUPLICATE KEY UPDATE ucount=ucount+1, sd24=VALUES(sd24)"
else: dk = ""

if "sd24" in obs.keys():
   try:    sd24 = int( np.round( obs["sd24"] ) )
   except: pass
   else:
      date = DOF + d
      day = date.strftime( Ymd )
      ts  = dt2ts( date )
      print(day)
      print(ts)
      print("SD24 (min):", sd24)
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,sunday) VALUES (10381,{day},{ts},0,'bufr',{sd24}) ON DUPLICATE KEY UPDATE ucount=ucount+1, sunday=VALUES(sunday);")

if len(sys.argv) == 2:
   dk = " ON DUPLICATE KEY UPDATE ucount=ucount+1, rr1x=VALUES(rr1x)"
else: dk = ""

if "rr1x" in obs.keys():
   date = DOF
   day  = date.strftime( Ymd )
   ts  = dt2ts( date )
   try:    rr1x = int( obs["rr1x"] * 10 )
   except: pass
   else:
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,rr1x) VALUES (10381,{day},{ts},0,'bufr',{rr1x}){dk};")

if len(sys.argv) == 2:
   dk = " ON DUPLICATE KEY UPDATE ucount=ucount+1, fx24=VALUES(fx24)"
else: dk = ""

if "fx_yd" in obs.keys():
   date = DOF
   day  = date.strftime( Ymd )
   ts  = dt2ts( date )
   try:
      fx24 = int( obs["fx_yd"] * 10 )
      if fx24 == 0: sys.exit()
   except: pass
   else:
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts},0,'bufr',{fx24}){dk};")

if "fx_2d" in obs.keys():
   date = DOF - d
   day  = date.strftime( Ymd )
   ts  = dt2ts( date )
   try:
      fx24 = int( obs["fx_2d"] * 10 )
      if fx24 == 0: sys.exit()
   except: pass
   else:
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts},0,'bufr',{fx24}){dk};")

if "fx_3d" in obs.keys():
   date = DOF - 2*d
   day  = date.strftime( Ymd )
   ts  = dt2ts( date )
   try:
      fx24 = int( obs["fx_3d"] * 10 )
      if fx24 == 0: sys.exit()
   except: pass
   else:
      sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,fx24) VALUES (10381,{day},{ts},0,'bufr',{fx24}){dk};")

today = dt.today()
today = today.replace(hour=0, minute=0, second=0, microsecond=0)

if len(sys.argv) == 2:
   dk = " ON DUPLICATE KEY UPDATE ucount=ucount+1, ff=VALUES(ff)"
else: dk = ""

if obs["ff_td"] and hour >= 12 and hour <= 14:
   day = today.strftime( Ymd )
   ts = dt2ts( today ) + 42600
   ff12 = obs["ff_td"]
   h = 1150
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff) VALUES (10381,{day},{ts},{h},'bufr',{ff12}){dk}")
if obs["ff_yd"] and hour >= 12 and hour <= 14:
   day = (today-d).strftime( Ymd )
   ts = dt2ts( today-d ) + 42600
   ff12 = obs["ff_yd"]
   h = 1150
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff) VALUES (10381,{day},{ts},{h},'bufr',{ff12}){dk}")
if obs["ff_2d"] and hour >= 12 and hour <= 14:
   dby = today-d-d
   day = (dby).strftime( Ymd )
   ts = dt2ts(dby) + 42600
   ff12 = obs["ff_2d"]
   h = 1150
   sql.append(f"INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,ff) VALUES (10381,{day},{ts},{h},'bufr',{ff12}){dk}")

##sql.append( "INSERT INTO live (statnr,datum,datumsec,stdmin,msgtyp,rr1x) VALUES (10381,20230305,1678017600,1200,'bufr',null) ON DUPLICATE KEY UPDATE ucount=ucount+1, stdmin=VALUES(stdmin), rr1x=VALUES(rr1x);")


for s in sql:
   print(s)
   try:  cur.execute( s )
   except Exception as e:
      print(e)

db.commit()
