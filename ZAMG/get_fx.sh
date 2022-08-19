#!/bin/bash
#receive the fx values for Austrian WMO stations from ZAMG OpenData

base="https://dataset.api.hub.zamg.ac.at/v1/station/historical/"
resource_id="klima-v1-1d"
parameters="vvmax"
station_ids="5904,5917,11803,11804"
start=${1:-$(date +%Y-%m-%d)}
if [ -z $2 ]; then
   end=$start
else
   end=$2
fi

wget "${base}${resource_id}?parameters=${parameters}&start=${start}&end=${end}&station_ids=${station_ids}" -O ${start}.json
