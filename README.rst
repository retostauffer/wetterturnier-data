What  is "Wetterturnier"
-------------------------

The "Berliner Wetterturnier" as it has been known as in the beginning was
launched in the year 2000 at the Institute of Meteorology at the FU Berlin.
Since 2005 five cities in Central Europe are included.

`Wetterturnier <http://wetterturnier.de>`_ is a platform where *hobby meteorologists*,
*experts* and *statistical forecast model developer* battle against each other. The
goal is to predict a set of meteorological variables, such as sunshine duration, wind speed,
or temperature as good as possible for the consecutive two days.

*This plugin is the frontend core* of the whole system providing full wordpress integration
(user management, messaging services, forums) and the platform where our users can *submit
their forecasts/bets*. Furthermore this plugin provides live ranking tables, a leader-board,
a data archive, and access to a set of important data sets such as observations and forecast maps.

.. image:: images/screenshot_frontend.png
   :width: 800px
   :height: 396px
   :scale: 100 %
   :alt: Screenshot Frontend
   :align: center

Please note that this is only one part of the system. To get the whole system running
the `Wetterturnier Wordpress Plugin <https://github.com/retostauffer/wp-wetterturnier>`_.
For more information please visit the `documentation on readthedocs <http://wetterturnier-backend.readthe
docs.io/en/latest/overview.html>_`.



Wetterturnier Data Tools
========================

This repository is part of the `Wetterturnier.de <http://www.wetterturnier.de>`_ system.
The `documentation for this repository can be found on readthedocs <http://wetterturnier-data.readthedocs.io/en/latest/>`_

GISCobservations
================


.. code-block:: bash

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


