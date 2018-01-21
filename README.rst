


Wetterturnier Data Tools
========================

This repository is part of the `Wetterturnier.de <http://www.wetterturnier.de>`_
system.

GISCobservations
================

virtualenv --no-site-packages venv
source venv/bin/activate   # activate virtualenv
pip install mysqlclient    # database access
pip install matplotlib     # For the synop symbols


export BUFR_TABLES=/path/to/your/bufr/tables
cd GISCobservations
python bufr.py


License Information
===================

The software in this repository is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version. The full :download:`LICENSE` file is included in the repository
and/or can be found on `gnu.org <https://www.gnu.org/licenses/gpl-3.0.txt>`_.


