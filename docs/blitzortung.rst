blitzortung
==================

I dont want to spend too much time to explain this mini thing.
The `Institute for Atmospheric and Cryospheric Sciences (ACINN) <http://acinn.uibk.ac.at>`_
is a member of the `Blitzortung.org <http://blitzortung.org>`_ network
and allowd to redistribute the raw data. At the ACINN there is a script
running to procude live lightning data plots. During this process a small
sqlite3 file is created which is copied via ``ssh`` to the prognose
server (into the ``blitzortung`` folder of this repository).

The :file:`blitzortug.R` script is run every X minutes
via cron and checks the current sqlite file to draw a small map for each
of our Wetterturnier cities (specified via :file:`stations.txt`)
and places a figure and a small file containing information about the last run
(to check whether the data are outdated) in the ``blitzortung`` folder.

This folder is linked to the webserver to grant access on the frontend, namely
via `Wetterturnier Wordpress Plugin Lightning Activity Widget <http://wetterturnier-wordpress-plugin.readthedocs.io/en/latest/thewidgets.html#lightning-activity>`_ .

.. note:: If there is someting wrong with the data one might ask Reto Stauffer
    or Georg J. Mayr (from the ACINN) to see wheter there is someting wrong
    or has been changed.

.. todo:: If we could replace this script with a python script we might be
    able to somewhen remove the R installation from the server (except the
    data handling from the not yet published and not yet finished R package
    wetterturnier, ask Reto Stauffer).


To get the code run (requires the sqlite3 file from the sqlite folder):

.. code-block:: bash

    ## Simply to this:
    Rscript blitzortung.R
