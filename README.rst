



GISCobservations
================

virtualenv --no-site-packages venv
source venv/bin/activate   # activate virtualenv
pip install mysqlclient    # database access
pip install matplotlib     # For the synop symbols


export BUFR_TABLES=/path/to/your/bufr/tables
cd GISCobservations
python bufr.py
