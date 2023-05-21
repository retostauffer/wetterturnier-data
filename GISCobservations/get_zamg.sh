#!/bin/bash
#receive the fx values for Austrian WMO stations from ZAMG OpenData

base="https://dataset.api.hub.zamg.ac.at/v1/station/historical/"
resource_id="klima-v1-10min"
parameters="FF,FFX,RR,SO"
station_ids="5904,5917,11803,11804"
start=${1:-$(date +%Y-%m-%d --date="1 day ago")}
if [ -z $2 ]; then
   end=$(date +%Y-%m-%d)
else
   end=$2
fi

mkdir -p ZAMG

wget "${base}${resource_id}?parameters=${parameters}&start=${start}&end=${end}&station_ids=${station_ids}" -O "ZAMG/${start}.test.json" && python3 extract_zamg.py ${start}
