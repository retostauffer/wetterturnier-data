#!/bin/bash
#receive the fx values for Austrian WMO stations from ZAMG OpenData

base="https://dataset.api.hub.zamg.ac.at/v1/station/historical/"
resource_id="klima-v1-10min"
parameters="FF,FFX,RR,SO"
station_ids="5904,5917,11803,11804"
yd=${1:-$(date +%Y-%m-%d --date="1 day ago")}
ts_yd=$(date --date="$yd" +"%s")
echo $ts_yd
ts_yd=$((ts_yd+86400))
echo $ts_yd
date -d @$ts_yd +"%Y-%m-%d"
td=$(date -d @${ts_yd} +"%Y-%m-%d")

mkdir -p ZAMG

wget "${base}${resource_id}?parameters=${parameters}&start=${yd}&end=${td}&station_ids=${station_ids}" -O "ZAMG/${yd}.json" && python3 extract_zamg.py ${yd}
